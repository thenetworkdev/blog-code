from ipaddress import IPv4Address

from pydantic import BaseModel


class Credentials(BaseModel):
    username: str
    password: str


class Device(BaseModel):
    nodeid: int
    ip: IPv4Address
    hostname: str
    platform: str
    serial: str | None
    version: str | None
