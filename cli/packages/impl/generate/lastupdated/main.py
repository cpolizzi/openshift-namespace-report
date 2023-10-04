#=====
# General dependencies
import io
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

class LastUpdatedReport(Command):
    """
    Generatetes the last updated report.
    """
    def __init__(self,
                 ):
        pass

    def generate(self,
              ):
        logging.info("Preparing last updated report")
        # Retrieve from every namespace all quotas

        command = "oc"
        report_file = "reports/namespace-last-updated-report.csv"

        # Get all namespaced resource types
        logging.info("Retrieving namespaced resource types")
        resource_types = []
        args = ('''
            api-resources \
                --namespaced=true \
                --verbs=list \
                -o name
            ''').strip()
        args = re.split(r' +', args)
        exec_cmd = [ command ] + args
        proc = subprocess.Popen(exec_cmd, stdout = subprocess.PIPE)
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            resource_types += [ line.strip() ]

        # Generate report
        logging.info("Generating report")
        with open(f"{report_file}", "w") as report:
            print(f"Namespace,Kind,Name,Timestamp", file = report)

            # Pull all resources from namespace
            args = []
            args.append('get')
            args.append(",".join(resource_types))
            args.append("-A")
            args.append("--ignore-not-found")
            args.append("-o")
            args.append("jsonpath={range .items[*]}{.metadata.namespace},{.kind},{.metadata.name},{.metadata.managedFields[0].time}{\"\\n\"}{end}")

            logging.info(f"Pulling all resources across all namespaces")
            exec_cmd = [ command ] + args
            proc = subprocess.Popen(exec_cmd, stdout = subprocess.PIPE)
            resources = []
            for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                line = line.strip()
                resources.append(LastUpdatedReport.Resource(*line.split(",")))

            logging.info(f"Sorting resources")
            resources.sort()

            # Filter namespaces and resource types
            logging.info("Filtering namespaces and resource types")
            resources = filter(self.resource_filter, resources)

            # Write report
            logging.info("Writing report")
            for resource in resources:
                print(resource, file = report)

            return

    class Resource():
        """
        Represents a resource.
        """
        def __init__(self,
                namespace : str,
                kind : str,
                name : str,
                timestamp):
            self.namespace = namespace
            self.kind = kind
            self.name = name
            self.timestamp = timestamp

        def __eq__(self,
                o):
            return repr(self) == repr(o)

        def __lt__(self,
                o):
            return repr(self) < repr(o)

        def __repr__(self):
            return f"resource=(namespace: {self.namespace}, kind: {self.kind}, name: {self.name}, timeatamp: {self.timestamp})"

        def __str__(self):
            return f"{self.namespace},{self.kind},{self.name},{self.timestamp}"

    def resource_filter(self,
            resource : Resource) -> bool:
        """
        Filters resources based on both namespace and resource type. Undesired namespaces and resource types are the candidates.
        Also filtered are resources that do not have a managed field timestamp.
        """
        undesired_namespace_regex = r'^(default|kube-|openshift$|openshift-)'
        undesired_resource_types = [
                "ClusterServiceVersion",
                "ControllerRevision",
                "EndpointSlice",
                "Endpoints",
                "Event",
                "FalconNodeSensor",
                "ImageManifestVuln",
                "ImageStreamTag",
                "ImageTag",
                "InstallPlan",
                "Lease",
                "Kind",
                "OperatorCondition",
                "OperatorGroup",
                "PodMetrics",
                "ServiceAccount",
                "Subscription",
                "TemplateInstance",
                "TridentBackend",
                "TridentBackendConfig",
                "TridentNode",
                "TridentSnapshot",
                "TridentStorageClass",
                "TridentVersion",
                "TridentVolume",
                "TridentVolumePublication",
            ]

        # Filter based on namespace
        match = re.search(undesired_namespace_regex, resource.namespace)
        if match:
            return False

        # Filter based on resource type
        if resource.kind in undesired_resource_types:
            return False

        # Filter based on timestamp
        if not resource.timestamp:
            return False

        return True
