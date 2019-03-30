import transaction
from datetime import date
from typing import Dict, List, Optional, Union

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload

from zam_repondeur.fetch import get_articles
from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import get_session
from zam_repondeur.fetch.an.dossiers.models import Chambre
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Dossier, Lecture, Texte, User
from zam_repondeur.models.events.lecture import ArticlesRecuperes
from zam_repondeur.models.users import Team
from zam_repondeur.resources import (
    AmendementCollection,
    LectureCollection,
    LectureResource,
)
from zam_repondeur.tasks.fetch import fetch_articles, fetch_amendements


@view_config(context=LectureCollection, renderer="lectures_list.html")
def lectures_list(
    context: LectureCollection, request: Request
) -> Union[Response, dict]:

    all_lectures = context.models()

    lectures = [
        lecture
        for lecture in all_lectures
        if lecture.owned_by_team is None or lecture.owned_by_team in request.user.teams
    ]

    if not lectures:
        return HTTPFound(request.resource_url(context, "add"))

    return {"lectures": lectures}


@view_defaults(context=LectureCollection, name="add")
class LecturesAdd:
    def __init__(self, context: LectureCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossiers_by_uid: Dict[str, Dossier] = {
            dossier.uid: dossier for dossier in DBSession.query(Dossier).all()
        }

    @view_config(request_method="GET", renderer="lectures_add.html")
    def get(self) -> dict:
        lectures = self.context.models()
        return {
            "dossiers": [
                {"uid": uid, "titre": dossier.titre}
                for uid, dossier in self.dossiers_by_uid.items()
            ],
            "lectures": lectures,
            "hide_lectures_link": len(lectures) == 0,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        dossier = self._get_dossier()
        lecture = self._get_lecture(dossier)
        get_articles(lecture)
        ArticlesRecuperes.create(request=None, lecture=lecture)
        # Call to fetch_* tasks below being asynchronous, we need to make
        # sure the lecture already exists once and for all in the database
        # for future access. Otherwise, it may create many instances and
        # thus many objects within the database.
        transaction.commit()
        fetch_amendements(lecture.pk)
        self.request.session.flash(
            Message(
                cls="success",
                text=(
                    "Lecture créée avec succès, amendements en cours de récupération."
                ),
            )
        )
        return HTTPFound(
            location=self.request.resource_url(
                self.context[lecture.url_key], "amendements"
            )
        )

    def _get_dossier(self) -> Dossier:
        # TODO: avoid retrieving all Dossiers.
        try:
            dossier_uid = self.request.POST["dossier"]
        except KeyError:
            raise HTTPBadRequest
        try:
            dossier = self.dossiers_by_uid[dossier_uid]
        except KeyError:
            raise HTTPNotFound
        return dossier

    def _get_lecture(self, dossier: Dossier) -> Lecture:
        # TODO: deal with chambre
        chambre = Chambre.AN
        try:
            texte_uid, organe, partie_str = self.request.POST["lecture"].split("-", 2)
        except (KeyError, ValueError):
            raise HTTPBadRequest
        partie: Optional[int]
        if partie_str == "":
            partie = None
        else:
            partie = int(partie_str)
        texte = Texte.get(uid=texte_uid)
        if not texte:
            raise HTTPBadRequest
        session = get_session(chambre, texte)

        # TODO: create all lectures and then activate explicitely?
        if Lecture.exists(str(chambre), session, texte, partie, organe):
            self.request.session.flash(
                Message(cls="warning", text="Cette lecture existe déjà…")
            )
            lecture = Lecture.get(str(chambre), session, texte, partie, organe)
            if not lecture:
                # TODO: force mypy?
                raise HTTPBadRequest
        else:
            lecture = Lecture.create(
                str(chambre),
                session,
                texte,
                titre="TODO",
                organe=organe,
                dossier=dossier,
                partie=partie,
                owned_by_team=self.request.team,
            )
        return lecture


@view_defaults(context=LectureResource)
class LectureView:
    def __init__(self, context: LectureResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.model()

    @view_config(request_method="POST")
    def post(self) -> Response:
        if self.request.user.can_delete_lecture:
            DBSession.delete(self.lecture)
            DBSession.flush()
            self.request.session.flash(
                Message(cls="success", text="Lecture supprimée avec succès.")
            )
        else:
            self.request.session.flash(
                Message(
                    cls="warning",
                    text="Vous n’avez pas les droits pour supprimer une lecture.",
                )
            )
        return HTTPFound(location=self.request.resource_url(self.context.parent))


@view_config(context=AmendementCollection, renderer="amendements.html")
def list_amendements(context: AmendementCollection, request: Request) -> dict:
    lecture_resource = context.parent
    lecture = lecture_resource.model(joinedload("articles"), joinedload("user_tables"))
    return {
        "lecture": lecture,
        "lecture_resource": lecture_resource,
        "current_tab": "index",
        "amendements": lecture.amendements,
        "articles": lecture.articles,
        "check_url": request.resource_path(context.parent, "check"),
        "timestamp": lecture.modified_amendements_at_timestamp,
    }


@view_defaults(
    context=LectureResource,
    renderer="transfer_amendements.html",
    name="transfer_amendements",
)
class TransferAmendements:
    def __init__(self, context: LectureResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.from_index = bool(request.GET.get("from_index"))
        self.amendements_nums: list = self.request.GET.getall("nums")

    @view_config(request_method="GET")
    def get(self) -> dict:
        from_save = bool(self.request.GET.get("from_save"))
        lecture = self.context.model(joinedload("amendements"))
        my_table = self.request.user.table_for(lecture)
        amendements = [
            amendement
            for amendement in lecture.amendements
            if str(amendement.num) in self.amendements_nums
        ]
        amendements_with_table, amendements_without_table = [], []
        for amendement in amendements:
            if amendement.user_table:
                amendements_with_table.append(amendement)
            else:
                amendements_without_table.append(amendement)
        return {
            "lecture": lecture,
            "amendements": amendements,
            "amendements_with_table": amendements_with_table,
            "amendements_without_table": amendements_without_table,
            "users": self.target_users,
            "from_index": int(self.from_index),
            "from_save": from_save,
            "show_transfer_to_index": bool(amendements_with_table),
            "show_transfer_to_myself": any(
                amendement.user_table is not my_table
                for amendement in amendements_with_table
            )
            or not amendements_with_table,
            "back_url": self.back_url,
        }

    @property
    def target_users(self) -> List[User]:
        team: Optional[Team] = self.request.team
        if team is not None:
            return team.everyone_but_me(self.request.user)
        return User.everyone_but_me(self.request.user)

    @property
    def back_url(self) -> str:
        return self.index_url if self.from_index else self.table_url

    @property
    def index_url(self) -> str:
        return self.request.resource_url(self.context["amendements"])

    @property
    def table_url(self) -> str:
        return self.request.resource_url(
            self.context["tables"][self.request.user.email]
        )


@view_config(context=LectureResource, name="manual_refresh")
def manual_refresh(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    fetch_amendements(lecture.pk)
    fetch_articles(lecture.pk)
    request.session.flash(
        Message(
            cls="success",
            text=(
                "Rafraichissement des amendements et des articles en cours. "
                "Vous serez notifié·e dès que les nouvelles informations "
                "seront disponibles."
            ),
        )
    )
    return HTTPFound(location=request.resource_url(context, "amendements"))


@view_config(context=LectureResource, name="check", renderer="json")
def lecture_check(context: LectureResource, request: Request) -> dict:
    lecture = context.model()
    timestamp = float(request.GET["since"])
    modified_amendements_at_timestamp = lecture.modified_amendements_at_timestamp
    modified_amendements_numbers: list = []
    if timestamp < modified_amendements_at_timestamp:
        modified_amendements_numbers = lecture.modified_amendements_numbers_since(
            timestamp
        )
    return {
        "modified_amendements_numbers": modified_amendements_numbers,
        "modified_at": modified_amendements_at_timestamp,
    }


@view_config(route_name="choices_lectures", renderer="json")
def choices_lectures(request: Request) -> dict:
    uid = request.matchdict["uid"]
    dossier = Dossier.get(uid=uid)
    if not dossier:
        return {}
    return {
        "lectures": [
            {"key": lecture.key, "label": lecture.label} for lecture in dossier.lectures
        ]
    }


@view_config(context=LectureResource, name="journal", renderer="lecture_journal.html")
def lecture_journal(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    return {"lecture": lecture, "today": date.today()}


@view_config(context=LectureResource, name="options", renderer="lecture_options.html")
def lecture_options(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    return {"lecture": lecture, "lecture_resource": context, "current_tab": "options"}
