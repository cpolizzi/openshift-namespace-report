import sys

import typer
from rich import print

app = typer.Typer(rich_markup_mode="rich")

from impl.generate.limitrange import LimitRangeReport
from impl.generate.quota import QuotaReport


@app.command()
def limitranges(
        ):
    """
    Generates the limit range report.
    """
    target = LimitRangeReport()
    target.generate()


@app.command()
def quotas(
        ):
    """
    Generates the quota report.
    """
    target = QuotaReport()
    target.generate()


if __name__ == "__main__":
    app()


