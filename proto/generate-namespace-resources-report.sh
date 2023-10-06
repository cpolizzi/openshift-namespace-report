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
# - https://access.redhat.com/solutions/3986301
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
report_file=reports/namespace-resource-report.${report_timestamp}.csv
mkdir -p $(dirname ${report_file})

# Redirect stdout to the report file
exec 1>"${report_file}"

# Retrieve from every namespace all resources
log "Retrieving all resources from all namespaces"
echo "Namespace,Kind,Name,Timestamp"
oc get \
    $(oc api-resources --namespaced=true --verbs=list -o name | awk '{printf "%s%s",sep,$0;sep=","}') \
    -A \
     -o jsonpath='{range .items[*]}{.metadata.namespace},{.kind},{.metadata.name},{.metadata.managedFields[0].time}{"\n"}{end}' \
    --ignore-not-found \
    --sort-by='metadata.namespace'

# Filter out system namespaces
log "Filtering out system namespace resources"
mv ${report_file} ${report_file}.0
egrep -v '^(default,|kube-|openshift,|openshift-)' ${report_file}.0 > ${report_file}
rm -f ${report_file}.0

log "Report is located in ${report_file}"
