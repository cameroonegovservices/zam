"""
Récupérer la liste des amendements à un texte de loi au Sénat
"""
import argparse
import math
from typing import (
    Iterable,
    Iterator,
    List,
    Optional,
)

from fetcher import (
    fetch_and_parse_amendements,
    fetch_and_parse_amendements_discussion,
)
from models import Amendement
from writer import write_csv


def main(argv: List[str] = None) -> None:
    args = parse_args(argv=argv)

    # Tous les amendements déposés, par ordre de dépôt
    amendements = fetch_and_parse_amendements(
        session=args.session,
        num=args.texte,
    )

    processed_amendements = process_amendements(
        amendements=amendements,
        session=args.session,
        num=args.texte,
    )

    save_output(
        amendements=processed_amendements,
        filename=f'amendements_{args.session}_{args.texte}.csv',
    )


def parse_args(argv: List[str] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--session',
        required=True,
        help='session parlementaire (p.ex. 2017-2018)',
    )
    parser.add_argument(
        '--texte',
        required=True,
        help='numéro du texte au Sénat (p.ex. 330)',
    )
    return parser.parse_args(argv)


def process_amendements(
    amendements: Iterable[Amendement],
    session: str,
    num: str,
) -> Iterable[Amendement]:

    # Les amendements discutés en séance, par ordre de passage
    amendements_derouleur = fetch_and_parse_amendements_discussion(
        session=session,
        num=num,
        phase='seance',
    )

    return _sort(
        _enrich(amendements, amendements_derouleur),
        amendements_derouleur,
    )


def _enrich(
    amendements: Iterable[Amendement],
    amendements_derouleur: Iterable[Amendement],
) -> Iterator[Amendement]:
    """
    Enrichir les amendements avec les informations du dérouleur

    - discussion commune ?
    - amendement identique ?
    """
    amendements_discussion_by_num = {
        amend.num_int: amend
        for amend in amendements_derouleur
    }
    return (
        _enrich_one(amend, amendements_discussion_by_num.get(amend.num_int))
        for amend in amendements
    )


def _enrich_one(
    amend: Amendement,
    amend_discussion: Optional[Amendement],
) -> Amendement:
    if amend_discussion is None:
        return amend
    return amend.evolve(
        discussion_commune=amend_discussion.discussion_commune,
        identique=amend_discussion.identique,
    )


def _sort(
    amendements: Iterable[Amendement],
    amendements_derouleur: Iterable[Amendement],
) -> List[Amendement]:
    """
    Trier les amendements par ordre de passage, puis par numéro
    """
    amendements_discussion_order = {
        amend.num_int: index
        for index, amend in enumerate(amendements_derouleur)
    }
    return sorted(
        amendements,
        key=lambda a: (
            amendements_discussion_order.get(a.num_int, math.inf),
            a.num_int,

        ),
    )


def save_output(amendements: Iterable[Amendement], filename: str) -> None:
    nb_rows = write_csv(amendements, filename)
    print(f'Wrote {nb_rows} rows to {filename}')


if __name__ == '__main__':
    main()
