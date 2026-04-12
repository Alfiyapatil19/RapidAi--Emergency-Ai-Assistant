"""
RapidAid - SMS Notification Service
Uses Twilio API to send real panic alerts.
"""

import os
import logging
from twilio.rest import Client

logger = logging.getLogger(__name__)

# Load environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")


def send_panic_sms(contacts: list, sender_name: str, user_location: str = "") -> dict:
    """
    Send panic alert SMS using Twilio
    """

    if not contacts:
        return {"success": False, "message": "No contacts to alert.", "results": []}

    message_body = (
        f"🚨 EMERGENCY ALERT!\n"
        f"{sender_name} needs help immediately!\n"
        f"{'Location: ' + user_location if user_location else ''}\n"
        f"Call them or dial 108."
    )
    
    logger.info(f"--- SMS BEING SENT ---\n{message_body}\n----------------------")

    results = []

    # ❌ If credentials missing → simulation
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        logger.warning("Twilio not configured. Running in simulation mode.")
        for c in contacts:
            results.append({
                "name": c["name"],
                "phone": c["phone"],
                "status": "simulated",
                "message": "SMS simulated (Twilio not configured)"
            })
        return {
            "success": True,
            "simulated": True,
            "message": "Simulation mode — add Twilio credentials",
            "results": results
        }

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        for c in contacts:
            try:
                msg = client.messages.create(
                    body=message_body,
                    from_=TWILIO_PHONE_NUMBER,
                    to=format_phone(c["phone"])
                )

                results.append({
                    "name": c["name"],
                    "phone": c["phone"],
                    "status": "sent",
                    "sid": msg.sid
                })

            except Exception as e:
                results.append({
                    "name": c["name"],
                    "phone": c["phone"],
                    "status": "failed",
                    "message": str(e)
                })

        return {
            "success": True,
            "simulated": False,
            "message": f"Sent to {len(contacts)} contacts",
            "results": results
        }

    except Exception as e:
        logger.error(f"Twilio error: {e}")
        return {
            "success": False,
            "message": str(e),
            "results": []
        }


def format_phone(phone: str) -> str:
    """
    Convert phone to international format (+91...)
    """
    digits = "".join(filter(str.isdigit, phone))

    if not digits.startswith("91"):
        digits = "91" + digits

    return "+" + digits