import json
from collections import OrderedDict
from http import HTTPStatus
from pathlib import Path
from typing import List, Tuple, Union
from urllib.parse import urljoin

import xmltodict

from ..exceptions import NotFound
from ..http import cached_session
from .models import Amendement, SubDiv
from .parser import _parse_subdiv


BASE_URL = "http://www.assemblee-nationale.fr"

# Deprecation warning: this API for fetching amendements will be removed in the future
# and has no Service Level Agreement (SLA)
PATTERN_LISTE = "/{legislature}/amendements/{texte}/{organe}/liste.xml"
PATTERN_AMENDEMENT = "/{legislature}/xml/amendements/{texte}/{organe}/{numero}.xml"


def build_url(legislature: int, texte: int, numero: int = 0, organe: str = "AN") -> str:
    if numero:
        path = PATTERN_AMENDEMENT.format(
            legislature=legislature, texte=f"{texte:04}", organe=organe, numero=numero
        )
    else:
        path = PATTERN_LISTE.format(
            legislature=legislature, texte=f"{texte:04}", organe=organe
        )
    url: str = urljoin(BASE_URL, path)
    return url


def get_auteur(amendement: OrderedDict) -> str:
    if int(amendement["auteur"]["estGouvernement"]):
        return "LE GOUVERNEMENT"
    return f"{amendement['auteur']['nom']} {amendement['auteur']['prenom']}"


def get_groupe(amendement: OrderedDict, groups_folder: Path) -> str:
    auteur = amendement["auteur"]
    if int(auteur["estGouvernement"]) or "@xsi:nil" in auteur["groupeTribunId"]:
        return ""
    groupe_raw = (groups_folder / f"PO{auteur['groupeTribunId']}.json").read_text()
    libelle: str = json.loads(groupe_raw)["organe"]["libelle"]
    return libelle


def get_sort(amendement: OrderedDict) -> str:
    sort: Union[str, OrderedDict] = amendement["sortEnSeance"]
    if isinstance(sort, OrderedDict):
        if "@xsi:nil" in sort:
            return ""
        else:
            raise NotImplementedError
    return sort.lower()


def unjustify(content: str) -> str:
    return content.replace(' style="text-align: justify;"', "")


def fetch_amendement(
    legislature: int,
    texte: int,
    numero: int,
    organe: str,
    groups_folder: Path,
    position: int,
) -> Amendement:
    """
    Récupère un amendement depuis son numéro.
    """
    url = build_url(legislature=legislature, texte=texte, numero=numero, organe=organe)

    resp = cached_session.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
        raise NotFound(url)

    content = xmltodict.parse(resp.content)
    amendement = content["amendement"]
    subdiv = parse_division(amendement["division"])
    return Amendement(  # type: ignore
        chambre="an",
        session=str(legislature),
        num_texte=texte,
        num=int(amendement["numero"]),
        subdiv_type=subdiv.type_,
        subdiv_num=subdiv.num,
        subdiv_mult=subdiv.mult,
        subdiv_pos=subdiv.pos,
        sort=get_sort(amendement),
        position=position,
        matricule=amendement["auteur"]["tribunId"],
        groupe=get_groupe(amendement, groups_folder),
        auteur=get_auteur(amendement),
        dispositif=unjustify(amendement["dispositif"]),
        objet=unjustify(amendement["exposeSommaire"]),
    )


def parse_division(division: dict) -> SubDiv:
    if division["type"] == "TITRE":
        return SubDiv("titre", "", "", "")
    subdiv = _parse_subdiv(division["titre"])
    if division["avantApres"]:
        subdiv = subdiv._replace(pos=division["avantApres"].lower())
        if subdiv.pos == "a":  # TODO: understand what it means...
            subdiv = subdiv._replace(pos="")
    return subdiv


def fetch_amendements(
    legislature: int, texte: int, organe: str
) -> Tuple[str, List[OrderedDict]]:
    """
    Récupère la liste des références aux amendements, dans l'ordre de dépôt.
    """
    url = build_url(legislature=legislature, texte=texte, organe=organe)

    resp = cached_session.get(url)
    if resp.status_code == HTTPStatus.NOT_FOUND:  # 404
        raise NotFound(url)

    content = xmltodict.parse(resp.content)
    amendements_raw = content["amdtsParOrdreDeDiscussion"]["amendements"]["amendement"]
    title = content["amdtsParOrdreDeDiscussion"]["@titre"]
    return title, amendements_raw


def fetch_and_parse_all(
    legislature: int, texte: int, organe: str, groups_folder: Path
) -> Tuple[str, List[Amendement], List[str]]:
    title, amendements_raw = fetch_amendements(legislature, texte, organe)
    amendements = []
    index = 1
    errored = []
    for item in amendements_raw:
        try:
            amendement = fetch_amendement(
                legislature=legislature,
                texte=texte,
                numero=item["@numero"],
                organe=organe,
                groups_folder=groups_folder,
                position=index,
            )
        except NotFound:
            errored.append(item["@numero"])
            continue
        amendements.append(amendement)
        index += 1
    return title, amendements, errored
