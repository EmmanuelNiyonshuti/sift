import logging
import os

from dotenv import load_dotenv

from core.data import get_prompt, load_bio
from core.dispatch import send_email
from core.weigh import get_google_genai_async_client, validate_match_from_gemini
from sources.ini_rw import InRw

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger(__name__)


async def evaluate_jobs(
    job_listings: list[dict], client, bio: str, threshold: int = 0
) -> list:
    """
    Evaluate job listings by passing them into google gemini model and run them concurently with `asyncio.gather`.
    checks score from gemini response against the arbitrary threshold with default of  6 and returns job listings that match.
    """

    async def evaluate_one(job: dict) -> tuple[dict]:
        prompt = get_prompt(bio, job)
        result = await validate_match_from_gemini(client, prompt)
        return job, result

    results = await asyncio.gather(*[evaluate_one(j) for j in job_listings])

    matches = []
    for job, result in results:
        if result.get("score", 0) >= threshold:
            matches.append({**job, "job_match": result})
    return matches


async def main():
    """
    send an email if there is a job match
    """
    client = get_google_genai_async_client(api_key=os.getenv("GOOGLE_API_KEY"))
    bio = await load_bio()
    job_listings = await InRw().get_normalized_listings()

    matches = await evaluate_jobs(job_listings=job_listings, client=client, bio=bio)
    if matches:
        await send_email(
            matches=matches,
            sender=os.getenv("EMAIL_SENDER"),
            recipient=os.getenv("EMAIL_RECIPIENT"),
            app_password=os.getenv("APP_PASSWORD"),
        )


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"An unexpected error occured: {e}")
