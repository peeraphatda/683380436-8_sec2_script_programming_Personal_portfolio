# Week 12 LabX BASIC: Automating Communications (Email & SMS)

Python project that sends and receives email and sends SMS (via email-to-SMS gateway).

- **Send email (SMTP + STARTTLS)**: plain text, HTML, attachments (`smtplib`, `email.mime`)
- **Receive email (IMAP SSL)**: search UNSEEN by sender/subject, parse, download attachments, mark as read (`imaplib`)
- **SMS via email gateway**: build `number@carrier-gateway` and send through SMTP
- **Secure credentials**: `.env` + `python-dotenv` (never hard-coded, `.env` is git-ignored)
- **Logging & error handling**: try/except around network, auth and parsing

## Project structure
```
email-sms-automator/
├── src/
│   ├── __init__.py
│   ├── email_sender.py     # SMTP sending
│   ├── email_receiver.py   # IMAP receiving
│   ├── sms_gateway.py      # email-to-SMS
│   └── utils.py            # logging, env vars, directory helpers
├── data/
│   ├── attachments/        # downloaded attachments
│   └── dummy_report.pdf    # sample attachment
├── tests/test_automator.py # offline unit tests (mocked, no network)
├── .env.example            # template for credentials
├── .gitignore
├── main.py                 # runs Tasks 1-4
└── requirements.txt
```

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
```
Edit `.env` with your Gmail address and a **Gmail App Password**
(Google Account -> Security -> 2-Step Verification -> App passwords).
Your normal Gmail password will not work.

## Run
```bash
python main.py                        # Task 1 plain email, 2 attachment, 3 SMS, 4 receive
python -m unittest discover tests     # unit tests (no credentials needed)
```

## Troubleshooting
- `ValueError: Environment variable ... not set` -> `.env` missing or misnamed.
- `SMTPAuthenticationError` -> wrong App Password / 2FA not enabled.
- Connection errors -> check server/port (Gmail: `smtp.gmail.com:587`, `imap.gmail.com`) and firewall.
- No email found in Task 4 -> wait longer for delivery; check IMAP is enabled in Gmail settings.
- SMS not arriving -> many carriers (e.g. AT&T in the US) have retired email-to-SMS gateways, and
  Thai numbers are not supported by these gateways. The script still shows the email was handed to SMTP.
  For reliable SMS use an API such as Twilio.

## Extension ideas
Scheduled reports (`schedule`/APScheduler), Jinja2 templates, command-by-email processing,
Twilio for production SMS, alert emails on script errors.
