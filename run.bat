@echo off

start cmd /k "cd Server && python transcribe.py"

start cmd /k "cd Website && http-server -p 8080 -c-1"