FROM node:24-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm i

COPY . .

# Vite bakes these into the JS bundle at build time.
# Pass them with: docker build --build-arg VITE_API_URL=https://api.example.com ...
ARG VITE_API_URL=http://127.0.0.1:8000
ARG VITE_NEON_AUTH_URL=
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_NEON_AUTH_URL=$VITE_NEON_AUTH_URL

RUN npm run build

FROM nginx:alpine AS runner
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
