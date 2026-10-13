from soccera.storage.models.league import League
from soccera.storage.repositories.base import SourceKeyedRepository


class LeagueRepository(SourceKeyedRepository[League]):
    model = League
