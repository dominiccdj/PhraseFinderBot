# PhraseFinderBot
PhraseFinderBot is an automated web monitoring tool that scans specified websites for phrases and sends Telegram(Telepush https://telepush.dev/) notifications when they're found.

## Features
- Configurable Monitoring: Set any URL and search phrase via environment variables
- Smart Detection: Count occurrences of phrases and set minimum thresholds
- Instant Notifications: Get alerts via Telegram(Telepush) when phrases are detected
- Anti-Detection Measures: Mimics real browser behavior to avoid being blocked
- Docker Ready: Easy deployment with included Dockerfile and docker-compose.yml

## Quick Start
### Using Docker
```
docker run -d --name phrase-finder-bot \
  -e URL="https://example.com/jobs" \
  -e SEARCH_PHRASE="Software Engineer" \
  -e RECIPIENT_TOKEN="your-telepush-token" \
  -e MIN_OCCURRENCES="1" \
  -e CHECK_INTERVAL="60" \
  dominiccdj/phrasefinderbot:v1
```
### Using Docker Compose
Create a docker-compose.yml file:
```
version: '3.8'

services:
  phrase-finder:
    image: dominiccdj/phrasefinderbot:v1
    container_name: phrase-finder-bot
    restart: unless-stopped
    environment:
      - URL=https://example.com/jobs
      - SEARCH_PHRASE=Software Engineer
      - RECIPIENT_TOKEN=your-telegram-token
      - MIN_OCCURRENCES=1
      - CHECK_INTERVAL=60
```
Run with:
```
docker-compose up -d
```
## Configuration
|Environment Variable |	Description |	Default |
| ------------------- | ----------- | ------- |
|URL |	Website URL to monitor |	None |
|SEARCH_PHRASE |	Phrase to search for |	None |
|RECIPIENT_TOKEN |	Telegram(Telepush) token for notifications |	None |
|MIN_OCCURRENCES |	Minimum occurrences required |	1 |
|CHECK_INTERVAL |	Minutes between checks |	60 |

## How It Works
The bot periodically checks the specified URL for the search phrase

When the phrase is found at least the minimum number of times, a notification is sent

The bot automatically stops checking once the phrase is found

Browser-like headers are used to avoid being blocked by websites

## Development
Prerequisites
- Python 3.9+
- pip
- Telepush token https://telepush.dev/ 

Setup
Clone the repository:
```
git clone https://github.com/dominiccdj/phrasefinderbot.git
cd phrasefinderbot
```
Install dependencies:
```
pip install -r requirements.txt
```
Create a .env file with your configuration

Run the application:
```
python main.py
```
## License
MIT

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
