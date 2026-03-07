from uuid import uuid4


def make_create_user_token_payload(**overrides):
    payload = {
        "first_name": f"Test-{uuid4().hex[:8]}",
        "last_name": "User",
    }
    payload.update(overrides)
    return payload