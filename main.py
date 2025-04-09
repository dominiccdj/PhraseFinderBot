import requests
from bs4 import BeautifulSoup
import schedule
import time
import logging
import sys
from datetime import datetime
import pytz
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Get environment variables with defaults
URL = os.getenv('URL', 'placeholderURL')
SEARCH_PHRASE = os.getenv('SEARCH_PHRASE', 'placeholderSearchPhrase')
RECIPIENT_TOKEN = os.getenv('RECIPIENT_TOKEN', 'placeholderToken')
MIN_OCCURRENCES = int(os.getenv('MIN_OCCURRENCES', '1'))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # Minutes between checks

# Configure requests with retry mechanism
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

# Common browser user agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'
]

def get_headers():
    """Generate headers that mimic a real browser."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

def download_and_search(url, sentence, min_occurrences, timeout=30):
    try:
        # Add a small random delay to appear more human-like
        time.sleep(random.uniform(1, 3))
        
        # Use proper headers
        headers = get_headers()
        
        # Make the request
        response = session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        occurrences = text.count(sentence)
        
        return occurrences >= min_occurrences, occurrences
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None, 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None, 0

def send_telepush_message(recipient_token, message):
    try:
        url = f"https://telepush.dev/api/messages/{recipient_token}"
        data = {"text": message}
        response = session.post(url, json=data, timeout=10)
        response.raise_for_status()
        logger.info("Message sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False

def run_job():
    logger.info(f"Checking for '{SEARCH_PHRASE}' at {URL}")
    found, occurrences = download_and_search(URL, SEARCH_PHRASE, MIN_OCCURRENCES)
    
    if found is True:
        logger.info(f"The phrase '{SEARCH_PHRASE}' was found {occurrences} times.")
        message = f"The phrase '{SEARCH_PHRASE}' was found {occurrences} times on {URL}."
        send_telepush_message(RECIPIENT_TOKEN, message)
        return schedule.CancelJob  # This will stop the job from running again
    elif found is False:
        logger.info(f"The phrase '{SEARCH_PHRASE}' was found {occurrences} times, which is less than the minimum required.")
    else:
        error_msg = f"Failed to check the webpage {URL}"
        logger.error(error_msg)
        send_telepush_message(RECIPIENT_TOKEN, f"ERROR: {error_msg}")

# Log configuration
logger.info(f"Configuration: URL={URL}, SEARCH_PHRASE='{SEARCH_PHRASE}', MIN_OCCURRENCES={MIN_OCCURRENCES}, CHECK_INTERVAL={CHECK_INTERVAL} minutes")

# Initial notification
if send_telepush_message(RECIPIENT_TOKEN, f"Monitoring app started. Checking {URL} for '{SEARCH_PHRASE}'"):
    logger.info("App started and initial notification sent.")
else:
    logger.warning("App started but failed to send initial notification.")

# Run the job immediately once
run_job()

# Schedule the job to run at the specified interval
schedule.every(CHECK_INTERVAL).minutes.do(run_job)

# Keep the scheduler running
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")
        send_telepush_message(RECIPIENT_TOKEN, "Monitoring app stopped.")
        break
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        send_telepush_message(RECIPIENT_TOKEN, f"ERROR: Scheduler error: {e}")
        time.sleep(60)
