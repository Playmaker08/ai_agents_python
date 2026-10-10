"""Run after installing .[live] and configuring .env."""

from common import client, model

response = client.responses.create(model=model, input="Explain tool calling in three sentences.")
print(response.output_text)
