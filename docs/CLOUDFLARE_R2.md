# Cloudflare R2 – Media Storage Setup

The application can store uploaded profile images and lead photos in Cloudflare R2 through its S3-compatible API. This keeps new uploads independent of the web service's local filesystem. Render's free web-service disk is ephemeral, so local uploads are lost across deploys or restarts.

R2 is optional. Without a complete R2 configuration, Django uses the local `media/` directory. Local debug serving and production media delivery have different requirements, described below.

## Prerequisites

- A [Cloudflare account](https://dash.cloudflare.com/) with R2 enabled.
- Project dependencies installed from `requirements.txt`, including `django-storages[s3]` and `boto3`.
- Access to the application's environment configuration and a test account authorised to view the uploaded image.

## 1. Create a bucket and credentials

1. Open **R2 Object Storage** in the Cloudflare Dashboard and create a bucket, for example `crm-media`.
2. Under R2 API token management, create credentials with **Object Read & Write** access scoped to that bucket.
3. Save the **Access Key ID** and **Secret Access Key** privately.
4. Copy the account's S3 API endpoint. For a standard bucket it is `https://<account-id>.r2.cloudflarestorage.com`.

For a different endpoint, including a jurisdiction-specific endpoint, set `R2_ENDPOINT_URL` explicitly. See [Cloudflare's S3 API reference](https://developers.cloudflare.com/r2/api/s3/api/) for endpoint and credential details.

## 2. Set environment variables

Use the root `.env` locally or your host's environment settings in production:

| Variable | Requirement and behaviour |
| --- | --- |
| `USE_R2` | Set to `true`. Disabled automatically during `manage.py test`. |
| `R2_BUCKET_NAME` | Required bucket name. |
| `R2_ACCESS_KEY_ID` | Required R2 access key. |
| `R2_SECRET_ACCESS_KEY` | Required R2 secret key. |
| `R2_ACCOUNT_ID` | Used to construct the endpoint unless `R2_ENDPOINT_URL` is set. |
| `R2_ENDPOINT_URL` | Optional explicit S3 API endpoint; takes precedence over the account-derived endpoint. |
| `R2_REGION_NAME` | Defaults to `auto`. |
| `USE_R2_MEDIA_PROXY` | Defaults to `true`; controls the URL and delivery mode below. |
| `SITE_URL` | Application origin for proxy URLs; defaults to the Render hostname or local development URL. |
| `R2_PUBLIC_DOMAIN` | Hostname without scheme, for direct public delivery. |
| `R2_PUBLIC_URL` | Optional full URL used to construct `MEDIA_URL` in direct mode; see its limitation below. |

Minimal configuration with placeholders:

```env
USE_R2=true
R2_ACCOUNT_ID=your-account-id
R2_BUCKET_NAME=crm-media
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
USE_R2_MEDIA_PROXY=true
SITE_URL=https://your-app.example.com
```

`USE_R2=true` alone is insufficient. The bucket, endpoint and both credentials must be present; otherwise settings fall back to local filesystem storage rather than failing startup. The application does not test credentials or create the bucket on startup, so populated but invalid values can fail on the first upload or read.

The root `.env` overrides existing environment values. Keep deployment secrets in the hosting environment and avoid shipping a development `.env` with conflicting settings.

## 3. Choose how images are delivered

### Application proxy (default)

With `USE_R2_MEDIA_PROXY=true`, Django uses `djcrm.storage.R2ProxyStorage`. Uploads go to R2, while generated URLs point to `SITE_URL/media-proxy/<object-key>`.

- The bucket does not need public access or a custom domain.
- Requests pass through the application and require login.
- The view checks ownership/organisation or agent access for `lead_photos/` and `profile_images/`. Unknown prefixes, unauthorised access and missing objects return 404; anonymous requests redirect to login. Only GET is accepted.
- Set `SITE_URL` to the correct reachable application origin, especially when using a custom domain.
- R2 read/open errors can result in a 404 or server error, depending on where the storage operation fails; inspect server logs as well as the browser response.

The proxy currently sends `Cache-Control: public, max-age=86400`. If a reverse proxy or CDN is used, exclude protected media responses from shared caching; application authorisation alone does not establish safe shared-cache behaviour.

### Direct public URLs

With `USE_R2_MEDIA_PROXY=false`, uploads use the standard S3 storage backend and image requests go directly to storage. Configure public bucket access through a Cloudflare custom domain or an enabled `r2.dev` URL, then set its hostname:

```env
USE_R2_MEDIA_PROXY=false
R2_PUBLIC_DOMAIN=media.example.com
```

`R2_PUBLIC_DOMAIN` must omit `https://` and any path. Direct access bypasses the application's media permission checks, so use it only for files intended to be public. The current storage configuration disables signed URL query parameters.

`R2_PUBLIC_URL` changes `MEDIA_URL`, but the standard S3 backend generates `FileField.url` independently. Setting `R2_PUBLIC_URL` alone does not configure the backend's public custom domain. Set `R2_PUBLIC_DOMAIN` for working direct image URLs; without it the backend can return the S3 endpoint, which is not a public bucket URL.

See [Cloudflare public bucket configuration](https://developers.cloudflare.com/r2/buckets/public-buckets/). An S3 API endpoint and a public delivery domain serve different purposes.

## 4. Verify an upload

1. Restart or redeploy the application with the selected environment settings.
2. Sign in and upload a new profile image or lead photo through the application.
3. Confirm the object appears under `profile_images/` or `lead_photos/` in the configured bucket.
4. Open the image from an authorised account and inspect its URL. Proxy mode should use the application origin; direct mode should use the configured public hostname.
5. On a disposable deployment, confirm that the same image remains available after a restart.

The test suite disables R2 and uses local test storage; it does not verify bucket connectivity or production permissions.

## Existing files and operational limits

Enabling R2 affects subsequent storage operations. It does **not** copy files already stored in local `media/` or in another bucket. Copy existing files separately while preserving their relative keys, such as `profile_images/example.jpg`, because the database retains those keys. Preserve a backup before changing storage.

Storage uses `file_overwrite=True`: uploading an object with the same key may replace it. Do not use a shared bucket/prefix for unrelated environments unless overwrites and access are intentionally managed.

With R2 disabled, Django's `/media/` helper serves files only when `DEBUG=True`. A production deployment using local filesystem storage needs persistent storage and a separately configured media server; WhiteNoise handles static assets, not these uploads.
