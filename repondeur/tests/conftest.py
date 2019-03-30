import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import transaction

from fixtures.dossiers import mock_dossiers  # noqa: F401
from fixtures.organes_acteurs import mock_organes_acteurs  # noqa: F401
from testapp import TestApp as BaseTestApp

HERE = Path(os.path.dirname(__file__))


DOSSIERS = HERE / "fetch" / "sample_data" / "Dossiers_Legislatifs_XV.json"


class TestApp(BaseTestApp):
    def login(self, email, headers=None):
        resp = self.post("/identification", {"email": email}, headers=headers)
        assert resp.status_code == 302

    def get(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if user is not None:
            self.login(user, headers=kwargs.get("headers"))
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if user is not None:
            self.login(user, headers=kwargs.get("headers"))
        return super().post(*args, **kwargs)


@pytest.fixture(scope="session")
def settings():
    return {
        "pyramid.debug_authorization": True,
        "sqlalchemy.url": os.environ.get(
            "ZAM_TEST_DB_URL", "postgresql://zam@localhost/zam-test"
        ),
        "zam.tasks.redis_url": os.environ.get(
            "ZAM_TEST_TASKS_REDIS_URL", "redis://localhost:6379/10"
        ),
        "zam.tasks.always_eager": True,
        "zam.data.redis_url": os.environ.get(
            "ZAM_TEST_DATA_REDIS_URL", "redis://localhost:6379/11"
        ),
        "zam.users.redis_url": os.environ.get(
            "ZAM_TEST_USERS_REDIS_URL", "redis://localhost:6379/12"
        ),
        "zam.session_secret": "dummy",
        "zam.auth_secret": "dummier",
    }


@pytest.fixture(scope="session")  # noqa: F811
def wsgi_app(settings, mock_organes_acteurs):
    from zam_repondeur import make_app

    return make_app(None, **settings)


@pytest.yield_fixture(scope="session", autouse=True)
def use_app_registry(wsgi_app):
    from pyramid.testing import testConfig

    with testConfig(registry=wsgi_app.registry):
        yield


@pytest.fixture
def db():
    from zam_repondeur.models import Base, DBSession

    Base.metadata.drop_all()
    Base.metadata.create_all()

    yield DBSession

    DBSession.close()
    Base.metadata.drop_all()
    DBSession.remove()


@pytest.fixture
def data_repository():
    from zam_repondeur.data import repository

    repository.load_data()


@pytest.fixture
def users_repository():
    from zam_repondeur.users import repository

    repository.clear_data()

    yield

    repository.clear_data()


@pytest.fixture
def app(wsgi_app, db, data_repository, users_repository):
    yield TestApp(
        wsgi_app, extra_environ={"HTTP_HOST": "zam.test", "wsgi.url_scheme": "https"}
    )


@pytest.fixture
def team_zam(db):
    from zam_repondeur.models import Team

    return Team.create(name="Zam")


@pytest.fixture
def user_david(db, team_zam):
    from zam_repondeur.models import User

    return User.create(name="David", email="david@example.com")


@pytest.fixture
def user_ronan(db):
    from zam_repondeur.models import User

    return User.create(name="Ronan", email="ronan@example.com")


@pytest.fixture
def user_daniel(db):
    from zam_repondeur.models import User

    return User.create(name="Daniel", email="daniel@example.com")


@pytest.fixture
def texte_an(db):
    from zam_repondeur.models import Texte

    with transaction.manager:
        texte = Texte.create(
            uid="foo",
            type_="bar",
            numero=269,
            titre_long="Titre long",
            titre_court="Titre court",
            date_depot=datetime(2018, 11, 8),
            lectures=[],
        )

    return texte


@pytest.fixture
def dossier_an(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        texte = Dossier.create(uid="foo", titre="Titre dossier legislatif AN")

    return texte


@pytest.fixture
def lecture_an(db, texte_an, dossier_an):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_an,
            titre="Numéro lecture – Titre lecture",
            organe="PO717460",
            dossier=dossier_an,
        )

    return lecture


@pytest.fixture
def user_david_table_an(user_david, lecture_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        DBSession.add(table)

    return table


@pytest.fixture
def user_ronan_table_an(user_ronan, lecture_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_ronan)
        table = user_ronan.table_for(lecture_an)
        DBSession.add(table)

    return table


@pytest.fixture
def user_daniel_table_an(user_daniel, lecture_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_daniel)
        table = user_daniel.table_for(lecture_an)
        DBSession.add(table)

    return table


@pytest.fixture
def texte_commission_publique(db):
    from zam_repondeur.models import Texte

    with transaction.manager:
        texte = Texte.create(
            uid="foo",
            type_="bar",
            numero=806,
            titre_long="Titre long",
            titre_court="Titre court",
            date_depot=datetime(2018, 11, 8),
            lectures=[],
        )

    return texte


@pytest.fixture
def texte_senat(db):
    from zam_repondeur.models import Texte

    with transaction.manager:
        texte = Texte.create(
            uid="foo",
            type_="bar",
            numero=63,
            titre_long="Titre long",
            titre_court="Titre court",
            date_depot=datetime(2018, 11, 8),
            lectures=[],
        )

    return texte


@pytest.fixture
def dossier_senat(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        texte = Dossier.create(uid="foo", titre="Titre dossier legislatif sénat")

    return texte


@pytest.fixture
def lecture_senat(db, texte_senat, dossier_senat):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            texte=texte_senat,
            titre="Numéro lecture – Titre lecture sénat",
            organe="PO78718",
            dossier=dossier_senat,
        )

    return lecture


@pytest.fixture
def user_david_table_senat(user_david, lecture_senat):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_senat)
        DBSession.add(table)

    return table


@pytest.fixture
def chapitre_1er_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_an, type="chapitre", num="Ier")

    return article


@pytest.fixture
def article1_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_an, type="article", num="1")

    return article


@pytest.fixture
def article1av_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_an, type="article", num="1", pos="avant"
        )

    return article


@pytest.fixture
def article7bis_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_an, type="article", num="7", mult="bis"
        )

    return article


@pytest.fixture
def annexe_an(db, lecture_an):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_an, type="annexe")

    return article


@pytest.fixture
def article1_senat(db, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(lecture=lecture_senat, type="article", num="1")

    return article


@pytest.fixture
def article1av_senat(db, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_senat, type="article", num="1", pos="avant"
        )

    return article


@pytest.fixture
def article7bis_senat(db, lecture_senat):
    from zam_repondeur.models import Article

    with transaction.manager:
        article = Article.create(
            lecture=lecture_senat, type="article", num="7", mult="bis"
        )

    return article


@pytest.fixture
def amendements_an(db, lecture_an, article1_an):
    from zam_repondeur.models import Amendement

    with transaction.manager:
        amendements = [
            Amendement.create(
                lecture=lecture_an, article=article1_an, num=num, position=position
            )
            for position, num in enumerate((666, 999), 1)
        ]

    return amendements


@pytest.fixture
def amendements_senat(db, lecture_senat, article1_senat):
    from zam_repondeur.models import Amendement

    with transaction.manager:
        amendements = [
            Amendement.create(
                lecture=lecture_senat,
                article=article1_senat,
                num=num,
                position=position,
            )
            for position, num in enumerate((6666, 9999), 1)
        ]

    return amendements


@pytest.fixture
def texte_essoc(db):
    from zam_repondeur.models import Texte

    with transaction.manager:
        texte = Texte.create(
            uid="foo",
            type_="bar",
            numero=806,
            titre_long="Titre long",
            titre_court="Titre court",
            date_depot=datetime(2018, 11, 8),
            lectures=[],
        )

    return texte


@pytest.fixture
def dossier_essoc(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        texte = Dossier.create(
            uid="foo",
            titre="Fonction publique : un Etat au service d'une société de confiance",
        )

    return texte


@pytest.fixture
def lecture_essoc(db, texte_essoc, dossier_essoc):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_essoc,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
            dossier=dossier_essoc,
        )

    return lecture


@pytest.fixture
def textes(db):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_textes

    with open(DOSSIERS) as f_:
        data = json.load(f_)
    return parse_textes(data["export"])


@pytest.fixture
def dossiers(db):
    from zam_repondeur.models import DBSession
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
        get_dossiers_legislatifs
    )

    with patch(
        "zam_repondeur.fetch.an.dossiers.dossiers_legislatifs.extract_from_remote_zip"
    ) as m_open:
        m_open.return_value = DOSSIERS.open()
        with transaction.manager:
            dossiers_by_uid = get_dossiers_legislatifs(15)
            for dossier in dossiers_by_uid.values():
                DBSession.add(dossier)
                DBSession.add_all(dossier.lectures)

    return dossiers_by_uid
