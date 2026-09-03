import json
import threading
from pathlib import Path
from typing import Any


class JSONStore:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write_raw([])

    def _read_raw(self) -> list:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_raw(self, data: list):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def read(self) -> list:
        with self._lock:
            return self._read_raw()

    def write(self, data: list):
        with self._lock:
            self._write_raw(data)

    def find(self, key_or_predicate, value: Any = None) -> list | dict | None:
        """find(predicate) → list; find(key, value) → first match or None."""
        with self._lock:
            data = self._read_raw()
            if callable(key_or_predicate):
                return [item for item in data if key_or_predicate(item)]
            for item in data:
                if item.get(key_or_predicate) == value:
                    return item
            return None

    def find_all(self, key: str, value: Any) -> list:
        with self._lock:
            data = self._read_raw()
            return [item for item in data if item.get(key) == value]

    def find_by_id(self, id: str) -> dict | None:
        return self.find("id", id)

    def update(self, id: str, updates: dict) -> dict | None:
        with self._lock:
            data = self._read_raw()
            for i, item in enumerate(data):
                if item.get("id") == id:
                    data[i] = {**item, **updates}
                    self._write_raw(data)
                    return data[i]
            return None

    def append(self, item: dict) -> dict:
        with self._lock:
            data = self._read_raw()
            data.append(item)
            self._write_raw(data)
            return item

    def delete(self, id: str) -> bool:
        with self._lock:
            data = self._read_raw()
            new_data = [item for item in data if item.get("id") != id]
            if len(new_data) == len(data):
                return False
            self._write_raw(new_data)
            return True
