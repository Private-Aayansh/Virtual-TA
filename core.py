import os
import re
import json
import requests
import numpy as np
from PIL import Image
import pytesseract
import io, base64
from dotenv import load_dotenv
from discourse import discourse_query_search
from course import course_query_search
from typing import Optional

load_dotenv()

AIPROXY_API_KEY = os.getenv("AIPROXY_API_KEY")
TOGETHER_AI_API_KEY = os.getenv("TOGETHER_AI_API_KEY")


def get_together_embedding(text: str):
    API_URL = "https://api.together.xyz/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {TOGETHER_AI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "intfloat/multilingual-e5-large-instruct",
        "input": text
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    output = response.json()

    return np.array(output["data"][0]["embedding"], dtype=np.float32)


def query_search(query: str):
    embedding = get_together_embedding(query)
    discourse_results = discourse_query_search(embedding, "./data/discourse_index.faiss", "./data/discourse_metadata.json")
    course_results = course_query_search(embedding, "./data/course_index.faiss", "./data/course_metadata.json")
    discourse_context = "\n\n".join([f"{r['text']}\nURL: {r['metadata']['url']}" for r in discourse_results])
    course_context = "\n\n".join([f"{r['text']}\nURL: {r['metadata']['url']}" for r in course_results])

    return discourse_context, course_context


def extract_text_from_base64(img_b64: str) -> str:
    if "," in img_b64:
        base64_data = img_b64.split(",", 1)[1]
    else:
        base64_data = img_b64
    data = base64.b64decode(base64_data)
    img = Image.open(io.BytesIO(data))
    return pytesseract.image_to_string(img)


def create_llm_prompt(query: str, topic_context: str, course_context: str, base64_image: Optional[str] = None) -> str:
    image_section = ""
    if base64_image:
        base64_image_text = extract_text_from_base64(base64_image)
        if base64_image_text.strip():
            image_section = f"\n\nThe student also provided an image with the following text:\n{base64_image_text}"
        else:
            image_section = "\n\nThe student provided an image, but no text could be extracted."

    prompt = f"""
You are a Virtual Teaching Assistant for Tools in Data Science course. A student asked:

"{query}"{image_section}

Use **ONLY** the provided context — Forum Posts, Course Material, and any extracted image text to answer the question clearly, briefly cite excerpts with URLs.
If you cannot answer the question based on the context or are uncertain, respond with a clear refusal and set `"sources": []`.

Respond **ONLY** in this JSON format:

```json
{{
  "answer": "<a comprehensive yet concise answer, or a clear refusal>",
  "links": [
    {{
      "url": "<exact_url_1>",
      "text": "<brief quote or description>"
    }},
    {{
      "url": "<exact_url_2>",
      "text": "<brief quote or description>"
    }}
    // …add more entries if you used more sources
  ]
}}
```

Requirements:
Don’t invent or infer—stick strictly to what’s in the context.
Copy URLs exactly as they appear in the context.

———————————————
Forum Posts:
{topic_context}

Course Material:
{course_context}

"""
    return prompt


def generate_response(prompt):
    # Send request
    system_prompt = "You are an assistant answering based only on the provided context. Do not search anything else!"
    response = requests.post(
        "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AIPROXY_API_KEY}"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
    )

    raw = response.json()['choices'][0]['message']['content']
    clean = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(clean)
