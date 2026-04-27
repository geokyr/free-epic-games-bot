import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
EPIC_API_URL = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=GR&allowCountries=GR"
)


def get_free_games():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(EPIC_API_URL, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return []

    data = response.json()
    games = data["data"]["Catalog"]["searchStore"]["elements"]
    free_games = []

    for game in games:
        price_info = game.get("price", {}).get("totalPrice", {})
        discount_price = price_info.get("discountPrice", -1)

        promotions = game.get("promotions", {})
        if not promotions:
            continue

        promotional_offers = promotions.get("promotionalOffers", [])

        if promotional_offers and discount_price == 0:
            title = game.get("title")
            description = game.get("description")

            images = game.get("keyImages", [])
            image_url = ""
            for img in images:
                if img["type"] == "OfferImageWide":
                    image_url = img["url"]
                    break

            page_slug = ""
            catalog_ns = game.get("catalogNs", {}).get("mappings", [])
            if catalog_ns:
                page_slug = catalog_ns[0].get("pageSlug", "")

            if not page_slug:
                offer_mappings = game.get("offerMappings", [])
                if offer_mappings:
                    page_slug = offer_mappings[0].get("pageSlug", "")

            if not page_slug:
                page_slug = game.get("productSlug") or game.get("urlSlug") or ""

            game_url = (
                f"https://store.epicgames.com/en-US/p/{page_slug}"
                if page_slug
                else "https://store.epicgames.com/en-US/free-games"
            )

            free_games.append(
                {"title": title, "description": description, "image_url": image_url, "game_url": game_url}
            )

    return free_games


def send_email(games):
    if not games:
        print("No free games found to email.")
        return

    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECEIVER_EMAIL:
        print("Missing email configuration environment variables.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "New Free Epic Games Available!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    html_content = """
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Here are your free Epic Games for the week!</h2>
        <hr>
    """

    for game in games:
        game_url = game.get("game_url", "https://store.epicgames.com/en-US/free-games")
        html_content += f"<h3 style='color: #0078F2;'><a href='{game_url}' style='color: #0078F2; text-decoration: none;'>{game['title']}</a></h3>"
        html_content += f"<p>{game['description']}</p>"
        if game["image_url"]:
            html_content += (
                f"<a href='{game_url}'><img src='{game['image_url']}' width='400' style='border-radius: 8px;'></a><br>"
            )
        html_content += f"<p><a href='{game_url}' style='display: inline-block; padding: 10px 15px; background-color: #0078F2; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;'>Claim {game['title']}</a></p><br><br>"

    html_content += """
        <hr>
        <p><a href="https://store.epicgames.com/en-US/free-games" style="color: #0078F2;">View all free games on the Epic Games Store</a></p>
      </body>
    </html>
    """

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        print("Connecting to email server...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    print("Fetching games...")
    current_free_games = get_free_games()

    print(f"Found {len(current_free_games)} free games:")
    for game in current_free_games:
        print(f"- {game['title']}")

    send_email(current_free_games)
