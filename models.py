from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel


# Для расширения не обязательно все переносить сюда всё из других микросервисов. Сейчас это сделано для документации.
# возможно парсить документацию микросервисов и прикручивать.

class DateRange(BaseModel):
    start: date
    end: date


class ModelId(BaseModel):
    id: int


class Role(Enum):
    """-1 - un_auth, 0 - user, 1 - dispatcher, 2 - driver"""

    un_auth = -1
    user = 0
    dispatcher = 1
    driver = 2


class UserCredit(BaseModel):
    login: str
    password: str


class UserCreditCreate(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str


class User(BaseModel):
    id: int

    role: Role
    first_name: str
    second_name: str
    number: str


class CarType(BaseModel):
    description: str


class Car(BaseModel):
    id: int

    park: str
    type: CarType
    name: str
    number: str
    driver: Optional[User]


class TaskCredit(BaseModel):
    date: date
    car_type: str
    place: str


class TaskAccept(BaseModel):
    id: int


class TaskStatus(Enum):
    """-1 - finished, 0 - wait, 1 - process"""
    finished = -1
    wait = 0
    process = 1

    def to_int(self):
        return {
            TaskStatus.finished: -1,
            TaskStatus.wait: 0,
            TaskStatus.process: 1
        }[self]


class TaskModerate(BaseModel):
    dispatcher: User
    status: TaskStatus


class Task(BaseModel):
    id: int

    date: date
    moderate: Optional[TaskModerate]
    place: str
    car: Optional[Car]


class DispatcherAllowCredits(BaseModel):
    task_id: int
    status: TaskStatus

