"""
Small CLI to inspect the analytics layer from the terminal while there's no
web frontend yet. Each subcommand just calls a function in soccera.analytics
and prints it — all the real logic lives there so a future web API can
reuse it unchanged.

Usage:
  python scripts/analyze.py standings  --league 11535 --season 2026
  python scripts/analyze.py goals      --league 11535 --season 2026
  python scripts/analyze.py discipline --league 11535 --season 2026
  python scripts/analyze.py stats      --league 11535 --season 2026 [--stat KEY]
  python scripts/analyze.py match      --match 16317893

  --source defaults to sofascore (the only source with current-season +
  match-statistics coverage for the Liga Tica); pass --source api_football
  to look at the older backfilled seasons instead.
"""

import argparse

from soccera.analytics.discipline import build_discipline
from soccera.analytics.goals import build_goal_stats
from soccera.analytics.match_report import build_match_report
from soccera.analytics.match_stats import build_match_stat_averages
from soccera.analytics.standings import build_standings
from soccera.cli.formatters import print_table
from soccera.storage.database import session_scope

DEFAULT_STATS = [
    ("ballPossession", "Poss%"),
    ("totalShotsOnGoal", "Shots"),
    ("cornerKicks", "Corners"),
    ("fouls", "Fouls"),
    ("expectedGoals", "xG"),
]


def cmd_standings(args: argparse.Namespace) -> None:
    with session_scope() as session:
        standings = build_standings(session, args.source, args.league, args.season)
        headers = ["#", "Team", "PJ", "G", "E", "P", "GF", "GC", "DG", "Pts"]
        rows = [
            [i + 1, t.team_name, t.played, t.won, t.drawn, t.lost, t.goals_for, t.goals_against, t.goal_diff, t.points]
            for i, t in enumerate(standings.rows)
        ]
        print_table(headers, rows)


def cmd_goals(args: argparse.Namespace) -> None:
    with session_scope() as session:
        stats = build_goal_stats(session, args.source, args.league, args.season)
        print(f"Partidos finalizados: {stats.matches_played}")
        print(f"Goles totales:        {stats.total_goals}")
        print(f"Goles por partido:    {stats.avg_goals_per_match:.2f}")
        print(f"Ambos anotan (BTTS):  {stats.btts_pct:.1f}%")
        print(f"Over 2.5 goles:       {stats.over_2_5_pct:.1f}%")
        print(f"Victoria local:       {stats.home_win_pct:.1f}%")
        print(f"Empate:               {stats.draw_pct:.1f}%")
        print(f"Victoria visitante:   {stats.away_win_pct:.1f}%")


def cmd_discipline(args: argparse.Namespace) -> None:
    with session_scope() as session:
        rows_data = build_discipline(session, args.source, args.league, args.season)
        headers = ["Team", "Amarillas", "Rojas", "Total"]
        rows = [[t.team_name, t.yellow_cards, t.red_cards, t.total_cards] for t in rows_data]
        print_table(headers, rows)


def cmd_stats(args: argparse.Namespace) -> None:
    with session_scope() as session:
        teams = build_match_stat_averages(session, args.source, args.league, args.season)
        if not teams:
            print("(sin match_statistics para esta fuente/liga/temporada)")
            return

        if args.stat:
            headers = ["Team", args.stat]
            rows = sorted(
                ([t.team_name, round(t.averages.get(args.stat, 0.0), 2)] for t in teams),
                key=lambda r: -r[1],
            )
        else:
            headers = ["Team"] + [label for _, label in DEFAULT_STATS]
            rows = [
                [t.team_name] + [round(t.averages.get(key, 0.0), 2) for key, _ in DEFAULT_STATS]
                for t in teams
            ]
        print_table(headers, rows)


def cmd_match(args: argparse.Namespace) -> None:
    with session_scope() as session:
        report = build_match_report(session, args.source, args.match)

        print(f"{report.home_team} {report.home_score} - {report.away_score} {report.away_team}")
        print(
            f"HT {report.home_score_ht}-{report.away_score_ht}  "
            f"Jornada: {report.round}  {report.match_date:%Y-%m-%d %H:%M}  [{report.status}]"
        )

        print("\nCronología:")
        for e in report.events:
            extra = f"+{e.extra_minute}" if e.extra_minute else ""
            print(f"  {e.minute}{extra}'  [{e.team_name}]  {e.event_type} ({e.event_detail})")

        print("\nComparativa (local vs visitante):")
        headers = ["Stat", report.home_team, report.away_team]
        rows = [[s.stat_type, s.home_value, s.away_value] for s in report.stat_comparison]
        print_table(headers, rows)

        for insight in (report.home_insight, report.away_insight):
            print(f"\nPuntos clave — {insight.team_name}:")
            if not insight.notes:
                print("  (sin desviaciones notables respecto a su promedio de temporada)")
            for note in insight.notes:
                print(f"  - {note}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SoccerA analytics CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, handler in [
        ("standings", cmd_standings),
        ("goals", cmd_goals),
        ("discipline", cmd_discipline),
        ("stats", cmd_stats),
    ]:
        sub = subparsers.add_parser(name)
        sub.add_argument("--source", default="sofascore")
        sub.add_argument("--league", required=True, help="league_source_id, e.g. 11535")
        sub.add_argument("--season", required=True, type=int, help="season_year, e.g. 2026")
        if name == "stats":
            sub.add_argument("--stat", default=None, help="single stat key, e.g. expectedGoals")
        sub.set_defaults(func=handler)

    match_sub = subparsers.add_parser("match")
    match_sub.add_argument("--source", default="sofascore")
    match_sub.add_argument("--match", required=True, help="match_source_id, e.g. 16317893")
    match_sub.set_defaults(func=cmd_match)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
