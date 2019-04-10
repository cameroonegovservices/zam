import datetime

import transaction


def test_dossier_has_ordered_textes_by_date_depot(
    db,
    dossier_plfss2018,
    # Fixtures are not in the correct order intentionnaly.
    lecture_plfss2018_an_seconde_lecture,
    lecture_plfss2018_senat_premiere_lecture,
    lecture_plfss2018_senat_seconde_lecture,
    lecture_plfss2018_an_premiere_lecture,
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
