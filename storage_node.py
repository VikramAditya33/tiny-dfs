import os
import sys
import requests

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

app = FastAPI()

NODE_ID = os.environ.get("NODE_ID", "node1")
PORT = int(os.environ.get("PORT", "9001"))

MASTER_URL = os.environ.get(
    "MASTER_URL",
    "http://localhost:8000"
)

SELF_URL = os.environ.get(
    "SELF_URL",
    f"http://localhost:{PORT}"
)

DATA_DIR = os.environ.get(
    "DATA_DIR",
    f"./data-{NODE_ID}"
)

os.makedirs(DATA_DIR, exist_ok=True)


@app.on_event("startup")
def startup():
    response = requests.post(
        f"{MASTER_URL}/nodes/register",
        json={
            "node_id": NODE_ID,
            "url": SELF_URL
        }
    )

    response.raise_for_status()

    print(
        f"{NODE_ID} registered with master"
    )


@app.put("/chunks/{chunk_id}")
async def store_chunk(
    chunk_id: str,
    request: Request
):
    data = await request.body()

    path = os.path.join(
        DATA_DIR,
        chunk_id
    )

    with open(path, "wb") as f:
        f.write(data)

    return {
        "chunk_id": chunk_id,
        "bytes": len(data)
    }


@app.get("/chunks/{chunk_id}")
def read_chunk(chunk_id: str):

    path = os.path.join(
        DATA_DIR,
        chunk_id
    )

    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail="Chunk not found"
        )

    with open(path, "rb") as f:
        data = f.read()

    return Response(
        content=data,
        media_type="application/octet-stream"
    )


@app.delete("/chunks/{chunk_id}")
def delete_chunk(chunk_id: str):

    path = os.path.join(
        DATA_DIR,
        chunk_id
    )

    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail="Chunk not found"
        )

    os.remove(path)

    return {
        "deleted": chunk_id
    }
