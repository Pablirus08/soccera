from soccera.storage.models.player import Player
from soccera.storage.repositories.base import SourceKeyedRepository


class PlayerRepository(SourceKeyedRepository[Player]):
    model = Player
