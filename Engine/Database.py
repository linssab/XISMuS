#################################################################
#                                                               #
#          Database functions                                   #
#                        version: 2.5.0 - Dec - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import json
import logging
import os, sys
import Constants
from .SpecRead import __BIN__

logger = logging.getLogger("logfile")

def load_user_database():
    """ Read database file and load all entries to global variable """    

    path = os.path.join(__BIN__,"database.json")
    try: 
        with open(path, "r") as db:
            Constants.USER_DATABASE = json.load(db)
    except FileNotFoundError:
        logger.info("Database.json does not exist. Creating file...")
        f = open(path, "w")
        f.close()
        try:
            with open(path, "r") as db:
                Constants.USER_DATABASE = json.load(db)
        except:
            logger.info("Failed to create database.json!")
            sys.exit(1)
    except json.decoder.JSONDecodeError:
        logger.info("Failed to read database! It may be empty or corrupted!")
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

