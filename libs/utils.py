import pickle
import logging
import time
import traceback
import os

# user imports
from libs.config import CONFIG

logger = logging.getLogger(__name__)


def conn_handler(conn, fn):
    """
    handle the client connection
    """
    try:
        while True:
            response = conn.recv(CONFIG['MAX_HEADER_SIZE'])
            if not response:
                continue
            logger.info("response {}".format(response))
            message_length = int(response.decode("utf-8"))
            message = conn.recv(message_length)
            response = fn(message)
            send_message(response, conn)
    except ConnectionResetError:
        pass
    logger.info("client disconnected {}".format(conn))

def send_message(message, conn):
    """
    Format message before sending to the client
    """
    message = pickle.dumps(message)
    message_length = "{:<{}}".format(len(message), CONFIG['MAX_HEADER_SIZE'])
    # send header
    conn.send(bytes(message_length, "utf-8"))
    logger.debug(message)
    # send data
    conn.send(message)

def receive_message(conn):
    """
    Receives response on the given connection
    """
    conn.settimeout(5)
    # In case of no response from cache servers, the response will be False
    response = False  
    while True:
        try:
            response = conn.recv(CONFIG["MAX_HEADER_SIZE"])
            if not response:
                continue
            message_length = int(response.decode("utf-8"))
            response = conn.recv(message_length)
            response = pickle.loads(response)
        finally:
            break
    return response

def every(delay, task):
    """
    To excucte the functions without blocking the main thread
    Avoids drifting
    """
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
        next_time += (time.time() - next_time) // delay * delay + delay

def expire_dict_value(instance, key, ttl):
    """
    Delete cache entry based on ttl
    """
    time.sleep(int(ttl))
    instance._delete(key)
    logger.info("EXPIRED the key {}".format(key))

def setup_dir():
    os.makedirs(CONFIG["BACKUP_DIR"], exist_ok=True)
