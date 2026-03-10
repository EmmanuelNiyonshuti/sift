# Sift

This script fetches job listings, evaluates each posting against your profile using Gemini, and emails you only the roles worth applying for. I wrote this to avoid checking job boards manually.

## How it works

1. Fetches job listings from configured sources
2. Filters out listings you've already seen, titles that don't match, and postings past their closing date
3. Passes each remaining job and your profile to Gemini, which returns a match score and basic reasoning
4. Sends a single email with every job that scores 6 or above including strengths, gaps, and a direct application link

No database. We save seen jobs to a json file and It runs on a schedule via GitHub Action.

Below is what you might do if you want to use it.
## Setup

**1. Clone the repo**
```bash
git clone https://github.com/EmmanuelNiyonshuti/sift.git
cd sift
```

**2. Install dependencies**
```bash
uv sync
```

**3. Configure environment variables**

Copy the template and fill in your credentials:
```bash
cp .env.template .env
```

> Gmail [App Password](https://support.google.com/accounts/answer/185833)!

**4. Edit your profile**

Open `profile.txt` and describe yourself, Gemini will uses your profile to evaluate every job against your background.

**5. Run it**
```bash
uv run python main.py
```

## Deploying with GitHub Actions

It run unattended on a schedule, the included workflow fires every day at 16:00 UTC, you can adjust that!.

Add the following secrets to your repository under Settings → Secrets and variables → Actions:

`GOOGLE_API_KEY`
`EMAIL_SENDER`
`EMAIL_RECIPIENT`
`APP_PASSWORD`

Also go to Settings → Actions → General → Workflow permissions and enable **Read and write permissions** so the workflow can commit `seen.json` back to the repo after each run.

To trigger a run manually, go to the Actions tab and click **Run workflow**.

## Adding a new source
You might want to add new sources since I only have one source so far!
You might create a new file in `sources/` that inherits from `Base` and add implementations based on your new added source:

```python
from .base import Base

class NewSource(Base):
    def __init__(self, url: str = "https://api.example.com/jobs"):
        super().__init__(url)
    def params(self) -> dict:
        return {"type": "full-time"}

    def normalize(self, job: dict) -> dict:
        return {
            "id": job["id"],
            "title": job["title"],
            "job_description": job["description"],
            # ... map the rest of the fields
        }

    async def get_normalized_listings(self) -> list[dict]:
        raw = await self.fetch_job_listings()
        fresh = await self.filter(raw)
        return [self.normalize(job) for job in fresh]
```

Then add it to `main.py` alongside the existing sources.

## Note

- Match scoring uses a 1–10 scale. Only jobs scoring 6 or above trigger an email. You can adjust this threshold in `main.py`.
- `seen.json` is committed back to the repo after every run so duplicates are never sent.
- Gemini calls are made concurrently using `asyncio.gather`, one call per job, all fired at the same time.
- The matching logic is only as good as your `profile.txt`.
