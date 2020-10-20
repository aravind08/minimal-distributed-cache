import socket
import sys
import pickle
import threading
import logging
import time

# user imports
from libs.config import CONFIG
from libs import utils


class Client(object):
    """
    Client to access the distributed db
    """
    def __init__(self):
        self.db = None
        # initialize the nodes
        self._nodes = CONFIG["SERVER_POOL"]
        # to track the nodes
        self._health_store = {}
        # initialize the socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def close(self):
        if self.connected is True:
            self._socket.close()

    def connect(self, db):
        # close the present connection
        self.close()
        # start the socket server to accept connections
        try:
            self.db = db
            host, port = self._nodes[db]
            self._socket.connect((host, port))
            self.connected = True
        except KeyError:
            logger.error("Invalid DB ID || Available ones: %s" % ", ".self._nodes.keys())

    def _execute_query(self, key, message):
        """
        find the cache node to be accessed and send request
        """
        if not self.db:
            raise Exception("Please connect to a node first using connect()")
        utils.send_message(message, self._socket)
        response = utils.receive_message(self._socket)
        self._health_check(response, self.db)
        return response

    def _health_check(self, response):
        """
        Maintain the status of cluster nodes
        """
        if response is False:
            self._health_store[db] = self._health_store.get(db, 0)
            self._health_store[db] += 1
            if self._health_store[db] == CONFIG["HEALTH_THRESHOLD"]:
                logger.error("Node %s is down" % db)
        else:
            self._health_store[db] = 0

    def get(self, key):
        """
        :param key: the key whose value is to be retrieved
        """
        return self._execute_query(key, ("get", key))

    def set(self, key, value):
        """
        :param key: key whose value is to be set.
        """
        return self._execute_query(key, ("set", key, value))

    def expire(self, key, ttl):
        """
        set expiry in seconds for the given key
        """
        return self._execute_query(key, ("expire", key, ttl))
    
    def ttl(self, key):
        """
        :param key: returns the ttl for the key if any
        """
        return self._execute_query(key, ("ttl", key))