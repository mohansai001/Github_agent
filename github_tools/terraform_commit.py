from typing import Dict
import httpx
import base64

async def commit_terraform_files(
        self,
        repo: str,
        branch: str,
        terraform_files: Dict[str, str],
        workflow_content: str,
        gh_token: str
    ) -> None:
        """Commit Terraform files and workflow to repository."""
        
        headers = {
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Create terraform directory structure
        files_to_commit = {
            "terraform/main.tf": terraform_files.get("main.tf", ""),
            "terraform/variables.tf": terraform_files.get("variables.tf", ""),
            "terraform/outputs.tf": terraform_files.get("outputs.tf", ""),
            "terraform/versions.tf": terraform_files.get("versions.tf", ""),
            ".github/workflows/terraform-deploy.yml": workflow_content
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            for file_path, content in files_to_commit.items():
                if not content:
                    continue
                
                # Check if file exists
                url = f"{self.github_api}/repos/{repo}/contents/{file_path}"
                response = await client.get(url, headers=headers, params={"ref": branch})
                
                # Prepare commit data
                commit_data = {
                    "message": f"feat: add {file_path} via DevOps Agent",
                    "content": base64.b64encode(content.encode()).decode(),
                    "branch": branch
                }
                
                # Add SHA if file exists (for updates)
                if response.status_code == 200:
                    existing_file = response.json()
                    commit_data["sha"] = existing_file["sha"]
                
                # Commit file
                await client.put(url, headers=headers, json=commit_data)