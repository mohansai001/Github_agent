from fastapi import APIRouter, Depends, HTTPException
from vida.models.requests.Agents_requests import github_agent_request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials #type: ignore
from vida.utils.request_context import github_pat_ctx
from github_agent import github_agent
from github_tools.mcp_tool import github_mcp_tool
router = APIRouter()
security = HTTPBearer()

@router.post("/github_agent")
async def github_agent_call(request: github_agent_request): #, authorization: HTTPAuthorizationCredentials = Depends(security)):
    # print("SCHEME:", authorization.scheme)
    # print("AUTH:", authorization.credentials)

    # if not authorization:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Missing token"
    #     )
    git_token = request.pat_token # .credentials #.replace("Bearer ", "")
    print(f"Token received: {git_token}")
    prompt = request.prompt

    token_ref = github_pat_ctx.set(git_token) #type: ignore
    session = request.session
    try:
        agent = await github_agent()
        async with github_mcp_tool() as mcp:
            response = await agent.run(prompt, tools=[mcp],session=session)

        return {
            "response": f"Github agent executed successfully",
            "agent_output": response
        }

    finally:
        github_pat_ctx.reset(token_ref)