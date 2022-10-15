from datetime import date
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


# Для расширения не обязательно все переносить сюда всё из других микросервисов. Сейчас это сделано для документации.
# возможно парсить документацию микросервисов и прикручивать.

class DateRange(BaseModel):
    start: date
    end: date


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


class Driver(BaseModel):
    id: int

    first_name: str
    second_name: str


class Car(BaseModel):
    id: int

    park: str
    description: str
    name: str
    number: str
    driver: Optional[Driver]


class CarType(BaseModel):
    description: str


class CarTypes(BaseModel):
    types: List[CarType]


class TaskCredit(BaseModel):
    date: date
    car_type: str


class TaskAccept(BaseModel):
    id: int


class Task(BaseModel):
    id: int

    date: date
    car_accept: bool
    car: Optional[Car]


class Tasks(BaseModel):
    tasks: List[Task]


class Time(BaseModel):
    time: float
