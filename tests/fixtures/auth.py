from uuid import uuid4


def unique_email() -> str:
    return f"test_{uuid4().hex[:12]}@example.com"


def make_register_payload(**overrides):
    payload = {
        "email": unique_email(),
        "password": "StrongPass123!",
        "first_name": "Gleb",
        "last_name": "Tester",
        "company": "Test Company",
    }
    payload.update(overrides)
    return payload


def make_login_payload(**overrides):
    payload = {
        "email": unique_email(),
        "password": "StrongPass123",
    }
    payload.update(overrides)
    return payload


def make_refresh_payload(**overrides):
    payload = {
        "refresh_token": "invalid-or-placeholder-token",
    }
    payload.update(overrides)
    return payload