"""Datu modeļi pēc API līguma (API contract) docs/openapi.yaml."""

import re
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

# CR-1: 11 cipari, drīkst būt viena defise tieši pēc 6. cipara.
# Jaunajam un vecajam formātam noteikums ir vienāds, kontrolciparu nepārbauda.
PERSONAL_CODE_RE = re.compile(r"[0-9]{6}-?[0-9]{5}")


class PreferredChannel(str, Enum):
    EMAIL = "EMAIL"
    POST = "POST"
    E_ADDRESS = "E_ADDRESS"


class ReplyChannel(str, Enum):
    EMAIL = "EMAIL"
    POST = "POST"
    E_ADDRESS = "E_ADDRESS"


class Topic(str, Enum):
    ROADS = "ROADS"
    WASTE = "WASTE"
    PLANNING = "PLANNING"
    PARKS = "PARKS"
    OTHER = "OTHER"  # Vienmēr saraksta beigās


TOPIC_NAMES = {
    Topic.ROADS: "Ceļi un ielas",
    Topic.WASTE: "Atkritumi",
    Topic.PLANNING: "Teritorijas plānošana",
    Topic.PARKS: "Parki un skvēri",
    Topic.OTHER: "Cits",
}


class TopicItem(BaseModel):
    code: Topic
    name: str


class SubmissionStatus(str, Enum):
    RECEIVED = "RECEIVED"
    IN_PROGRESS = "IN_PROGRESS"
    FORWARDED = "FORWARDED"
    ANSWERED = "ANSWERED"
    WITHDRAWN = "WITHDRAWN"


class SubmissionCreate(BaseModel):
    personalCode: str
    fullName: str
    email: str  # TODO: pārbaudīt e-pasta formātu
    preferredChannel: PreferredChannel
    topic: Topic
    subject: str
    body: str

    @field_validator("personalCode")
    @classmethod
    def normalize_personal_code(cls, value: str) -> str:
        value = value.strip()
        if not value:
            # Tukša vērtība tāpat kā trūkstošs lauks: REQUIRED (CR-1 precizējums).
            raise PydanticCustomError("missing", "Field required")
        if not PERSONAL_CODE_RE.fullmatch(value):
            raise ValueError("invalid personal code format")
        return value.replace("-", "")


class SubmissionCreated(BaseModel):
    id: str
    status: SubmissionStatus
    receivedAt: datetime
    dueDate: date
    replyChannel: ReplyChannel
    reasonCode: str | None = None


class Submission(SubmissionCreated, SubmissionCreate):
    pass


class Health(BaseModel):
    status: str
    version: str


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class Error(BaseModel):
    error: ErrorBody
