import models
import proxy


def tasks(tasks: [dict]) -> [models.Task]:
    # get cars
    try:
        cars = proxy.cars('/cars/get_cars', {}, 'get').json()
    except:
        cars = {}

    cars = {i['id']: i for i in cars}
    users = set([i['driver_id'] for i in cars.values()])
    for i in tasks:
        if i['moderate']:
            users.add(i['moderate']['dispatcher_id'])

    try:
        users = proxy.users('/accounts/get_users_info', [{'id': i} for i in list(users)]).json()
    except:
        users = {}
    users = {i['id']: i for i in users}

    for i in cars.values():
        if i['driver_id']:
            i['driver'] = models.User(**users[i['driver_id']])

    out = []
    for i in tasks:
        if i['moderate']:
            i['moderate']['dispatcher'] = users.get(i['moderate']['dispatcher_id'])
        else:
            i['moderate'] = None
        i['car'] = cars.get(i['car_id'])
        out.append(models.Task(**i))

    return out