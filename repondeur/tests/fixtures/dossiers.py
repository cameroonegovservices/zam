from datetime import date
from unittest.mock import patch

import pytest


@pytest.yield_fixture(autouse=True)
def mock_dossiers(db):
    from zam_repondeur.models import Dossier, Texte, Lecture
    from zam_repondeur.fetch.an.dossiers.models import Chambre, TypeTexte

    with patch(
        "zam_repondeur.fetch.an.dossiers.dossiers_legislatifs.get_dossiers_legislatifs"
    ) as m_dossiers:
        dossier_DLR5L15N36030 = Dossier.create(
            uid="DLR5L15N36030", titre="Sécurité sociale : loi de financement 2018"
        )
        dossier_DLR5L15N36030.lectures.append(
            Lecture.create(
                chambre=str(Chambre.AN),
                session="15",
                titre="Première lecture – Titre lecture",
                texte=Texte.create(
                    uid="PRJLANR5L15B0269",
                    type_=str(TypeTexte.PROJET),
                    numero=269,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                    titre_court="PLFSS pour 2018",
                    date_depot=date(2017, 10, 11),
                    lectures=[],
                ),
                dossier=dossier_DLR5L15N36030,
                organe="PO717460",  # séance publique
            )
        )
        dossier_DLR5L15N36159 = Dossier.create(
            uid="DLR5L15N36159",
            titre="Fonction publique : un Etat au service d'une société de confiance",
        )
        dossier_DLR5L15N36159.lectures.append(
            Lecture.create(
                chambre=str(Chambre.AN),
                session="15",
                titre="Nouvelle lecture – Titre lecture",
                texte=Texte.create(
                    uid="PRJLANR5L15B0806",
                    type_=str(TypeTexte.PROJET),
                    numero=806,
                    titre_long="projet de loi renforçant l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                    titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                    date_depot=date(2018, 3, 21),
                    lectures=[],
                ),
                dossier=dossier_DLR5L15N36159,
                organe="PO744107",  # commission spéciale
            )
        )
        dossier_DLR5L15N36892 = Dossier(
            uid="DLR5L15N36892", titre="Sécurité sociale : loi de financement 2019"
        )
        dossier_DLR5L15N36892.lectures.append(
            Lecture.create(
                chambre=str(Chambre.SENAT),
                session="2018-2019",
                titre="Première lecture – Titre lecture",
                texte=Texte.create(
                    uid="PRJLSNR5S319B0106",
                    type_=str(TypeTexte.PROJET),
                    numero=106,
                    titre_long="projet de loi de financement de la sécurité sociale pour 2019",  # noqa
                    titre_court="PLFSS pour 2019",
                    date_depot=date(2018, 11, 5),
                    lectures=[],
                ),
                dossier=dossier_DLR5L15N36892,
                organe="PO78718",  # séance publique
            )
        )
        m_dossiers.return_value = {
            "DLR5L15N36030": dossier_DLR5L15N36030,
            "DLR5L15N36159": dossier_DLR5L15N36159,
            "DLR5L15N36892": dossier_DLR5L15N36892,
        }
        yield
