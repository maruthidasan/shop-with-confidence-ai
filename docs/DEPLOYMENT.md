# Deployment

Deploy the repository as one Vercel **Services** project. `vercel.json` uses `experimentalServices` route prefixes to mount Next.js at `/` and FastAPI at `/api`. Do not add catch-all rewrites: they bypass Next.js App Router/RSC and `/_next/*` routing.

1. In Vercel Project Settings, choose **Services** as the framework. This is required for the `services` configuration.
2. Add the variables from `.env.example` in Vercel. Do not set `NEXT_PUBLIC_API_URL` when using the included same-origin routes.
3. For a live experience, set `AI_MODE=live` plus valid Gemini and Perfect Corp credentials. Keep them server-side; none use the `NEXT_PUBLIC_` prefix.
4. Deploy and check `GET /api/health`, then load `/upload` directly and after a refresh. A `GET /upload` must render the frontend page, not the backend.

`AI_MODE=mock` is deliberately supported for credential-free demo deployments. It returns placeholder VTO previews and does not claim to be live provider output.
