#=====
# General dependencies
import logging
import re
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
                -o jsonpath='{range .items[*]}{.metadata.namespace},{.kind},{.metadata.name},{.spec.limits[?(@.type=="Pod")].min.cpu},{.spec.limits[?(@.type=="Pod")].max.cpu},{.spec.limits[?(@.type=="Container")].min.cpu},{.spec.limits[?(@.type=="Container")].max.cpu},{.spec.limits[?(@.type=="Container")].default.cpu},{.spec.limits[?(@.type=="Container")].defaultRequest.cpu}{"\\n"}{end}' \
                --ignore-not-found \
                --sort-by='metadata.namespace'
            ''').strip()
        args += f" >> {report_file}"
        args = re.split(r' +', args)

        # Execute the CLI command
        self.execute(command = command, args = args)
