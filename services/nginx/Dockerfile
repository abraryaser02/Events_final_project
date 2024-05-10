# Use an official Nginx image
FROM nginx:latest

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Expose port 80 to the outside world
EXPOSE 80
