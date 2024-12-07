from dotenv import load_dotenv
from llm import askllm
import os
import base64
import httpx
import logging


load_dotenv()
api_key = os.getenv('COHERE_API_KEY')

async def retrieve(repo_owner, repo, files_changed, github_token):
    files = []
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    for file_path in files_changed:
        url = f"https://api.github.com/repos/{repo_owner}/{repo}/contents/{file_path}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                json_response = response.json()
                file_content = base64.b64decode(json_response['content'])
                files.append((file_path, file_content))
            else:
                raise Exception(f"Failed to fetch file: {response.status_code} {response.text}")

    doc = await retrieve_previous_documentation(repo_owner, repo, github_token)

    if doc == "NO DOCUMENTATION FOUND":
        return "No previous documentation found"

    try:
        response = await askllm(files, api_key, doc)
        return response
    except Exception as e:
        logging.error(f"Exception in askllm: {e}")
        return "Failed to generate documentation"

async def retrieve_previous_documentation(repo_owner, repo, github_token):
    file_path = "documentation.md"
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f"https://api.github.com/repos/{repo_owner}/{repo}/contents/{file_path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            json_response = response.json()
            file_content = base64.b64decode(json_response['content'])
            return file_content.decode('utf-8')
        else:
            return "NO DOCUMENTATION FOUND"
