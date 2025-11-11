# Base image
FROM node:18-alpine

WORKDIR /app

# Copy package.json & package-lock.json first (for caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Build the production app
RUN npm run build

# Expose port
EXPOSE 3001

# Start the server
CMD ["npm", "run", "start:prod"]
