from fastapi import APIRouter, Depends, HTTPException
from vida.models.requests.Agents_requests import github_agent_request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials #type: ignore
from github_agent import github_agent
from github_tools.mcp_tool import github_mcp_tool
from vida.utils.preprocess import try_parse_json
from vida.models.requests.Agent_Task_requests import AgentTaskDetailsCreateRequest, AgentTaskDetailsUpdateRequest
from vida.database.database import sessionlocal
from vida.utils.request_context import github_pat_ctx, task_id_ctx

from vida.utils.crud_ops import AgentTaskOps as ato
from datetime import datetime, timezone

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
    # print(f"Token received: {git_token}")
    task_id = request.task_id
    db = sessionlocal()

    if not task_id:
        payload = AgentTaskDetailsCreateRequest(
            agent_id = 3,
            task_status = "pending",
            task_prompt = request.prompt,
            task_name = request.prompt[:20],
            start_time = datetime.now(timezone.utc)
        )

        task_id= ato().add_task(db=db, task=payload)
        if not task_id:
            ato().update_task(
                db=db,
                task_id=task_id,
                task = AgentTaskDetailsUpdateRequest(
                    task_status = "failed",
                    end_time = datetime.now(timezone.utc),
                    issue = "Failed to create task"
                )
            )
            return {"message": "Failed to create task"}
        else:
            task_id_ref = task_id_ctx.set(task_id)
    else:
        task_id_ref = task_id_ctx.set(task_id)

    if git_token:
        token_ref = github_pat_ctx.set(git_token)
    else:
        ato().update_task(
            db=db,
            task_id=task_id,
            task = AgentTaskDetailsUpdateRequest(
                task_status = "failed",
                end_time = datetime.now(timezone.utc),
                issue = "No git token provided"
            )
        )
        return {"message": "No git token provided"}

    prompt = request.prompt

    token_ref = github_pat_ctx.set(git_token) #type: ignore
    session = request.session
    try:
        agent = await github_agent()
        async with github_mcp_tool() as mcp:
            response = await agent.run(prompt, tools=[mcp],session=session,task_id=task_id)

        # mcp= github_agent()
        # response = await agent.run(prompt, tools=[mcp],session=session)
        if response:
            output, is_json = try_parse_json(response.text)
            ato().update_task(
                db=db,
                task_id=task_id,
                task = AgentTaskDetailsUpdateRequest(
                    db=db,
                    task_id = task_id,
                    task_status = "success",
                    end_time = datetime.now(timezone.utc),
                    )
                )
            return {
                "response": f"Github agent executed successfully",
                "raw": response,
                "is_json": is_json,
                "output": output
            }
        print("Failed to get response from agent")  
        ato().update_task(
            db=db,
            task_id=task_id,
            task = AgentTaskDetailsUpdateRequest(
                db=db,
                task_id=task_id,
                end_time = datetime.now(timezone.utc),
                task_status = "failed",
                issue = "Failed to get response from agent"
            )
        )             
        return {"message": "Failed to get response from agent"}

    except Exception as e:
        issue = str(e)
        ato().update_task(
            db=db,
            task_id=task_id,
            task = AgentTaskDetailsUpdateRequest(
                task_status = "failed",
                end_time = datetime.now(timezone.utc),
                issue = issue
            )
        )
        raise

    finally:
        github_pat_ctx.reset(token_ref)
        task_id_ctx.reset(task_id_ref)
        db.close()

from vida.adapters.github.git_action import git_dispatch_workflow
from vida.utils.github_client import get_github_client

@router.get("/github_agent/test_dispatch_workflow")
async def test_dispatch_workflow():
    git_dispatch_workflow("Hari-var/test1","pipeline.yml", "/fix/probable-solutions-20260706",g=get_github_client("s"))
    return ("workflow dispatched successfully")