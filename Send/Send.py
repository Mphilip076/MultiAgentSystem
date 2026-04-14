import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

APPROVED_RECIPIENTS = {
    "leader@example.com",
    "team@example.com"
}

LOG_FILE = "email_audit.log"


def log_event(report_id, status, details=""):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {report_id} | {status} | {details}\n")


def recipients_are_approved(recipients):
    return all(email in APPROVED_RECIPIENTS for email in recipients)


def attachment_exists(path):
    return path and os.path.exists(path)


def should_auto_send(report):
    if report.get("quality_score", 0) < 8.0:
        return False, "quality score below threshold"

    if report.get("risk_flag", False):
        return False, "risk flag raised"

    if report.get("requires_review", False):
        return False, "report marked for review"

    if not recipients_are_approved(report.get("recipients", [])):
        return False, "recipient list not approved"

    if not attachment_exists(report.get("attachment_path")):
        return False, "attachment missing"

    return True, "passed all checks"


def build_email_subject(report):
    return f"{report['title']} - {datetime.now().strftime('%Y-%m-%d')}"


def build_email_body(report):
    return f"""Hello,

Attached is the completed report: {report['title']}.

Executive Summary:
{report['summary']}

This message was generated and sent automatically by the Competitive Intelligence Agent.

Best,
Competitive Intelligence Delivery System
"""


def send_email(report, sender_email, app_password, smtp_server="smtp.gmail.com", smtp_port=587):
    subject = build_email_subject(report)
    body = build_email_body(report)

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = ", ".join(report["recipients"])
    msg["Subject"] = subject
    msg.set_content(body)

    with open(report["attachment_path"], "rb") as f:
        data = f.read()
        filename = os.path.basename(report["attachment_path"])

    msg.add_attachment(
        data,
        maintype="application",
        subtype="octet-stream",
        filename=filename
    )

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)


def queue_for_review(report, reason):
    review_path = f"review_queue/{report['report_id']}.txt"
    os.makedirs("review_queue", exist_ok=True)

    with open(review_path, "w") as f:
        f.write(f"Report ID: {report['report_id']}\n")
        f.write(f"Reason held: {reason}\n")
        f.write(f"Title: {report['title']}\n")
        f.write(f"Recipients: {', '.join(report['recipients'])}\n")
        f.write(f"Attachment: {report['attachment_path']}\n")
        f.write("\nSummary:\n")
        f.write(report["summary"])

    log_event(report["report_id"], "HELD_FOR_REVIEW", reason)


def delivery_agent(report, sender_email, app_password):
    allowed, reason = should_auto_send(report)

    if allowed:
        try:
            send_email(report, sender_email, app_password)
            log_event(report["report_id"], "SENT", "email delivered successfully")
            return "sent"
        except Exception as e:
            log_event(report["report_id"], "SEND_FAILED", str(e))
            return "failed"
    else:
        queue_for_review(report, reason)
        return "held"