import json
import os
from pathlib import Path

import pytest

HERE = Path(os.path.dirname(__file__))


def test_number_of_dossiers(dossiers):
    assert len(dossiers) == 839


@pytest.fixture
def dossier_plfss_2018():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36030.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_plfss_2018(dossier_plfss_2018, textes):
    from zam_repondeur.models import Lecture, Texte
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_dossier
    from zam_repondeur.fetch.an.dossiers.models import Chambre

    dossier = parse_dossier(dossier_plfss_2018, textes)

    assert dossier.uid == "DLR5L15N36030"
    assert dossier.titre == "Sécurité sociale : loi de financement 2018"
    assert dossier.lectures == [
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0269"),
            partie=None,
            organe="PO420120",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0269"),
            partie=None,
            organe="PO59048",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0269"),
            partie=None,
            organe="PO717460",
        ),
        Lecture.get(
            session="2017-2018",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0063"),
            partie=None,
            organe="PO211493",
        ),
        Lecture.get(
            session="2017-2018",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0063"),
            partie=None,
            organe="PO211494",
        ),
        Lecture.get(
            session="2017-2018",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0063"),
            partie=None,
            organe="PO78718",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0387"),
            partie=None,
            organe="PO420120",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0387"),
            partie=None,
            organe="PO717460",
        ),
        Lecture.get(
            session="2017-2018",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0121"),
            partie=None,
            organe="PO211493",
        ),
        Lecture.get(
            session="2017-2018",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0121"),
            partie=None,
            organe="PO78718",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0434"),
            partie=None,
            organe="PO420120",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0434"),
            partie=None,
            organe="PO717460",
        ),
    ]


@pytest.fixture
def dossier_plf_2018():
    with open(HERE / "sample_data" / "dossier-DLR5L15N35854.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_plf_2018(dossier_plf_2018, textes):
    from zam_repondeur.models import Lecture, Texte
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_dossier
    from zam_repondeur.fetch.an.dossiers.models import Chambre

    dossier = parse_dossier(dossier_plf_2018, textes)

    assert dossier.uid == "DLR5L15N35854"
    assert dossier.titre == "Budget : loi de finances 2018"
    assert dossier.lectures == [
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO59048",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO59048",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO420120",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO420120",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO419604",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO419604",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO419610",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO419610",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO59047",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO59047",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO59046",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO59046",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO59051",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO59051",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO419865",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO419865",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=1,
            organe="PO717460",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0235"),
            partie=2,
            organe="PO717460",
        ),
        Lecture.get(
            session="2018-2019",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0107"),
            partie=1,
            organe="PO211494",
        ),
        Lecture.get(
            session="2018-2019",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0107"),
            partie=2,
            organe="PO211494",
        ),
        Lecture.get(
            session="2018-2019",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0107"),
            partie=1,
            organe="PO78718",
        ),
        Lecture.get(
            session="2018-2019",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0107"),
            partie=2,
            organe="PO78718",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0485"),
            partie=None,
            organe="PO59048",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0485"),
            partie=None,
            organe="PO717460",
        ),
        Lecture.get(
            session="2018-2019",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0172"),
            partie=None,
            organe="PO211494",
        ),
        Lecture.get(
            session="2018-2019",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0172"),
            partie=None,
            organe="PO78718",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0506"),
            partie=None,
            organe="PO59048",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0506"),
            partie=None,
            organe="PO717460",
        ),
    ]


@pytest.fixture
def dossier_essoc_dict():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36159.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_parse_dossier_essoc(dossier_essoc_dict, textes):
    from zam_repondeur.models import Lecture, Texte
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_dossier
    from zam_repondeur.fetch.an.dossiers.models import Chambre

    dossier = parse_dossier(dossier_essoc_dict, textes)

    assert dossier.uid == "DLR5L15N36159"
    assert (
        dossier.titre
        == "Fonction publique : un Etat au service d'une société de confiance"
    )
    assert dossier.lectures == [
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0424"),
            partie=None,
            organe="PO744107",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15BTC0575"),
            partie=None,
            organe="PO717460",
        ),
        Lecture.get(
            session="2018-2019",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299B0259"),
            partie=None,
            organe="PO748821",
        ),
        Lecture.get(
            session="2018-2019",
            chambre=str(Chambre.SENAT),
            texte=Texte.get(uid="PRJLSNR5S299BTC0330"),
            partie=None,
            organe="PO78718",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15B0806"),
            partie=None,
            organe="PO744107",
        ),
        Lecture.get(
            session="15",
            chambre=str(Chambre.AN),
            texte=Texte.get(uid="PRJLANR5L15BTC1056"),
            partie=None,
            organe="PO717460",
        ),
    ]


@pytest.fixture
def dossier_pacte_ferroviaire_dict():
    with open(HERE / "sample_data" / "dossier-DLR5L15N36460.json") as f_:
        return json.load(f_)["dossierParlementaire"]


def test_dossier_pacte_ferroviaire(dossier_pacte_ferroviaire_dict, textes):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import parse_dossier

    dossier = parse_dossier(dossier_pacte_ferroviaire_dict, textes)

    assert dossier.uid == "DLR5L15N36460"
    assert len(dossier.lectures) > 4


def test_extract_actes(dossier_essoc):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import extract_actes

    assert len(extract_actes(dossier_essoc)) == 4


class TestGenLectures:
    def test_create_lectures_essoc(self, dossier_essoc_dict, textes):
        from zam_repondeur.models import DBSession, Lecture
        from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
            create_lectures,
            parse_dossier,
        )

        acte = dossier_essoc_dict["actesLegislatifs"]["acteLegislatif"][0]

        dossier = parse_dossier(dossier_essoc_dict, textes)
        create_lectures(dossier, acte, textes)

        lectures = DBSession.query(Lecture).all()

        assert len(lectures) == 2
        assert "Commission saisie au fond" in lectures[0].titre
        assert "Séance publique" in lectures[1].titre

    def test_create_lectures_pacte_ferroviaire(
        self, dossier_pacte_ferroviaire_dict, textes
    ):
        from zam_repondeur.models import DBSession, Lecture
        from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
            create_lectures,
            parse_dossier,
        )

        acte = dossier_pacte_ferroviaire_dict["actesLegislatifs"]["acteLegislatif"][0]

        dossier = parse_dossier(dossier_pacte_ferroviaire_dict, textes)
        create_lectures(dossier, acte, textes)

        lectures = DBSession.query(Lecture).all()

        assert len(lectures) == 3
        assert "Commission saisie au fond" in lectures[0].titre
        assert "Commission saisie pour avis" in lectures[1].titre
        assert "Séance publique" in lectures[2].titre


def test_walk_actes(dossier_essoc_dict, textes):
    from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
        walk_actes,
        WalkResult,
    )

    acte = dossier_essoc_dict["actesLegislatifs"]["acteLegislatif"][0]
    assert list(walk_actes(acte)) == [
        WalkResult(
            phase="COM-FOND",
            organe="PO744107",
            texte="PRJLANR5L15B0424",
            premiere_lecture=True,
        ),
        WalkResult(
            phase="DEBATS",
            organe="PO717460",
            texte="PRJLANR5L15BTC0575",
            premiere_lecture=True,
        ),
    ]
