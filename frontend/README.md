# Frontend

React web app for uploading images, selecting VLM models, and viewing benchmark results.

## Admin Login (dev)

email = `admin@ocrbench.com`
password = `admin123`

## How to Run

```sh
# Install dependencies
npm i

# Start dev server
npm run dev
```

## Tech Stack

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## Deployment

The frontend is containerized for production. It builds as a static bundle served by nginx.

```bash
# Via docker-compose from the project root (serves on port 8080):
docker compose up frontend
```

See `Dockerfile` and `nginx.conf` for the production setup.

## Routes

```
/login
/benchmark
/models
/account
/admin
```
