# 1. Use official Node.js base image
FROM node:18

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy all source files into the container
COPY . .

# 4. Install dependencies
RUN npm install

# 5. Expose the port used by Express (default 5000)
EXPOSE 5000

# 6. Start the Express server
CMD ["node", "index.js"]
