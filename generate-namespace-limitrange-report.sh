#!/bin/sh

function get_timestamp_format() {
    local result="%Y-%m-%dT%H:%M:%SZ"

    echo ${result}
}

function log() {
    local now=$(date -u +"$(get_timestamp_format)")

    echo "[${now}] - $@" >/dev/tty
}

# Prepare for report data capture
report_timestamp=$(date -u +"$(get_timestamp_format)")
report_file=reports/namespace-limitrange-compute-report.${report_timestamp}.csv
mkdir -p $(dirname ${report_file})

# Redirect stdout to the report file
exec 1>"${report_file}"

# Retrieve from every namespace all limit ranges
log "Retrieving limit ranges from all namespaces"
echo 'Namespace,Kind,Name,"Pod Min CPU","Pod Max CPU","Container Min CPU","Container Max CPU","Container Default CPU","Container Default Request CPU"'
oc get \
    limitrange \
    -A \
    -o jsonpath='{range .items[*]}{.metadata.namespace},{.kind},{.metadata.name},{.spec.limits[?(@.type=="Pod")].min.cpu},{.spec.limits[?(@.type=="Pod")].max.cpu},{.spec.limits[?(@.type=="Container")].min.cpu},{.spec.limits[?(@.type=="Container")].max.cpu},{.spec.limits[?(@.type=="Container")].default.cpu},{.spec.limits[?(@.type=="Container")].defaultRequest.cpu}{"\n"}{end}' \
    --ignore-not-found \
    --sort-by='metadata.namespace'

# Filter out system namespaces
log "Filtering out system namespace resources"
mv ${report_file} ${report_file}.0
egrep -v '^(default,|kube-|openshift,|openshift-)' ${report_file}.0 > ${report_file}
rm -f ${report_file}.0

# Filter out non-compute quotas
log "Filtering out non-compute quotas"
mv ${report_file} ${report_file}.0
egrep -v ',$' ${report_file}.0 > ${report_file}
rm -f ${report_file}.0

log "Report is located in ${report_file}"
