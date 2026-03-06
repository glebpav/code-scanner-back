import pytest

from fixtures.auth import (
    make_login_payload,
    make_refresh_payload,
    make_register_payload,
)


class TestRegisterEndpoint:
    def test_register_returns_tokens_and_role(self, session, base_url):
        payload = make_register_payload()

        response = session.post(f"{base_url}/auth/register", json=payload)

        assert response.status_code in (200, 201), response.text
        body = response.json()

        assert "access_token" in body
        assert "refresh_token" in body
        assert body.get("role") is not None

    def test_register_returns_conflict_for_existing_email(self, session, base_url):
        payload = make_register_payload()

        first_response = session.post(f"{base_url}/auth/register", json=payload)
        assert first_response.status_code in (200, 201), first_response.text

        second_response = session.post(f"{base_url}/auth/register", json=payload)

        assert second_response.status_code in (400, 409), second_response.text

    @pytest.mark.parametrize(
        ("payload", "expected_status"),
        [
            (
                make_register_payload(first_name=None, last_name=None),
                422,
            ),
            (
                make_register_payload(email="not-an-email"),
                422,
            ),
            (
                make_register_payload(password="weakpass"),
                422,
            ),
        ],
    )
    def test_register_returns_validation_error(self, session, base_url, payload, expected_status):
        response = session.post(f"{base_url}/auth/register", json=payload)

        assert response.status_code == expected_status, response.text


class TestLoginEndpoint:
    def test_login_returns_tokens_and_role(self, session, base_url):
        register_payload = make_register_payload()
        register_response = session.post(f"{base_url}/auth/register", json=register_payload)
        assert register_response.status_code in (200, 201), register_response.text

        login_payload = make_login_payload(
            email=register_payload["email"],
            password=register_payload["password"],
        )

        response = session.post(f"{base_url}/auth/login", json=login_payload)

        assert response.status_code == 200, response.text
        body = response.json()

        assert "access_token" in body
        assert "refresh_token" in body
        assert body.get("role") is not None

    def test_login_returns_not_found_or_unauthorized_for_unknown_user(self, session, base_url):
        payload = make_login_payload()

        response = session.post(f"{base_url}/auth/login", json=payload)

        assert response.status_code in (401, 404), response.text

    def test_login_returns_unauthorized_for_wrong_password(self, session, base_url):
        register_payload = make_register_payload()
        register_response = session.post(f"{base_url}/auth/register", json=register_payload)
        assert register_response.status_code in (200, 201), register_response.text

        login_payload = make_login_payload(
            email=register_payload["email"],
            password="WrongPass123",
        )

        response = session.post(f"{base_url}/auth/login", json=login_payload)

        assert response.status_code == 401, response.text


class TestRefreshEndpoint:
    def test_refresh_returns_new_tokens(self, session, base_url):
        register_payload = make_register_payload()
        register_response = session.post(f"{base_url}/auth/register", json=register_payload)
        assert register_response.status_code in (200, 201), register_response.text

        register_body = register_response.json()
        refresh_token = register_body["refresh_token"]

        response = session.post(
            f"{base_url}/auth/refresh",
            json=make_refresh_payload(refresh_token=refresh_token),
        )

        assert response.status_code == 200, response.text
        body = response.json()

        assert "access_token" in body

    def test_refresh_returns_unauthorized_for_invalid_token(self, session, base_url):
        response = session.post(
            f"{base_url}/auth/refresh",
            json=make_refresh_payload(refresh_token="definitely-invalid-token"),
        )

        assert response.status_code in (401, 403), response.text