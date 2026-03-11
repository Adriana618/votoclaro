"""Notification service for VotoClaro.

Handles generation of WhatsApp share URLs and notification messages.
"""

from urllib.parse import quote

from app.config import settings


def generate_whatsapp_url(message: str) -> str:
    """Generate a WhatsApp share URL with the given message.

    Args:
        message: The text message to share.

    Returns:
        WhatsApp API URL for sharing.
    """
    encoded = quote(message, safe="")
    return f"https://api.whatsapp.com/send?text={encoded}"


def build_anti_vote_share_message(
    recommended_party: str,
    region_name: str,
    seats_saved: int,
) -> str:
    """Build a shareable message for anti-vote results.

    Args:
        recommended_party: Name of the recommended party.
        region_name: Name of the region.
        seats_saved: Number of seats saved from rejected parties.

    Returns:
        Formatted share message.
    """
    msg = (
        f"🗳️ Segun VotoClaro, en {region_name} puedo quitar "
        f"{seats_saved} escano(s) a los partidos que rechazo "
        f"votando por {recommended_party}.\n\n"
        f"Calcula tu voto estrategico en {settings.BASE_URL}"
    )
    return msg


def build_quiz_share_message(
    top_party: str,
    match_percentage: float,
) -> str:
    """Build a shareable message for quiz results.

    Args:
        top_party: Name of the top matching party.
        match_percentage: Match percentage with that party.

    Returns:
        Formatted share message.
    """
    msg = (
        f"🧭 Segun el quiz de VotoClaro, mi mayor afinidad "
        f"ideologica es con {top_party} ({match_percentage}%).\n\n"
        f"¿Y tu? Descubrelo en {settings.BASE_URL}/quiz"
    )
    return msg


def build_fact_share_message(fact_text: str) -> str:
    """Build a shareable message for a fact.

    Args:
        fact_text: The fact text.

    Returns:
        Formatted share message.
    """
    msg = (
        f"📊 ¿Sabias que...?\n\n{fact_text}\n\n"
        f"Mas datos en {settings.BASE_URL}"
    )
    return msg
