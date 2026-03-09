from google import genai


def get_google_genai_client(self, api_key: str):
    assert api_key, "Missing API Key"
    client = genai.Client(api_key=api_key)
    return client


def validate_match_from_gemini(api_key: str, prompt: str) -> str:
    """
    Calls gemini-3-flash-preview with job description and profile bio to check if the job can be a good match.
    """
    client = get_google_genai_client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    return response.text
