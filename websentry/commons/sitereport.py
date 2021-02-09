from typing import Optional
import json
from dataclasses import dataclass, field, asdict

@dataclass
class SiteReport():
    url: str
    code: int
    response_ms: int
    regexp_match: Optional[str] = field(default=None)

    def as_dict(self):
        return asdict(self)

    def as_json(self) -> str:
        return json.dumps(self.as_dict())

    @classmethod
    def from_dict(cls, data: dict) -> 'SiteReport':
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'SiteReport':
        return cls(**json.loads(json_str))
