#!/bin/sh

# References:
# - https://access.redhat.com/solutions/3986301

data_file=namespace-resources-report.csv
exec 1>>"${data_file}"

# Retrieve from every namespace all resources
echo "Namespace,Kind,Name,Timestamp"
oc get \
    $(oc api-resources --namespaced=true --verbs=list -o name | awk '{printf "%s%s",sep,$0;sep=","}') \
    -A \
     -o jsonpath='{range .items[*]}{.metadata.namespace},{.kind},{.metadata.name},{.metadata.managedFields[0].time}{"\n"}{end}' \
    --ignore-not-found \
    --sort-by='metadata.namespace'

# Filter out system namespaces
mv ${data_file} ${data_file}.0
egrep -v '^(default,|kube-|openshift,|openshift-)' ${data_file}.0 > ${data_file}
rm -f ${data_file}.0
