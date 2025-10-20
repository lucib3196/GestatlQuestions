# syntax=docker/dockerfile:1
# ---- Build stage ----
FROM node:20-alpine AS front-end-build
WORKDIR /app

# Copy dependency files first
COPY package*.json ./

# Install dependencies cleanly for Linux
RUN npm install

# Copy source code
COPY . .

# Rebuild optional native deps (fixes Rollup optional dep bug)
RUN npm rebuild

# Build project (Vite + TypeScript)
RUN npm run build

# ---- Serve stage ----
FROM nginx:alpine

# Copy build output from previous stage to Nginx’s static directory
COPY --from=front-end-build /app/dist /usr/share/nginx/html

# Expose port 80 so you can access it in the browser
EXPOSE 80

# Nginx runs automatically when container starts
CMD ["nginx", "-g", "daemon off;"]
