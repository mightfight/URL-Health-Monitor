# URL Health Checker

A simple command-line tool to check the health and availability of websites.

## Features

- Checks multiple URLs simultaneously
- Shows status codes and response times
- Color-coded output for easy reading
- Handles HTTP and HTTPS protocols
- Timeout protection
- Error handling for failed requests

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python url_health_checker.py [URL1] [URL2] ...
```

Example:
```bash
python url_health_checker.py google.com example.com
```

The output will show:
- URL being checked
- HTTP status code (colored green for success, red for errors)
- Response time in milliseconds
- Any error messages if applicable
