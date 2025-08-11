#!/bin/bash

# Screens
SCREEN_MAIN="goflow"
SCREEN_WEBUI="goflow-webui"

# Paths
SCRIPT_MAIN="gfsys.py"
SCRIPT_WEBUI="gfwebui:app"

# Start the main script
screen -dmS $SCREEN_MAIN bash -c "python3 $SCRIPT_MAIN; exec bash"

# Start the webui/api
screen -dmS $SCREEN_WEBUI bash -c "gunicorn $SCRIPT_WEBUI; exec bash"

echo "GoFlow is running in these screens:"
echo "- $SCREEN_MAIN"
echo "- $SCREEN_WEBUI"
