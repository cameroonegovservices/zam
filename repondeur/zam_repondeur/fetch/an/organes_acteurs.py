from json import load
from typing import Dict, Tuple

from .common import extract_from_remote_zip, roman


def get_organes_acteurs(legislature: int) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    data = fetch_organes_acteurs(legislature)
    organes = extract_organes(data)
    acteurs = extract_acteurs(data)
    return organes, acteurs


def fetch_organes_acteurs(legislature: int) -> dict:
    legislature_roman = roman(legislature)
    filename = f"AMO10_deputes_actifs_mandats_actifs_organes_{legislature_roman}.json"
    url = f"http://data.assemblee-nationale.fr/static/openData/repository/{legislature}/amo/deputes_actifs_mandats_actifs_organes/{filename}.zip"  # noqa
    with extract_from_remote_zip(url, filename) as json_file:
        data: dict = load(json_file)
    return data


def extract_organes(data: dict) -> Dict[str, dict]:
    return {organe["uid"]: organe for organe in data["export"]["organes"]["organe"]}


def extract_acteurs(data: dict) -> Dict[str, dict]:
    return {
        organe["uid"]["#text"]: organe for organe in data["export"]["acteurs"]["acteur"]
    }