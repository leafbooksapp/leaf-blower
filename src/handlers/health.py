from utils import response


def lambda_handler(event, context):
    return response.success(
        {"status": "ok", "service": "leaf-blower"},
        headers={"Cache-Control": "max-age=60"},
    )
