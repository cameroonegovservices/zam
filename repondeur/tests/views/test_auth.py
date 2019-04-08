import time

import pytest
import transaction


@pytest.fixture
def unnamed_user(db):
    from zam_repondeur.models import User

    with transaction.manager:
        return User.create(email="jane.doe@example.com", password="secret")


@pytest.fixture
def passwordless_user(db):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        user = User(email="old@example.com")
        DBSession.add(user)

    return user


class TestUserLogin:
    def test_unauthentified_user_can_view_user_login_page(self, app):
        resp = app.get("/identification/utilisateur")
        assert resp.status_code == 200

    def test_login_page_asks_for_email(self, app):
        resp = app.get("/identification/utilisateur")
        assert list(resp.form.fields.keys()) == ["email", "submit"]
        assert resp.form.fields["email"][0].attrs["type"] == "email"

    def test_user_gets_an_error_message_when_email_is_missing(self, app):
        resp = app.post("/identification/utilisateur", {"email": ""})

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/identification/utilisateur"
        resp = resp.follow()
        assert "La saisie d’une adresse de courriel est requise." in resp.text

    def test_user_gets_asked_for_password_when_email_is_given(self, app, user_david):
        resp = app.post("/identification/utilisateur", {"email": user_david.email})

        assert resp.status_code == 200
        assert list(resp.form.fields.keys()) == ["email", "password", "submit"]
        assert resp.form.fields["email"][0].attrs["type"] == "hidden"
        assert resp.form.fields["password"][0].attrs["type"] == "password"

    def test_login_page_asks_for_password_if_email_was_provided(self, app):
        resp = app.get("/identification/utilisateur?email=foo")
        assert list(resp.form.fields.keys()) == ["email", "password", "submit"]
        assert resp.form.fields["email"][0].attrs["type"] == "hidden"
        assert resp.form.fields["password"][0].attrs["type"] == "password"

    def test_user_gets_an_error_message_when_email_is_wrong(self, app):
        resp = app.post(
            "/identification/utilisateur",
            {"email": "nobody@example.com", "password": "secret"},
        )

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/identification/utilisateur"
        resp = resp.follow()
        assert "Le courriel ou le mot de passe est incorrect." in resp.text

    def test_user_gets_an_error_message_when_password_is_wrong(self, app, user_david):
        resp = app.post(
            "/identification/utilisateur",
            {"email": user_david.email, "password": "badpassword"},
        )

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/identification/utilisateur"
        resp = resp.follow()
        assert "Le courriel ou le mot de passe est incorrect." in resp.text

    def test_user_gets_an_auth_cookie_after_successful_login(self, app, user_david):
        assert "auth_tkt" not in app.cookies  # no auth cookie yet

        app.post(
            "/identification/utilisateur",
            {"email": user_david.email, "password": "secret"},
        )

        assert "auth_tkt" in app.cookies  # and now we have the auth cookie

        domains = {cookie.domain for cookie in app.cookiejar}
        assert domains == {".zam.test", "zam.test"}

        for cookie in app.cookiejar:
            assert cookie.name == "auth_tkt"
            assert cookie.path == "/"
            assert cookie.secure is True

            # Auth cookie should expire after 7 days
            assert cookie.expires == int(time.time()) + (7 * 24 * 3600)

            # We want users to be able to follow an e-mailed link to the app
            # (see: https://www.owasp.org/index.php/SameSite)
            assert cookie.get_nonstandard_attr("SameSite") == "Lax"

    def test_user_gets_redirected_to_source_after_successful_login(
        self, app, user_david
    ):

        resp = app.post(
            "/identification/utilisateur?source=https%3A%2F%2Fzam.test%2Flectures%2F",
            {"email": user_david.email, "password": "secret"},
        )

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/lectures/"

    def test_passwordless_user_cannot_login(self, app, passwordless_user):
        resp = app.post(
            "/identification/utilisateur",
            {"email": passwordless_user.email, "password": ""},
        )
        assert resp.status_code == 302
        assert resp.location == "https://zam.test/identification/utilisateur"
        resp = resp.follow()
        assert "Le courriel ou le mot de passe est incorrect." in resp.text

    def test_authentified_user_gets_redirected(self, app, user_david):
        resp = app.get("/identification/utilisateur", user=user_david)
        assert resp.status_code == 302
        assert resp.location == f"https://zam.test/lectures/"


class TestLogout:
    def test_user_loses_the_auth_cookie_on_logout(self, app, user_david):
        app.post(
            "/identification/utilisateur",
            {"email": user_david.email, "password": "secret"},
        )
        assert "auth_tkt" in app.cookies  # the auth cookie is set

        app.get("/deconnexion")
        assert "auth_tkt" not in app.cookies  # the auth cookie is gone


class TestAuthentication:
    def test_unauthenticated_user_is_redirected_to_login_page(self, app):
        resp = app.get("/lectures/add")
        assert resp.status_code == 302
        assert resp.location == (
            "https://zam.test/identification/utilisateur"
            "?source=https%3A%2F%2Fzam.test%2Flectures%2Fadd"
        )

    def test_authenticated_user_is_not_redirected_to_login_page(self, app, user_david):
        app.post(
            "/identification/utilisateur",
            {"email": user_david.email, "password": "secret"},
        )
        resp = app.get("/lectures/add")
        assert resp.status_code == 200

    def test_authenticated_user_without_password_gets_logged_out(self, app, user_david):
        from zam_repondeur.models import DBSession

        app.post(
            "/identification/utilisateur",
            {"email": user_david.email, "password": "secret"},
        )
        resp = app.get("/lectures/add")
        assert resp.status_code == 200

        with transaction.manager:
            DBSession.add(user_david)
            user_david.password = None

        resp = app.get("/lectures/add")
        assert resp.status_code == 302
        assert resp.location == (
            "https://zam.test/identification/utilisateur"
            "?source=https%3A%2F%2Fzam.test%2Flectures%2Fadd"
        )


class TestNewUserOnboarding:
    def test_unnamed_user_is_asked_to_enter_their_name(self, app, unnamed_user):
        from zam_repondeur.models import DBSession, User

        resp = app.post(
            "/identification/utilisateur",
            {"email": unnamed_user.email, "password": "secret"},
        )
        assert resp.status_code == 302
        assert (
            resp.location
            == "https://zam.test/bienvenue?source=https%3A%2F%2Fzam.test%2Flectures%2F"
        )
        resp = resp.follow()

        assert resp.form["name"].value == "Jane Doe"  # prefilled based on email

        resp.form["name"] = " Something Else  "
        resp.form.submit()

        user = DBSession.query(User).filter_by(email="jane.doe@example.com").first()
        assert user.name == "Something Else"

    def test_unnamed_user_cannot_leave_their_name_empty(self, app, unnamed_user):
        resp = app.post(
            "/identification/utilisateur",
            {"email": unnamed_user.email, "password": "secret"},
        ).follow()

        resp.form["name"] = ""
        resp = resp.form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/bienvenue"
        resp = resp.follow()
        assert "La saisie d’un nom est requise." in resp.text


class TestWelcomePage:
    def test_user_with_name_can_edit_it(self, app, user_david):
        from zam_repondeur.models import DBSession, User

        resp = app.get("/bienvenue", user=user_david)
        assert resp.status_code == 200
        assert resp.form["name"].value == "David"
        resp.form["name"] = " Something Else  "
        resp.form.submit()

        user = DBSession.query(User).filter_by(email=user_david.email).first()
        assert user.name == "Something Else"

    def test_user_with_a_name_skips_the_welcome_page(self, app, user_david):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(user_david)

        assert user_david.name == "David"

        resp = app.post(
            "/identification/utilisateur",
            {"email": "david@example.com", "password": "secret"},
        )
        assert resp.status_code == 302
        assert resp.location == f"https://zam.test/lectures/"


class TestTeamLogin:
    def test_unauthentified_user_can_view_team_login_page(self, app):
        resp = app.get("/identification/equipe")
        assert resp.status_code == 200
