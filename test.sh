#!/bin/sh

set -e # exit immediately if newman complains
trap 'kill $SERVER_PID' EXIT # kill the server on exit

./run.sh &
SERVER_PID=$!

newman run forum_multiple_posts.postman_collection.json -e env.json
newman run forum_post_read_delete.postman_collection.json 
# newman run forum_sample_tests.postman_collection.json -e env.json

