#!/bin/bash

# Non-production URL
url="https://phwkhyzqsyiqz45zuriob6vnu40ueddp.lambda-url.us-east-1.on.aws/"

# Check for --prod argument
if [ "$1" == "--prod" ]; then
    # Production URL
    url="https://d4ym2c66xyygdt7grr7j2ndzcq0ewjdy.lambda-url.us-east-1.on.aws/"
fi

# Invoke the selected URL with data from data.json
curl -X POST "$url" --data @data.json