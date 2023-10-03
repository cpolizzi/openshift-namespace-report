#=====
# General dependencies
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

        report_file = "reports/namespace-quota-compute-report.csv"

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
            limit_ranges = json.loads(exec_cmd_result.stdout)

            # Process results
            for limit_range in limit_ranges["items"]:
                result = []
                expr = parse("($.metadata.namespace)|($.kind)|($.metadata.name)")
                metadata = [ match.value for match in expr.find(limit_range) ]

                expr = parse("($.spec.hard.pods)|($.spec.hard.'requests.cpu')|($.spec.hard.'limits.cpu')")
                spec = ([ match.value for match in expr.find(limit_range) ])
                if spec:
                    result += spec

                if result:
                    print(",".join(metadata + result), file = report)
                logging.info(f"Processed namespace: {metadata[0]}")
