from utils import auth, response


def lambda_handler(event, context):
    claims = auth.get_claims(event)
    if not claims:
        return response.error("UNAUTHORIZED", "Missing or invalid token", 401)

    return response.success({
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "username": claims.get("cognito:username"),
    })
