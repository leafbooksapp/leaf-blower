def get_claims(event):
    """Returns the Cognito claims dict or None if the request is unauthenticated."""
    rc = event.get("requestContext") or {}
    authorizer = rc.get("authorizer") or {}
    claims = authorizer.get("claims") or authorizer
    if not isinstance(claims, dict) or not claims.get("sub"):
        return None
    return claims


def get_user_id(event):
    """Returns the caller's UUID (Cognito sub claim) or None."""
    claims = get_claims(event)
    return claims["sub"] if claims else None
