import requests
from azure.identity import DefaultAzureCredential

PROJECT_ENDPOINT = "https://aamilabdulla0-1117-resource.services.ai.azure.com/api/projects/aamilabdulla0-1117"
credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default").token

url = f"{PROJECT_ENDPOINT}/agents/research-agent/endpoint/protocols/invocations"

response = requests.post(url, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}, params={"api-version": "v1"}, json={
    "message": "Where is Seattle?"
})

print(response.status_code)
print(response.json())