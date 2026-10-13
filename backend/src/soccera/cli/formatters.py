"""Plain-text table printing for the terminal — no external dependencies."""

from collections.abc import Sequence
from typing import Any


def print_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> None:
    if not rows:
        print("(no data)")
        return

    str_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def format_row(cells: Sequence[str]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print(format_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in str_rows:
        print(format_row(row))
