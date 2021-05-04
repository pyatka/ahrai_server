from settings import PAIRED
from model import PositionModel, EmployerModel

processors = {
    "ADD": [
        "add_duty_with_holiday",
        "add_same_cover_position",
        "add_full_day_position",
    ],
    "DELETE": [
        "delete_duty_holiday",
        "delete_duty",
    ]
}

def position_edit(type):
    def decorator(function):
        def wrapper(*args, **kwargs):
            global processors
            result = []
            for fname in processors[type]:
                result.extend(globals()[fname](*args, **kwargs))
            result.extend(function(*args, **kwargs))
            return result
        return wrapper
    return decorator

def add_duty_with_holiday(day, position_id, employer_id, view_order, **kwargs):
    result = []
    if str(position_id) in PAIRED.keys():
        tomorrow = day.get_tomorrow()
        result.extend(tomorrow.add_position_employer(PAIRED[str(position_id)], employer_id, 0))

        pm = PositionModel(PAIRED[str(position_id)])
        em = EmployerModel(employer_id)

        result.append({
            "type": "info",
            "message": "%s added to %s tomorrow (%s)" % (str(em), str(pm), str(tomorrow))
        })
    return result

def add_full_day_position(day, position_id, employer_id, view_order, **kwargs):
    result = []

    pm = PositionModel(position_id)
    cpdata = pm.get_position_data()
    if cpdata["capacity"] == 3:
        positions = day.get_employer_positions(employer_id)
        if len(positions) > 0:
            to_disable = False
            for p in positions:
                data = p.get_position_data()
                if(data["capacity"] != 2):
                    to_disable = True
                    break
            
            if to_disable:
                em = EmployerModel(employer_id)
                for p in positions:
                    result.extend(day.force_delete_position_employer(p.id, employer_id))
                    result.append({
                        "type": "danger",
                        "message": "%s deleted from %s today (%s)" % (str(em), str(p), str(day))
                    })

    return result

def add_same_cover_position(day, position_id, employer_id, view_order, **kwargs):
    result = []

    pm = PositionModel(position_id)
    cpdata = pm.get_position_data()
    if cpdata["capacity"] == 2:
        for p in day.get_employer_positions(employer_id):
            data = p.get_position_data()
            if(data["capacity"] == 2):
                result.extend(day.force_delete_position_employer(p.id, employer_id))
                em = EmployerModel(employer_id)

                result.append({
                    "type": "danger",
                    "message": "%s deleted from %s today (%s)" % (str(em), str(p), str(day))
                })

    return result

def delete_duty_holiday(day, position_id, employer_id, **kwargs):
    result = []
    if position_id in PAIRED.values():
        yesterday = day.get_yesterday()
        for p in PAIRED.keys():
            if PAIRED[p] == position_id:
                result.extend(yesterday.delete_position_employer(int(p), employer_id))
                if yesterday.pg.count > 0:
                    pm = PositionModel(int(p))
                    em = EmployerModel(employer_id)

                    result.append({
                        "type": "danger",
                        "message": "%s deleted from %s yesterday (%s)" % (str(em), str(pm), str(yesterday))
                    })

    return result

def delete_duty(day, position_id, employer_id, **kwargs):
    result = []
    if str(position_id) in PAIRED.keys():
        tomorrow = day.get_tomorrow()
        result.extend(tomorrow.force_delete_position_employer(PAIRED[str(position_id)], employer_id))

        pm = PositionModel(PAIRED[str(position_id)])
        em = EmployerModel(employer_id)

        result.append({
            "type": "warning",
            "message": "%s deleted from %s tomorrow (%s)" % (str(em), str(pm), str(tomorrow))
        })
    return result