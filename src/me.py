import json


def lambda_handler(event, context):
    rc = event.get("requestContext") or {}
    auth = rc.get("authorizer") or {}
    claims = auth.get("claims") or auth
    if not isinstance(claims, dict) or not claims.get("sub"):
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Unauthorized"}),
        }
    body = {
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "username": claims.get("cognito:username"),
    }
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
