"""
This script has been authored by Red Hat Customer Success for 3M.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDER BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARSING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTARE OR THE USE OF OTHER DEALINGS IN THE SOFTWARE.
"""

import sys

import typer
from rich import print

app = typer.Typer(rich_markup_mode="rich")

from impl.generate.lastupdated import LastUpdatedReport
from impl.generate.limitrange import LimitRangeReport
from impl.generate.quota import QuotaReport


@app.command()
def last_updated(
        summary: bool = typer.Option(True, help="Generates a summary report."),
        ):
    """
    Generates the last updated report.
    """
    target = LastUpdatedReport(
        summary = summary
        )
    target.generate()


@app.command()
def limit_ranges(
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


