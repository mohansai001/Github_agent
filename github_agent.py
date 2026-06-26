from dotenv import load_dotenv
load_dotenv()
from vida.agents.Base_agent import Base_Agent
from agent_framework import Agent #type: ignore
from agent_framework import tool #type: ignore
from typing import Annotated
from pydantic import Field
from github_tools.base_trail import (
    get_user, monitor_workflows, commit_files, read_file, set_secret,
    list_branches, create_branch, list_commits, list_workflows,
    create_pull_request, create_issue, create_release, 
)
from vida.utils.prompt_manager_v2 import AgentDescriptionPrompt, AgentInstructionPrompt, ToolFieldsPrompt
from vida.utils.logger import get_logger
from github_tools.mcp_tool import github_mcp_tool

logger = get_logger(__name__)

from dataclasses import dataclass

@dataclass
class GithubContext:
    github_pat: str

class GithubAgent(Base_Agent):   
    name = "github_agent"
    instructions = str(AgentInstructionPrompt("github-agent-instructions"))
    tools = [ get_user, monitor_workflows ] 
    #     , commit_files, read_file,
    #     list_branches, create_branch, list_commits, list_workflows,
    #     create_pull_request, create_issue, create_release,
    # ]

_git_agent_field = ToolFieldsPrompt("git-agent-field-description")

@tool(name="Github_Agent", description=str(AgentDescriptionPrompt("github-agent-description")), approval_mode="never_require")
async def github_agent(): #prompt: Annotated[str, Field(description = _git_agent_field.get("prompt"))]):
    logger.info("[github_agent] Called with prompt.")
    print("[github_agent] Called with prompt.")
    # logger.debug(f"[github_agent] Prompt: {prompt}")
    # print(f"[github_agent] Prompt: {prompt}")
    try:
        agent = GithubAgent.get_instance()
        # if agent._session != None:
        print(vars(agent._session))
        print(agent._session)
        # async with github_mcp_tool() as mcp:
        #     result = await agent.run(prompt, tools=[mcp]) #type: ignore
        # result = await GithubAgent.get_instance().run(prompt) #type: ignore
        logger.info("[github_agent] Successfully generated GitHub agent output.")
        print("[github_agent] Successfully generated GitHub agent output.")
        return agent
    except Exception as e:
        logger.error(f"[github_agent] Error occurred: {e}", exc_info=True)
        print(f"[github_agent] Error occurred: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    print(asyncio.run(GithubAgent.get_instance().run("get the owner name"))) #type: ignore


