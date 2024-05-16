@echo off

start cmd /k "cd Server && node server.js"

start cmd /k "cd Website && http-server -p 8080 -c-1"

open http://localhost:8080