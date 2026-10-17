# Google Cloud Console & Gmail API Setup

The CRM uses Gmail API for signup verification, account invitations, password reset and scheduled task deadline emails when Gmail API is selected. For local development, Gmail SMTP with an App Password is also supported; see [Email Configuration](../README.md#email-configuration).

Render's **free web services** block outbound SMTP ports 25, 465 and 587. Gmail API sends through HTTPS, so the included free-service Blueprint selects it. This is a hosting-plan restriction, not a general requirement for every Render service. See [Render's free-service limits](https://render.com/docs/free#outbound-port-restrictions).

## 1. Create a Google Cloud project and enable Gmail API

1. Open [Google Cloud Console](https://console.cloud.google.com/) and create or select a project.
2. Open **APIs & Services → Library**.
3. Find **Gmail API** and enable it for that project.

## 2. Configure OAuth consent

In **Google Auth Platform** (or **APIs & Services → OAuth consent screen**), configure the application name, support email, audience and developer contact.

For an external application in **Testing**, add the sending Gmail account as a test user. Request the send-only scope:

```text
https://www.googleapis.com/auth/gmail.send
```

Google may require verification depending on the audience and requested access. Refresh tokens for external applications in Testing generally expire after seven days when Gmail scopes are used. Before relying on unattended email, configure the appropriate publishing status and review [Google's refresh-token expiration rules](https://developers.google.com/identity/protocols/oauth2#expiration). Tokens can also be revoked or invalidated later.

## 3. Create OAuth credentials

1. Open **Clients** in Google Auth Platform, or **APIs & Services → Credentials**.
2. Create an **OAuth client ID** with application type **Desktop app**.
3. Download its client JSON and keep it outside the repository.
4. Retain the client ID and client secret for the application's environment settings.

Use the same client and sending Gmail account when generating the refresh token.

## 4. Generate a refresh token

Activate the project's virtual environment and install `requirements.txt` first. It already includes `django-gmailapi-backend` and its `google-auth-oauthlib` dependency.

The backend package's legacy `gmail_oauth2 --generate_oauth2_token` helper uses Google's retired out-of-band redirect. In the inspected package version **0.3.4**, the alternative `--ugo2t` branch refers to an unregistered `credentials_path` option. Use the supported local-server flow directly instead of relying on those helper commands.

Start `python` on a computer with a browser, then run the following Python code. Enter the path to your downloaded Desktop client JSON when prompted:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    input("OAuth client JSON path: "),
    scopes=["https://www.googleapis.com/auth/gmail.send"],
)
credentials = flow.run_local_server(
    port=0,
    access_type="offline",
    prompt="consent",
)
print(credentials.refresh_token)
```

Sign in as the Gmail account that will send application email and approve the requested access. Store the returned refresh token privately as `GMAIL_API_REFRESH_TOKEN`. Do not commit the client JSON or token, or paste either into documentation. If no refresh token is returned, repeat the consent flow and check the client's audience and account permissions.

The helper uses a temporary loopback callback; it is run locally to obtain credentials, not inside the deployed web service. See [Google's desktop OAuth flow](https://developers.google.com/identity/protocols/oauth2/native-app) and the [library reference](https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html).

## 5. Configure the application

Set these in the root `.env` for local development, or in your deployment environment:

| Variable | Value |
| --- | --- |
| `USE_GMAIL_API` | `true` to select Gmail API locally. |
| `GMAIL_API_CLIENT_ID` | Client ID from the Desktop OAuth client. |
| `GMAIL_API_CLIENT_SECRET` | Secret from that same client. |
| `GMAIL_API_REFRESH_TOKEN` | Token from the authorised sending account. |
| `DEFAULT_FROM_EMAIL` | Gmail address used during consent. |

Example with placeholders:

```env
USE_GMAIL_API=true
GMAIL_API_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_API_CLIENT_SECRET=your-client-secret
GMAIL_API_REFRESH_TOKEN=your-refresh-token
DEFAULT_FROM_EMAIL=sender@example.com
```

The Blueprint sets `USE_GMAIL_API=true`; provide the other four values in the Render Dashboard. Settings also select Gmail API whenever `RENDER_EXTERNAL_HOSTNAME` is present, even if `USE_GMAIL_API=false`.

Settings load a root `.env` with `override=True`. On deployment, keep actual configuration in the host environment and do not ship a development `.env` that would override it.

For links sent by scheduled commands, set `SITE_URL` to the application's public origin. It defaults to the Render hostname when available, otherwise `http://127.0.0.1:8000`. Views build their verification and reset links from the incoming request.

## 6. Verify delivery

From the repository root with the virtual environment activated, run:

```bash
python manage.py shell
```

Then send to a mailbox you control:

```python
from django.conf import settings
from django.core.mail import send_mail

send_mail(
    "CRM email configuration check",
    "Gmail API is configured for this environment.",
    settings.DEFAULT_FROM_EMAIL,
    [input("Recipient email: ")],
    fail_silently=False,
)
```

Check the return value and recipient inbox. This sends a real email. The application test suite uses Django's in-memory email backend and does not establish real Gmail delivery.

## Failure behaviour

- Missing or mismatched client credentials, expired/revoked refresh tokens and insufficient scopes can prevent the backend from obtaining access or sending mail. Check application logs and repeat consent with the correct client/account if needed.
- Signup and invitations save the new account, profile and verification token in one database transaction. A delivery failure rolls them back, removes the newly uploaded profile photo when storage is available, and displays a retry message. A storage cleanup failure is logged separately. Password-reset delivery failures display a form error instead of an HTTP 500 response.
- After a successful password reset, the application sends a separate confirmation email. If that notification fails, the new password remains valid, the failure is logged, and the completion page shows a warning.
- An `invalid_grant` error can mean an expired or revoked refresh token; it does not by itself prove seven-day expiration. Check the OAuth application status and the full provider error. After changing an external application from Testing to the appropriate production status, obtain a new refresh token with the same client and sending account, update `GMAIL_API_REFRESH_TOKEN` in the deployment environment and restart/redeploy before testing delivery. Existing tokens are not renewed by changing the status alone.
- `check_task_deadlines` logs a failed delivery and skips creating that reminder's notification. It requires a separately configured scheduler; the Blueprint does not schedule it.
- Changing `USE_GMAIL_API` alone cannot select SMTP on Render while `RENDER_EXTERNAL_HOSTNAME` is present. For local SMTP, leave that variable unset and configure the SMTP values documented in the README.
