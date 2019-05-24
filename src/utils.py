from __future__ import print_function

import os
import io
import sys

ENCODING = 'ISO-8859-1'


def is_empty(val):
    """Check if a variable is an empty string or an empty list."""
    return val == "" or val == []


def clean_input(prompt="", split_char='', ignore_empty=False, dtype=None):
    """Clean the user-input from the CLI before adding it."""
    while True:
        val = input(prompt).strip()
        # split to list type if split_char specified
        if split_char != "":
            val = [v.strip() for v in val.split(split_char) if v.strip() != ""]
        # do not ignore empty input if not allowed
        if not ignore_empty and is_empty(val):
            print("\tError: empty input. Need one or more values.\n")
            continue
        # ensure correct input datatype if specified
        if not is_empty(val) and dtype is not None:
            try:
                if not type(eval(val)) == dtype:
                    print("\tError: input doesn't match required type ", dtype, "\n")
                    continue
            except:
                print("\tError: illegal argument. Input type should be ", dtype, "\n")
                continue
        break
    return val


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
