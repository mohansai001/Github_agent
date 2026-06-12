from agent_framework import tool #type: ignore
from typing import Annotated
from pydantic import Field
from vida.utils.prompt_manager_v2 import ToolDescriptionPrompt, ToolFieldsPrompt
from vida.utils.github_client import get_github_client
from vida.adapters.github.git_write import commit_files as github_commit_files, set_github_secret as github_set_secret
from vida.adapters.github.git_read import github_read_contents, wait_for_latest_workflow
from vida.adapters.github.git_search import github_find_folder

@tool(name="get_user", description=str(ToolDescriptionPrompt("git-get-user-tool-description")), approval_mode="never_require")
def get_user():
    g_client = get_github_client()
    user = g_client.get_user()
    print("login:", user.login)
    return user


# ── commit_files ──────────────────────────────────────────────────────────────

_git_commit_fields = ToolFieldsPrompt("git-commit-field-description")

@tool(
    name="commit_files",
    description=str(ToolDescriptionPrompt("git-commit-tool-description")),
    approval_mode="never_require"
)
def commit_files(
    repo: Annotated[str, Field(description=_git_commit_fields.get("repo"))],
    file_path: Annotated[str, Field(description=_git_commit_fields.get("file_path"))],
    commit_message: Annotated[str, Field(description=_git_commit_fields.get("commit_message"))],
    branch: Annotated[str, Field(description=_git_commit_fields.get("branch"))],
    content: Annotated[str, Field(description=_git_commit_fields.get("content"))],
):
    return github_commit_files(
        repo=repo,
        file_path=file_path,
        commit_message=commit_message,
        branch=branch,
        content=content,
    )


# ── read_file ─────────────────────────────────────────────────────────────────

_git_read_fields = ToolFieldsPrompt("git-read-file-field-description")

@tool(name="read_file", description=str(ToolDescriptionPrompt("git-read-file-tool-description")), approval_mode="never_require")
def read_file(
    path: Annotated[str, Field(description=_git_read_fields.get("path"))],
    repo_owner: Annotated[str, Field(description=_git_read_fields.get("repo_owner"))],
    repo_name: Annotated[str, Field(description=_git_read_fields.get("repo_name"))],
):
    return github_read_contents(path=path, repo_owner=repo_owner, repo_name=repo_name)


# ── set_secret ────────────────────────────────────────────────────────────────

_git_secret_fields = ToolFieldsPrompt("git-set-secret-field-description")

@tool(name="set_secret", description=str(ToolDescriptionPrompt("git-set-secret-tool-description")), approval_mode="never_require")
async def set_secret(
    repo_full_name: Annotated[str, Field(description=_git_secret_fields.get("repo_full_name"))],
    secret_name: Annotated[str, Field(description=_git_secret_fields.get("secret_name"))],
    secret_value: Annotated[str, Field(description=_git_secret_fields.get("secret_value"))],
):
    return await github_set_secret(repo_full_name=repo_full_name, secret_name=secret_name, secret_value=secret_value)


# ── New tools from GitHubAPIWrapper (base.py) ─────────────────────────────────

from vida.adapters.github.base import GitHubAPIWrapper

def _get_wrapper() -> GitHubAPIWrapper:
    return GitHubAPIWrapper()


# ── list_branches ─────────────────────────────────────────────────────────────

_git_list_branches_fields = ToolFieldsPrompt("git-list-branches-field-description")

@tool(name="list_branches", description=str(ToolDescriptionPrompt("git-list-branches-tool-description")), approval_mode="never_require")
def list_branches(
    repo_full_name: Annotated[str, Field(description=_git_list_branches_fields.get("repo_full_name"))],
):
    branches = _get_wrapper().get_branches(repo_full_name)
    return [b.name for b in branches]


# ── create_branch ─────────────────────────────────────────────────────────────

_git_create_branch_fields = ToolFieldsPrompt("git-create-branch-field-description")

@tool(name="create_branch", description=str(ToolDescriptionPrompt("git-create-branch-tool-description")), approval_mode="never_require")
def create_branch(
    repo_full_name: Annotated[str, Field(description=_git_create_branch_fields.get("repo_full_name"))],
    branch_name: Annotated[str, Field(description=_git_create_branch_fields.get("branch_name"))],
    source_branch: Annotated[str, Field(description=_git_create_branch_fields.get("source_branch"))],
):
    wrapper = _get_wrapper()
    source = wrapper.get_branch(repo_full_name, source_branch)
    sha = source.commit.sha
    ref = f"refs/heads/{branch_name}"
    wrapper.create_git_ref(repo_full_name, ref, sha)
    return f"Branch '{branch_name}' created from '{source_branch}' in '{repo_full_name}'."


# ── list_commits ──────────────────────────────────────────────────────────────
""" Not working"""
_git_list_commits_fields = ToolFieldsPrompt("git-list-commits-field-description")

@tool(name="list_commits", description=str(ToolDescriptionPrompt("git-list-commits-tool-description")), approval_mode="never_require")
def list_commits(
    repo_full_name: Annotated[str, Field(description=_git_list_commits_fields.get("repo_full_name"))],
    branch: Annotated[str, Field(description=_git_list_commits_fields.get("branch"))],
): 
    print("Called list_commits tools")
    try:
        commits = _get_wrapper().get_commit(repo_full_name, sha=branch)
        print(commits)
        # print([
        #     {"sha": c.sha[:7], "message": c.commit.message.splitlines()[0], "author": c.commit.author.name}
        #     for c in list(commits)[:10]
        # ])

        return [
            {"sha": c.sha[:7], "message": c.commit.message.splitlines()[0], "author": c.commit.author.name}
            for c in list(commits)[:10] #type: ignore
        ]
    except Exception as e:
        # logger.error(f"[list_commits] Error occurred: {e}", exc_info=True)
        return {"error": str(e)}
   


# ── list_workflows ────────────────────────────────────────────────────────────

_git_list_workflows_fields = ToolFieldsPrompt("git-list-workflows-field-description")

@tool(name="list_workflows", description=str(ToolDescriptionPrompt("git-list-workflows-tool-description")), approval_mode="never_require")
def list_workflows(
    repo_full_name: Annotated[str, Field(description=_git_list_workflows_fields.get("repo_full_name"))],
):
    try:
        workflows = _get_wrapper().get_workflows(repo_full_name)
        print([w.name for w in workflows])
        return [{"id": w.id, "name": w.name, "path": w.path, "state": w.state} for w in workflows]
    except Exception as e:
        # logger.error(f"[list_workflows] Error occurred: {e}", exc_info=True)
        print("Error:", str(e))
        return {"error": str(e)}


# ── create_pull_request ───────────────────────────────────────────────────────``

_git_create_pr_fields = ToolFieldsPrompt("git-create-pull-request-field-description")

@tool(name="create_pull_request", description=str(ToolDescriptionPrompt("git-create-pull-request-tool-description")), approval_mode="never_require")
def create_pull_request(
    repo_full_name: Annotated[str, Field(description=_git_create_pr_fields.get("repo_full_name"))],
    title: Annotated[str, Field(description=_git_create_pr_fields.get("title"))],
    body: Annotated[str, Field(description=_git_create_pr_fields.get("body"))],
    base: Annotated[str, Field(description=_git_create_pr_fields.get("base"))],
    head: Annotated[str, Field(description=_git_create_pr_fields.get("head"))],
):
    try:
        print(f"Called create_pull_request tool with details title: {title}, body: {body}, base: {base}, head: {head}")
        pr = _get_wrapper().create_pull(repo_full_name, title=title, body=body, base=base, head=head)
        return {"number": pr.number, "url": pr.html_url, "state": pr.state}
    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}

import traceback

# ── create_issue ──────────────────────────────────────────────────────────────

_git_create_issue_fields = ToolFieldsPrompt("git-create-issue-field-description")

@tool(name="create_issue", description=str(ToolDescriptionPrompt("git-create-issue-tool-description")), approval_mode="never_require")
def create_issue(
    repo_full_name: Annotated[str, Field(description=_git_create_issue_fields.get("repo_full_name"))],
    title: Annotated[str, Field(description=_git_create_issue_fields.get("title"))],
    body: Annotated[str, Field(description=_git_create_issue_fields.get("body"))],
):
    try:
        print("STEP 1")

        wrapper = _get_wrapper()

        print("STEP 2:", wrapper)
        print(f"[Creat issue] tool called with details - Repo: {repo_full_name}, Title: {title}, Body: {body}")
        issue = wrapper.create_issue(repo_full_name, title=title, body=body)
        print("STEP 3:", issue)

        print({"number": issue.number, "url": issue.html_url, "state": issue.state})
        return {"number": issue.number, "url": issue.html_url, "state": issue.state}
    except Exception as e:
        print("EXCEPTION OCCURRED")
        traceback.print_exc()

        return {
            "error": str(e),
            "type": str(type(e))
        }


# ── create_release ────────────────────────────────────────────────────────────

_git_create_release_fields = ToolFieldsPrompt("git-create-release-field-description")

@tool(name="create_release", description=str(ToolDescriptionPrompt("git-create-release-tool-description")), approval_mode="never_require")
def create_release(
    repo_full_name: Annotated[str, Field(description=_git_create_release_fields.get("repo_full_name"))],
    tag: Annotated[str, Field(description=_git_create_release_fields.get("tag"))],
    name: Annotated[str, Field(description=_git_create_release_fields.get("name"))],
    message: Annotated[str, Field(description=_git_create_release_fields.get("message"))],
    draft: Annotated[bool, Field(description=_git_create_release_fields.get("draft"))] = False,
    prerelease: Annotated[bool, Field(description=_git_create_release_fields.get("prerelease"))] = False,
):
    release = _get_wrapper().create_git_release(repo_full_name, tag=tag, name=name, message=message, draft=draft, prerelease=prerelease)
    return {"id": release.id, "url": release.html_url, "tag": release.tag_name}


