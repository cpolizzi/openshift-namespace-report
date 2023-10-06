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

class QuotaReport(Command):
    """
    Generatetes the quota report.
    """
    def __init__(self,
                 ):
        pass

    def generate(self,
              ):
        logging.info("Preparing quota report")
        # Retrieve from every namespace all quotas

        logging.debug("Retrieving quotas from all namespaces")
        command = "oc"

        report_date = datetime.datetime.now().strftime('%Y-%m-%d')
        report_file = f"reports/namespace-quota-compute-report-{report_date}.csv"

        with open(f"{report_file}", "w") as report:
            print(f'Namespace,Kind,Name,Pods,"Request CPU","Limit CPU"', file = report)
            args = ('''
                get \
                    quota \
                    -A \
                    -o json
                ''').strip()
            args = re.split(r' +', args)

            # Execute the CLI command
            exec_cmd = [ command ] + args
            exec_cmd_result = subprocess.run(exec_cmd, stdout = subprocess.PIPE)
            quotas = json.loads(exec_cmd_result.stdout)

            # Process results
            for quota in quotas["items"]:
                result = []
                expr = parse("($.metadata.namespace)|($.kind)|($.metadata.name)")
                metadata = [ match.value for match in expr.find(quota) ]

                expr = parse("($.spec.hard.pods)|($.spec.hard.'requests.cpu')|($.spec.hard.'limits.cpu')")
                spec = ([ match.value for match in expr.find(quota) ])
                if spec:
                    result += spec

                if result:
                    print(",".join(metadata + result), file = report)
                logging.info(f"Processed namespace: {metadata[0]}")

        # Inform of report locations
        logging.info(f"Report is in {report_file}")
