import sys

import typer
from rich import print

app = typer.Typer(rich_markup_mode="rich")

from impl.generate.limitrange import LimitRangeReport


@app.command()
def limitranges(
        ):
    """
    Generates the limit range report.
    """
    target = LimitRangeReport()
    target.generate()


if __name__ == "__main__":
    app()


