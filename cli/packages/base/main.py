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

import sys
import os


class Command:
    def execute(self,
                append_to_logfile : bool = False,
                args : list = [],
                command : str = None,
                debug : bool = False,
                logfile : str = None,
                stderr = sys.stderr,
                stdout = sys.stdout,
                ):
        cmdline = "{} {}".format(command, " ".join(args))
        if debug:
            print(f"Executing command: {cmdline}")
        os.system(cmdline)
