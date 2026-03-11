"""Celery task for strategy recalculation.

Periodically recalculates anti-vote strategies when new polling data
arrives or when triggered manually.
"""

from app.tasks import celery_app
from app.data.regions import REGIONS
from app.services.anti_vote import (
    DEFAULT_POLL_PERCENTAGES,
    percentages_to_votes,
)
from app.services.dhondt import dhondt_method


@celery_app.task(name="recalculate_all_regions", bind=True, max_retries=3)
def recalculate_all_regions(self):
    """Recalculate seat allocations for all regions with current poll data.

    This task runs periodically to keep cached results fresh.
    Returns a summary of allocations per region.
    """
    results = {}
    votes = percentages_to_votes(DEFAULT_POLL_PERCENTAGES)

    for region in REGIONS:
        slug = region["slug"]
        seats = region["seats_diputados"]

        try:
            allocation = dhondt_method(votes, seats)
            # Only include parties that got seats
            results[slug] = {
                "region": region["name"],
                "seats": seats,
                "allocation": {p: s for p, s in allocation.items() if s > 0},
            }
        except Exception as exc:
            results[slug] = {"error": str(exc)}

    return {
        "status": "completed",
        "regions_processed": len(REGIONS),
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
