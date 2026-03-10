import json

from google import genai


def get_google_genai_async_client(api_key: str):
    assert api_key, "Missing API Key"
    return genai.Client(api_key=api_key)


async def validate_match_from_gemini(genai_client, prompt: str) -> str:
    """
    Calls gemini-3-flash-preview model with job description and profile bio to check if the job can be a good match.
    """
    response = await genai_client.aio.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
