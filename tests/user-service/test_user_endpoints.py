import os
from uuid import uuid4

import pytest

from fixtures.user_token import make_create_user_token_payload


@pytest.fixture(scope="session")
def user_service_base_url(base_url):
    """
    Lets you point tests either:
    - directly to user-service, e.g. http://127.0.0.1:5000
    - or to a gateway/proxy if you expose /user-token there

    Priority:
    1. TEST_USER_SERVICE_BASE_URL
    2. TEST_BASE_URL
    3. base_url fixture fallback
    """
    return (
        os.getenv("TEST_USER_SERVICE_BASE_URL")
        or os.getenv("TEST_BASE_URL")
        or base_url
    )


class TestCreateUserTokenEndpoint:
    def test_create_user_token_returns_created_token(self, session, user_service_base_url):
        payload = make_create_user_token_payload()

        response = session.post(
            f"{user_service_base_url}/user-token/create",
            json=payload,
        )

        assert response.status_code == 201, response.text
        body = response.json()

        assert body.get("token_id") is not None
        assert body["first_name"] == payload["first_name"]
        assert body["last_name"] == payload["last_name"]
        assert body["is_active"] is True
        assert body.get("created_at") is not None
        assert body.get("token")
        assert isinstance(body["token"], str)

    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"first_name": "OnlyFirstName"},
            {"last_name": "OnlyLastName"},
            {"first_name": None, "last_name": "User"},
            {"first_name": "Test", "last_name": None},
        ],
    )
    def test_create_user_token_returns_validation_error(self, session, user_service_base_url, payload):
        response = session.post(
            f"{user_service_base_url}/user-token/create",
            json=payload,
        )

        assert response.status_code == 422, response.text
        body = response.json()
        assert "error" in body


class TestGetUserTokensEndpoint:
    def test_get_user_tokens_returns_created_token(self, session, user_service_base_url):
        payload = make_create_user_token_payload()

        create_response = session.post(
            f"{user_service_base_url}/user-token/create",
            json=payload,
        )
        assert create_response.status_code == 201, create_response.text
        created_body = create_response.json()

        response = session.get(f"{user_service_base_url}/user-token/all")

        assert response.status_code == 200, response.text
        body = response.json()

        assert isinstance(body, list)
        assert any(item["token_id"] == created_body["token_id"] for item in body)

        matched_item = next(item for item in body if item["token_id"] == created_body["token_id"])
        assert matched_item["first_name"] == payload["first_name"]
        assert matched_item["last_name"] == payload["last_name"]
        assert matched_item["is_active"] is True
        assert matched_item.get("token")


class TestDeactivateUserTokenEndpoint:
    def test_deactivate_token_returns_no_content_and_marks_token_inactive(self, session, user_service_base_url):
        payload = make_create_user_token_payload()

        create_response = session.post(
            f"{user_service_base_url}/user-token/create",
            json=payload,
        )
        assert create_response.status_code == 201, create_response.text
        created_body = create_response.json()
        token_id = created_body["token_id"]

        deactivate_response = session.delete(
            f"{user_service_base_url}/user-token/deactivate/{token_id}"
        )

        assert deactivate_response.status_code == 204, deactivate_response.text
        assert not deactivate_response.text

        list_response = session.get(f"{user_service_base_url}/user-token/all")
        assert list_response.status_code == 200, list_response.text
        tokens = list_response.json()

        matched_item = next(item for item in tokens if item["token_id"] == token_id)
        assert matched_item["is_active"] is False

    def test_deactivate_token_returns_validation_error_for_invalid_uuid(self, session, user_service_base_url):
        response = session.delete(
            f"{user_service_base_url}/user-token/deactivate/not-a-valid-uuid"
        )

        assert response.status_code == 422, response.text
        body = response.json()
        assert "error" in body

    def test_deactivate_non_existing_token_still_returns_no_content(self, session, user_service_base_url):
        non_existing_token_id = str(uuid4())

        response = session.delete(
            f"{user_service_base_url}/user-token/deactivate/{non_existing_token_id}"
        )

        # Current implementation returns 204 even when token does not exist.
        assert response.status_code == 204, response.text