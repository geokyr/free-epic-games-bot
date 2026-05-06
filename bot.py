import logging
import os
import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

EPIC_API_URL = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=GR&allowCountries=GR"
)
DEFAULT_GAME_URL = "https://store.epicgames.com/en-US/free-games"


@dataclass
class FreeGame:
    title: str
    description: str
    image_url: str
    game_url: str


def _extract_game_slug(game: dict) -> str:
    """Helper to extract the page slug from deeply nested Epic API response."""
    mappings = game.get("catalogNs", {}).get("mappings", [])
    if mappings and mappings[0].get("pageSlug"):
        return mappings[0]["pageSlug"]

    offer_mappings = game.get("offerMappings", [])
    if offer_mappings and offer_mappings[0].get("pageSlug"):
        return offer_mappings[0]["pageSlug"]

    return game.get("productSlug") or game.get("urlSlug") or ""


def _extract_image_url(images: list[dict]) -> str:
    """Helper to find the wide offer image from the image list."""
    for img in images:
        if img.get("type") == "OfferImageWide":
            return img.get("url", "")
    return ""


def _build_email_html(games: list[FreeGame]) -> str:
    """Generates the HTML content for the email."""
    html_parts = [
        "<html>",
        "<body style='font-family: Arial, sans-serif; color: #333;'>",
        "<h2>Here are your free Epic Games for the week!</h2>",
        "<hr>",
    ]

    for game in games:
        html_parts.extend(
            [
                f"<h3 style='color: #0078F2;'><a href='{game.game_url}' style='color: #0078F2; text-decoration: none;'>{game.title}</a></h3>",
                f"<p>{game.description}</p>",
            ]
        )
        if game.image_url:
            html_parts.append(
                f"<a href='{game.game_url}'><img src='{game.image_url}' width='400' style='border-radius: 8px;'></a><br>"
            )

        html_parts.append(
            f"<p><a href='{game.game_url}' style='display: inline-block; padding: 10px 15px; background-color: #0078F2; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;'>Claim {game.title}</a></p><br><br>"
        )

    html_parts.extend(
        [
            "<hr>",
            f"<p><a href='{DEFAULT_GAME_URL}' style='color: #0078F2;'>View all free games on the Epic Games Store</a></p>",
            "</body>",
            "</html>",
        ]
    )

    return "".join(html_parts)


def get_free_games() -> list[FreeGame]:
    """Fetches and parses currently free games from the Epic Games API."""
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(EPIC_API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from Epic API: {e}")
        return []

    games_data = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
    free_games = []

    for game in games_data:
        price = game.get("price") or {}
        total_price = price.get("totalPrice") or {}
        discount_price = total_price.get("discountPrice", -1)

        promotions = game.get("promotions") or {}
        promotional_offers = promotions.get("promotionalOffers") or []

        if promotional_offers and discount_price == 0:
            title = game.get("title", "Unknown Title")
            description = game.get("description", "No description available.")

            image_url = _extract_image_url(game.get("keyImages", []))
            page_slug = _extract_game_slug(game)

            game_url = f"https://store.epicgames.com/en-US/p/{page_slug}" if page_slug else DEFAULT_GAME_URL

            free_games.append(FreeGame(title, description, image_url, game_url))

    return free_games


def send_email(games: list[FreeGame], sender_email: str, sender_password: str, receiver_email: str) -> None:
    """Constructs and sends the email notification."""
    if not games:
        logging.info("No free games found to email.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "New Free Epic Games Available!"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    html_content = _build_email_html(games)
    msg.attach(MIMEText(html_content, "html"))

    try:
        logging.info("Connecting to email server...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logging.info("Email sent successfully!")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending email: {e}")


def main():
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL")

    if not all([sender_email, sender_password, receiver_email]):
        logging.error("Missing required email environment variables. Exiting.")
        return

    logging.info("Fetching games from Epic Games API...")
    current_free_games = get_free_games()

    if not current_free_games:
        logging.info("No free games to process at this time.")
        return

    logging.info(f"Found {len(current_free_games)} free games:")
    for game in current_free_games:
        logging.info(f" - {game.title}")

    send_email(current_free_games, sender_email, sender_password, receiver_email)


if __name__ == "__main__":
    main()
