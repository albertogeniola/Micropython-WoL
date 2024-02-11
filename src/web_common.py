import ujson

from microdot_asyncio import Response

_RESP_HEADERS = {"Content-Type": "application/json"}
_HTML_HEADERS = {"Content-Type": "text/html"}


class BadRequest(Exception):
    pass


def make_json_response(data, error=None, status_code=None, additional_headers=None):
    code = status_code if status_code is not None else 400 if error is not None else 200
    data = ujson.dumps({"data": data, "error": error})
    headers = _RESP_HEADERS
    if additional_headers is not None:
        headers = _RESP_HEADERS.copy()
        headers.update(additional_headers)
    return Response(data, status_code=code, headers=headers)
