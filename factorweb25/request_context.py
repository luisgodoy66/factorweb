from contextvars import ContextVar


request_id_context = ContextVar("request_id", default=None)


def get_request_id():
    return request_id_context.get()