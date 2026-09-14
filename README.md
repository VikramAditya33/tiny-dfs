## Tiny Distributed Filesystem
A distributed file system is used in a distributed system where a client writes/reads a file and is controlled via central metadata engine and with a replication factor of 2. The metadata layer doesn't hold the files but keeps the metadata information such as which block of the file lives in which node and then it points to that particular node where file is distributed and client directly talks with the storage server.
### How to use?
**Step 1:**
Activate venv first
```python
# Create it
python3 -m venv .venv

# Activate it
source .venv/bin/activate
```
**Step 2:**
Install
```python
pip install fastapi uvicorn requests
```
**Step 3:**
Run it
```python
uvicorn master:app \
    --host 0.0.0.0 \
    --port 8000
```
**Step 4:**
Node 1
```python
NODE_ID=node1 \
PORT=9001 \
SELF_URL=http://localhost:9001 \
DATA_DIR=./node1-data \
uvicorn storage_node:app \
    --host 0.0.0.0 \
    --port 9001
```
**Step 5:**
Node 2
```python
NODE_ID=node2 \
PORT=9002 \
SELF_URL=http://localhost:9002 \
DATA_DIR=./node2-data \
uvicorn storage_node:app \
    --host 0.0.0.0 \
    --port 9002
```
**Step 6:**
Node 3
```python
NODE_ID=node3 \
PORT=9003 \
SELF_URL=http://localhost:9003 \
DATA_DIR=./node3-data \
uvicorn storage_node:app \
    --host 0.0.0.0 \
    --port 9003
```
This is gonna setup your whole distributed file system running on different ports locally.

Now you can upload or download any file using this:
```python
python client.py upload vikram.exe /vikram.exe
```
You might see:
```markdown
f91ab... -> node1
f91ab... -> node2

8ff3c... -> node3
8ff3c... -> node1

02a17... -> node2
02a17... -> node3
```
So physically:
```markdown
node1-data/
    f91ab...
    8ff3c...

node2-data/
    f91ab...
    02a17...

node3-data/
    8ff3c...
    02a17...
```
But logically the user sees:
```markdown
/vikram.exe
```
That's basically the illusion a distributed filesystem creates lol.

Download:
```python
python client.py download \
    /vikram.exe \
    vikram.exe
```

Just a fun implementation of DFS.
Byeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
