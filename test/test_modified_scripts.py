"""This module, when run, attempts to install datasets for modified Retriever
scripts in the /scripts folder (except for those listed in ignore_list)
"""
from __future__ import absolute_import
from __future__ import print_function

from future import standard_library

standard_library.install_aliases()

import os
import sys
import subprocess
import requests
from imp import reload
from distutils.version import LooseVersion

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.utils import get_script_version

ENCODING = 'ISO-8859-1'

reload(sys)
if hasattr(sys, 'setdefaultencoding'):
    sys.setdefaultencoding(ENCODING)

file_location = os.path.dirname(os.path.realpath(__file__))
retriever_scripts_root_dir = os.path.abspath(os.path.join(file_location, os.pardir))


def setup_module():
    """Make sure that you are in the source main directory.

    This ensures that scripts obtained are from the scripts directory
    and not the .retriever's script directory.
    """
    os.chdir(retriever_scripts_root_dir)


def get_modified_scripts():
    """Get modified script list, using version.txt in repo and master upstream"""
    modified_list = []
    version_file = requests.get(
        "https://raw.githubusercontent.com/harshitbansal05/Retriever-Scripts/master/version.txt")
    local_repo_scripts = get_script_version()

    upstream_versions = {}
    version_file = version_file.text.splitlines()[1:]
    for line in version_file:
        master_script_name, master_script_version = line.lower().strip().split(",")
        upstream_versions[master_script_name] = master_script_version

    for item in local_repo_scripts:
        local_script, local_version = item.lower().split(",")
        # check for new scripts or a change in versions for present scripts
        # repo script versions compared with upstream.
        if local_script not in upstream_versions.keys():
            modified_list.append(os.path.basename(local_script).split('.')[0])
        elif LooseVersion(local_version) != upstream_versions[local_script]:
            modified_list.append(os.path.basename(local_script).split('.')[0])
    print("List: ", modified_list)
    return modified_list


def install_modified():
    """Installs modified scripts and returns any errors found"""
    try:
        import retriever as rt
    except ImportError:
        print("Retriever is not installed. Skipping tests...")
        return

    setup_module()
    os_password = ""
    if os.name == "nt":
        os_password = "Password12!"

    ignore = [
        "forest-inventory-analysis",
        "bioclim",
        "prism-climate",
        "vertnet",
        "NPN",
        "mammal-super-tree"
    ]
    ignore_list = [dataset.lower() for dataset in ignore]

    modified_scripts = get_modified_scripts()
    if modified_scripts is None:
        print("No new scripts found. Database is up to date.")
        sys.exit()

    if os.path.exists("test_modified"):
        subprocess.call(['rm', '-r', 'test_modified'])
    os.makedirs("test_modified")
    os.chdir("test_modified")
    dbfile = os.path.normpath(os.path.join(os.getcwd(), 'testdb_retriever.sqlite'))

    engine_test = {
        rt.install_xml: {'table_name': '{db}_{table}.xml'},

        rt.install_json: {'table_name': '{db}_{table}.json'},

        rt.install_csv: {'table_name': '{db}_{table}.csv'},

        rt.install_sqlite: {'file': dbfile,
                            'table_name': '{db}_{table}'}
    }

    errors = []
    for script in modified_scripts:
        if script in ignore_list:
            continue
        for install_function in engine_test:
            args = engine_test[install_function]
            try:
                install_function(script, **args)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print("ERROR.")
                errors.append((args["engine"], script, e))

    os.chdir("..")
    subprocess.call(['rm', '-r', 'test_modified'])

    if errors:
        print("Engine, Dataset, Error")
        for error in errors:
            print(error)
        exit(1)
    else:
        print("All tests passed. All scripts are updated to latest version.")
        exit(0)

if __name__ == "__main__":
    install_modified()
