from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from threading import Lock
from typing import List
import uuid

app = FastAPI()

lock = Lock()

nodes = {}
files = {}

round_robin_cursor = 0


class RegisterNodeRequest(BaseModel):
    node_id: str
    url: str


class CreateFileRequest(BaseModel):
    path: str
    size: int
    chunks: int
    replication_factor: int = 2


@app.post("/nodes/register")
def register_node(req: RegisterNodeRequest):
    with lock:
        nodes[req.node_id] = {
            "id": req.node_id,
            "url": req.url,
        }

    return {
        "registered": req.node_id
    }


def select_nodes(count: int):
    global round_robin_cursor

    available = list(nodes.values())

    if len(available) < count:
        raise HTTPException(
            status_code=503,
            detail="Not enough storage nodes"
        )

    result = []

    for _ in range(count):
        node = available[
            round_robin_cursor % len(available)
        ]

        round_robin_cursor += 1

        result.append(node)

    return result


@app.post("/files")
def create_file(req: CreateFileRequest):
    if req.path in files:
        raise HTTPException(
            status_code=409,
            detail="File already exists"
        )

    if len(nodes) < req.replication_factor:
        raise HTTPException(
            status_code=503,
            detail="Not enough nodes for requested replication factor"
        )

    chunks = []

    with lock:
        for index in range(req.chunks):

            chunk_id = str(uuid.uuid4())

            replicas = select_nodes(
                req.replication_factor
            )

            chunks.append({
                "index": index,
                "chunk_id": chunk_id,
                "replicas": replicas
            })

        files[req.path] = {
            "path": req.path,
            "size": req.size,
            "chunks": chunks
        }

    return files[req.path]


@app.get("/files/{path:path}")
def get_file(path: str):

    actual_path = "/" + path

    file = files.get(actual_path)

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return file


@app.get("/nodes")
def get_nodes():
    return list(nodes.values())


@app.get("/files")
def list_files():
    return list(files.values())
