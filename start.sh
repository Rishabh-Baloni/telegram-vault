#!/bin/bash
# Keep the service alive by running a simple HTTP server alongside the bot
python -m http.server 8080 & python run.py
