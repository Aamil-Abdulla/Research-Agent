import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointProtocol,
    ContainerConfiguration,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)
from azure.identity import DefaultAzureCredential

load_dotenv()

PROJECT_ENDPOINT = "https://aamilabdulla0-1117-resource.services.ai.azure.com/api/projects/aamilabdulla0-1117"

credential = DefaultAzureCredential()
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)

image_ref = "aamilabdulla0research.azurecr.io/research-agent-hosted:v4"
print("Deploying image:", image_ref)

agent = project.agents.create_version(
    agent_name="research-agent",
    definition=HostedAgentDefinition(
        protocol_versions=[
            ProtocolVersionRecord(protocol=AgentEndpointProtocol.INVOCATIONS, version="1.0.0")
        ],
        cpu="1",
        memory="2Gi",
        container_configuration=ContainerConfiguration(
            image=image_ref
        ),
        environment_variables={
            "TAVILY_API_KEY": os.environ["TAVILY_API_KEY"],
            "GROQ_API_KEY": os.environ["GROQ_API_KEY"],
        },
    )
)

print("Full response object:", agent)
print(f"Agent created: {agent.name}, version: {agent.version}")