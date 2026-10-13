from soccera.storage.models.venue import Venue
from soccera.storage.repositories.base import SourceKeyedRepository


class VenueRepository(SourceKeyedRepository[Venue]):
    model = Venue
