"""Open Graph image generation endpoints for WhatsApp link previews."""

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.services.og_image import generate_anti_vote_image, generate_quiz_image

router = APIRouter(prefix="/og", tags=["og"])


@router.get("/anti-vote")
async def og_anti_vote(
    region: str = Query(..., description="Region name"),
    rejected: str = Query(..., description="Rejected party/candidate"),
    recommended: str = Query(..., description="Recommended party/candidate"),
):
    """Generate an Open Graph image (1200x630) for anti-vote WhatsApp sharing."""
    png_bytes = generate_anti_vote_image(
        region=region,
        rejected=rejected,
        recommended=recommended,
    )
    return Response(content=png_bytes, media_type="image/png")


@router.get("/quiz")
async def og_quiz(
    match: str = Query(..., description="Matching party/candidate name"),
    percent: float = Query(..., description="Match percentage"),
):
    """Generate an Open Graph image (1200x630) for quiz result WhatsApp sharing."""
    png_bytes = generate_quiz_image(
        match=match,
        percent=percent,
    )
    return Response(content=png_bytes, media_type="image/png")
