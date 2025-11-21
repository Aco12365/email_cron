from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from functions.gpt_email import generate_email_from_prompt
from functions.email_sender import send_email

# -------------------- FastAPI app --------------------

app = FastAPI()


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] while testing
    allow_credentials=True,
    allow_methods=["*"],          # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],          # allow Content-Type, Authorization, etc.
)

# -------------------- Scheduler setup --------------------

scheduler = BackgroundScheduler()
scheduler.start()

# In-memory store:
# job_id -> { "config": <dict from StaggeredEmailJob>, "email_body": str, "next_index": int }
jobs_store: Dict[str, Dict[str, Any]] = {}


# -------------------- Pydantic models --------------------

class EmailRequest(BaseModel):
    """
    Used for a one-off send to all recipients at once.
    """
    from_email: EmailStr
    from_name: Optional[str] = None
    recipients: List[EmailStr]
    prompt: str  # GPT instructions
    subject: Optional[str] = None  # optional custom subject


class StaggeredEmailJob(EmailRequest):
    """
    Used for a scheduled job that sends to one recipient per run.
    """
    cron: str  # e.g. "*/2 * * * *" = every 2 minutes


# -------------------- Routes --------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate-and-send-email")
def generate_and_send_email(body: EmailRequest):
    """
    One-off:
    1) Generate an email with GPT using `prompt`
    2) Send the same email to ALL recipients immediately
    """
    try:
        email_text = generate_email_from_prompt(body.prompt)
        subject = body.subject or "Automated Email"

        send_email(
            from_email=body.from_email,
            from_name=body.from_name,
            to_emails=[str(r) for r in body.recipients],
            subject=subject,
            body=email_text,
        )

        return {
            "status": "sent",
            "subject": subject,
            "body": email_text,
            "recipients": body.recipients,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule-staggered-email-job")
def schedule_staggered_email_job(job: StaggeredEmailJob):
    """
    Schedule a recurring job that:
    - Generates the email ONCE using GPT
    - Immediately sends to the FIRST recipient
    - On each cron run sends to the NEXT recipient
    - When all recipients have received one email, the job STOPS and is removed
    """
    if not job.recipients:
        raise HTTPException(status_code=400, detail="At least one recipient is required.")

    # 1) Generate the email ONCE here
    try:
        email_body = generate_email_from_prompt(job.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate email: {e}")

    # 2) Create unique job id
    job_id = str(uuid.uuid4())

    # 3) Store configuration + generated email + starting index
    jobs_store[job_id] = {
        "config": job.dict(),
        "email_body": email_body,
        "next_index": 0,  # index of the next recipient to send to
    }

    # 4) Parse cron expression
    try:
        trigger = CronTrigger.from_crontab(job.cron)
    except ValueError:
        jobs_store.pop(job_id, None)
        raise HTTPException(status_code=400, detail="Invalid cron expression.")

    # 5) Add scheduled job (for future runs)
    scheduler.add_job(
        run_staggered_email_job,
        trigger=trigger,
        id=job_id,
        args=[job_id],
        replace_existing=True,
    )

    # 6) Immediately send to first recipient using the same generated email
    run_staggered_email_job(job_id)

    return {"job_id": job_id, "message": "Staggered email job scheduled."}


# -------------------- Job runner --------------------

def run_staggered_email_job(job_id: str):
    """
    Called by the scheduler and once immediately when a job is created.

    Logic:
    - If we've already sent to all recipients, remove the job and stop.
    - Otherwise:
        * send the STORED email_body to recipients[next_index]
        * increment next_index
    """
    job_entry = jobs_store.get(job_id)
    if not job_entry:
        print(f"[Scheduler] Job {job_id} not found (maybe already finished).")
        return

    config = job_entry["config"]
    email_body: str = job_entry["email_body"]
    next_index: int = job_entry["next_index"]
    recipients: List[str] = config["recipients"]

    # If we've sent to everyone, clean up and stop
    if next_index >= len(recipients):
        print(f"[Scheduler] Job {job_id} completed all recipients. Removing job.")
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass
        jobs_store.pop(job_id, None)
        return

    recipient_email = recipients[next_index]
    subject = config.get("subject") or "Automated Scheduled Email"

    try:
        # Send the stored email body to the current recipient only
        send_email(
            from_email=config["from_email"],
            from_name=config.get("from_name"),
            to_emails=[recipient_email],
            subject=subject,
            body=email_body,
        )

        print(f"[Scheduler] Job {job_id}: sent to {recipient_email} (index {next_index}).")

        # Move to the next recipient for the next run
        job_entry["next_index"] = next_index + 1

    except Exception as e:
        # Don't crash the scheduler; just log the error
        print(f"[Scheduler] Job {job_id} failed: {e}")
