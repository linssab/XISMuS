"""
Copyright (c) 2020 Sergio Augusto Barcellos Lins & Giovanni Ettore Gigante

The example data distributed together with XISMuS was kindly provided by
Giovanni Ettore Gigante and Roberto Cesareo. It is intelectual property of 
the universities "La Sapienza" University of Rome and Università degli studi di
Sassari. Please do not publish, commercialize or distribute this data alone
without any prior authorization.

This software is distrubuted with an MIT license.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Credits:
Few of the icons used in the software were obtained under a Creative Commons 
Attribution-No Derivative Works 3.0 Unported License (http://creativecommons.org/licenses/by-nd/3.0/) 
from the Icon Archive website (http://www.iconarchive.com).
XISMuS source-code can be found at https://github.com/linssab/XISMuS
"""

import json
import os, sys
import Constants
from tkinter import messagebox
from .SpecRead import __BIN__

def load_user_database():
    """ Read database file and load all entries to global variable """    

    path = os.path.join(__BIN__,"database.json")
    if not os.path.exists( path ):
        Constants.LOGGER.info("database.json does not exist. Creating file...")
        try: 
            f = open(path, "w")
            f.close()
        except Exception as e:
            messagebox.showerror("Error",f"Could not create a database file.\n{e}")
            Constants.LOGGER.warning("Failed to create database file.")
            sys.exit(1)
    try: 
        with open(path, "r") as db:
            Constants.USER_DATABASE = json.load(db)
    except json.decoder.JSONDecodeError:
        Constants.LOGGER.warning("Failed to read database! It may be empty or corrupted!")
    return

def write_to_user_database(name, 
        sample_path, 
        prefix, 
        count, 
        extension, 
        indexing):

    Constants.USER_DATABASE[name] = {}
    Constants.USER_DATABASE[name]["path"] = sample_path
    Constants.USER_DATABASE[name]["prefix"] = prefix
    Constants.USER_DATABASE[name]["mcacount"] = count
    Constants.USER_DATABASE[name]["extension"] = extension
    Constants.USER_DATABASE[name]["indexing"] = indexing
    write_to_json()
    return

def write_to_json():
    path = os.path.join(__BIN__,"database.json")
    with open(path, "w") as db:
        json.dump(Constants.USER_DATABASE, db)

def remove_entry_from_database(samples_to_remove):
    """ receives a list of samples to remove from the JSON file """

    for sample in samples_to_remove:
        Constants.USER_DATABASE.pop(sample)
    write_to_json()
    return

