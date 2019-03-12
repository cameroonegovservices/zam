import pickle
from typing import Dict, List

from pyramid.config import Configurator
from redis import Redis

from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
    get_dossiers_legislatifs
)
from zam_repondeur.fetch.an.organes_acteurs import get_organes_acteurs

from .initialize import needs_init


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.data")
    """
    init_repository(config.registry.settings)
    repository.clear_data()
    repository.load_data()


def init_repository(settings: Dict[str, str]) -> None:
    repository.initialize(
        redis_url=settings["zam.data.redis_url"],
        legislatures=[int(legi) for legi in settings["zam.legislatures"].split(",")],
    )


class DataRepository:
    """
    Store and access global data in Redis
    """

    def __init__(self) -> None:
        self.initialized = True

    def initialize(self, redis_url: str, legislatures: List[int]) -> None:
        self.connection = Redis.from_url(redis_url)
        self.legislatures = legislatures
        self.initialized = True

    @needs_init
    def clear_data(self) -> None:
        self.connection.flushdb()

    @needs_init
    def load_data(self) -> None:
        dossiers = get_dossiers_legislatifs(*self.legislatures)
        organes, acteurs = get_organes_acteurs()
        self.connection.set("dossiers", pickle.dumps(dossiers))
        self.connection.set("organes", pickle.dumps(organes))
        self.connection.set("acteurs", pickle.dumps(acteurs))

    @needs_init
    def get_data(self, key: str) -> dict:
        raw_bytes = self.connection.get(key)
        if raw_bytes is None:
            return {}

        data: dict = pickle.loads(raw_bytes)
        return data


repository = DataRepository()
