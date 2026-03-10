from datetime import datetime, timedelta

import httpx

from core.data import get_job_seen
from core.utils import parse_datetimes


class Base:
    def __init__(self, url: str):
        self.url = url

    def params(self) -> dict:
        return {}

    async def fetch_job_listings(self) -> str:
        assert self.url and self.url.strip(), "Missing API url"
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.url}", params=self.params())
            response.raise_for_status()

            return response.json()

    async def already_seen(self, job_listing_id: str) -> bool:
        """
        Checks if we already have seen the job listing.
        """
        job_seen = await get_job_seen()
        if not job_seen:
            return False
        for job in job_seen:
            if job.get("id") == job_listing_id:
                return True
        return False

    def is_fresh(self, created_at: str, closing_dt: str) -> bool:
        """
        Check if the job listing was posted in the past seven days window.
        we don't need old job listings so we consider 7 days window a fresh job, and it hasn't been expired(closing dt).
        """
        if created_at is None or closing_dt is None:
            return False
        creation_dt = parse_datetimes(created_at)
        closing_dt = parse_datetimes(closing_dt)
        tday = datetime.now()
        seven_days_ago = tday - timedelta(days=7)
        if (
            creation_dt >= seven_days_ago and closing_dt >= tday
        ):  # job posted lasted five days and their closind date is from today till the future
            return True
        return False
