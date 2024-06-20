# Build stage
FROM node AS builder
WORKDIR /usr/src/app
COPY . .
RUN npm install --force
RUN npm run build

# Run stage
FROM nginxinc/nginx-unprivileged
COPY --from=builder /usr/src/app/build /var/www/app
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8081
