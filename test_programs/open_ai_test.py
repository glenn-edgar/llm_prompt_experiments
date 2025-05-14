from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

response = client.chat.completions.create(
    model="grok-beta",  # Specify the Grok model
    messages=[{"role": "user", "content": "Hello, Grok!"}]
)
print(response.choices[0].message.content)

