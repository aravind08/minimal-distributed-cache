# Minimal Distributed Cache 

Pure python implementation of the distributed cache using the  **consistent hashing** technique.

Being the principal behind the popular cache DB's like *redis* and *memecache*, Consistent Hashing offers seamless horizontal scaling, high availability through replicas, and distributes the data evenly across the nodes in the cluster when paired with right hashing techniques (like Google's Jump or Guava).

Implemented a basic Hash Ring using python's hash() and weighted distribution technique. Nothing fancy here.

![alt text](https://uploads.toptal.io/blog/image/129309/toptal-blog-image-1551794743400-9a6fd84dca83745f8b6ca95a2890cdc2.png)

## Goals Met
 - [x] Users should be able to connect to the database over the network.
 - [x] Users should be able to GET/SET a key.
 - [x] Users should be able to EXPIRE (auto-delete after a given duration) a key.
 - [ ] Since the database will be distributed, users should be able to connect to any node to SET a key, and connect to any other node to GET the key.
 - [x] Multiple users should be able to concurrently use the database.
 - [x] The database should be fully functional even if one node goes down.

## Explanation
The idea of the distributed database is to design a successful strategy to store/access data across the nodes in the cluster. **Point 4** which states that the user should be able to connect with any nodes, seemed like **a grey area** in the problem statement. So, I've created a separate branch called **minimal** that meets 100% of the goal without implementing the distribution algorithm.

## Architecture & Implementation

#### 1. Application Server:
 - Implements Hash Ring
 - Initializes the cache clusters
 - Performs health-check of the clusters
 - Also, acts as client-server for DB functions

#### 2. Hash Nodes:
 - Individual sockets which serve the Application Server.
 - LRU Cache
 - Backup DB data to local file at regular intervals
 - Data recovery on restart

![alt text](https://hazelcast.com/wp-content/uploads/2020/04/39_Distributed-Cache.png)


## Usage

Start the application server using `python server.py` under python3 env and start making the calls as shown below. No external dependencies required.

```python
import socket

host, port = ('localhost', 6600)
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((host, int(port), ))

conn.send(bytes("SET A 123", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.send(bytes("SET B ANACONDA", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.send(bytes("GET A", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.send(bytes("GET B", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.send(bytes("EXPIRE B 10", "utf-8"))
data = conn.recv(1024)
print(data.decode("utf-8"))

conn.close()
```
