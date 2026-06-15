from pathlib import Path


class LocalDocumentStorage:
    def __init__(self, root_path: str) -> None:
        self._root_path = Path(root_path)
        self._root_path.mkdir(parents=True, exist_ok=True)

    def save(self, storage_key: str, content: bytes) -> None:
        destination = self._root_path / storage_key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    def delete(self, storage_key: str) -> None:
        path = self._root_path / storage_key

        if path.exists():
            path.unlink()

    def exists(self, storage_key: str) -> bool:
        return (self._root_path / storage_key).exists()