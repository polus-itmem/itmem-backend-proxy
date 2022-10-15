import time
from hashlib import sha256

import uvicorn
from fastapi import FastAPI, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import models
import proxy
from config import config
from dependencies import get_user_id

app = FastAPI(title = 'Proxy api')


# user = Authorize([models.Role.user])


@app.get("/api/time", description = "Server time", response_model = int)
async def time_check():
    return int(time.time())


@app.post("/api/users/auth", response_model = models.User, description = "Check user conditionals")
async def user_authorization(user_credit: models.UserCredit, response: Response):
    out = proxy.user_microservice('/accounts/auth', user_credit.dict()).json()
    response.set_cookie(key = 'user_id', value = out['id'])
    response.set_cookie(key = 'role', value = out['role'])
    _hash = sha256((str(out['role']) + config.web_secret.get_secret_value() + str(out['id'])).encode()).hexdigest()
    response.set_cookie(key = 'user_auth', value = _hash)
    return models.User(**out)


# @app.get("/api/users/auth_test", response_model = models.User, description = "Check user conditionals")
# async def user_authorization(response: Response):
#     out = {
#         "id": 4,
#         "role": 0,
#         "first_name": "Vova",
#         "second_name": "Nazarov"
#     }
#     response.set_cookie(key = 'user_id', value = out['id'])
#     response.set_cookie(key = 'role', value = out['role'])
#     _hash = sha256((str(out['role']) + config.web_secret.get_secret_value() + str(out['id'])).encode()).hexdigest()
#     response.set_cookie(key = 'user_auth', value = _hash)
#     return models.User(**out)


@app.get("/api/users/check_id", description = "Use for check auth", response_model = int)
async def user_role(request: Request, response: Response):
    user_id = get_user_id([models.Role.user], request, response)
    return user_id


@app.post("/api/users/tasks", description = "Authorized: User", response_model = models.User)
async def user_tasks(request: Request, response: Response):
    user_id = get_user_id([models.Role.user], request, response)
    return


@app.post("/api/users/create_task", description = "Authorized: User", response_model = models.Task)
async def user_task_create(request: Request, response: Response, task_credit: models.TaskCredit):
    user_id = get_user_id([models.Role.user], request, response)
    return


# @app.post("/api/users/task", response_model = models.User)
# async def user_change(task_id: int, user_credit: models.UserCreditCreate):
#     return


# @app.post("/api/tasks/all", description = "Authorized: Dispatcher", response_model = List[models.Task])
# async def tasks_all(dispatcher_id=authorize_user):
#     return
#
#
# @app.post("/api/tasks/accept", description = "Authorized: Dispatcher", response_model = models.Task)
# async def tasks_accept(task_accept: models.TaskAccept, dispatcher_id=authorize_user):
#     return


# @app.post("/api/tasks/get")
# async def task_get(user_id=dependencies.dispatcher_auth()):
#     return

@app.get("/api/cars/types", description = "Authorized: None", response_model = models.CarTypes)
async def cars_type():
    return


@app.post("/api/cars/free", description = "Authorized: User, Dispatcher", response_model = models.CarTypes)
async def cars_free(date_range: models.DateRange):
    return


app.add_middleware(
    CORSMiddleware, allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
uvicorn.run(app)
