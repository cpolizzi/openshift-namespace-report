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

        report_file = "reports/namespace-limitrange-compute-report.csv"

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
            for limit_range in limit_ranges["items"]:
                result = []
                expr = parse("($.metadata.namespace)|($.kind)|($.metadata.name)")
                metadata = [ match.value for match in expr.find(limit_range) ]

                expr = parse("$.spec.limits[?(@.type=='Pod')]")
                if [ match.value for match in expr.find(limit_range) ]:
                    # Pod limit range
                    expr = parse("($.spec.limits[?(@.type=='Pod')].min.cpu)")
                    result += [ match.value for match in expr.find(limit_range) ]
                    expr = parse("($.spec.limits[?(@.type=='Pod')].max.cpu)")
                    result += [ match.value for match in expr.find(limit_range) ]

                expr = parse("$.spec.limits[?(@.type=='Container')]")
                if [ match.value for match in expr.find(limit_range) ]:
                    # Container limit range
                    expr = parse("($.spec.limits[?(@.type=='Container')].min.cpu)")
                    result += [ match.value for match in expr.find(limit_range) ]
                    expr = parse("($.spec.limits[?(@.type=='Container')].max.cpu)")
                    result += [ match.value for match in expr.find(limit_range) ]
                    expr = parse("($.spec.limits[?(@.type=='Container')].default.cpu)")
                    result += [ match.value for match in expr.find(limit_range) ]
                    expr = parse("($.spec.limits[?(@.type=='Container')].defaultRequest.cpu)")
                    result += [ match.value for match in expr.find(limit_range) ]

                if result:
                    print(",".join(metadata + result), file = report)
                logging.info(f"Processed namespace: {metadata[0]}")
