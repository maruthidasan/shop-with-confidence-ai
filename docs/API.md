# API

All public API routes are same-origin and begin with `/api`.

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health check |
| POST | `/api/recommend` | Create the recommendation edit and initial VTO previews |
| POST | `/api/tryon` | Generate the complete-the-look VTO |
| POST | `/api/upload` | Validate upload metadata (reserved for object-storage integration) |

`POST /api/recommend` accepts `occasion`, optional `category`, `gender`, `preferredColors`, and `photoUrl` (a browser data URL). Error responses include a safe `message`, an error code, and a request ID when available.
