import socket
import logging
import threading
import pickle
from collections import OrderedDict
import json
import os
from functools import partial

# user imports
from libs import utils

# initiate the logger to print to sdtout
logger = logging.getLogger(__name__)


class HashNode(object):
    """
    Individual Cache Nodes
    """
    def __init__(self, host, port, config):
        self._config = config
        self._host = host
        self._port = port
        # using python's ordered dict to implement lru
        self._cache = OrderedDict()
        self._ttl_cache = {}
        self._capacity = self._config['LRU_CAPACITY']
        # backup filename
        backup_file = self._config["BACKUP_FILENAME_FORMAT"] + self._host.replace(".", "") + str(self._port)
        # load the backup if any
        self._load_backup(backup_file)
        # start backup service
        threading.Thread(
            target=(lambda filename: utils.every(
                self._config["BACKUP_CACHE_SECONDS"], 
                partial(self._backup_cache, filename)
            )),
            args=[backup_file]
        ).start()
        # start the socket server
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((host, port))
        self._server.listen(self._config['MAX_CONNECTIONS']) 
        self._run()

    def _load_backup(self, filename):
        if os.path.exists(filename):
            with open(filename, mode='rb') as db:
                data = pickle.load(db)
                self._cache = OrderedDict(json.loads(data))
                logger.info("loaded from backup: {} \n {}".format(filename, json.dumps(self._cache)))

    def _backup_cache(self, filename):
        """
        dumps the cache data into a file at "BACKUP_CACHE_SECONDS" intervals
        """
        logger.info("backed-up cache at {}:{}".format(self._host, str(self._port)))
        with open(filename, mode='wb') as db:
            pickle.dump(json.dumps(self._cache), db)

    def get_response(self, message):
        message = pickle.loads(message)
        logger.info("message received: {}".format(message))
        command = message[0].upper()
        if command == "SET":
            return self._set(message[1], message[2])
        elif command == "GET":
            return self._get(message[1])
        elif command == "EXPIRE":
            return self._expire(message[1], message[2])
        else:
            raise Exception("Internal Server Error: only these commands are supported: get, set, expire")

    def _run(self):
        # handle new client
        while True:
            conn, client = self._server.accept()
            logger.info("New client connection accepted: {}:{}".format(*client))
            threading.Thread(target=utils.conn_handler, args=[conn, self.get_response]).start()

    def _get(self, key):
        """
        :param key: the key whose value is to be retrieved
        """
        value = self._cache.get(key, None)
        if value is None:
            return None

        self._cache.move_to_end(key)
        return value

    def _set(self, key, value):
        """
        :param key: key whose value is to be set.
        """
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self._cache) > self._capacity - 1:
            self._cache.popitem(last = False)
        return "OK"

    def _expire(self, key, ttl):
        """
        Auto deletes the key at the end of ttl
        :param key: key for which ttl has to be enabled.
        :param ttl: ttl in seconds.
        """
        if key in self._cache:
            self._ttl_cache[key] = int(ttl)
            threading.Thread(target=utils.expire_dict_value, args=(self, key, ttl)).start()
            return 1
        return 0

    def _delete(self, key):
        """
        Deletes key from cache.
        :param key: the key which is to be deleted from the cache
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl_cache:
            del self._ttl_cache[key]
