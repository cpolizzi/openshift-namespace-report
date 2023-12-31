#!/bin/sh

# This script has been authored by Red Hat Customer Success for 3M.
# 
# THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDER BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARSING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTARE OR THE USE OF OTHER DEALINGS IN THE SOFTWARE.

# References:
# - https://kubernetes.io/docs/reference/kubectl/jsonpath/


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
report_file=reports/namespace-quota-compute-report.${report_timestamp}.csv
mkdir -p $(dirname ${report_file})

# Redirect stdout to the report file
exec 1>"${report_file}"

# Retrieve from every namespace all quotas
log "Retrieving quotas from all namespaces"
echo 'Namespace,Kind,Name,Pods,"Request CPU", "Limit CPU"'
oc get \
    quota \
    -A \
     -o jsonpath='{range .items[*]}{.metadata.namespace},{.kind},{.metadata.name},{.spec.hard.pods},{.spec.hard.requests\.cpu},{.spec.hard.limits\.cpu}{"\n"}{end}' \
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
