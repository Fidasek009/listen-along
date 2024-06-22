# Build stage
FROM node:20-alpine AS builder
WORKDIR /usr/src/app

# Copy the application code
COPY . .

# Build the application
RUN npm install --force
RUN npm run build

# Run stage
FROM nginxinc/nginx-unprivileged
# Copy built assets from builder stage
COPY --from=builder /usr/src/app/build /var/www/app
# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Use COPY to set permissions for an unprivileged user
COPY --chown=nginx:nginx . /var/www/app

# Expose port 8081 for the service
EXPOSE 8081

# Best practice: specify a non-root user to run the container
USER nginx
