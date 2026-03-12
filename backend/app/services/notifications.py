"""Notification service for VotoClaro.

WhatsApp share message generators matching spec section 2.1.
"""

from urllib.parse import quote

from app.config import settings


def generate_whatsapp_url(message: str) -> str:
    """Generate a WhatsApp share URL."""
    encoded = quote(message, safe="")
    return f"https://api.whatsapp.com/send?text={encoded}"


def build_anti_vote_share_message(
    recommended_party: str,
    region_name: str,
    seats_saved: int = 0,
    rejected_label: str = "",
) -> str:
    """Spec 2.1: Anti-vote share message."""
    rejected = rejected_label or "los que no quieres"
    return (
        f"🗳️ *VotoClaro* — Que la ignorancia no gane las elecciones\n\n"
        f"En *{region_name}*, si no quieres que {rejected} tenga curules, "
        f"tu voto más estratégico es por *{recommended_party}*.\n\n"
        f"⚠️ Viciar tu voto les AYUDA a los que no quieres.\n\n"
        f"Simula tu voto acá 👉 {settings.FRONTEND_URL}/simulador"
    )


def build_quiz_share_message(
    top_party: str,
    match_percentage: float,
) -> str:
    """Spec 2.1: Quiz result share message."""
    return (
        f"🎯 Hice el test de VotoClaro y coincido {match_percentage}% "
        f"con *{top_party}*.\n\n"
        f"¿Con quién coincides tú? 👉 {settings.FRONTEND_URL}/quiz\n\n"
        f"_Que la ignorancia no gane las elecciones_ 🇵🇪"
    )


def build_fact_share_message(fact_text: str) -> str:
    """Spec 2.1: Shareable fact message."""
    return (
        f"🔥 ¿Sabías que {fact_text}?\n\n"
        f"Descubre más datos que los candidatos no quieren "
        f"que sepas 👉 {settings.FRONTEND_URL}/sabias-que\n\n"
        f"_VotoClaro — Que la ignorancia no gane las elecciones_ 🇵🇪"
    )
