# Week 12 LabX ADV: Agentic Communication Workflows (Advanced Email & SMS)

A configuration-driven **CommunicationAgent** that runs a pipeline of email / SMS / inbox tasks
declared in `configs/comm_pipeline_config.json`. It continues the BASIC lab (same Gmail + App Password).

## Features
- **Declarative JSON pipeline** with a task dispatcher (`send_email`, `send_sms`, `process_inbox`)
- **Shared context** (`agent.context`): dynamic values for templates; a task can store its result via `output_context_key`
- **Templating**: `{report_date}`, `${sales_figure:.2f}` in subjects, bodies, SMS, attachment paths
- **Env placeholders in config**: `${SENDER_EMAIL}` etc. are filled from `.env` (secrets never live in the JSON)
- **Email**: To / CC / BCC, multiple attachments, plain or HTML (`"is_html": true`)
- **Rule-based inbox processing** (`if` conditions are AND-ed, case-insensitive):
  - conditions: `from_sender_is`, `subject_contains`, `body_contains`, `has_attachments`
  - actions: `download_attachments` (+ `allowed_extensions`), `send_sms_alert`, `reply_with_template`, `mark_as_read`
- **Audit log**: every step -> `audit_reports/audit_report_comm_<timestamp>.json` (summary + entries)
- **Error handling**: failed tasks don't stop the run; optional `error_alert` emails you a summary

## Structure
```
agentic-comm-automator/
├── configs/comm_pipeline_config.json
├── src/
│   ├── __init__.py
│   ├── communication_agent.py   # agent, dispatcher, context, rules, audit
│   ├── config_parser.py         # load + ${ENV} expansion + validation
│   ├── email_tasks.py           # SMTP send, IMAP search/fetch/download/mark read
│   ├── sms_tasks.py             # SMS via email gateway
│   ├── template_renderer.py
│   └── utils.py                 # logging, env, directories, audit entries
├── data/
│   ├── reports/                 # sales_report.pdf, summary_data.xlsx (samples)
│   ├── attachments/
│   └── incoming_attachments/    # downloaded from processed emails
├── tests/test_agent.py          # offline unit tests (mocked)
├── .env.example  .gitignore  requirements.txt  main.py  README.md
```

## Setup & run
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env  -> fill in values
python main.py                    # runs the pipeline
python -m unittest discover tests # offline tests (no credentials needed)
```
Set `STUDENT_NAME` and `STUDENT_ID` in `.env`: they are printed at the bottom of the report, request and reply emails.

Gmail needs 2-Step Verification + an **App Password** (Google Account -> Security -> App passwords)
and IMAP enabled in Gmail settings.

## What `python main.py` does
1. Sends the Daily Sales Report email (To + CC, 2 attachments) with dynamic subject/body
2. Sends an SMS with dynamic text
3. Sends a "Data Request ... Urgent" email to yourself (the simulated incoming request)
4. Processes the inbox (waits/retries for delivery, ignores `Re:` replies):
   - Rule 1: from self + subject contains "Request" -> download attachments, mark as read
   - Rule 2: body contains "urgent" -> SMS alert
   - Rule 3: body contains "new data processing" -> auto-reply
5. Writes the audit report. Exit code: 0 = all OK, 2 = some task failed, 1 = config/fatal error.

## Troubleshooting
- `Config references ${X} but the environment variable is not set` -> add X to `.env`.
- `SMTPAuthenticationError` / IMAP error -> use an App Password, check IMAP is enabled.
- Task 4 finds nothing -> increase `wait_before_seconds` / `retries` in the config.
- SMS not received -> many carrier email-to-SMS gateways are retired and non-US numbers are unsupported;
  the task only proves the email reached SMTP. Use Twilio for production.
- Template error -> a `{placeholder}` is not in the context (see the audit report).

## Extension ideas
Chain with a data agent that produces reports, Jinja2 HTML templates, scheduling (`schedule`),
Twilio SMS, folder-watching triggers, NLP-based inbox rules, reply threading (`In-Reply-To`).
