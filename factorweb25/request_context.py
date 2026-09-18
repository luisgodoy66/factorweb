from contextvars import ContextVar


request_id_context = ContextVar("request_id", default=None)
empresa_id_context = ContextVar("empresa_id", default=None)


def get_request_id():
    return request_id_context.get()


def get_current_empresa_id():
    return empresa_id_context.get()