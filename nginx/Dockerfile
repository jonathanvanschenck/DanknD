# This tells docker how to construct our nginx container

FROM nginx

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Attach new configuration
COPY nginx.conf /etc/nginx/conf.d/
