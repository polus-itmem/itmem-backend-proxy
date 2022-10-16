import time
from hashlib import sha256
from typing import List

import uvicorn
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware

import collector
import models
import proxy
from config import config
from dependencies import get_user_id

app = FastAPI(title = 'Proxy api', version = '1.1.0')


@app.get("/api/time", description = "Server time", response_model = int)
async def time_check():
    return int(time.time())


@app.post("/api/users/auth", response_model = models.User, description = "Check user conditionals")
async def user_authorization(user_credit: models.UserCredit, response: Response):
    out = proxy.users('/accounts/auth', user_credit.dict()).json()
    response.set_cookie(key = 'user_id', value = out['id'], samesite = "none", secure = True)
    response.set_cookie(key = 'role', value = out['role'], samesite = "none", secure = True)
    _hash = sha256((str(out['role']) + config.web_secret.get_secret_value() + str(out['id'])).encode()).hexdigest()
    response.set_cookie(key = 'user_auth', value = _hash, samesite = "none", secure = True)
    return models.User(**out)


# @app.get("/api/users/auth_test", response_model = models.User, description = "Dont use")
# async def test_user_authorization(response: Response):
#     out = {
#         "id": 3,
#         "role": 2,
#         "first_name": "Vova",
#         "second_name": "Nazarov",
#         'number': '123123123'
#     }
#     response.set_cookie(key = 'user_id', value = out['id'])
#     response.set_cookie(key = 'role', value = out['role'])
#     _hash = sha256((str(out['role']) + config.web_secret.get_secret_value() + str(out['id'])).encode()).hexdigest()
#     response.set_cookie(key = 'user_auth', value = _hash)
#     return models.User(**out)


@app.get("/api/users/out", description = "Use for check auth", response_model = int)
async def user_out(request: Request, response: Response):
    response.set_cookie(key = 'user_id', value = "", samesite = "none", secure = True)
    response.set_cookie(key = 'role', value = "", samesite = "none", secure = True)
    response.set_cookie(key = 'user_auth', value = "", samesite = "none", secure = True)
    return 1


@app.get("/api/users/check_id", description = "Use for check auth", response_model = int)
async def user_role(request: Request, response: Response):
    user_id = get_user_id([models.Role.user, models.Role.driver, models.Role.dispatcher], request, response)
    return user_id


@app.get("/api/users/get_info", description = "Authorized: None", response_model = models.User)
async def user_info(request: Request, response: Response):
    user_id = get_user_id([models.Role.driver, models.Role.driver, models.Role.dispatcher], request, response)
    return proxy.users('/accounts/get_user_info', {'id': user_id}).json()


@app.post("/api/users/create_task", description = "Authorized: User", response_model = models.Task)
async def user_task_create(request: Request, response: Response, task_credit: models.TaskCredit):
    user_id = get_user_id([models.Role.user], request, response)
    cars = proxy.cars('/cars/get_car_types', {'description': task_credit.car_type}).json()
    out = proxy.tasks('/tasks/create', {
        'user_id': user_id,
        'place': task_credit.place,
        'date': str(task_credit.date),
        'cars_ids': [car['id'] for car in cars]
    }).json()
    return collector.tasks([out])[0]


@app.get("/api/users/task", description = "Authorized: User", response_model = List[models.Task])
async def user_tasks(request: Request, response: Response):
    user_id = get_user_id([models.Role.user], request, response)
    return collector.tasks(proxy.tasks('/tasks/user', {'id': user_id}).json())


@app.get("/api/tasks/all", description = "Authorized: None", response_model = List[models.Task])
async def tasks_all(request: Request, response: Response):
    # user_id = get_user_id([models.Role.dispatcher], request, response)
    return collector.tasks(proxy.tasks('/tasks/all', {}, 'get').json())


# @app.post("/api/tasks/accept", description = "Authorized: Dispatcher", response_model = models.Task)
# async def tasks_accept(task_accept: models.TaskAccept, dispatcher_id=authorize_user):
#     return


@app.get("/api/cars/types", description = "Authorized: None", response_model = List[models.CarType])
async def cars_type():
    return proxy.cars('/cars/types', {}, 'get').json()


@app.get("/api/cars/get_cars", description = "Authorized: None", response_model = List[models.Car])
async def get_cars():
    cars = proxy.cars('/cars/get_cars', {}, 'get').json()
    ids = [{'id': i['driver_id']} for i in cars]
    try:
        users = proxy.users('/accounts/get_users_info', ids).json()
    except:
        users = {}
    users = {i['id']: models.User(**i) for i in users}
    return [models.Car(**car, driver = users.get(car['driver_id'])) for car in cars]


@app.get("/api/cars/get_my_car", description = "Authorized: Driver", response_model = List[models.Car])
async def driver_my_car(request: Request, response: Response):
    user_id = get_user_id([models.Role.driver], request, response)
    cars = proxy.cars('/cars/get_driver_car', {'id': user_id}).json()
    try:
        user = proxy.users('/accounts/get_user_info', {'id': user_id}).json()
    except:
        user = None
    return [models.Car(**car, driver = user) for car in cars]


@app.get("/api/driver/get_info", description = "Authorized: Driver", response_model = List[models.Task])
async def driver_my_info(request: Request, response: Response):
    user_id = get_user_id([models.Role.driver], request, response)
    cars = proxy.cars('/cars/get_driver_car', {'id': user_id}).json()
    tasks = proxy.tasks('/tasks/car', [{'id': i['id']} for i in cars]).json()
    return collector.tasks(tasks)


@app.post("/api/dispatcher/change_status", description = "Authorized: Dispatcher", response_model = models.Task)
async def dispatcher_moderate(request: Request, response: Response, task_credits: models.DispatcherAllowCredits):
    user_id = get_user_id([models.Role.dispatcher], request, response)
    tasks = proxy.tasks('/tasks/change',
                        {'dispatcher_id': user_id, 'task_id': task_credits.task_id, 'status': task_credits.status.to_int()}).json()
    return collector.tasks([tasks])[0]


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "https://2bac-85-143-144-46.ngrok.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials = True,
    allow_origins = origins,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

uvicorn.run(app)
