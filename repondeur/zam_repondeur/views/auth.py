from datetime import datetime
from typing import Any

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.security import NO_PERMISSION_REQUIRED, remember, forget
from pyramid.view import forbidden_view_config, view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Team, User
from zam_repondeur.resources import Root


@view_defaults(route_name="team_login", permission=NO_PERMISSION_REQUIRED, context=Root)
class TeamLogin:
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request
        self.context = context

    @view_config(request_method="GET", renderer="auth/team_login.html")
    def get(self) -> Any:
        return {"team_name": self.request.params.get("nom", "")}

    @view_config(request_method="POST")
    def post(self) -> Any:
        team_name = self.request.POST.get("team_name")
        team_password = self.request.POST.get("team_password")

        print(f"team_name = {team_name!r}")
        print(f"team_password = {team_password!r}")

        # Team name is required
        if not team_name:
            self.request.session["missing_team_name"] = True
            return HTTPFound(location=self.request.route_url("team_login"))

        # Team password is required
        if not team_password:
            self.request.session["missing_team_password"] = True
            return HTTPFound(
                location=self.request.route_url("team_login", _query={"nom": team_name})
            )

        # Check team credentials
        team = DBSession.query(Team).filter_by(name=team_name).first()
        print(f"team = {team}")
        print(f"verify = {team.password == team_password}")
        if team is None or team.password != team_password:
            self.request.session["bad_credentials"] = True
            return HTTPFound(
                location=self.request.route_url("team_login", _query={"nom": team_name})
            )

        # Successful team auth!
        self.request.session["authenticated_teamid"] = team.pk

        return HTTPFound(location=self.next_url)

    @property
    def next_url(self) -> Any:
        url = self.request.params.get("source")
        if self.request.user is None:
            query = {"source": url} if url else {}
            url = self.request.route_url("user_login", _query=query)
        if url is None:
            url = self.request.resource_url(self.context["lectures"])
        return url


@view_defaults(route_name="user_login", permission=NO_PERMISSION_REQUIRED, context=Root)
class UserLogin:
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request
        self.context = context

    @view_config(request_method="GET", renderer="auth/user_login.html")
    def get(self) -> Any:

        # Skip the form if we're already logged in
        if self.request.unauthenticated_userid:
            next_url = self.request.params.get("source")
            if next_url is None or next_url == self.request.route_url("user_login"):
                next_url = self.request.resource_url(self.context["lectures"])
            return HTTPFound(location=next_url)

        return {"email": self.request.GET.get("email", "")}

    @view_config(request_method="POST", renderer="auth/user_login.html")
    def post(self) -> Any:
        email = User.normalize_email(self.request.POST.get("email", ""))

        # Show error message if email is missing
        if not email:
            self.request.session["missing_email"] = True
            return HTTPFound(location=self.request.route_url("user_login"))

        # Ask for password if only email was submitted
        password = self.request.POST.get("password")
        if password is None:
            return {"email": email}

        # Try to authenticate user if we have both email and password
        user = DBSession.query(User).filter_by(email=email).first()
        if user is None:
            print(f"Authentication failed for {email} (no such user)")
            authentication_failed = True
        elif user.password is None:
            print(f"Authentication failed for {email} (no password defined)")
            authentication_failed = True
        elif user.password != password:
            print(f"Authentication failed for {email} (bad password)")
            authentication_failed = True
        else:
            print(f"Authentication succeeded for {email}")
            authentication_failed = False

        # Go back to form and show error message
        if authentication_failed:
            self.request.session["bad_credentials"] = True
            return HTTPFound(location=self.request.route_url("user_login"))

        # Successful authentication
        user.last_login_at = datetime.utcnow()

        next_url = self.next_url
        if not user.name:
            next_url = self.request.route_url("welcome", _query={"source": next_url})

        headers = remember(self.request, user.pk)
        print(headers)
        return HTTPFound(location=next_url, headers=headers)

    @property
    def next_url(self) -> Any:
        url = self.request.params.get("source")
        if url is None or url == self.request.route_url("user_login"):
            url = self.request.resource_url(self.context["lectures"])
        return url


@view_defaults(route_name="welcome", context=Root)
class Welcome:
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request
        self.context = context

    @view_config(request_method="GET", renderer="auth/welcome.html")
    def get(self) -> Any:
        return {"name": self.request.user.name or self.request.user.default_name()}

    @view_config(request_method="POST")
    def post(self) -> Any:
        name = self.request.params.get("name")
        if not name:
            self.request.session["missing_name"] = True
            return HTTPFound(location=self.request.route_url("welcome"))

        self.request.user.name = User.normalize_name(name)
        next_url = self.request.params.get("source") or self.request.resource_url(
            self.context["lectures"]
        )
        return HTTPFound(location=next_url)


@view_config(route_name="logout", permission=NO_PERMISSION_REQUIRED)
def logout(request: Request) -> Any:

    # Clear user authentication cookie
    headers = forget(request)

    # Clear team authentication from session
    request.session.pop("authenticated_teamid", None)

    next_url = request.route_url("user_login")
    return HTTPFound(location=next_url, headers=headers)


@forbidden_view_config()
def forbidden_view(request: Request) -> Any:

    # Redirect to the user login page if needed
    if request.user is None:
        return HTTPFound(
            location=request.route_url("user_login", _query={"source": request.url})
        )

    # # Redirect to the team login page if needed
    # if request.team is None:
    #     return HTTPFound(
    #         location=request.route_url("team_login", _query={"source": request.url})
    #     )

    # Redirect authenticated ones to the home page with an error message
    request.session.flash(
        Message(
            cls="warning",
            text="L’accès à cette lecture est réservé aux personnes autorisées.",
        )
    )
    return HTTPFound(location=request.resource_url(request.root))
