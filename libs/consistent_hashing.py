from bisect import bisect_right
import logging

logger = logging.getLogger(__name__)


class ConsistentHashing(object):
    """
    Implements consistent hashing
    """
    def __init__(self, nodes):
        """
        :param nodes: list of tuples containing server and replica set 
        """
        self._ring = []
        self._generate_hashring(nodes)

    def _hash_function(self, key):
        return hash(key)

    def _generate_hashring(self, nodes):
        for node in nodes:
            for i in range(node[1]):
                key = "{}_{}".format(node[0], i)
                position = self._hash_function(key)
                self._ring.append((position, node[0],))
        self._ring.sort(key= lambda x: x[0])

    def get_node(self, key):
        """
        Get the node/server where the key is or should be.
        :param key: key whose node/server is to be computed.
        """
        position = bisect_right(self._ring, (self._hash_function(key),))
        if position == len(self._ring):
            position = 0
        return self._ring[position][1]

    def remove_node(self, node):
        """
        Remove node from the ring because it is dead or unavailable.
        :param node: node to be removed from the consistent hashing scheme.
        """
        temp = []
        for position, ip in self._ring:
            if ip != node:
                temp.append((position, ip))
        self._ring = temp.copy()
        del temp

    def add_node(self, node, weight=3):
        """
        Add node to the HashRing of consistent hashing scheme.
        :param node: (ip,port)
        :param weight: weight of the new node to be added.
        """
        self._generate_hashring([(node, weight)])