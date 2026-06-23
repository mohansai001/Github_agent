from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from typing import Annotated

from agent_framework import tool                 # type: ignore
from agent_framework._mcp import MCPTool         # type: ignore
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from pydantic import Field

from vida.agents.Base_agent import Base_Agent
from vida.utils.prompt_manager_v2 import AgentDescriptionPrompt, AgentInstructionPrompt, ToolFieldsPrompt
from vida.utils.logger import get_logger
from vida.utils.request_context import github_pat_ctx
import os

logger = get_logger(__name__)



from vida.utils.config import github_token 

@asynccontextmanager
async def github_mcp_tool():
    token = github_pat_ctx.get(None) or github_token
    # if not token:
    #     raise RuntimeError("GitHub token not found in context or environment")

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={
            **os.environ,                               
            "GITHUB_PERSONAL_ACCESS_TOKEN": token
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield MCPTool(
                name="github",
                session=session,
                tool_name_prefix="github",
                approval_mode="never_require",
            )

class GithubAgent(Base_Agent):
    name = "github_agent"
    instructions = str(AgentInstructionPrompt("github-agent-instructions"))
    tools = []
_git_agent_field = ToolFieldsPrompt("git-agent-field-description")

@tool(
    name="Github_Agent",
    description=str(AgentDescriptionPrompt("github-agent-description")),
    approval_mode="never_require",
)
async def github_agent(
    prompt: Annotated[str, Field(description=_git_agent_field.get("prompt"))]
):
    logger.info("[github_agent] Called with prompt.")
    logger.debug(f"[github_agent] Prompt: {prompt}")
    try:
        async with github_mcp_tool() as mcp:
            result = await GithubAgent.get_instance().run(prompt, tools=[mcp])
        logger.info("[github_agent] Successfully generated output.")
        logger.debug(f"[github_agent] Output: {result}")
        return result
    except Exception as e:
        logger.error(f"[github_agent] Error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    import asyncio
    git_token = input("Enter GitHub token: ")
    github_pat_ctx.set(git_token)
    prompt = input("Enter prompt for GitHub agent: ")
    print(asyncio.run(github_agent(prompt)))
