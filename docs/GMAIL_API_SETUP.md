# Google Cloud Console & Gmail API Setup

This project can send email (signup verification, password reset) via **Gmail API** using OAuth 2.0. This is required on **Render** because Render blocks outbound SMTP ports (25, 465, 587). For local development you can use either Gmail API or SMTP (App Password).

---

## Why Gmail API on Render?

- On Render, SMTP ports are blocked, so `EMAIL_HOST`/`EMAIL_HOST_PASSWORD` (SMTP) will not work.
- Gmail API uses HTTPS and works on Render. Set `USE_GMAIL_API=true` and provide the OAuth credentials and refresh token below.

---

## Step 1: Create a Google Cloud project

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown → **New Project**.
3. Name it (e.g. `crm-email`) and create.

---

## Step 2: Enable Gmail API

1. In the project, go to **APIs & Services** → **Library**.
2. Search for **Gmail API** and open it.
3. Click **Enable**.

---

## Step 3: Configure OAuth consent screen

1. Go to **APIs & Services** → **OAuth consent screen**.
2. Choose **External** (unless you use a Google Workspace org) → **Create**.
3. Fill **App name**, **User support email**, and **Developer contact**. Save.
4. **Scopes:** Add scope `https://www.googleapis.com/auth/gmail.send` (send email only). Save.
5. **Test users** (if app is in Testing): Add the Gmail address you will use to send mail. Save.

---

## Step 4: Create OAuth 2.0 credentials

1. Go to **APIs & Services** → **Credentials**.
2. **Create Credentials** → **OAuth client ID**.
3. Application type: **Desktop app**.
4. Name it (e.g. `CRM Desktop`) and create.
5. Copy the **Client ID** and **Client secret** (you will use these as `GMAIL_API_CLIENT_ID` and `GMAIL_API_CLIENT_SECRET`).

---

## Step 5: Get a refresh token

The app uses a **refresh token** to get access tokens and send email. You generate it once using the same Gmail account that will send mail.

### Option A: Using `gmail_oauth2` (recommended)

1. Install the package used by the project:
   ```bash
   pip install django-gmailapi-backend
   ```
2. Run (replace with your Client ID and Client secret from Step 4):
   ```bash
   gmail_oauth2 --generate_oauth2_token --client_id="YOUR_CLIENT_ID.apps.googleusercontent.com" --client_secret="YOUR_CLIENT_SECRET" --scope="https://www.googleapis.com/auth/gmail.send"
   ```
3. A browser window opens. Log in with the **Gmail account that will send mail** and allow the app.
4. Copy the **refresh token** from the script output (starts with `1//...`). This is `GMAIL_API_REFRESH_TOKEN`.
5. The sending address is `DEFAULT_FROM_EMAIL` — use that same Gmail address.

### Option B: Manual / other tools

You can use any OAuth 2.0 flow that requests the scope `https://www.googleapis.com/auth/gmail.send` and returns a refresh token for the sending Gmail account. Store that as `GMAIL_API_REFRESH_TOKEN`.

---

## Step 6: Environment variables

Add these to your `.env` (local) or to your host’s environment (e.g. Render Dashboard):

| Variable | Required | Description |
|----------|----------|-------------|
| `USE_GMAIL_API` | Yes | Set to `true` to use Gmail API instead of SMTP. |
| `GMAIL_API_CLIENT_ID` | Yes | OAuth 2.0 Client ID (from Step 4). |
| `GMAIL_API_CLIENT_SECRET` | Yes | OAuth 2.0 Client secret (from Step 4). |
| `GMAIL_API_REFRESH_TOKEN` | Yes | Refresh token from Step 5. |
| `DEFAULT_FROM_EMAIL` | Yes | Gmail address that sends mail (same as the account used for the refresh token). |

**Example:**

```env
USE_GMAIL_API=true
GMAIL_API_CLIENT_ID=123456789-xxxx.apps.googleusercontent.com
GMAIL_API_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxx
GMAIL_API_REFRESH_TOKEN=1//0xxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=your-sender@gmail.com
```

On **Render**, `USE_GMAIL_API` is set to `true` in `render.yaml`; you only need to add the four variables above in the Dashboard.

---

## How the project uses Gmail API

- When `USE_GMAIL_API=true` (or when `RENDER_EXTERNAL_HOSTNAME` is set, for Render), Django uses the `gmailapi_backend` email backend.
- It reads `GMAIL_API_CLIENT_ID`, `GMAIL_API_CLIENT_SECRET`, `GMAIL_API_REFRESH_TOKEN`, and `DEFAULT_FROM_EMAIL` from the environment and sends mail via Gmail API.

---

## Summary checklist

1. Create a Google Cloud project and enable Gmail API.
2. Configure OAuth consent screen and add scope `https://www.googleapis.com/auth/gmail.send`.
3. Create OAuth 2.0 Client ID (Desktop app) and copy Client ID and Client secret.
4. Generate a refresh token with that client and the Gmail account you will use for sending.
5. Set `USE_GMAIL_API=true`, `GMAIL_API_CLIENT_ID`, `GMAIL_API_CLIENT_SECRET`, `GMAIL_API_REFRESH_TOKEN`, and `DEFAULT_FROM_EMAIL` in your environment.

For **local** development you can instead use SMTP with a Gmail App Password; see the main [README](../README.md) → Email Configuration (Option A).
