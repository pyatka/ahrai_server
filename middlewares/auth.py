from settings import UNPROTECTED_PATH
from model import auth_by_token

def auth(permissions=[], response=None):
    def decorator(function):
        def wrapper(*args, **kwargs):
            result = response
            if kwargs["user"] is not None and kwargs["user"].check_permissoins(permissions):
                result = function(*args, **kwargs)
            return result
        return wrapper
    return decorator

def is_ignored(path):
    for upath in UNPROTECTED_PATH:
        if len(path) > len(upath):
            if set(path[:len(upath)]) == upath:
                return True
        elif set(path) == upath:
            return True
    return False

def authorization_middleware(next, root, info, **args):
    if "user" not in args.keys():
        auth_token = info.context.headers.get("Authorization", None)
        if auth_token is not None:
            args["user"] = auth_by_token(auth_token[7:])
        else:
           args["user"] = None 

    if is_ignored(info.path):
        return next(root, info, **args)
    else:
        return next(root, info, **args)