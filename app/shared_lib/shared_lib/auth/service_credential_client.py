import time
from typing import Optional, Dict, Any

import httpx
from fastapi import HTTPException


class ClientCredentialsClient:
    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: Optional[str] = None,
        timeout: float = 5.0,
    ) -> None:
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope
        self._timeout = timeout

        # Token cache
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0

        self._http_client = httpx.AsyncClient(timeout=self._timeout)

    async def close(self) -> None:
        await self._http_client.aclose()

    async def _fetch_token(self) -> None:
        data: Dict[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        print(f"{data=}")

        if self._scope:
            data["scope"] = self._scope

        try:
            resp = await self._http_client.post(
                self._token_url,
                data=data,
            )
            print(f"{resp=}, {resp.status_code} {resp.text}")
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"OAuth2 token request error: {exc}",
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"OAuth2 token request failed: {resp.status_code} {resp.text}",
            )

        payload = resp.json()

        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in", 3600)

        if not access_token:
            raise HTTPException(
                status_code=500,
                detail="OAuth2 token response does not contain 'access_token'",
            )

        self._access_token = access_token
        self._expires_at = time.time() + int(expires_in) - 10

    async def get_access_token(self) -> str:
        """
        Public method - always returns valid access token.
        It can renew it if needed.
        """
        now = time.time()
        if self._access_token is None or now >= self._expires_at:
            await self._fetch_token()
        return self._access_token

    async def auth_headers(self) -> Dict[str, str]:
        token = await self.get_access_token()
        return {"Authorization": f"Bearer {token}"}