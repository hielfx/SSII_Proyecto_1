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
            return tuple([key, hexified_hmac])
        else:
            return None

    def get_cursor():

        cursor = None
        try:
            #we check if the table exist. If the table doesn't exist we create it.
            check_table = "SELECT * FROM sqlite_master WHERE name ='{0}' and type='table';".format(app_name)
            logger.debug("Check table statement: "+check_table)
            cursor = conn.execute(check_table)
            logger.info("Checking if the table {0} exists...".format(app_name))
            # If cursor.fetch() is None means that the table desn't exist, so we have to create it.
            if cursor.fetchone() is None:
                # We create the create_table script
                logger.info("The table {0} doesn't exists. Creating table...".format(app_name))
                create_table = "CREATE TABLE {0} (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT UNIQUE, hex_key TEXT, hex_hmac TEXT);".format(app_name)
                conn.execute(create_table)
                # We commit the changes
                conn.commit()
                logger.info("Table '{0}' created correctly".format(app_name))
            else:
                logger.info("The table {0} already exists".format(app_name))
        except Exception:
            generate_error_message("Error while connecting to the database.")

        # We check if the path is already in the db.
        # If the path is in the db, we hash it and compare with the one in the db.
        # If not, we hash it and insert it into the db.
        select = "SELECT hex_key,hex_hmac FROM {0} where path=?;".format(app_name)
        c = f.path
        try:
            logger.info("Checking if the path '{0}' exists in the db...".format(c))
            cursor = conn.execute(select, (c,))
            # logger.info("Select statement executed correctly")
        except TypeError:
            # generate_error_message("An error occurred while executing the SELECT statement")
            logger.info("The table already exists")
        return cursor

    def insert_hmac(_path, _key, _hmac):
        logger.info("Inserting hashed file in the Data Base...")
        # We use 'memoryview(_key)' in order to insert he b'hex_key' into the Data Base.
        bin
        insert = "INSERT INTO {0} (path, hex_key, hex_hmac) VALUES ('{1}',?,'{2}');".format(app_name, _path, _hmac)
        print(insert)
        logger.debug("INSERT statement: "+insert)
        # print(insert,(_key,))
        cursor = None
        try:
            cursor = conn.execute(insert,(_key,))
            conn.commit()
            logger.info("File hash has been saved correctly in the Data Base")
        except Exception:
            generate_error_message("Error while trying to insert the file hash in the Data Base")

        return cursor

    def check_integrity(_cursor, path):
        key = _cursor.fetchone()[0]
        old_hmac = _cursor.fetchone()[1]
        _hashed = hash_file(path, key)
        if _hashed is not None and _hashed[1] == old_hmac:
            logger.info("The integrity of the file '{0}' is correct!".format(path))
        else:
            logger.warn("The integrity of the file '{0}' failed, the data may have been modified!")


    ###################################################
    ##########                               ##########
    ##########   Here starts the execution   ##########
    ##########                               ##########
    ###################################################

    config = None
    conn = sqlite3.connect(str(app_name)+".db")

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

                        # We check if the table exists in the db.
                        custom_cursor = get_cursor()

                        one = custom_cursor.fetchone()
                        if one is not None:
                            logger.info("The path exists in the db")
                            _cursor = None
                            logger.info("Checking the integrity of the file '"+f.path+"'...")
                            cursor = check_integrity(_cursor, f.path)
                        else:
                            logger.info("The path doesn't exists in the DB")
                            #We get the absolute path to the file, so we cant secure hash it
                            logger.info("Hashing "+str(f.name)+" file...")
                            hashed = hash_file(f.path)
                            cursor = insert_hmac(f.path, hashed[0], hashed[1])

                    else:
                        hashed = None

                    # if hashed is not None:

        # return result
    except Exception:
        generate_error_message("Error while scanning the directories")

    # We close the connection with the DB once we finished
    conn.close()

    return 0


if __name__ == "__main__":
    main_method()