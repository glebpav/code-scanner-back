#!/bin/sh
# Wait a bit for the app to be up
sleep 5

# Test nginx configuration
nginx -t || exit 1

# Start nginx
nginx -g 'daemon off;'