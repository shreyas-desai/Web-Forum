#!/bin/sh

set -e # exit immediately if newman complains
trap 'kill $SERVER_PID' EXIT # kill the server on exit

# start_server() {
./run.sh &
SERVER_PID=$!
#     echo "SERVER_PID: $SERVER_PID"
# }

# stop_server() {
#     if [ -n "$SERVER_PID" ]; then
#         echo "Stopping server with PID: $SERVER_PID"
#         kill -TERM $SERVER_PID
#         wait $SERVER_PID 2>/dev/null || true
#         unset SERVER_PID
#     else
#         echo "No server running"
#     fi
# }

# start_server
newman run forum_multiple_posts.postman_collection.json -e env.json
newman run forum_post_read_delete.postman_collection.json 
newman run forum_sample_tests.postman_collection.json -e env.json
# stop_server