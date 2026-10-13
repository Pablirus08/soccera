from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from soccera.storage.models.base import Base, TimestampMixin


class TeamPlayer(Base, TimestampMixin):
    """
    A player's squad membership at a specific team for a specific season.
    Players transfer between teams, so this association is scoped by
    season rather than being a plain team<->player many-to-many.
    """

    __tablename__ = "team_players"
    __table_args__ = (
        UniqueConstraint("team_id", "player_id", "season_id", name="uq_team_players_roster"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    shirt_number: Mapped[int | None] = mapped_column(Integer)
    position: Mapped[str | None] = mapped_column(String(20))
