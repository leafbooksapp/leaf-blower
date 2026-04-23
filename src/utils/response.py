import json


def success(data, status_code=200, headers=None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    return {
        "statusCode": status_code,
        "headers": h,
        "body": json.dumps({"data": data, "error": None}),
    }


def error(code, message, status_code=400):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"data": None, "error": {"code": code, "message": message}}),
    }
