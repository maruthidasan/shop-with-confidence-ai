# Shop with Confidence

**See an occasion-ready edit on your own photo before deciding what to buy.**

Online fashion often comes down to one unresolved question: **“Will this actually suit me?”** Shop with Confidence builds a small, explained fashion edit around a shopper photo and occasion, then uses YouCam Apparel Virtual Try-On (VTO) to make the options visual.

> **AI can recommend. YouCam lets the shopper see. The shopper decides.**

## Demo / Product Overview

The working application includes a browsable fashion storefront and an AI Stylist journey. A shopper uploads one full-body photo, chooses an occasion and a men's or women's style profile, and receives three catalogue-grounded recommendations with VTO previews. The shopper can compare the results, view a confidence-oriented explanation, and try a complementary loafer on the generated look. Checkout and ordering are demonstration UI only; they do not process payments or fulfil orders.

No public demo URL is committed in this repository.

## The Problem

Product grids provide choice, but limited help with purchase uncertainty. Shoppers must judge whether an outfit fits the moment, narrow many alternatives, and imagine the result without seeing themselves in it.

## The Solution

Shop with Confidence separates recommendation from decision-making. Gemini can compare the original shopper image with image-backed catalogue candidates and return a structured edit for the chosen occasion. YouCam Apparel VTO then creates the visual try-on results. The final choice remains with the shopper.

## Customer Journey

1. Browse the demonstration storefront or open the AI Stylist.
2. Upload one JPEG, PNG, or WebP full-body photo in the browser.
3. Choose an occasion and a men's or women's style profile.
4. Submit the photo and context to `POST /api/recommend`.
5. Review three recommendations and their full-body VTO previews.
6. Compare looks, read the confidence-oriented summary, or add the selected look to a demo order.
7. Optionally send the generated outfit result through a second VTO task with a complementary loafer.

The active customer form does **not** ask for a separate preferences input. Although the backend request schema can accept `preferredColors`, the current frontend sends an empty list.

## YouCam Apparel VTO Integration

The live YouCam integration is implemented in [`backend/services/youcam_client.py`](backend/services/youcam_client.py) and orchestrated by [`backend/services/recommendation_service.py`](backend/services/recommendation_service.py).

In live mode:

1. The backend decodes the shopper's image data URL without altering its bytes.
2. It derives the Clothes file endpoint from the configured `/task/cloth` URL, requests a provider file upload, and uploads the image bytes to the returned presigned URL.
3. Local, image-backed catalogue garments are uploaded through the same file flow; their provider file IDs are cached for the lifetime of the service instance.
4. The backend posts a `full_body` task (or `shoes` for the complementary loafer) containing the shopper source reference and garment reference ID.
5. It polls `GET {task-endpoint}/{task_id}` every two seconds, for up to 30 attempts, until `task_status` is `success` or `error`.
6. The result image URL is returned inside the recommendation or try-on API response and rendered by the Next.js frontend.

The backend waits for each VTO task during the request; the browser does not poll YouCam directly and never receives provider credentials. In mock mode, no YouCam request is made and placeholder preview URLs are returned.

## Architecture

```text
Shopper
   |
   | full-body photo + occasion + style profile
   v
Next.js frontend
   |
   | POST /api/recommend
   v
FastAPI orchestration
   |
   +--> Local, image-backed catalogue candidates
   |
   +--> Gemini structured ranking (live) or deterministic edit (mock)
   |
   +--> YouCam Apparel VTO tasks (live) or placeholders (mock)
   |
   v
Three recommendations + VTO result URLs
   |
   +--> Comparison and confidence-oriented summary
   |
   +--> Optional loafer VTO via POST /api/tryon
   v
Shopper decision / demo order UI
```

## Tech Stack

| Area | Verified technology |
| --- | --- |
| Frontend | Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4 |
| Backend | Python, FastAPI, Pydantic 2, HTTPX, Uvicorn |
| AI | Google Gemini through the `google-genai` Python SDK |
| Virtual try-on | Perfect Corp / YouCam Apparel Clothes VTO API |
| Deployment configuration | Vercel multi-service configuration for Next.js and FastAPI |

YouCam Skin AI is **not part of the implemented customer flow**.

## Project Structure

```text
.
|-- frontend/
|   |-- app/                  # Next.js storefront and AI Stylist routes
|   |-- components/           # Store and journey UI components
|   `-- public/               # Product and editorial demo assets
|-- backend/
|   |-- routers/              # FastAPI route handlers
|   |-- services/             # Catalogue, Gemini, VTO, and orchestration logic
|   |-- schemas/              # Pydantic request/response models
|   |-- assets/vto/           # Garment references used by the backend VTO flow
|   `-- tests/                # Backend API and image/VTO service tests
|-- docs/                     # API, deployment, and security notes
|-- .env.example              # Safe configuration template
`-- vercel.json               # Same-origin frontend/backend routing
```

## API / Backend Overview

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Return service health status. |
| `POST` | `/api/recommend` | Build the catalogue edit and initial VTO previews from shopper context. |
| `POST` | `/api/tryon` | Create a VTO result for a specified recommendation; the UI uses it for the loafer step. |
| `POST` | `/api/upload` | Validate image metadata only; binary storage is not implemented. |

Interactive FastAPI documentation is available at `/docs` and `/redoc` when the backend is running directly.

## Running Locally

### Prerequisites

- Node.js 20 or later and npm
- Python 3.11 or later
- Vercel CLI only if you want the same combined routing used by deployment

### Combined application

From PowerShell at the repository root:

```powershell
Copy-Item .env.example backend/.env

cd frontend
npm ci

cd ..\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

cd ..
vercel dev -L
```

`vercel dev -L` serves the Next.js frontend and FastAPI backend behind the same origin according to `vercel.json`.

### Services separately

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm run dev
```

The frontend calls relative `/api/*` paths. Running it separately therefore requires a local proxy or the combined Vercel development setup for the full journey.

## Environment Variables

Copy [`.env.example`](.env.example) to `backend/.env`. Never commit real credentials.

| Variable | Required | Purpose |
| --- | --- | --- |
| `APP_ENV` | No | Application environment label. |
| `DEBUG` | No | Enables FastAPI debug behavior. |
| `AI_MODE` | Yes | `mock` avoids provider calls; `live` enables Gemini and YouCam. |
| `ALLOWED_ORIGINS` | No | Comma-separated CORS origins for direct cross-origin API use. |
| `REQUEST_TIMEOUT_SECONDS` | No | Timeout for YouCam HTTP operations. |
| `GEMINI_API_KEY` | Live only | Server-side Gemini credential. |
| `GEMINI_MODEL` | Live only | Primary Gemini model identifier. |
| `GEMINI_FALLBACK_MODEL` | No | Model used after a transient primary-model failure. |
| `GEMINI_TIMEOUT_MS` | No | Gemini SDK request timeout. |
| `GEMINI_RETRY_ATTEMPTS` | No | Gemini SDK retry-attempt count. |
| `YOUCAM_API_KEY` | Live only | Server-side Perfect Corp / YouCam credential. |
| `YOUCAM_CLOTHES_TRYON_URL` | Live only | Tenant Clothes API `/task/cloth` endpoint. |
| `YOUCAM_AUTH_HEADER` | No | Provider authentication header name; defaults to `X-API-KEY`. |
| `YOUCAM_AUTH_PREFIX` | No | Optional text prepended to the provider credential. |

## Live vs Demo/Mock Mode

`AI_MODE` is read in [`backend/config.py`](backend/config.py).

| Mode | Gemini | YouCam | Intended use |
| --- | --- | --- | --- |
| `mock` | Returns a deterministic catalogue edit; no API call. | Returns placeholder result URLs; no API call. | Credential-free development and demonstrations. |
| `live` | Sends the original shopper image, context, structured catalogue data, and eligible garment images to Gemini. | Uploads shopper/garment images, creates Apparel VTO tasks, and polls for results. | Provider-backed testing with valid credentials and endpoints. |

If both Gemini models fail with a transient service/timeout error, live mode falls back to a deterministic catalogue-grounded edit. VTO still requires the live YouCam service.

## Challenges / Engineering Decisions

- Provider credentials remain server-side behind same-origin API routes.
- YouCam's asynchronous task lifecycle is contained in the backend, with bounded polling and safe provider errors.
- Gemini is constrained to image-backed catalogue IDs and structured JSON; invalid or out-of-catalogue results are rejected.
- Mock mode keeps the journey reproducible without consuming provider credits, while clearly returning placeholders rather than live VTO output.
- Browser loading and error states cover the potentially long recommendation/VTO request.

## Retail Value

This prototype explores a product hypothesis rather than reporting measured commercial results.

For shoppers, the journey could provide greater visual confidence, reduce choice overload, and make complementary-product discovery more relevant. For retailers, it could potentially support stronger conversion, fewer avoidable expectation-related returns, contextual cross-sell, and higher basket value. These outcomes have not been validated by production analytics in this repository.

## Future Direction

YouCam Skin AI is a **future product idea, not a currently implemented feature**. A future version could use structured Skin AI results as grounded input for contextual reasoning alongside occasion information, before YouCam Apparel VTO provides visual validation:

```text
Shopper Image
   |
YouCam Skin AI
   |
Structured Insights + Occasion
   |
Contextual Reasoning
   |
Personalized Selection
   |
YouCam Apparel VTO
   |
Visual Validation
```

Developer feedback: an apparel journey already captures a full-body shopper image for VTO. Where image quality permits, compatible YouCam analysis capabilities could ideally reuse that capture and request an additional face-focused image only when necessary. This is a future workflow suggestion, not current application behavior.

Other future work includes consent-aware storage, rate limiting, production authentication, real checkout integration, and broader end-to-end test coverage.

## Hackathon

Shop with Confidence was created for the YouCam API Skin AI & Apparel VTO Hackathon. The implemented integration focuses on YouCam Apparel VTO; Skin AI remains a future direction.

## Asset Provenance

The repository uses fictional demo retail imagery created or generated for this hackathon prototype with OpenAI-assisted tooling. See [ASSET_PROVENANCE.md](ASSET_PROVENANCE.md) for the provenance statement and branding clarification.

## Validation

```powershell
cd frontend
npm run lint
npm run build

cd ..\backend
python -m pytest tests
```

See also [API notes](docs/API.md), [deployment guidance](docs/DEPLOYMENT.md), and [security notes](docs/SECURITY.md).
