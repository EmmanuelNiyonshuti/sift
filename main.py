import asyncio
import os

from dotenv import load_dotenv

from sources.ini_rw import InRw

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

url = os.getenv("INI_RW_API_URL")

ini_rw = InRw(url)

raw = asyncio.run(ini_rw.fetch_job_listings())
fresh = ini_rw.filter(raw)
normalized_listings = [ini_rw.normalize(job) for job in fresh]

print("Normalized:", normalized_listings)
