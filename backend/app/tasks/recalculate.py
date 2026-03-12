"""Celery task for strategy recalculation.

Periodically recalculates anti-vote strategies when new polling data
arrives or when triggered manually.  When a recommendation changes for
a region, queues notifications to subscribed users (spec section 3.3).
"""

import logging

from app.tasks import celery_app
from app.data.regions import REGIONS
from app.services.anti_vote import (
    DEFAULT_POLL_PERCENTAGES,
    percentages_to_votes,
)
from app.services.dhondt import dhondt_method
from app.services import web_push

logger = logging.getLogger(__name__)

# Cache of the last computed allocations keyed by region slug.
# Used to detect when a recommendation has changed so we only
# notify users about meaningful updates.
_previous_allocations: dict[str, dict[str, int]] = {}


@celery_app.task(name="recalculate_all_regions", bind=True, max_retries=3)
def recalculate_all_regions(self):
    """Recalculate seat allocations for all regions with current poll data.

    This task runs periodically to keep cached results fresh.
    When an allocation changes relative to the previous run it queues
    notifications for subscribed users.

    Returns a summary of allocations per region.
    """
    results = {}
    changed_regions: list[str] = []
    votes = percentages_to_votes(DEFAULT_POLL_PERCENTAGES)

    for region in REGIONS:
        slug = region["slug"]
        seats = region["seats_diputados"]

        try:
            allocation = dhondt_method(votes, seats)
            # Only keep parties that won seats
            filtered = {p: s for p, s in allocation.items() if s > 0}
            results[slug] = {
                "region": region["name"],
                "seats": seats,
                "allocation": filtered,
            }

            # Detect changes from previous run
            prev = _previous_allocations.get(slug)
            if prev is not None and prev != filtered:
                changed_regions.append(slug)
                logger.info(
                    "Allocation changed for %s: %s -> %s",
                    slug,
                    prev,
                    filtered,
                )
            _previous_allocations[slug] = filtered

        except Exception as exc:
            results[slug] = {"error": str(exc)}

    # Queue notifications for changed regions
    if changed_regions:
        _notify_strategy_changes(changed_regions, results)

    return {
        "status": "completed",
        "regions_processed": len(REGIONS),
        "regions_changed": changed_regions,
        "results": results,
    }


@celery_app.task(name="recalculate_region", bind=True, max_retries=3)
def recalculate_region(self, region_slug: str):
    """Recalculate seat allocation for a single region.

    Args:
        region_slug: The slug of the region to recalculate.
    """
    region = next((r for r in REGIONS if r["slug"] == region_slug), None)
    if not region:
        return {"error": f"Region '{region_slug}' not found"}

    votes = percentages_to_votes(DEFAULT_POLL_PERCENTAGES)
    allocation = dhondt_method(votes, region["seats_diputados"])

    return {
        "region": region["name"],
        "seats": region["seats_diputados"],
        "allocation": {p: s for p, s in allocation.items() if s > 0},
    }


def _notify_strategy_changes(
    changed_regions: list[str],
    results: dict,
) -> None:
    """Send push notifications to subscribed users about strategy changes.

    For now this iterates over all subscriptions and sends a generic
    notification.  A production implementation would match users to
    their saved region preferences and only notify about relevant
    changes.
    """
    subscriptions = web_push.get_all_subscriptions()
    if not subscriptions:
        logger.info(
            "Strategy changed in %d region(s) but no push subscribers",
            len(changed_regions),
        )
        return

    region_names = []
    for slug in changed_regions:
        entry = results.get(slug, {})
        region_names.append(entry.get("region", slug))

    title = "VotoClaro: cambio en estrategia"
    body = (
        f"La recomendacion de voto cambio en: {', '.join(region_names)}. "
        "Revisa tu simulador para ver la nueva estrategia."
    )

    sent = 0
    for user_id in subscriptions:
        ok = web_push.send_push_notification(
            user_id=user_id,
            title=title,
            body=body,
            url="/simulador",
        )
        if ok:
            sent += 1

    logger.info(
        "Notified %d/%d subscribers about changes in %s",
        sent,
        len(subscriptions),
        changed_regions,
    )
