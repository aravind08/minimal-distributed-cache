import sys
import socket
import pickle
import threading
import logging
import time

# user imports
from libs.config import CONFIG
from libs import utils
from libs.hash_node import HashNode
from libs.hash_ring import HashRing

# configure the main logger to print to sdtout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

# set the exception handler
def exception_handler(type, value, tb):
    logger.exception("Error: {0}".format(str(value)), exc_info=True)
sys.excepthook = exception_handler


class Server(object):
    """
    Starts the cache cluster
    Implements Consistent Hashing
    Handles client request 
    """
    def __init__(self, host='localhost', port=6600):
        # initialize the hash ring
        self.ring = HashRing(CONFIG["SERVER_POOL"])
        # start the cache servers
        self._server_threads = {}
        self.start_cache_servers()
        # command handlers
        self.commands = {
            'SET': lambda key, value: self._execute_query(key, ("set", key, value)),
            'GET': lambda key, _: self._execute_query(key, ("get", key)),
            'EXPIRE': lambda key, ttl: self._execute_query(key, ("expire", key, ttl)),
        }
        # create directories
        utils.setup_dir()
        self._health_store = {}
        # start the socket server to accept connections
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((host, port))
        self._server.listen(CONFIG['MAX_CLIENTS']) 
        self._run()

    def _get_node_from_hashring(self, key):
        """
        Get the node ip for the given key
        """
        return self.ring.get_node(key)

    def _execute_query(self, key, message):
        """
        find the cache node to be accessed and send request
        """
        # Get the ip of the server containing the key
        ip = self._get_node_from_hashring(key)
        # Create a socket to send the message to the server
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host, port = ip.split(":")
        conn.connect((host, int(port), ))
        utils.send_message(message, conn)
        response = utils.receive_message(conn)
        self._health_check(response, ip)
        conn.close()
        return response

    def _health_check(self, response, ip):
        """
        Maintain the status of cluster nodes
        """
        if response is False:
            self._health_store[ip] = self._health_store.get(ip, 0)
            self._health_store[ip] += 1
            if self._health_store[ip] == CONFIG["HEALTH_THRESHOLD"]:
                # remove the node from the hash ring
                self.ring.remove_node(ip)
                # @TODO: handle shutdown of the node
        else:
            self._health_store[ip] = 0

    def conn_handler(self, conn, fn):
        """
        handle the client connection
        """
        try:
            while True:
                message = conn.recv(CONFIG['MAX_HEADER_SIZE'])
                if not message:
                    continue
                logger.info("message {}".format(message))
                response = fn(message.decode("utf-8"))
                self.client_send(response, conn)
        except ConnectionResetError:
            pass
        logger.info("client disconnected {}".format(conn))

    def client_send(self, message, conn):
        """
        Format message before sending to the client
        """
        logger.debug(message)
        # send data
        conn.send(bytes(message, "utf-8"))

    def _run(self):
        while True:
            conn, client = self._server.accept()
            logger.info("New client connection accepted: {}:{}".format(*client))
            threading.Thread(target=self.conn_handler, args=[conn, self.get_response]).start()

    def get_response(self, message):
        logger.info("message received: {}".format(message))
        message_array = message.split(' ')
        # call the appropriate commands
        try:
            return self.commands[message_array[0]](
                message_array[1],
                message_array[2] if len(message_array) > 2 else ""
            )
        except KeyError:
            raise Exception('BAD REQUEST')

    def start_cache_servers(self):
        for node in CONFIG["SERVER_POOL"]:
            host, port = node[0].split(":")
            thread = threading.Thread(target=HashNode, args=[host, int(port), CONFIG])
            self._server_threads[node[0]] = thread
            thread.start()


if __name__ == '__main__':
    client = Server(
        host=CONFIG["APPLICATION_SERVER_IP"],
        port=CONFIG["APPLICATION_SERVER_PORT"]
    )