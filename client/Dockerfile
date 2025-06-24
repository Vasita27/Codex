# 1. Base image with Node.js installed
FROM node:18

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy all files from your local client/ folder into the container's /app
COPY . .

# 4. Install dependencies listed in package.json
RUN npm install

# 5. Build production version of the app
RUN npm run build

# 6. Expose port 3000 (used by Vite preview server)
EXPOSE 3000

# 7. Run Vite's preview server to serve the build
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
