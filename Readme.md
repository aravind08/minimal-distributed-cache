# Distributed Cache Instance

Python implementation of **In-Memory LRU Cache Server** running as a cluster and a client to access them individually.

## Goals Met
 - [x] Users should be able to connect to the database over the network.
 - [x] Users should be able to GET/SET a key.
 - [x] Users should be able to EXPIRE (auto-delete after a given duration) a key.
 - [x] Since the database will be distributed, users should be able to connect to any node to SET a key, and connect to any other node to GET the key.
 - [x] Multiple users should be able to concurrently use the database.
 - [x] The database should be fully functional even if one node goes down.

## Architecture & Implementation

![alt text](https://i.ibb.co/mtH1f5P/Screenshot-2020-10-21-at-3-53-51-AM.png)


#### 1. Cache DB Servers:
 - Individual LRU Cache with a socket server
 - Snapshots DB to local file at regular intervals
 - Data recovery on restart
#### 2. Client:
 - Connect to cache DB nodes using ID and helper functions
 

## Usage

start the server using `python server.py` under a python3 env. Use client class to access the cluster as shown.

```python3
from client import Client

client = Client()
client.connect("n1")
res = client.set("A", 123)
print(res)
res = client.get("A")
print(res)
res = client.expire("A", 10)
print(res)
client.close()
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
