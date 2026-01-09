#!/bin/bash
# Helper script to start the backend server with all required environment variables
# Usage: ./start_server.sh

echo "================================"
echo "Starting A2I2 Backend Server"
echo "================================"

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    # Robustly load KEY=VALUE lines (tolerate whitespace around '=' and ignore blank/comment lines)
    while IFS= read -r line; do
        # Skip comments/blank lines
        [[ -z "$line" ]] && continue
        [[ "$line" =~ ^[[:space:]]*# ]] && continue

        # Normalize whitespace around '=' (e.g., "KEY = VALUE" -> "KEY=VALUE")
        line="$(echo "$line" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//; s/[[:space:]]*=[[:space:]]*/=/')"

        # Export if it looks like KEY=VALUE
        if [[ "$line" == *=* ]]; then
            key="${line%%=*}"
            val="${line#*=}"

            # Strip surrounding quotes (common in .env files)
            if [[ "$val" =~ ^\".*\"$ ]]; then
                val="${val:1:${#val}-2}"
            elif [[ "$val" =~ ^\'.*\'$ ]]; then
                val="${val:1:${#val}-2}"
            fi

            export "${key}=${val}"
        fi
    done < .env
else
    echo "⚠️  No .env file found!"
    echo ""
    echo "Please create a .env file from env.example:"
    echo "  cp env.example .env"
    echo "  # Then edit .env with your actual API keys"
    echo ""
    exit 1
fi

# Check for required environment variables
MISSING_VARS=""

if [ -z "$OPENAI_API_KEY" ]; then
    MISSING_VARS="$MISSING_VARS\n  - OPENAI_API_KEY"
fi

if [ -z "$HUGGINGFACE_TOKEN" ]; then
    MISSING_VARS="$MISSING_VARS\n  - HUGGINGFACE_TOKEN"
fi

if [ -n "$MISSING_VARS" ]; then
    echo "❌ ERROR: Missing required environment variables:"
    echo -e "$MISSING_VARS"
    echo ""
    echo "Please update your .env file with these values."
    echo ""
    echo "Get your tokens from:"
    echo "  - OpenAI: https://platform.openai.com/api-keys"
    echo "  - Hugging Face: https://huggingface.co/settings/tokens"
    echo ""
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "Attempting to activate: /Users/tzhang/projects/A2I2/venv"
    
    if [ -f "/Users/tzhang/projects/A2I2/venv/bin/activate" ]; then
        source /Users/tzhang/projects/A2I2/venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Could not find virtual environment"
        echo "Please activate manually: source /path/to/venv/bin/activate"
        exit 1
    fi
fi

echo ""
echo "✅ Environment variables loaded:"
echo "  - OPENAI_API_KEY: ${OPENAI_API_KEY:0:8}...${OPENAI_API_KEY: -4}"
echo "  - HUGGINGFACE_TOKEN: ${HUGGINGFACE_TOKEN:0:8}...${HUGGINGFACE_TOKEN: -4}"
echo "  - MODEL: ${OPENAI_MODEL:-gpt-4o-mini}"
echo "  - HF_MODEL: ${HUGGINGFACE_MODEL_ID:-tzhang62-iql-fire-rescue-api.hf.space}"
echo ""
echo "Starting server..."
echo ""

# Start the server
python server.py

