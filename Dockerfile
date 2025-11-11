# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Install build dependencies (for Prisma/native modules)
RUN apk add --no-cache python3 make g++ bash

# Copy package.json & lock files for caching
COPY package.json  package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Build the app
RUN npm run build

# Stage 2: Production image
FROM node:18-alpine AS production

WORKDIR /app

# Only copy package.json & lock files
COPY package.json package-lock.json ./

# Install production dependencies only
RUN npm install --production

# Copy the built dist folder and Prisma client
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma

# Expose port
EXPOSE 3001

# Set environment
ENV NODE_ENV=production

# Start the server
CMD ["node", "dist/main.js"]
