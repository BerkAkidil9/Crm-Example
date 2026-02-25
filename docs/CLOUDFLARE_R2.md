# Cloudflare R2 – Media Storage Setup

This project can store uploaded files (profile photos, lead images, etc.) in **Cloudflare R2** so they persist across deploys on platforms like Render, where the filesystem is ephemeral.

---

## Why R2?

On Render (and similar PaaS):

1. **Ephemeral disk** — The server disk is reset on each deploy or restart. Files written to `media/` are lost.
2. **Broken images** — The database keeps the file path (e.g. `profile_images/abc.jpg`), but the file no longer exists on the server, so images return 404.

**Solution:** Store media in cloud storage. This project is configured to use **Cloudflare R2** (S3-compatible API, 10 GB free tier).

---

## Prerequisites

- A [Cloudflare](https://cloudflare.com/) account
- The project already includes `django-storages[s3]` and `boto3` in `requirements.txt` — no extra install needed.

---

## Step 1: Create an R2 bucket

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/) and open **R2 Object Storage**.
2. Click **Create bucket**.
3. Choose a name (e.g. `crm-media`) and create the bucket.

---

## Step 2: Create an R2 API token

1. In R2, go to **Manage R2 API Tokens** (or **Overview** → **Manage API Tokens**).
2. Click **Create API token**.
3. Name it (e.g. `crm-media-token`).
4. Permissions: **Object Read & Write**. Scope: this bucket only, or “Apply to all buckets”.
5. Create the token and **copy** the **Access Key ID** and **Secret Access Key** (the secret is shown only once).

---

## Step 3: Get your Account ID and optional public URL

- **Account ID:** In the R2 section, the URL is like `https://dash.cloudflare.com/<ACCOUNT_ID>/r2`. That `<ACCOUNT_ID>` is your `R2_ACCOUNT_ID`. You can also find it in the dashboard footer.
- **Endpoint:** The app builds it as `https://<R2_ACCOUNT_ID>.r2.cloudflarestorage.com`. You can override with `R2_ENDPOINT_URL` if needed.
- **Public access (optional):** If you want direct URLs to files:
  - Open your bucket → **Settings** → **Public access** → **Allow Access**.
  - Note the public URL (e.g. `https://pub-xxxx.r2.dev`). Use either the host as `R2_PUBLIC_DOMAIN` (e.g. `pub-xxxx.r2.dev`) or the full URL as `R2_PUBLIC_URL`.

If you skip public access, the app can still serve files via **USE_R2_MEDIA_PROXY** (see below).

---

## Step 4: Environment variables

Add these to your `.env` (local) or to your host’s environment (e.g. Render Dashboard):

| Variable | Required | Description |
|----------|----------|-------------|
| `USE_R2` | Yes | Set to `true` to enable R2. |
| `R2_ACCOUNT_ID` | Yes | Your Cloudflare account ID. |
| `R2_BUCKET_NAME` | Yes | Bucket name (e.g. `crm-media`). |
| `R2_ACCESS_KEY_ID` | Yes | From the R2 API token. |
| `R2_SECRET_ACCESS_KEY` | Yes | From the R2 API token. |
| `R2_PUBLIC_DOMAIN` | Optional | Public host only (e.g. `pub-xxxx.r2.dev`). |
| `R2_PUBLIC_URL` | Optional | Full public URL (e.g. `https://pub-xxxx.r2.dev`). Use one of `R2_PUBLIC_DOMAIN` or `R2_PUBLIC_URL`. |
| `R2_ENDPOINT_URL` | Optional | Override endpoint (default: `https://<R2_ACCOUNT_ID>.r2.cloudflarestorage.com`). |
| `R2_REGION_NAME` | Optional | Default `auto`. |
| `USE_R2_MEDIA_PROXY` | Optional | Default `true`. See below. |

**Example (minimal):**

```env
USE_R2=true
R2_ACCOUNT_ID=your-account-id
R2_BUCKET_NAME=crm-media
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
```

If you enabled public access on the bucket, add either:

```env
R2_PUBLIC_DOMAIN=pub-xxxx.r2.dev
```

or:

```env
R2_PUBLIC_URL=https://pub-xxxx.r2.dev
```

---

## USE_R2_MEDIA_PROXY (default: true)

Some networks block or reset connections to `pub-xxx.r2.dev`. When `USE_R2_MEDIA_PROXY=true` (default):

- Media is served through your app at a path like `/media-proxy/...`.
- No need for a custom domain or Worker for R2.
- Set to `false` if you prefer direct R2 public URLs.

---

## How the project uses R2

- **Django settings** read the env vars above and configure `storages.backends.s3.S3Storage` (S3-compatible) for the default file storage when `USE_R2=true` and required vars are set.
- **Models and forms** do not need changes; uploads go to R2 automatically when R2 is enabled.
- **Locally:** Set `USE_R2=true` and the same env vars in `.env` to test R2 on your machine.

---

## Summary checklist

1. Create R2 bucket (e.g. `crm-media`).
2. Create R2 API token (Read & Write); save Access Key ID and Secret Access Key.
3. Note Account ID; optionally enable public access and note `R2_PUBLIC_DOMAIN` or `R2_PUBLIC_URL`.
4. Set `USE_R2=true` and all required `R2_*` variables in `.env` or host environment.
5. Deploy or run locally; new uploads will be stored in R2 and persist across deploys.
