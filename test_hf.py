from huggingface_hub import InferenceClient

import os
token = os.environ.get("HF_TOKEN", "your_token_here")
client = InferenceClient(api_key=token)

try:
    # Try a simple text generation task using Mistral
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=[{"role": "user", "content": "Hello! What is 2 + 2?"}],
        max_tokens=50
    )
    print("SUCCESS")
    print(response.choices[0].message.content)
except Exception as e:
    print("FAILED")
    print(e)
