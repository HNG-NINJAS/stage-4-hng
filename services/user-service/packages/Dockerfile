# --- Builder stage ---
FROM node:20-alpine AS builder
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package*.json ./

# Configure npm for better reliability
RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000

# Install dependencies with retry
RUN npm install --legacy-peer-deps || \
    npm install --legacy-peer-deps || \
    npm install --legacy-peer-deps

# Copy source code
COPY . .

# Generate Prisma client (if prisma schema exists)
RUN if [ -f prisma/schema.prisma ]; then npx prisma generate; fi

# Build application
RUN npm run build

# --- Runner stage ---
FROM node:20-alpine AS runner
WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache tini

# Copy built application
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Expose port 3001 (User Service port)
EXPOSE 3001

# Set environment variable for port
ENV PORT=3001
ENV NODE_ENV=production

# Use tini for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Start application
CMD ["node", "dist/main.js"]
