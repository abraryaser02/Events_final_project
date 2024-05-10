# Stage 1: Build the React application
FROM mhart/alpine-node:12 AS builder

WORKDIR /usr/src/app

ENV PATH /usr/src/app/node_modules/.bin:$PATH

# Copy package.json and package-lock.json separately to leverage Docker cache
COPY package.json /usr/src/app/package.json
COPY package-lock.json /usr/src/app/package-lock.json

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . /usr/src/app

# Build the application
RUN npm run build --production

# Stage 2: Serve the React application with NGINX
FROM nginx:1.15.8-alpine

# Remove the default NGINX configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy the custom NGINX configuration file
COPY ./nginx.conf /etc/nginx/nginx.conf

# Copy the site-specific NGINX configuration file
COPY ./services/nginx/prod.conf /etc/nginx/conf.d/default.conf

# Copy the build output to the NGINX html directory
COPY --from=builder /usr/src/app/build /usr/share/nginx/html

# Expose port 80 to the outside world
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
