from datetime import datetime, timedelta

import transaction
from freezegun import freeze_time


def test_user_activity_default(users_repository, user_david):
    assert not user_david.is_active


def test_user_activity_in_use(app, user_david):
    app.get("/lectures/", user=user_david)
    assert user_david.is_active


def test_user_activity_not_anymore_in_use(app, user_david):
    app.get("/lectures/", user=user_david)
    assert user_david.is_active

    with freeze_time(datetime.utcnow() + timedelta(minutes=29)):
        assert user_david.is_active

    with freeze_time(datetime.utcnow() + timedelta(minutes=31)):
        assert not user_david.is_active


def test_user_set_team(team_zam, user_david):
    from zam_repondeur.models import DBSession, User

    DBSession.add(user_david)
    user_david.teams.append(team_zam)
    assert DBSession.query(User).first().teams == [team_zam]


def test_user_unset_team(team_zam, user_david):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)
        assert user_david.teams == []
        user_david.teams.append(team_zam)

    with transaction.manager:
        DBSession.add(user_david)
        assert user_david.teams == [team_zam]
        user_david.teams.remove(team_zam)

    with transaction.manager:
        DBSession.add(user_david)
        assert user_david.teams == []


def test_user_password_is_stored_as_a_secure_hash(user_david):
    from sqlalchemy_utils.types.password import Password

    assert isinstance(user_david.password, Password)
    assert user_david.password.hash.startswith(b"$pbkdf2-sha512$")


def test_verify_correct_user_password(user_david):
    assert user_david.password == "secret"


def test_verify_incorrect_user_password(user_david):
    assert user_david.password != "badpassword"
