from dotenv import load_dotenv

from core.data import TITLES, add_to_seen
from core.utils import strip_html

from .base import Base

load_dotenv()


class InRw(Base):
    def __init__(self, url: str = "https://opportunityapi.ini.rw/api/opportunities"):
        super().__init__(url)

    def params(self) -> dict:
        return {"status": "approved", "limit": 20}

    async def filter(self, job_listings: list[dict]) -> list[dict]:
        result = []
        seen_jobs = {}
        for job in job_listings:
            if await self.already_seen(job.get("id")):
                continue
            if not any(t in job.get("title_en").lower() for t in TITLES):
                continue
            if not self.is_fresh(job.get("created_at"), job.get("closing_date")):
                continue
            seen_jobs.update({"id": job.get("id"), "title": job.get("title_en")})
            result.append(job)
        if seen_jobs:
            await add_to_seen(seen_jobs)
        return result

    def normalize(self, job: dict) -> dict:
        return {
            "company": job.get("company_name", ""),
            "title": job.get("title_en", ""),
            "job_description": strip_html(job.get("description", "")),
            "skills": job.get("skills", []),
            "employment_type": job.get("employment_type_en", ""),
            "seniority": job.get("seniority", ""),
            "experience": job.get("experience"),
            "company_website": job.get("company", {}).get("website_url", ""),
            "location": job.get("location_en", ""),
            "headquarters": job.get("company", {}).get("headquarters"),
            "industry": job.get("company", {}).get("industry"),
            "salary_range": job.get("salary_range_en"),
            "apply_url": job.get("apply_url", ""),
        }

    async def get_normalized_listings(self) -> list[dict]:
        raw = await self.fetch_job_listings()
        fresh = await self.filter(raw)
        normalized_listings = [self.normalize(job) for job in fresh]
        return normalized_listings
