#!/bin/bash

# Run the Flask app in the background and redirect output to a log file
# nohup python3 app.py > flask_app.log 2>&1 &
nohup python app.py 
