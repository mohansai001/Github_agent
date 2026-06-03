import requests
from typing import Any
import httpx

@property
def _headers(self) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {self.token}",
        "X-GitHub-Api-Version": self.api_version,
        "User-Agent": "devops-agent-maf",
    }

async def _request(
    self,
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    follow_redirects: bool = False,
) -> httpx.Response:
    async with httpx.AsyncClient(
        base_url=self.api_base_url,
        headers=self._headers,
        timeout=self.timeout_seconds,
        follow_redirects=follow_redirects,
    ) as client:
        response = await client.request(method, path, params=params, json=json_body)

    if response.status_code in {401}:
        raise AdapterAuthenticationError("GitHub authentication failed.")
    if response.status_code in {403}:
        raise AdapterAuthorizationError(response.text or "GitHub authorization failed.")
    if response.status_code in {404}:
        raise AdapterNotFoundError(f"GitHub resource not found for {path}.")
    if response.status_code in {409, 422}:
        raise AdapterConflictError(response.text or "GitHub reported a conflicting state.")
    if response.status_code >= 400:
        raise AdapterValidationError(f"GitHub request failed with status {response.status_code}: {response.text}")
    return response

async def get_languages(self, repo: str) -> dict[str, int]:
        """Fetch language distribution for a repository."""
        owner, repo_name = self._split_repo(repo)
        response = requests.get(f"/repos/{owner}/{repo_name}/languages")
        return response.json()