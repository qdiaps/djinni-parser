# Djinni Vanancy Monitor & Notifier

> [!IMPORTANT]
> **Disclaimer:** This tool is for educational purposes only. Please respect the website's terms of service and robots.txt.

An automated bot for monitoring the number of vacancies on the [Djinni.co](https://djinni.co) website. The script parses data daily from multiple search URLs defined in the configuration, saves the history in Google Sheets, and sends a detailed report to Telegram.

## Table of Contents
- [Functionality](#functionality)
- [Preliminary preparation](#preliminary-preparation)
  - [Configuring Google Cloud Console](#configuring-google-cloud-console)
  - [Creating a Telegram bot](#creating-a-telegram-bot)
  - [Preparing Google Sheets](#preparing-google-sheets)
- [Installation and startup](#installation-and-startup)
- [Configuration](#configuration)
  - [Environment Variables (.env)](#environment-variables-env)
  - [URLs Configuration (config.json)](#urls-configuration-configjson)
  - [Advanced: Custom Systemd Configuration](#advanced-custom-systemd-configuration)
- [Problem solving](#problem-solving)

## Functionality
1. Collects the number of vacancies from multiple URLs specified in a JSON configuration file.
2. Saves the date and vacancy counts for each category in Google Sheets.
3. Sends a daily summary to Telegram. Example:
```text
📊 Daily Report
All Vacancies: 238
DevOps: 102
```
4. Runs in the background via `systemd` (timer set to `12:00` daily).
5. Includes the Bash script install.sh for automatic configuration of the environment, dependencies, and services.

## Preliminary preparation
Before installing the code, you need to obtain API keys.

### Configuring Google Cloud Console
You need a service account to work with tables.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. In the `APIs & Services > Library` section, find and enable two APIs:
    - Google Sheets API
    - Google Drive API
4. In the `Credentials` section, click `Create Credentials > Service Account`.
5. Fill in your name and click `Create`. Select the role `Editor`.
6. Click on the created service account email, go to the `Keys > Add Key > Create new key > JSON`.
7. The file will download to your computer. Rename it to `creds.json` and save it - you'll need it later.

### Creating a Telegram bot
1. Write to [@BotFather](https://t.me/BotFather) on Telegram.
2. Command `/newbot` > Come up with a name.
3. Get a `Token`.
4. Find out your `Chat ID` (you can do this via the [@userinfobot](https://t.me/userinfobot) bot).

### Preparing Google Sheets
1. Create a new Google Sheet.
2. **Important:** The script relies on column names to map data. In the first line, create headings manually:
    - Cell A1: `Date` (matches the `DATE_COLUMN_NAME` variable).
    - Subsequent Cells: create columns for each category you plan to track. Their names `must match` the `name` fields in your `config.json` (e.g., `All Vacancies`, `DevOps`).
3. Click the `Share` button.
4. Enter the email address for your service account (from step 1, it looks like `bot@project.iam.gserviceaccount.com`) and grant **Editor** permissions.

## Installation and startup
The project is designed to run on `Linux` (Ubuntu/Debian) using `Systemd`.

1. Clone the repository:
```bash
git clone https://github.com/qdiaps/djinni-parser.git
cd djinni-parser
```
2. Add keys:
    - Copy your `creds.json` file to the root of your project folder.
    - Create an `.env` file and `config.json` (see the [Configuration](#configuration) section).
3. Run the automatic installation. The script will create a virtual environment, install libraries, and configure autostart via systemd:
```bash
chmod +x install.sh
./install.sh
```
4. Follow the instructions on the screen.

## Configuration
### Environment Variables (.env)
Create an `.env` file based on the example:
```bash
cp .env.example .env
```

Description of variables:
| Variable | Description | Example |
| --- | --- | --- |
| `BOT_TOKEN` | Token from [@BotFather](https://t.me/BotFather) | `1234567890:ABCDEFgHIJKLmNOPQrstUvwXYZ` |
| `CHAT_ID` | Your Telegram chat ID | `987654321` |
| `SHEET_NAME` | Name of the Google Sheet | `Vacancies` |
| `CREDS_PATH` | Path to the `creds.json` file | Filled in automatically via `install.sh` |
| `DATE_COLUMN_NAME` | Name of the column for dates | `Date` |
| `URLS_CONFIG_PATH` | Path to the JSON config | `config.json` |

### URLs Configuration (config.json)
This file defines which URLs to parse. Create `config.json` in the project root:
```bash
cp config.json.example config.json
```
Format:
```json
[
  {
    "name": "All Vacancies",
    "url": "https://djinni.co/jobs"
  },
  {
    "name": "DevOps",
    "url": "https://djinni.co/jobs/?primary_keyword=DevOps"
  }
]
```
**Note:** The `name` field must match the column header in your Google Sheet.

### Advanced: Custom Systemd Configuration
By default, `install.sh` generates standard configuration files (runs daily at 12:00). If you want to customize the schedule or service parameters (e.g., run every hour), you can provide your own systemd files.

1. Create files named `djinni_parser.service` and `djinni_parser.timer` in the project root **before** running the installer.
2. The installer will detect these files and use them instead of the defaults.

**Template for `djinni_parser.timer` (e.g., run at 09:00):**
```ini
[Unit]
Description=Run Djinni Parser Daily at 09:00

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true
Unit=djinni_parser.service

[Install]
WantedBy=timers.target
```
**Template for `djinni_parser.service`:**
> [!NOTE]
> When using custom files, you must provide `absolute paths` to your project and python executable inside `.venv`.
```ini
[Unit]
Description=Djinni Parser Service
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/your_user/djinni-parser
ExecStart=/home/your_user/djinni-parser/.venv/bin/python /home/your_user/djinni-parser/main.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

## Problem solving
1. **The script is not working, the timer is not starting.** Check the service status:
```bash
systemctl --user status djinni_parser.service
```
Check the logs (the cause of the error will be there):
```bash
journalctl --user -u djinni_parser.service
```
2. **"Google Sheets API Error" error.** Make sure you have added the service bot's email (from `creds.json`) to your spreadsheet's access settings as an `Editor`.
3. **"Spreadsheet is missing columns" error.** Ensure that every `name` in your `config.json` corresponds to a column header in your Google Sheet.
3. **How do I change the start time?** Edit the timer file:
```bash
nano ~/.config/systemd/user/djinni_parser.timer
```
After making changes, be sure to update the configuration:
```bash
systemctl --user daemon-reload
systemctl --user restart djinni_parser.timer
```
