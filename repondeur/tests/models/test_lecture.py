import pytest
import transaction


# We need data about dossiers, texts and groups
pytestmark = pytest.mark.usefixtures("data_repository")


class TestLectureToStr:
    def test_an_seance_publique(self, texte_plfss2018_an_premiere_lecture):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO717460",
        )
        result = (
            "Assemblée nationale, 15e législature, Séance publique, Nouvelle lecture, "
            "texte nº\u00a0269"
        )
        assert str(lecture) == result

    def test_an_commission(self, texte_plfss2018_an_premiere_lecture):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO59048",
        )
        result = (
            "Assemblée nationale, 15e législature, Commission des finances, "
            "Nouvelle lecture, texte nº\u00a0269"
        )
        assert str(lecture) == result

    def test_an_commission_speciale(
        self, texte_essoc2018_an_nouvelle_lecture_commission_fond
    ):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            texte=texte_essoc2018_an_nouvelle_lecture_commission_fond,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
        )
        result = (
            "Assemblée nationale, 15e législature, Commission spéciale sur la société "
            "de confiance, Nouvelle lecture, texte nº\u00a0806"
        )
        assert str(lecture) == result

    def test_senat_seance_publique(self, texte_plfss2018_senat_premiere_lecture):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="senat",
            session="2017-2018",
            texte=texte_plfss2018_senat_premiere_lecture,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO78718",
        )
        result = (
            "Sénat, session 2017-2018, Séance publique, Nouvelle lecture, "
            "texte nº\u00a063"
        )
        assert str(lecture) == result


def test_lecture_previous_lecture(
    db,
    dossier_plfss2018,
    lecture_plfss2018_an_premiere_lecture_seance_publique,
    lecture_plfss2018_senat_premiere_lecture_seance_publique,
    lecture_plfss2018_an_nouvelle_lecture_seance_publique,
    lecture_plfss2018_senat_nouvelle_lecture_seance_publique,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert lecture_plfss2018_an_premiere_lecture_seance_publique.previous is None
        assert (
            lecture_plfss2018_senat_premiere_lecture_seance_publique.previous
            == lecture_plfss2018_an_premiere_lecture_seance_publique
        )
        assert (
            lecture_plfss2018_an_nouvelle_lecture_seance_publique.previous
            == lecture_plfss2018_senat_premiere_lecture_seance_publique
        )
        assert (
            lecture_plfss2018_senat_nouvelle_lecture_seance_publique.previous
            == lecture_plfss2018_an_nouvelle_lecture_seance_publique
        )


def test_lecture_previous_lecture_with_gaps(
    db,
    dossier_plfss2018,
    # Only textes are imported for Senat, no existing lecture.
    lecture_plfss2018_an_premiere_lecture_seance_publique,
    texte_plfss2018_senat_premiere_lecture,
    lecture_plfss2018_an_nouvelle_lecture_seance_publique,
    texte_plfss2018_senat_nouvelle_lecture,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert lecture_plfss2018_an_premiere_lecture_seance_publique.previous is None
        assert (
            lecture_plfss2018_an_nouvelle_lecture_seance_publique.previous
            == lecture_plfss2018_an_premiere_lecture_seance_publique
        )


def test_lecture_next_lecture(
    db,
    dossier_plfss2018,
    lecture_plfss2018_an_premiere_lecture_seance_publique,
    lecture_plfss2018_senat_premiere_lecture_seance_publique,
    lecture_plfss2018_an_nouvelle_lecture_seance_publique,
    lecture_plfss2018_senat_nouvelle_lecture_seance_publique,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert (
            lecture_plfss2018_an_premiere_lecture_seance_publique.next
            == lecture_plfss2018_senat_premiere_lecture_seance_publique
        )
        assert (
            lecture_plfss2018_senat_premiere_lecture_seance_publique.next
            == lecture_plfss2018_an_nouvelle_lecture_seance_publique
        )
        assert (
            lecture_plfss2018_an_nouvelle_lecture_seance_publique.next
            == lecture_plfss2018_senat_nouvelle_lecture_seance_publique
        )
        assert lecture_plfss2018_senat_nouvelle_lecture_seance_publique.next is None


def test_lecture_next_lecture_with_gaps(
    db,
    dossier_plfss2018,
    # Only textes are imported for Senat, no existing lecture.
    lecture_plfss2018_an_premiere_lecture_seance_publique,
    texte_plfss2018_senat_premiere_lecture,
    lecture_plfss2018_an_nouvelle_lecture_seance_publique,
    texte_plfss2018_senat_nouvelle_lecture,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert (
            lecture_plfss2018_an_premiere_lecture_seance_publique.next
            == lecture_plfss2018_an_nouvelle_lecture_seance_publique
        )
        assert lecture_plfss2018_an_nouvelle_lecture_seance_publique.next is None


def test_lecture_no_previous_or_next(
    db,
    dossier_plfss2018,
    texte_plfss2018_an_premiere_lecture,
    texte_plfss2018_senat_premiere_lecture,
    # Only textes are imported for others, no other existing lecture.
    lecture_plfss2018_an_nouvelle_lecture_seance_publique,
    texte_plfss2018_senat_nouvelle_lecture,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert lecture_plfss2018_an_nouvelle_lecture_seance_publique.previous is None
        assert lecture_plfss2018_an_nouvelle_lecture_seance_publique.next is None
