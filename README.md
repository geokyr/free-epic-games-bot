# Free Epic Games Bot

A lightweight Python bot that automatically fetches the current free games from the Epic Games Store and sends a nicely formatted HTML email notification with game details and claim links. Designed to run seamlessly on GitHub Actions.

## Features
- **Automated Fetching:** Retrieves the latest free game promotions directly from the Epic Games API.
- **Email Notifications:** Sends an HTML email with game artwork, descriptions, and direct links to claim the games.
- **GitHub Actions Ready:** Perfect for running as a scheduled cron job to keep you updated weekly.

## Setup Requirements

To run the bot, you need to configure the following environment variables:

- `SENDER_EMAIL`: The email address (e.g., Gmail) used to send the notifications.
- `SENDER_PASSWORD`: The app password for the sender email.
- `RECEIVER_EMAIL`: The destination email address to receive the game alerts.

## Running Locally

Set the environment variables and run the script:

```bash
uv run epic_bot.py
```

## Deployment

To deploy this bot on GitHub Actions, follow these steps:

1.  Fork or clone this repository.
2.  Navigate to **Settings > Secrets and variables > Actions**.
3.  Add the following secrets:
    -   `SENDER_EMAIL`
    -   `SENDER_PASSWORD`
    -   `RECEIVER_EMAIL`
4.  Commit and push the changes. The action will run automatically based on the cron schedule defined in `.github/workflows/schedule.yml`.
