import datetime

import transaction


def test_dossier_has_ordered_textes_by_date_depot(
    db,
    dossier_plfss2018,
    # Fixtures are not in the correct order intentionnaly.
    lecture_plfss2018_an_nouvelle_lecture_seance_publique,
    lecture_plfss2018_senat_premiere_lecture_seance_publique,
    lecture_plfss2018_senat_nouvelle_lecture_seance_publique,
    lecture_plfss2018_an_premiere_lecture_seance_publique,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plfss2018)
        assert [
            (texte.numero, texte.date_depot) for texte in dossier_plfss2018.textes
        ] == [
            (269, datetime.date(2017, 10, 11)),
            (63, datetime.date(2017, 11, 6)),
            (387, datetime.date(2017, 11, 21)),
            (121, datetime.date(2017, 11, 30)),
        ]


def test_dossier_has_ordered_textes_by_date_depot_without_doublons(
    db,
    dossier_plf2018,
    # Fixtures are not in the correct order intentionnaly.
    lecture_plf2018_senat_premiere_lecture_seance_publique_2,
    lecture_plf2018_senat_nouvelle_lecture_seance_publique,
    lecture_plf2018_an_premiere_lecture_seance_publique_1,
    lecture_plf2018_an_nouvelle_lecture_seance_publique,
    lecture_plf2018_senat_premiere_lecture_seance_publique_1,
    lecture_plf2018_an_premiere_lecture_seance_publique_2,
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(dossier_plf2018)
        assert [
            (texte.numero, texte.date_depot) for texte in dossier_plf2018.textes
        ] == [
            (235, datetime.date(2017, 9, 27)),
            (107, datetime.date(2017, 11, 23)),
            (485, datetime.date(2017, 12, 12)),
            (172, datetime.date(2017, 12, 18)),
        ]
