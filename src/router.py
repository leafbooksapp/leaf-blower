from handlers import books_search, health, me
from utils import response

# (method, path) -> handler
ROUTES = {
    ("GET", "/v1/health"): health.lambda_handler,
    ("GET", "/v1/me"): me.lambda_handler,
    ("GET", "/v1/books/search"): books_search.lambda_handler,
}


def lambda_handler(event, context):
    method = event.get("httpMethod", "")
    path = event.get("path", "")
    handler = ROUTES.get((method, path))
    if not handler:
        return response.error("NOT_FOUND", f"No route for {method} {path}", 404)
    return handler(event, context)
