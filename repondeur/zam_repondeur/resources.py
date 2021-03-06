from typing import Any, Iterator, List, Optional, Tuple, cast

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.security import Allow, Authenticated, Deny
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from zam_repondeur.models import (
    Amendement,
    Article,
    DBSession,
    Lecture,
    User,
    UserTable,
)


# Access Control Entry (action, principal, permission)
ACE = Tuple[str, str, str]


class ResourceNotFound(HTTPNotFound):
    pass


class Resource(dict):
    """
    Location-aware resource

    See: https://docs.pylonsproject.org/projects/pyramid/en/latest/
    narr/resources.html#location-aware-resources
    """

    __name__: Optional[str] = None
    __parent__: Optional["Resource"] = None

    def __init__(self, name: str, parent: "Resource") -> None:
        self.__name__ = name
        self.__parent__ = parent

    @property
    def parent(self) -> Optional["Resource"]:
        return self.__parent__

    @property
    def parents(self) -> Iterator["Resource"]:
        parent = self.parent
        while parent is not None:
            yield parent
            parent = parent.parent

    @property
    def ancestors(self) -> List["Resource"]:
        return list(reversed(list(self.parents)))

    def add_child(self, child: "Resource") -> None:
        self[child.__name__] = child


class Root(Resource):
    __acl__ = [(Allow, Authenticated, "view")]

    def __init__(self, _request: Request) -> None:
        self.add_child(LectureCollection(name="lectures", parent=self))


class LectureCollection(Resource):
    def models(self) -> List[Lecture]:
        return Lecture.all()

    def __getitem__(self, key: str) -> Resource:
        try:
            chambre, session_or_legislature, num_texte, organe = key.split(".")
            partie: Optional[int]
            if "-" in num_texte:
                num_texte, partie_str = num_texte.split("-", 1)
                partie = int(partie_str)
            else:
                partie = None
        except ValueError:
            raise KeyError
        return LectureResource(
            name=key,
            parent=self,
            chambre=chambre,
            session_or_legislature=session_or_legislature,
            num_texte=int(num_texte),
            partie=partie,
            organe=organe,
        )


class LectureResource(Resource):
    def __acl__(self) -> List[ACE]:
        # If the lecture is owned by team, then team members can view it, but not others
        if self.lecture.owned_by_team is not None:
            return [
                (Allow, f"team:{self.lecture.owned_by_team.pk}", "view"),
                (Deny, Authenticated, "view"),
            ]

        # If the lecture is not owned by any team, anyone can view it
        return [(Allow, Authenticated, "view")]

    def __init__(
        self,
        name: str,
        parent: Resource,
        chambre: str,
        session_or_legislature: str,
        num_texte: int,
        partie: Optional[int],
        organe: str,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.chambre = chambre
        self.session_or_legislature = session_or_legislature
        self.num_texte = num_texte
        self.partie = partie
        self.organe = organe
        self.add_child(AmendementCollection(name="amendements", parent=self))
        self.add_child(ArticleCollection(name="articles", parent=self))
        self.add_child(TableCollection(name="tables", parent=self))

    @reify
    def lecture(self) -> Lecture:
        return self.model()

    def model(self, *options: Any) -> Lecture:
        lecture = Lecture.get(
            self.chambre,
            self.session_or_legislature,
            self.num_texte,
            self.partie,
            self.organe,
            *options,
        )
        if lecture is None:
            raise ResourceNotFound(self)
        return lecture


class AmendementCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        return AmendementResource(name=key, parent=self)

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)


class AmendementResource(Resource):
    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)
        self.num = int(name)

    @property
    def parent(self) -> AmendementCollection:
        return cast(AmendementCollection, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent

    def model(self) -> Amendement:
        try:
            amendement: Amendement = (
                DBSession.query(Amendement)
                .filter_by(lecture=self.lecture_resource.model(), num=self.num)
                .options(joinedload("article"), joinedload("lecture"))
                .one()
            )
        except NoResultFound:
            raise ResourceNotFound(self)
        return amendement


class ArticleCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        try:
            type, num, mult, pos = key.split(".")
        except ValueError:
            raise KeyError
        return ArticleResource(key, self, type, num, mult, pos)

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent

    def models(self) -> List[Article]:
        lecture: Lecture = self.lecture_resource.model(joinedload("articles"))
        articles: List[Article] = lecture.articles
        return articles


class ArticleResource(Resource):
    def __init__(
        self, name: str, parent: Resource, type: str, num: str, mult: str, pos: str
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.type = type
        self.num = num
        self.mult = mult
        self.pos = pos

    @property
    def parent(self) -> ArticleCollection:
        return cast(ArticleCollection, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent

    def model(self, *options: Any) -> Article:
        lecture: Lecture = self.lecture_resource.model()
        try:
            article: Article = (
                DBSession.query(Article)
                .filter_by(
                    lecture=lecture,
                    type=self.type,
                    num=self.num,
                    mult=self.mult,
                    pos=self.pos,
                )
                .options(*options)
                .one()
            )
        except NoResultFound:
            raise ResourceNotFound(self)
        return article


class TableCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        return TableResource(name=key, parent=self)

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)


class TableResource(Resource):
    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)

    @property
    def parent(self) -> TableCollection:
        return cast(TableCollection, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent

    @property
    def owner(self) -> User:
        try:
            user: User = DBSession.query(User).filter(User.email == self.__name__).one()
            return user
        except NoResultFound:
            raise ResourceNotFound

    def model(self) -> UserTable:
        return self.owner.table_for(lecture=self.lecture_resource.model())
