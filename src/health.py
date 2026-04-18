import json


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Cache-Control": "max-age=60",
        },
        "body": json.dumps({"status": "ok", "service": "leaf-blower"}),
    }
