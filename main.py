__author__ = 'Daniel Sánchez'

#encoding:utf-8

from hashlib import sha256
import hmac
import logging
import traceback
import os
import codecs
import datetime
import binascii


def hash_file(file_path):

    #Logger configuration
    logger = logging.getLogger('py_hids_app')
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

    logger.info("Started execution...")

    # Generate a random key with 8 bytes (64 bits)
    key = os.urandom(8)
    logger.debug("Random generated key: " + str(key))
    logger.debug("Hexified key: "+str(binascii.hexlify(key)))

    result = ""

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
        result = hashed.hexdigest()

    except Exception:
        logger.info("Error while processing the file\n\n")
        traceback.print_exc()
        logger.info(traceback.format_exc())

    return result

if __name__ == "__main__":

    file_path = "prueba.txt"

    generated_hmac = hash_file(file_path)

    print(generated_hmac)