"""

Copyright 2014 CSIRO

Authors: Tim Erwin, Tim Bedin

Utility functions to determine version information (both git and vistrails),
which is used to annotate netCDF files for reproducability.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os, re, subprocess, logging
from datetime import datetime

import vistrails.api

from cwsl.configuration import USER, PROJECT

log = logging.getLogger("cwsl.utils.utils")


def get_git_status(ifile):
    """
    Get git version information from filename
    """

    ifile = os.path.expandvars(ifile)

    if not os.path.exists(ifile):
        log.error("{} does not exist!".format(ifile))
        raise Exception

    cwd = os.getcwd()
    os.chdir(os.path.dirname(ifile))
    try:
        status = subprocess.check_output(['git','status',ifile])
        version = subprocess.check_output(['git','log',ifile])
        
        version = re.search('commit (.*?)\n',version)
        modified = re.search('Changed',status)
        if modified:
            git_version = "Git info: %s - with uncommited modifications" % version.group(1)
        else:
            git_version = "Git info: %s" % version.group(1)
    
    except subprocess.CalledProcessError:
        git_version = "Could not determine file version."
        
    
    os.chdir(cwd)

    return git_version


def get_vistrails_info():
    """
    Return a tuple with the VisTrails vt file and version information.

    """

    this_controller = vistrails.api.get_current_controller()
    
    filename = this_controller.vistrail.locator.name
    current_version = this_controller.current_version

    return(filename, current_version)


def build_metadata(command_line_list):
    """
    Takes in a full command line list, e.g. ['echo', 'infile.txt', 'outfile.txt']

    Create version metadata to embed in output files.
    Returns a string of form:
        User, NCI Project, Timestamp
        Current VisTrail, internal pipeline version, git version info
        Script to be run, git version info
        Full command line of the task.
    
    """

    rightnow = datetime.now()
    time_string = rightnow.isoformat()

    vt_info = get_vistrails_info()

    # Get the git information about the script and the vistrails file.
    vt_git = get_git_status(vt_info[0])
    script_git = get_git_status(command_line_list[0])
    
    vt_info_list = ['vt file:', str(vt_info[0]), 'vt file node:', str(vt_info[1]), 'vt file version:', vt_git]
    
    full_ver_string = (' '.join(['user:', USER, 'nci project:', PROJECT, 'time created:', time_string]) + '\n' + 
                       ' '.join(vt_info_list) + '\n' + 
                       ' '.join(['script executed:', os.path.expandvars(command_line_list[0]), 'script file version:', script_git]) + '\n' +
                       ' '.join(['full command line:'] + command_line_list))

    return full_ver_string
    
