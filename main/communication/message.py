"""For websocket communication."""

from dataclasses import dataclass, asdict, field
from typing import Union, Dict, Any
import json

PREFIX = b'!'
LENGTH = 8
DATA_LENGTH = LENGTH - 4

@dataclass
class ClientToServer:
    service: str
    data: Union[str, Dict[str, Any]]

    def __post_init__(self):
        assert isinstance(self.service, str), "ClientToServer.service should be a string"
        assert isinstance(self.data, (str, dict)), "ClientToServer.data should be a string or a dictionary"

    def show(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(asdict(self))


@dataclass
class ServerToClient:
    status: int
    data: Union[str, Dict[str, Any]]

    def __post_init__(self):
        assert isinstance(self.status, int), "ServerToClient.status should be an integer"
        assert isinstance(self.data, (str, dict)), "ServerToClient.data should be a string or a dictionary"

    def show(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(asdict(self))


@dataclass
class ToSerial:
    data: list[int]
    prefix: int = ord(PREFIX)
    length: int = LENGTH
    data_length: int = DATA_LENGTH
    checksum: list[int] = field(default_factory=lambda: [0, 0])

    def __post_init__(self):
        assert isinstance(self.data, list), "ToSerial.data should be a list"
        assert all(isinstance(x, int) for x in self.data), "All elements in ToSerial.data should be integers"
        assert all(0 <= x <= 255 for x in self.data), "All elements in ToSerial.data should be integers between 0 and 255"
        assert len(self.data) == DATA_LENGTH, "ToSerial.data length should be equal to ToSerial.data_length"

    def _update_checksum(self):
        checksum = sum([self.prefix, self.length, *self.data])
        self.checksum = [checksum // 256, checksum % 256]

    def show(self):
        self._update_checksum()
        return [self.prefix, self.length, *self.data, *self.checksum]

    def to_bytes(self):
        return bytes(self.show())