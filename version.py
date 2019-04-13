"""Generates a configuration file containing the version number."""
from __future__ import absolute_import

import io
import os
import sys
import imp
import json
from os.path import join, exists
from collections import OrderedDict

ENCODING = 'ISO-8859-1'

def open_fr(file_name, encoding=ENCODING, encode=True):
    """Open file for reading respecting Python version and OS differences.

    Sets newline to Linux line endings on Windows and Python 3
    When encode=False does not set encoding on nix and Python 3 to keep as bytes
    """
    if sys.version_info >= (3, 0, 0):
        if os.name == 'nt':
            file_obj = io.open(file_name, 'r', newline='', encoding=encoding)
        else:
            if encode:
                file_obj = io.open(file_name, "r", encoding=encoding)
            else:
                file_obj = io.open(file_name, "r")
    else:
        file_obj = io.open(file_name, "r", encoding=encoding)
    return file_obj


def read_json(json_file):
    """Read Json dataset package files

    Load each json and get the appropriate encoding for the dataset
    Reload the json using the encoding to ensure correct character sets
    """
    json_object = OrderedDict()
    json_file_encoding = None
    
    try:
        file_obj = open_fr(json_file)
        json_object = json.load(file_obj)
        if "encoding" in json_object:
            json_file_encoding = json_object['encoding']
        file_obj.close()
    except ValueError:
        pass

    # Reload json using encoding if available
    try:
        if json_file_encoding:
            file_obj = open_fr(json_file, encoding=json_file_encoding)
        else:
            file_obj = open_fr(json_file)
        json_object = json.load(file_obj)
        file_obj.close()
    except ValueError:
        pass

    if type(json_object) is dict and "version" in json_object.keys():
        return json_object["version"]
    return None


def read_py(script_name, search_path):
    file, pathname, desc = imp.find_module(script_name, [search_path])
    try:
        new_module = imp.load_module(script_name, file, pathname, desc)
        if hasattr(new_module.SCRIPT, "version"):
            return new_module.SCRIPT.version
    except Exception as e:
        pass
    return None


def get_script_version():
    """This function gets the version number of the scripts and returns them in array form."""
    search_path = 'scripts'
    loaded_files = []
    scripts = []
    if exists(search_path):
        data_packages = [file_i for file_i in os.listdir(search_path) if file_i.endswith(".json")]
        for script in data_packages:
            script_name = '.'.join(script.split('.')[:-1])
            script_version = read_json(os.path.join(search_path, script))
            if script_name not in loaded_files and script_version:
                scripts.append(','.join([script, str(script_version)]))
                loaded_files.append(script_name)

        files = [file for file in os.listdir(search_path)
                 if file[-3:] == ".py" and file[0] != "_" and
                 ('#retriever' in
                  ' '.join(open_fr(join(search_path, file), encoding=ENCODING).readlines()[:2]).lower())
                 ]
        for script in files:
            script_name = '.'.join(script.split('.')[:-1])
            script_version = read_py(script_name, search_path)
            if script_name not in loaded_files and script_version:
                scripts.append(','.join([script, str(script_version)]))
                loaded_files.append(script_name)

    scripts = sorted(scripts, key=str.lower)
    return scripts


def write_version_file(scripts):
    """The function creates / updates version.txt with the script version numbers."""
    if os.path.isfile("version.txt"):
        os.remove("version.txt")

    with open("version.txt", "w") as version_file:
        version_file.write("Retriever Scripts Versions")
        for script in scripts:
            version_file.write('\n' + script)


def update_version_file():
    """Update version.txt."""
    scripts = get_script_version()
    write_version_file(scripts)
    print("Version.txt updated.")


if __name__ == '__main__':
    update_version_file()
