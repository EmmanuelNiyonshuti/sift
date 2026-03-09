from core.data import TITLES, add_to_seen
from core.utils import strip_html

from .base import Base


class InRw(Base):
    def __init__(self, url: str):
        super().__init__(url)

    def params(self) -> dict:
        return {"status": "approved", "limit": 20}

    def filter(self, job_listings: list[dict]) -> list[dict]:
        result = []
        json_file_list = []
        for job in job_listings:
            if self.already_seen(job.get("id")):
                continue
            if not any(t in job.get("title_en").lower() for t in TITLES):
                continue
            if not self.is_fresh(job.get("created_at"), job.get("closing_date")):
                continue
            json_file_list.append({"id": job.get("id"), "title": job.get("title_en")})
            result.append(job)
        add_to_seen(json_file_list)
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
