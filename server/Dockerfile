# 1. Use official Node.js base image
FROM node:18-alpine

# 2. Set working directory
WORKDIR /app

# 3. Copy files
COPY . .

# 4. Install only production dependencies
RUN npm ci --omit=dev

# 5. Create non-root user
RUN addgroup app && adduser -S -G app app
USER app

# 6. Expose port
EXPOSE 5000

# 7. Run the server
CMD ["node", "index.js"]
