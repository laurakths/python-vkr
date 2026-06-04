from openai import OpenAI

client = OpenAI(
  api_key="<OPENAI_API_KEY>",
)

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
      {
        "role": "user",
        "content": "How many r's are in the word 'strawberry'?"
      }
    ]
)

response = response.choices[0].message

messages = [
  {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
  {
    "role": "assistant",
    "content": response.content
  },
  {"role": "user", "content": "Are you sure? Think carefully."}
]

response2 = client.chat.completions.create(
  model="gpt-4o",
  messages=messages
)