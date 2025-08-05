#!/bin/bash

if [ -z "$DISCORD_BOT_TOKEN" ]; then
    echo "Error: DISCORD_BOT_TOKEN environment variable is not set"
    echo "Please set it with: export DISCORD_BOT_TOKEN='your_token_here'"
    exit 1
fi

echo "Starting RankBot..."
/home/pxnity/Code/Python/RankBot/rankbotenv/bin/python /home/pxnity/Code/Python/RankBot/bot.py
