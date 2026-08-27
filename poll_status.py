import sys
import time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

PROJECT_ENDPOINT = "https://aamilabdulla0-1117-resource.services.ai.azure.com/api/projects/aamilabdulla0-1117"

agent_version = sys.argv[1] if len(sys.argv) > 1 else "3"

credential = DefaultAzureCredential()
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)

while True:
    version_info = project.agents.get_version(
        agent_name="research-agent",
        agent_version=agent_version
    )
    status = version_info["status"]
    print(f"Status: {status}")

    if status == "active":
        print("Agent is ready!")
        break
    elif status == "failed":
        print(f"Provisioning failed: {version_info['error']}")
        break

    time.sleep(5)