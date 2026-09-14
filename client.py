import os
import sys
import math
import requests

MASTER = "http://localhost:8000"

CHUNK_SIZE = 4 * 1024 * 1024


def upload(local_path, remote_path):

    file_size = os.path.getsize(local_path)

    number_of_chunks = math.ceil(
        file_size / CHUNK_SIZE
    )

    metadata = requests.post(
        f"{MASTER}/files",
        json={
            "path": remote_path,
            "size": file_size,
            "chunks": number_of_chunks,
            "replication_factor": 2
        }
    )

    metadata.raise_for_status()
    metadata = metadata.json()

    with open(local_path, "rb") as f:

        for chunk in metadata["chunks"]:

            data = f.read(CHUNK_SIZE)

            chunk_id = chunk["chunk_id"]

            successful_replicas = 0

            for node in chunk["replicas"]:

                try:

                    url = (
                        f"{node['url']}"
                        f"/chunks/{chunk_id}"
                    )

                    response = requests.put(
                        url,
                        data=data,
                        timeout=30
                    )

                    response.raise_for_status()

                    successful_replicas += 1

                    print(
                        f"{chunk_id} -> "
                        f"{node['id']}"
                    )

                except Exception as e:

                    print(
                        f"Failed replica "
                        f"{node['id']}: {e}"
                    )

            if successful_replicas == 0:
                raise RuntimeError(
                    f"Lost chunk {chunk_id}"
                )

    print(
        f"Uploaded {local_path} "
        f"as {remote_path}"
    )


def download(remote_path, local_path):

    path = remote_path.lstrip("/")

    response = requests.get(
        f"{MASTER}/files/{path}"
    )

    response.raise_for_status()

    metadata = response.json()

    chunks = sorted(
        metadata["chunks"],
        key=lambda c: c["index"]
    )

    with open(local_path, "wb") as output:

        for chunk in chunks:

            chunk_id = chunk["chunk_id"]

            downloaded = False

            for node in chunk["replicas"]:

                try:

                    url = (
                        f"{node['url']}"
                        f"/chunks/{chunk_id}"
                    )

                    response = requests.get(
                        url,
                        timeout=30
                    )

                    response.raise_for_status()

                    output.write(
                        response.content
                    )

                    downloaded = True

                    print(
                        f"{chunk_id} <- "
                        f"{node['id']}"
                    )

                    break

                except Exception:

                    print(
                        f"{node['id']} unavailable, "
                        f"trying next replica"
                    )

            if not downloaded:
                raise RuntimeError(
                    f"No replica available for "
                    f"{chunk_id}"
                )

    print(
        f"Downloaded {remote_path} "
        f"to {local_path}"
    )


def main():

    if len(sys.argv) < 4:
        print(
            "Usage:\n"
            "  python client.py upload "
            "<local> <remote>\n"
            "  python client.py download "
            "<remote> <local>"
        )

        return

    operation = sys.argv[1]

    if operation == "upload":

        upload(
            sys.argv[2],
            sys.argv[3]
        )

    elif operation == "download":

        download(
            sys.argv[2],
            sys.argv[3]
        )

    else:

        print("Unknown operation")


if __name__ == "__main__":
    main()
