# Free Epic Games Bot

A lightweight Python bot that fetches the current free games from the Epic Games Store and sends a formatted HTML email with claim links.

To run the bot a GitHub workflow is provided. It can be triggered through cron-job.org using a GitHub `repository_dispatch` event, and it can also be run manually with `workflow_dispatch`.

## Features

- Automated fetching from the Epic Games promotions API.
- HTML email notifications with game title, description, image, and claim button.
- Triggered GitHub Actions run via cron-job.org or the manual GitHub Actions run button.

## Environment Variables

Set these values in the environment where the bot runs:

- `SENDER_EMAIL`: Sender email address (for example, a Gmail account).
- `SENDER_PASSWORD`: App password for the sender email.
- `RECEIVER_EMAIL`: Destination email address.

## Running Locally

1. Export/set the required environment variables.
2. Run:

```bash
uv run bot.py
```

## Deployment with GitHub Actions and cron-job.org

To deploy this bot, first fork or clone this repository.

The workflow file is [run_bot.yml](.github/workflows/run_bot.yml).

It supports:
- `repository_dispatch` with event type `trigger-run-bot`
- `workflow_dispatch` for manual runs from GitHub UI

### 1. Add GitHub repository secrets

In your repository, go to **Settings > Secrets and variables > Actions**, then add:

- `SENDER_EMAIL`
- `SENDER_PASSWORD`
- `RECEIVER_EMAIL`

### 2. Create a GitHub Personal Access Token (PAT)

Create a PAT that can trigger repository dispatch events for this repository.

Go to **Settings > Developer settings > Personal access tokens > Fine-grained tokens**. Create a new token, set an expiration date, grant access to this repository only, and enable the Contents permissions (Read and write). When done, copy the generated PAT as you will need it for the next step.

### 3. Configure cron-job.org

Create a new cron-job.org job with:

- URL: `https://api.github.com/repos/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>/dispatches`
- Execution schedule: set a preferred time on Thursday after Epic's weekly refresh at 15:00 UTC
- Advanced > Headers:
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <YOUR_PAT>`
  - `Content-Type: application/json`
- Method: `POST`
- Body:

```json
{
  "event_type": "trigger-run-bot"
}
```

When cron-job.org sends this request, GitHub starts the workflow and the bot runs with your configured secrets.

## Manual Trigger

You can still run the bot manually from **Actions > Run Bot > Run workflow**.
