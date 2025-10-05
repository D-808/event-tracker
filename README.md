# Ticketmaster Event Tracker

A Python tool to track upcoming events and concerts using the ticketmaster Discovery API.

## what does it do?
- Search events by country and city
- Automatically fetches events for the next 14 days
- Exports results to JSON
- Supports all Ticketmaster regions worldwide

## Prerequisites

- Python 3.6+
- Ticketmaster API key (obtain a free key at [developer.ticketmaster.com](https://developer.ticketmaster.com/))
- This was only tested on MacOS env.

## Installation

```bash
pip install requests
```

Follow the prompts:
1. Enter your Ticketmaster API key
2. Enter country code (e.g., `NL`, `US`, `GB`)
3. Enter city name (optional)

Results are saved locally in .json format


[Country Code list](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)

## API ticketmaster limits

- Free tier: 5,000 requests/day
- Max 200 events per request
- Rate limit: 5 requests/second

## License
MIT