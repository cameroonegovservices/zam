from datetime import datetime
from typing import TYPE_CHECKING, Iterable

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base, DBSession

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .texte import Texte  # noqa


class Dossier(Base):
    __tablename__ = "dossiers"

    pk = Column(Integer, primary_key=True)

    uid = Column(Text, nullable=False)  # the Assemblée Nationale UID
    titre = Column(Text, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lectures = relationship("Lecture", back_populates="dossier")

    __repr_keys__ = ("pk", "uid", "titre")

    @classmethod
    def create(cls, uid: str, titre: str) -> "Dossier":
        now = datetime.utcnow()
        dossier = cls(uid=uid, titre=titre, created_at=now, modified_at=now)
        DBSession.add(dossier)
        return dossier

    @property
    def textes(self) -> Iterable["Texte"]:
        return sorted(lecture.texte for lecture in self.lectures)
