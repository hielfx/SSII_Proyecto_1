__author__ = 'Daniel Sánchez'

#encoding:utf-8

from hashlib import sha256
import hmac
import logging
import traceback
import os
import binascii
import yaml
import sqlite3


def main_method(app_name="py_hids_app"):
    """This is the main execution point and the root method.
    This is used to prevent variable names collisions.
    The *.ini file name and the app name must be the same."""

    # def logger_config():
    #     """This methods configure the logger object to our own purpose"""

    #Logger configuration
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('hids.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

        # return logger

    def generate_error_message(msg):
        logger.info(str(msg)+"\n\n")
        traceback.print_exc()
        logger.info(traceback.format_exc())

    def hash_file(file_path, key=os.urandom(8)):
        """This method hash the file and return the tupple (hexified_key, hexified_hmac)"""

        logger.info("Generating random key...")
        # Generate a random key with 8 bytes (64 bits)
        logger.debug("Random generated key: " + str(key))
        hexified_key = binascii.hexlify(key)
        logger.debug("Hexified key: "+str(hexified_key))

        hexified_hmac = ""

        exception = False
        try:

            logger.info('Opening file with path \'{0}\''.format(file_path))
            # Trying to open the file
            file = open(file_path, 'rb')# We use 'rb' to open the file in binary mode

            logger.info("Reading the lines of the file")
            msg = file.readlines()# it fails when trying to opening a no *.txt file

            hashed = hmac.new(key=key, digestmod=sha256)

            for line in msg:
                hashed.update(line)

            logger.info("Generated HMAC: " + str(hashed.hexdigest()+"\n\n"))
            hexified_hmac = hashed.hexdigest()
            file.close()
        except Exception:
            generate_error_message("Error while hashing the file")
            exception = True

        if not exception:
            return tuple([hexified_key, hexified_hmac])
        else:
            return None


    ###################################################
    ##########                               ##########
    ##########   Here starts the execution   ##########
    ##########                               ##########
    ###################################################

    config = None
    conn = sqlite3.connect(str(app_name)+".db")

    #we check if the table exist. If the table doesn't exist we create it.
    check_table = "SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';".format(app_name)
    try:
        cursor = conn.execute(check_table)
        logger.info("Checking of the table exists...")
        if len(cursor) == 0:
            # We create the create_table script
            logger.info("The table doesn't exists. Creating table...")
            create_table = "CREATE TABLE {0} (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, hexh_key TEXT, hexh_hmac TEXT);".format(app_name)
            conn.execute(create_table)
            # We commit the changes
            conn.commit()
        else:
            logger.info("The table exists")
    except Exception:
        generate_error_message("Error while connecting to the database.")
    try:

        logger.info("Opening the configuration file...")
        config = yaml.load(open(str(app_name)+".yaml",'r'))

    except yaml.YAMLError:

        generate_error_message("Error in configuration file")

    except Exception:

        generate_error_message("Error opening the config file")

    try:

        for d in config['scan_directories']:
            # if d not in config['exclude_directories']:
            split = d.split('\\')
            #We get the current directory name in order to show it in the logs
            directory_name = split[len(split)-1]
            logger.debug("Current directory name: "+str(directory_name))

            #We start the scanning in the directory
            logger.info("Scanning the directory "+str(d)+": \n"+str(os.scandir(d)))
            for f in os.scandir(d):
                if f.is_file():
                    #we get the file extension
                    file_split = os.path.splitext(f.path)
                    logger.info("Hashing "+str(f.name)+" file...")
                    #we put the extension in a variable if the file has a extension
                    if file_split[1] is not None:
                        extension = file_split[1]
                    else:
                        extension = ""

                    #In order to hash the file we check the following things:
                    #   - If the file doesn't have extension we proceed to hash it
                    #   - If the file has extension and the extension is in 'exclude_extensions',
                    #       we check if the whole file is not int 'excluded_files'.
                    #       Then we proceed to hash the file.
                    if(extension == ""
                       or (extension not in config['exclude_extensions']
                           and f.path not in config['excluded_files'])):
                        #We get the absolute path to the file, so we cant secure hash it
                        hashed = hash_file(f.path)
                    else:
                        hashed = None

                    if hashed is not None:
                        select = "SELECT hex_key,hex_mac FROM {0} where path=?;".format(app_name)
                        c = f.path
                        insert = "INSERT INTO {0} (path, hex_key,hex_hmac) VALUES ({1},{2},{3}) ;".format(app_name, f.path, hashed[0],hashed[1])
                        cursor = conn.execute(select)
                        if len(cursor)>=0:
                            # check_hmac(f.path, cursor[0]['hex_key'],cursor[0]['hex_hmac'])
                            logger.info("Checking the integrity of the file '"+f.path+"'...")

        # return result
    except Exception:
        generate_error_message("Error while scanning the directories")


if __name__ == "__main__":
    main_method()