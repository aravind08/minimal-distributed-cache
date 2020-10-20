from client import Client

client = Client()
client.connect("n1")
res = client.set("A", 123)
print(res)
res = client.get("A")
print(res)
res = client.expire("A", 10)
print(res)