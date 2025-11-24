from dataclasses import dataclass


@dataclass
class PanjiSignEntity(object):
    username: str = None
    password: str = None
    tenant_code: str = None
    expire_time: int = 18000000