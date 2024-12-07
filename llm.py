import httpx
import logging
import os

timeout = os.getenv('TIMEOUT')

async def askllm(files, api_key, prev_doc):
    cohere_api_url = 'https://api.cohere.ai/v1/chat'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    combined_content = "Previous Documentation:\n\n" + prev_doc + "\n\nNew Files:\n\n"
    for file_path, file_content in files:
        combined_content += f"File: {file_path}\n{file_content.decode('utf-8')}\n\n"

    message = f"Generate comprehensive documentation for the following files. Only generate documentation for API endpoints. Include parameter types, and avoid prefacing or adding outros:\n\n{combined_content}"
    payload = {
        'message': message,
    }

    try:
        # Use httpx for async HTTP requests
        async with httpx.AsyncClient(timeout=int(timeout)) as client:
            response = await client.post(cohere_api_url, headers=headers, json=payload)

        if response.status_code == 200:
            content = response.json()
            return content.get('text', "No text in response")
        else:
            raise Exception(f"Failed to get response from Cohere: {response.status_code} {response.text}")
    except httpx.TimeoutException:
        logging.error(f"Request to Cohere API timed out after {timeout} seconds.")
        return "Failed to generate documentation due to timeout."
    except Exception as e:
        print({e})
        logging.error(f"Exception in askllm: {e}")
        raise
