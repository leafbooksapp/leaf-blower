from domain import books
from utils import auth, response


def lambda_handler(event, context):
    if not auth.get_user_id(event):
        return response.error("UNAUTHORIZED", "Missing or invalid token", 401)

    params = event.get("queryStringParameters") or {}
    q = (params.get("q") or "").strip()
    if not q:
        return response.error("VALIDATION_ERROR", "Missing required query parameter: q", 400)

    results = books.search(q)
    return response.success({
        "items": [b.to_dict() for b in results] if results else [],
    })
