# -*- coding: utf-8 -*-

import os
import glob
import glob
import json
import urllib2

from . import EXAMPLES_DIR, HAVE_YAML

def to_yaml(data):
    """Serializes python data to a :ref:`yaml` string

    :type data: dict or list
    :param data: the python data to be encoded
    :return: a `tuple` containing

             - `str` with the encoded json
             - An `Error` message if encoding error, otherwise `None`
    """
    if HAVE_YAML == False:
        return None, "Error: yaml library not installed"

    import yaml
    try:
        yaml_str = yaml.safe_dump(data, default_flow_style=False )
        return yaml_str, None

    except Exception as e:
        return None, "Error: %s" % str(e)



def write_yaml_file(file_path, data):
    """Saves python data in a :ref:`json` encoded file

    :param file_path: The relative or absolute path of file to save.
    :type file_path: str
    :param data: The python data to save
    :type data: dict or list
    :return: `Error` message if write error, otherwise `None`
    """
    with open(file_path, "w") as f:
        yaml_str, err = to_yaml(data)
        if err:
            return err
        f.write(yaml_str)
        f.close()
    return None

def to_json(data, minify=False):
    """Serializes python data to a :ref:`json` string

    :type data: dict or list
    :param data: the python data to be encoded
    :type minify: bool
    :param minify:

            - When **`False`** the json string is minimized with no spaces, new lines etc.
            - When **`True`** the json string is human readable indented with four spaces, and sorted by key.

            .. note:: **Important**

                - By default this project uses **`minify=False`**.
                - For versioning (eg git), it is recommended to use **`minify=False`** as the string
                  will always be the same, ie sorted keys, and indentation


    :return: a `tuple` containing

             - `str` with the encoded json
             - An `Error` message if encoding error, otherwise `None`
    """
    # todo: catch json error
    if minify:
        return json.dumps(data, ensure_ascii=True, separators=(',', ':')), None
    return json.dumps(data, ensure_ascii=True, indent=4, sort_keys=True, separators=(',', ': ')), None



def write_json_file(file_path, data, minify=False):
    """Saves python data in a :ref:`json` encoded file

    :param file_path: The relative or absolute path of file to save.
    :type file_path: str
    :param data: The python data to save
    :type data: dict or list
    :param minify: see :func:`~ogt.utils.to_json`
    :type minify: bool
    :return: `Error` message if write error, otherwise `None`
    """
    with open(file_path, "w") as f:
        json_str, err = to_json(data, minify=minify)
        if err:
            return err
        f.write(json_str)
        f.close()
    return None

def read_json_file(file_path):
    """Read and decodes a :ref:`json` encoded file


    :param file_path: The relative or absolute path of file to read.
    :type file_path: str
    :rtype: tuple
    :return:
             - A decoded python `dict` or `list`
             - An `Error` message if file or decoding error, otherwise `None`
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data, None
    except Exception as e:
        return None, str(e)

def clean_str(source_str, replace="?"):
    """Ensure :ref:`ASCII` characters, and replace any non ascii

    :param source_str: The source str to clean
    :type source_str: str
    :param replace: The character(s) to replace non ascii characters with
    :type replace: str
    :return: a `tuple` containing

             - The ascii string
             - `True` if a non ascii character was encounteres, otherwise `False`
    """
    illegal = False
    try:
        sss = source_str.decode("ascii")
        return sss, illegal
    except UnicodeDecodeError:
        safeS = ""
        illegal = True
        for cIdx in  range(0, len(source_str)):
            singleS = source_str[cIdx]
            if ord(singleS) < 128:
                safeS += singleS
            else:
                safeS += replace
    return safeS, illegal

def delete_dir_contents(dir_path):
    """Deletes all the contents of a directory, not the directory itself

    :type dir_path: str
    :param dir_path: The relative or absolute path to the dir
    """
    filelist = glob.glob("%s/*" % dir_path)
    for f in filelist:
        #print "f=", f
        pass #os.remove(f)

def file_size_format(num, suffix='B'):
    """Formats a file size into human readable

    :param num: size (bytes)
    :param suffix:

        - **B** is default and return bytes
        - or one of **Ki**, **Mi**, **Gi**, **Ti**, **Pi**', **Ei**, **Zi**

    :return: **`str`** with file size
    """
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def file_size(file_path, human=True):
    """Returns a file's size

    :param file_path: relative or absolute path to file
    :type file_path: str
    :type human: bool
    :param human:

        - If **False**, return an **int** of the file size in bytes
        - If **True** returns a **str** with bytes in Kb, MB
    :return: `str` or `int` with the size
    """
    b = os.path.getsize(file_path)
    if human:
        return file_size_format(b)
    return b

def list_examples(sub_dir):
    # TODO check dir exists
    pth = os.path.join( EXAMPLES_DIR, sub_dir,  "*.ags")
    xfiles = glob.glob(pth)
    return xfiles, None

def get_example_dirs():
    if not os.path.exists(EXAMPLES_DIR):
        return None, "dir '%s' not exist " % EXAMPLES_DIR
    return sorted(os.listdir(EXAMPLES_DIR)), None



def to_int(obj):
    try:
        return int(obj)
    except:
        pass
    return None

def read_file(file_path):
    if not os.path.exists(file_path):
        return None, "file path '%s' not exist" % file_path

    with open(file_path, "r") as f:
        return f.read(), None
    return None, "Error reading '%' " % file_path

def write_file(file_path, contents):
    with open(file_path, "w") as f:
        f.write(contents)
        return None
    return "OOPS in write_file()"

def user_dir():
    return os.path.expanduser("~")

def ogt_dir():
    return os.path.join(user_dir(), "open-geotechnical")

def sanity_check():
    """Check env is sane with ags-data-dict"""
    if not os.path.exists(ogt_dir()):
        return False, "No data dict"
    if not os.path.exists(ags4_file()):
        return False, "Missing ags4 data dict"
    return True, None

def ags4_file():
    return os.path.join(ogt_dir(), "ags4.min.json")


def update():
    if not os.path.exists(ogt_dir()):
        os.makedirs(ogt_dir())

    u = "http://agsplay.daffodil.uk.com/ags4.min.json"
    print "Requesting: %s" % u
    try:
        response = urllib2.urlopen(u)
    except Exception as e:
        return e

    txt = response.read()

    ## check its ok
    try:
        json.loads(txt)
    except Exception as e:
        return e
    write_file(ags4_file(), txt)
    return None
