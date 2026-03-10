from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib


def build_email_body(matches: list[dict]) -> str:
    """
    builds email body from a job match list.
    """
    lines = []
    lines.append(f"Sift found {len(matches)} job(s) worth your attention today.\n")
    lines.append("=" * 60)

    for i, job in enumerate(matches, 1):
        job_match = job.get("job_match", {})
        lines.append(f"\n#{i} {job.get('title')} - {job.get('company')}")
        lines.append(
            f"Score: {job_match.get('score')}/10 | Recommendation: {job_match.get('recommendation', '').upper()}"
        )
        lines.append(f"\nSummary: {job_match.get('summary')}")

        strenghts = job_match.get("strengths", [])
        if strenghts:
            lines.append("\n Strengths:")
            for s in strenghts:
                lines.append(f" + {s}")
        gaps = job_match.get("gaps", [])
        if gaps:
            lines.append("\nGaps:")
            for g in gaps:
                lines.append(f"  - {g}")

        lines.append(f"\nLocation: {job.get('location')}")
        lines.append(f"Seniority: {job.get('seniority')}")
        lines.append(f"Employment: {job.get('employment_type')}")
        lines.append(f"Salary: {job.get('salary_range') or 'Not specified'}")
        lines.append(f"Company website: {job.get('company_website') or 'N/A'}")
        lines.append(f"\nApply here: {job.get('apply_url')}")
        lines.append("\n" + "=" * 60)

    return "\n".join(lines)


async def send_email(
    matches: list[dict],
    sender: str,
    recipient: str,
    app_password: str,
) -> None:
    """
    Sends email for the job matches via iosmtplib
    """

    subject = f"Sift - {len(matches)} job match{'es' if len(matches) > 1 else ''} today"
    body = build_email_body(matches)

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText(body, "plain"))

    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=465,
        username=sender,
        password=app_password,
        use_tls=True,
    )
