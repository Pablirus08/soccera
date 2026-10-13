"""
Walk-forward backtest of the Poisson model over every tournament from
--from-year on, plus the team ratings of a model fit on all finished matches.

Usage: python scripts/run_backtest.py [--from-year 2023]
"""

import argparse
from math import exp as _exp

from soccera.cli.formatters import print_table
from soccera.models.backtest import HistoricalMatch, Scores, walk_forward
from soccera.models.poisson import MatchResult, PoissonModel
from soccera.storage.database import session_scope
from soccera.storage.repositories import MatchRepository


def tournament_label(league_name: str, season_year: int) -> str:
    stage = "Apertura" if "Apertura" in league_name else "Clausura"
    return f"{stage} {season_year}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-year", type=int, default=2023)
    parser.add_argument("--source", default="sofascore")
    args = parser.parse_args()

    with session_scope() as session:
        rows = MatchRepository(session).get_finished(args.source)
        matches = [
            HistoricalMatch(
                match_date=m.match_date,
                tournament=tournament_label(m.league.name, m.season.year),
                result=MatchResult(m.home_team_id, m.away_team_id, m.home_score, m.away_score),
            )
            for m in rows
        ]
        team_names = {m.home_team_id: m.home_team.name for m in rows}
        team_names.update({m.away_team_id: m.away_team.name for m in rows})

    chronological = []
    for m in sorted(matches, key=lambda m: m.match_date):
        year = int(m.tournament.split()[1])
        if year >= args.from_year and m.tournament not in chronological:
            chronological.append(m.tournament)

    reports = walk_forward(matches, chronological)

    print("Backtest walk-forward (menor log-loss/Brier = mejor)\n")
    headers = ["Torneo", "Train", "Test", "LogLoss", "Base", "Brier", "Base", "Acierto", "Base"]
    total_model, total_base = Scores(), Scores()
    table = []
    for r in reports:
        total_model.merge(r.model)
        total_base.merge(r.baseline)
        table.append(_row(r.tournament, r.train_size, r.model, r.baseline))
    table.append(_row("TOTAL", "", total_model, total_base))
    print_table(headers, table)

    model = PoissonModel.fit([m.result for m in matches])
    print(f"\nVentaja de local (factor sobre goles esperados): x{_exp(model.home_advantage):.2f}\n")
    ratings = sorted(
        model.attack, key=lambda t: -(model.attack[t] + model.defense[t])
    )
    print_table(
        ["Equipo", "Ataque", "Defensa"],
        [[team_names[t], f"x{_exp(model.attack[t]):.2f}", f"x{_exp(model.defense[t]):.2f}"]
         for t in ratings],
    )
    print("\n(Ataque x1.20 = anota 20% más que el promedio; Defensa x1.20 = recibe ~17% menos.)")


def _row(label, train, model: Scores, base: Scores) -> list:
    return [
        label, train, model.n,
        f"{model.mean_log_loss:.3f}", f"{base.mean_log_loss:.3f}",
        f"{model.mean_brier:.3f}", f"{base.mean_brier:.3f}",
        f"{model.accuracy:.0%}", f"{base.accuracy:.0%}",
    ]



if __name__ == "__main__":
    main()
