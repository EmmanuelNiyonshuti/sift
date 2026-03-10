import json
from pathlib import Path

import aiofiles

SEEN_JOBS_FILE_PATH = Path(__file__).parent.parent
BIO_FILE_PATH = Path(__file__).parent.parent

seen_file_path = SEEN_JOBS_FILE_PATH / "seen.json"
bio_file_path = BIO_FILE_PATH / "profile.txt"
PROMPT = """ """
TITLES = [
    "python developer",
    "python backend developer",
    "api developer",
    "backend developer",
    "backend software developer",
    "software engineer",
    "software developer",
    "associate software developer",
    "associate software engineer",
    "entry level software developer",
    "system integrator",
]


async def load_bio() -> str:
    """
    lead bio/profile text file and returns its content
    """
    if not bio_file_path.exists():
        return ""
    async with aiofiles.open(bio_file_path, "r") as f:
        content = await f.read()

    return content


async def get_job_seen() -> list[dict]:
    if not seen_file_path.exists():
        return []
    async with aiofiles.open(seen_file_path) as json_file:
        content = await json_file.read()
        if not content:
            return []
        return json.loads(content.strip())


async def add_to_seen(data: dict) -> None:
    """
    takes a job listing(a dictionary of job id and title),
    append it to a list of already seen jobs and writes to a json file in the root directory.
    will create json file `seen.json` if it does not exists.
    """
    seen = await get_job_seen()
    seen.append(data)
    async with aiofiles.open(seen_file_path, "w") as f:
        json_data = json.dumps(seen, indent=2)
        await f.write(json_data)


def get_prompt(bio: str, job_listing: dict) -> str:
    title = job_listing.get("title")
    company = job_listing.get("company")
    location = job_listing.get("location")
    skills = job_listing.get("skills", [])
    seniority = job_listing.get("seniority")
    employment_type = job_listing.get("employment_type")
    description = job_listing.get("job_description")
    experience = job_listing.get("experience")
    salary_range = job_listing.get("salary_range")

    PROMPT = """
You are a pragmatic career advisor helping a backend developer in Kigali, Rwanda
evaluate job opportunities quickly and honestly.

You will be given a job listing and a developer profile. Your job is to assess
how good a fit this developer is for the role — not to be encouraging, but to
be accurate.

Return your response as a JSON object with exactly these fields:

{{
"score": <integer from 1 to 10>,
"recommendation": <"apply" | "skip" | "consider">,
"summary": <one sentence, plain language, why this is or isn't a good fit>,
"strengths": [<list of specific overlaps between the profile and the job>],
"gaps": [<list of specific things the job asks for that the profile lacks>]
}}

Scoring guide:
- 8-10: Strong match. Most requirements met, apply immediately.
- 6-7: Reasonable match. Some gaps but worth applying.
- 4-5: Weak match. Significant gaps, only consider if desperate.
- 1-3: Poor match. Wrong stack, wrong domain, wrong seniority. Skip.

Be specific in strengths and gaps. Do not mention generic things like
"communication skills". Only reference concrete technical or domain requirements
from the job description.

Do not add any explanation outside the JSON object. Return only valid JSON.

---

DEVELOPER PROFILE:
{bio}

---

JOB LISTING:
Title: {title}
Company: {company}
Location: {location}
Employment type: {employment_type}
Seniority: {seniority}
Required skills: {skills}
Experience required: {experience}
Salary: {salary_range}
Description:
{job_description}
"""
    return PROMPT.format(
        bio=bio,
        title=title,
        company=company,
        location=location,
        employment_type=employment_type,
        seniority=seniority,
        salary_range=salary_range,
        job_description=description,
        experience=experience,
        skills=skills,
    )
