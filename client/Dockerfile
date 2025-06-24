# Step 1: Build React App
FROM node:18-alpine AS builder
WORKDIR /app

# Install only necessary files
COPY package*.json ./
RUN npm install --frozen-lockfile

# Copy rest of the app and build
COPY . .
RUN npm run build

# Step 2: Serve with Nginx
FROM nginx:stable-alpine as production
LABEL maintainer="yourname@example.com"

# Remove default nginx static file config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
