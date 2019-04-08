from argparse import ArgumentParser, Namespace
import logging
import sys
from typing import List

from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config
import transaction

from zam_repondeur import BASE_SETTINGS
from zam_repondeur.models import DBSession, Team


logger = logging.getLogger(__name__)


def main(argv: List[str] = sys.argv) -> None:

    args = parse_args(argv[1:])
    print(args)

    setup_logging(args.config_uri)

    settings = get_appsettings(args.config_uri)
    settings = {**BASE_SETTINGS, **settings}

    engine = engine_from_config(
        settings, "sqlalchemy.", connect_args={"application_name": "zam_auth"}
    )

    DBSession.configure(bind=engine)

    args.func(args)


def parse_args(args: List[str]) -> Namespace:
    parser = ArgumentParser(description="Manage Zam teams and users.")
    parser.add_argument("config_uri")

    subparsers = parser.add_subparsers(title="subcommands")

    team_parser = subparsers.add_parser("team")

    team_subparser = team_parser.add_subparsers(title="team subcommands")

    list_teams_parser = team_subparser.add_parser("list")
    list_teams_parser.set_defaults(func=list_teams)

    add_team_parser = team_subparser.add_parser("add")
    add_team_parser.add_argument("--name", required=True)
    add_team_parser.add_argument("--password", required=True)
    add_team_parser.set_defaults(func=add_team)

    return parser.parse_args(args)


def list_teams(args: Namespace) -> None:
    for team in DBSession.query(Team):
        print(team.name)


def add_team(args: Namespace) -> None:
    with transaction.manager:
        team = Team.create(args.name, args.password)
        DBSession.add(team)
    print(f"Added team {team.name}")
