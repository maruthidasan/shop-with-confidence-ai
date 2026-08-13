# Security and privacy

- Keep Gemini and Perfect Corp credentials in Vercel environment variables, never source control.
- The current browser upload is passed directly to the recommendation request; the app does not persist user images itself.
- In live mode, the image is sent to the configured Gemini and Perfect Corp services to perform the requested styling/VTO workflow.
- Application logs intentionally avoid image bytes, authorization headers, and provider secrets.
- Add consent, retention controls, rate limiting, and a malware/object-storage pipeline before collecting production customer uploads at scale.
