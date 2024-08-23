from dataclasses import dataclass
from typing import Literal


@dataclass
class TimeEvent:
    timestamp: str
    value: float
    author: str
    message: str
    type: str


@dataclass
class UpdateTimerEvent:
    timestamp: str
    action: Literal["add"] | Literal["remove"] | Literal["update"]

    value: float


@dataclass
class Result:
    timestamp: str
    action: Literal["add"] | Literal["remove"] | Literal["update"]
    value: float
    timer: float

