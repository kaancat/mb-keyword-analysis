"""
Google Tag Manager Service.
Access GTM accounts, containers, and tags via the GTM API.
"""

import sys
from pathlib import Path

# Add plugin root to path for imports (works from any directory)
_plugin_root = Path(__file__).parent.parent.parent
if str(_plugin_root) not in sys.path:
    sys.path.insert(0, str(_plugin_root))

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from typing import List, Optional, Dict, Any
from backend.services.credentials import ensure_credentials

# Load credentials from ~/.mondaybrew/.env - MUST succeed or raise error
_cred_source = ensure_credentials()
print(f"[GTMService] Credentials loaded from: {_cred_source}")


class GTMService:
    def __init__(self):
        # OAuth 2.0 Authentication (User Context)
        # Uses the same "Master Token" pattern as other services

        client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
        refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")

        if not all([client_id, client_secret, refresh_token]):
            print("--- Error: Missing OAuth Credentials for GTMService ---")
            print(
                "Ensure GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, and GOOGLE_ADS_REFRESH_TOKEN are set in .env"
            )
            self.service = None
            return

        try:
            self.creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=[
                    "https://www.googleapis.com/auth/tagmanager.edit.containers",
                    "https://www.googleapis.com/auth/tagmanager.publish",
                ],
            )

            self.service = build("tagmanager", "v2", credentials=self.creds)
        except Exception as e:
            print(f"Failed to initialize GTMService with OAuth: {e}")
            self.service = None

    def list_accounts(self) -> List[Dict[str, Any]]:
        """Lists all GTM accounts."""
        print("--- Listing GTM Accounts ---")
        try:
            response = self.service.accounts().list().execute()
            accounts = []
            for account in response.get("account", []):
                accounts.append(
                    {
                        "account_id": account["accountId"],
                        "name": account["name"],
                        "path": account["path"],
                        "features": account.get("features", {}),
                    }
                )
            return accounts
        except Exception as e:
            print(f"Error listing accounts: {e}")
            return []

    def list_containers(self, account_path: str) -> List[Dict[str, Any]]:
        """Lists containers for a given account path (e.g., 'accounts/123456')."""
        try:
            response = (
                self.service.accounts().containers().list(parent=account_path).execute()
            )
            containers = []
            for container in response.get("container", []):
                containers.append(
                    {
                        "container_id": container["containerId"],
                        "name": container["name"],
                        "public_id": container["publicId"],
                        "path": container["path"],
                        "usage_context": container.get("usageContext", []),
                    }
                )
            return containers
        except Exception as e:
            print(f"Error listing containers for {account_path}: {e}")
            return []

    def list_workspaces(self, container_path: str) -> List[Dict[str, Any]]:
        """Lists workspaces for a given container path."""
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .list(parent=container_path)
                .execute()
            )
            workspaces = []
            for workspace in response.get("workspace", []):
                workspaces.append(
                    {
                        "workspace_id": workspace["workspaceId"],
                        "name": workspace["name"],
                        "path": workspace["path"],
                        "description": workspace.get("description", ""),
                    }
                )
            return workspaces
        except Exception as e:
            print(f"Error listing workspaces for {container_path}: {e}")
            return []

    def list_tags(self, workspace_path: str) -> List[Dict[str, Any]]:
        """Lists tags for a given workspace path."""
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .tags()
                .list(parent=workspace_path)
                .execute()
            )
            tags = []
            for tag in response.get("tag", []):
                tags.append(
                    {
                        "tag_id": tag["tagId"],
                        "name": tag["name"],
                        "type": tag["type"],
                        "path": tag["path"],
                        "firing_trigger_id": tag.get("firingTriggerId", []),
                        "blocking_trigger_id": tag.get("blockingTriggerId", []),
                    }
                )
            return tags
        except Exception as e:
            print(f"Error listing tags for {workspace_path}: {e}")

    def list_triggers(self, workspace_path: str) -> List[Dict[str, Any]]:
        """Lists triggers for a given workspace path."""
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .triggers()
                .list(parent=workspace_path)
                .execute()
            )
            triggers = []
            for trigger in response.get("trigger", []):
                triggers.append(
                    {
                        "trigger_id": trigger["triggerId"],
                        "name": trigger["name"],
                        "type": trigger["type"],
                        "path": trigger["path"],
                    }
                )
            return triggers
        except Exception as e:
            print(f"Error listing triggers for {workspace_path}: {e}")
            return []

    def get_container_snippet(self, container_path: str) -> str:
        """Gets the snippet for a container."""
        # Note: The API doesn't directly return the full HTML snippet in a simple call usually,
        # but we can construct it or look for it if available.
        # Actually, the API doesn't have a direct 'get snippet' endpoint in v2 standard listing.
        # It's usually constructed from the container ID (GTM-XXXX).
        # However, let's check if we can get the public ID easily.
        # We'll just return the public ID for now as the 'snippet' key usually implies the GTM ID.
        return container_path

    def get_tag(self, workspace_path: str, tag_id: str) -> Dict[str, Any]:
        """Gets a specific tag."""
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .tags()
                .get(path=f"{workspace_path}/tags/{tag_id}")
                .execute()
            )
            return response
        except Exception as e:
            print(f"Error getting tag {tag_id}: {e}")
            return {}

    # --- Write Methods ---

    def create_workspace(
        self, container_path: str, name: str, description: str = ""
    ) -> Dict[str, Any]:
        """Creates a new workspace."""
        print(f"--- Creating Workspace: {name} ---")
        try:
            body = {"name": name, "description": description}
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .create(parent=container_path, body=body)
                .execute()
            )
            return {
                "workspace_id": response["workspaceId"],
                "name": response["name"],
                "path": response["path"],
            }
        except Exception as e:
            print(f"Error creating workspace: {e}")
            return {}

    def create_tag(
        self, workspace_path: str, tag_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Creates a new tag."""
        print(f"--- Creating Tag: {tag_data.get('name')} ---")
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .tags()
                .create(parent=workspace_path, body=tag_data)
                .execute()
            )
            return response
        except Exception as e:
            print(f"Error creating tag: {e}")
            return {}

    def create_trigger(
        self, workspace_path: str, trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Creates a new trigger."""
        print(f"--- Creating Trigger: {trigger_data.get('name')} ---")
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .triggers()
                .create(parent=workspace_path, body=trigger_data)
                .execute()
            )
            return response
        except Exception as e:
            print(f"Error creating trigger: {e}")
            return {}

    def list_variables(self, workspace_path: str) -> List[Dict[str, Any]]:
        """Lists variables for a given workspace path."""
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .variables()
                .list(parent=workspace_path)
                .execute()
            )
            variables = []
            for variable in response.get("variable", []):
                variables.append(
                    {
                        "variable_id": variable["variableId"],
                        "name": variable["name"],
                        "type": variable["type"],
                        "path": variable["path"],
                    }
                )
            return variables
        except Exception as e:
            print(f"Error listing variables for {workspace_path}: {e}")
            return []

    def list_built_in_variables(self, workspace_path: str) -> List[Dict[str, Any]]:
        """Lists enabled built-in variables."""
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .built_in_variables()
                .list(parent=workspace_path)
                .execute()
            )
            return response.get("builtInVariable", [])
        except Exception as e:
            print(f"Error listing built-in variables for {workspace_path}: {e}")
            return []

    def enable_built_in_variable(
        self, workspace_path: str, variable_type: str
    ) -> Dict[str, Any]:
        """Enables a built-in variable."""
        print(f"--- Enabling Built-In Variable: {variable_type} ---")
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .built_in_variables()
                .create(parent=workspace_path, type=variable_type)
                .execute()
            )
            return response
        except Exception as e:
            print(f"Error enabling built-in variable {variable_type}: {e}")
            return {}

    def create_variable(
        self, workspace_path: str, variable_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Creates a new variable."""
        print(f"--- Creating Variable: {variable_data.get('name')} ---")
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .variables()
                .create(parent=workspace_path, body=variable_data)
                .execute()
            )
            return response
        except Exception as e:
            print(f"Error creating variable: {e}")
            return {}

    def update_tag(self, tag_path: str, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing tag."""
        print(f"--- Updating Tag: {tag_data.get('name')} ({tag_path}) ---")
        try:
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .tags()
                .update(path=tag_path, body=tag_data)
                .execute()
            )
            return response
        except Exception as e:
            print(f"Error updating tag: {e}")
            return {}

    def create_version(
        self, workspace_path: str, name: str, notes: str = ""
    ) -> Dict[str, Any]:
        """Creates a container version from a workspace."""
        print(f"--- Creating Version: {name} ---")
        try:
            body = {"name": name, "notes": notes}
            response = (
                self.service.accounts()
                .containers()
                .workspaces()
                .create_version(path=workspace_path, body=body)
                .execute()
            )
            return response.get("containerVersion", {})
        except Exception as e:
            print(f"Error creating version: {e}")
            return {}

    def publish_version(self, version_path: str) -> Dict[str, Any]:
        """Publishes a container version."""
        print(f"--- Publishing Version: {version_path} ---")
        try:
            response = (
                self.service.accounts()
                .containers()
                .versions()
                .publish(path=version_path)
                .execute()
            )
            return response
        except Exception as e:
            print(f"Error publishing version: {e}")
            return {}


if __name__ == "__main__":
    # Test
    service = GTMService()
    print("--- Testing Discovery ---")
    if service.service:
        accounts = service.list_accounts()
        print(f"Found {len(accounts)} accounts")
        if accounts:
            acc_path = accounts[0]["path"]
            print(f"Testing with account: {accounts[0]['name']} ({acc_path})")

            containers = service.list_containers(acc_path)
            print(f"Found {len(containers)} containers")

            if containers:
                cont_path = containers[0]["path"]
                print(f"Testing with container: {containers[0]['name']} ({cont_path})")

                workspaces = service.list_workspaces(cont_path)
                print(f"Found {len(workspaces)} workspaces")

                if workspaces:
                    ws_path = workspaces[0]["path"]
                    print(
                        f"Testing with workspace: {workspaces[0]['name']} ({ws_path})"
                    )

                    tags = service.list_tags(ws_path)
                    print(f"Found {len(tags)} tags")
                    if tags:
                        print(f"Sample tag: {tags[0]['name']} ({tags[0]['type']})")
