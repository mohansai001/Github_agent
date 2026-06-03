from fastapi import APIRouter, Depends, HTTPException
from vida.models.requests.Agents_requests import github_agent_request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials #type: ignore
from vida.utils.request_context import github_pat_ctx
from github_agent import github_agent
router = APIRouter()
security = HTTPBearer()

@router.post("/github_agent")
async def github_agent_call(request: github_agent_request, authorization: HTTPAuthorizationCredentials = Depends(security)):
    print("SCHEME:", authorization.scheme)
    print("AUTH:", authorization.credentials)

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing token"
        )
    git_token = authorization.credentials #.replace("Bearer ", "")
    print(f"Token received: {git_token}")
    prompt = request.prompt

    token_ref = github_pat_ctx.set(git_token)

    try:
        response = await github_agent(prompt)

        return {
            "response": f"Github agent executed successfully",
            "agent_output": response
        }

    finally:
        github_pat_ctx.reset(token_ref)