import time

Success = 200
NotLogin = 400
ResourceExist = 401
ResourceNotPermit = 403
ServerError = 500
ParameterError = 501


class Output(object):
    def __init__(self):
        pass

    @classmethod
    def output(cls, data, code, message):
        return {
            'responseTime': time.time(),
            'success': True,
            'code': code,
            'data': data,
            'message': message
        }

    @classmethod
    def success(cls, data):
        return cls.output(data, Success, "ok")

    @classmethod
    def error(cls, data):
        return cls.output(data, ServerError, "error")

