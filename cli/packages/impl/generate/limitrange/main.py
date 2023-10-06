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

#=====
# General dependencies
import datetime
import json
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
import logging
import re
import subprocess
#-----


#=====
# CLI dependencies
from base import *
#-----

# References:
# - https://kubernetes.io/docs/reference/kubectl/jsonpath/

class LimitRangeReport(Command):
    """
    Generatetes the limit range report.
    """
    def __init__(self,
                 ):
        pass

    def generate(self,
              ):
        logging.info("Preparing limit range report")
        # Retrieve from every namespace all limit ranges

        logging.debug("Retrieving limit ranges from all namespaces")
        command = "oc"

        report_date = datetime.datetime.now().strftime('%Y-%m-%d')
        report_file = f"reports/namespace-limitrange-compute-report-{report_date}.csv"

        with open(f"{report_file}", "w") as report:
            print(f'Namespace,Kind,Name,"Pod Min CPU","Pod Max CPU","Container Min CPU","Container Max CPU","Container Default CPU","Container Default Request CPU"', file = report)
            args = ('''
                get \
                    limitrange \
                    -A \
                    -o json
                ''').strip()
            args = re.split(r' +', args)

            # Execute the CLI command
            exec_cmd = [ command ] + args
            exec_cmd_result = subprocess.run(exec_cmd, stdout = subprocess.PIPE)
            limit_ranges = json.loads(exec_cmd_result.stdout)

            # Process results
            debug = 0
            for limit_range in limit_ranges["items"]:
                result = []
                expr = parse("($.metadata.namespace)|($.kind)|($.metadata.name)")
                metadata = [ match.value for match in expr.find(limit_range) ]

                # Pod limit range
                expr = parse("$.spec.limits[?(@.type=='Pod')].(min.cpu)|(max.cpu)")
                result += ([ match.value for match in expr.find(limit_range) ])

                # Container limit range
                expr = parse("$.spec.limits[?(@.type=='Container')].(min.cpu)|(max.cpu)|(default.cpu)|(defaultRequest.cpu)")
                result += ([ match.value for match in expr.find(limit_range) ])

                debug += 1
                if debug > 2:
                    pass

                if result:
                    print(",".join(metadata + result), file = report)
                logging.info(f"Processed namespace: {metadata[0]}")

        # Inform of report locations
        logging.info(f"Report is in {report_file}")
