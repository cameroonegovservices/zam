import pytest
import transaction
from time import sleep


pytestmark = pytest.mark.flaky(max_runs=5)


def test_table_notification_on_amendement_transfer(
    wsgi_server, driver, lecture_an, amendements_an, user_david_table_an, user_david
):
    from zam_repondeur.models import DBSession

    LECTURE_URL = f"{wsgi_server.application_url}lectures/{lecture_an.url_key}"
    with transaction.manager:
        DBSession.add(user_david_table_an)
        user_david_table_an.amendements.append(amendements_an[0])
        DBSession.add_all(amendements_an)

    driver.get(f"{LECTURE_URL}/tables/{user_david.email}")
    status = driver.find_element_by_css_selector('div[role="status"] div')
    assert not status.is_displayed()
    assert not status.text

    with transaction.manager:
        amendements_an[0].user_table = None
        DBSession.add_all(amendements_an)

    sleep(wsgi_server.settings["zam.check_for.transfers_from_to_my_table"])

    assert status.is_displayed()
    assert status.text == "L’amendement 666 a été retiré de votre table. Rafraîchir"
