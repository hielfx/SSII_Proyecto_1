__author__ = 'Daniel Sánchez'

#encoding:utf-8

from hashlib import sha256
import hmac
import logging
import traceback
import os
import binascii
import yaml
import glob


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

    def hash_file(file_path):
        """This method hash the file and return the tupple (hexified_key, hexified_hmac)"""

        # logger = logger_config()

        logger.info("Generating random key...")
        # Generate a random key with 8 bytes (64 bits)
        key = os.urandom(8)
        logger.debug("Random generated key: " + str(key))
        hexified_key = binascii.hexlify(key)
        logger.debug("Hexified key: "+str(hexified_key))

        hexified_hmac = ""

        try:

            logger.info('Opening file with path \'{0}\''.format(file_path))
            # Trying to open the file
            file = open(file_path, 'r')

            logger.info("Reading the lines of the file")
            msg = file.readlines()

            hashed = hmac.new(key=key, digestmod=sha256)

            for line in msg:
                hashed.update(line.encode('utf-8'))

            logger.info("Generated HMAC: " + str(hashed.hexdigest()+"\n\n"))
            hexified_hmac = hashed.hexdigest()

        except Exception:
            generate_error_message("Error while hashing the file", logger)

        return tuple(hexified_key, hexified_hmac)

    #Here starts the execution
    config = None

    try:

        logger.info("Opening the configuration file...")
        config = yaml.load(open(str(app_name)+".yaml",'r'))

    except yaml.YAMLError:

        generate_error_message("Error in configuration file")

    except Exception:

        generate_error_message("Error opening the config file")

    result = {}
    try:

        for d in config['scan_directories']:
            if d not in config['exclude_directories']:
                split = d.split('\\')
                #We get the current directory name
                directory_name = split[len(split)-1]
                logger.debug("Current directory name: "+str(directory_name))

                logger.info("Scaning the directory "+str(directory_name)+": \n"+str(os.scandir(d)))
                for f in os.scandir(d):
                    if f.is_file():
                        logger.info("Hashing "+str(f.name())+" file...")
                        #We get the absolute path to the file, so we cant secure hash it
                        (key, hmac) = hash_file(os.path.abspath(f))
                        result[key] = hmac # We introduce the key->hmac in the result directory

        return result
    except Exception:
        generate_error_message("Error while scanning the directories")



if __name__ == "__main__":

    config = yaml.load(open('py_hids_app.yaml', 'r'))
    print(config)