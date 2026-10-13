from soccera.storage.models.team import Team
from soccera.storage.repositories.base import SourceKeyedRepository


class TeamRepository(SourceKeyedRepository[Team]):
    model = Team
