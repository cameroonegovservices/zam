from datetime import date

import pytest
import transaction


@pytest.fixture
def dossier_plfss2018(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            uid="DLR5L15N36030", titre="Sécurité sociale : loi de financement 2018"
        )

    return dossier


@pytest.fixture
def texte_plfss2018_an_premiere_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLANR5L15B0269",
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=269,
            titre_long="projet de loi de financement de la sécurité sociale pour 2018",
            titre_court="PLFSS pour 2018",
            date_depot=date(2017, 10, 11),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_an_premiere_lecture(
    db, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def texte_plfss2018_senat_premiere_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLSNR5S299B0063",
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=63,
            titre_long="projet de loi de financement de la sécurité sociale pour 2018",
            titre_court="PLFSS pour 2018",
            date_depot=date(2017, 11, 6),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_senat_premiere_lecture(
    db, dossier_plfss2018, texte_plfss2018_senat_premiere_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            texte=texte_plfss2018_senat_premiere_lecture,
            titre="Première lecture – Séance publique",
            organe="PO78718",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def texte_plfss2018_an_seconde_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLANR5L15B0387",
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=387,
            titre_long="projet de loi de financement de la sécurité sociale pour 2018",
            titre_court="PLFSS pour 2018",
            date_depot=date(2017, 11, 21),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_an_seconde_lecture(
    db, dossier_plfss2018, texte_plfss2018_an_seconde_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="an",
            session="15",
            texte=texte_plfss2018_an_seconde_lecture,
            titre="Nouvelle lecture – Séance publique",
            organe="PO717460",
            dossier=dossier_plfss2018,
        )

    return lecture


@pytest.fixture
def texte_plfss2018_senat_seconde_lecture(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    with transaction.manager:
        texte = Texte.create(
            uid="PRJLSNR5S299B0121",
            type_=TypeTexte.PROJET,
            chambre=Chambre.SENAT,
            session=2017,
            numero=121,
            titre_long="projet de loi de financement de la sécurité sociale pour 2018",
            titre_court="PLFSS pour 2018",
            date_depot=date(2017, 11, 30),
        )

    return texte


@pytest.fixture
def lecture_plfss2018_senat_seconde_lecture(
    db, dossier_plfss2018, texte_plfss2018_senat_seconde_lecture
):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(
            chambre="senat",
            session="2017-2018",
            texte=texte_plfss2018_senat_seconde_lecture,
            titre="Nouvelle lecture – Séance publique",
            organe="PO78718",
            dossier=dossier_plfss2018,
        )

    return lecture
