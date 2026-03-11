"""Main router aggregating all API sub-routers."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.candidates import router as candidates_router
from app.api.parties import router as parties_router
from app.api.quiz import router as quiz_router
from app.api.regions import router as regions_router
from app.api.share import router as share_router
from app.api.simulator import router as simulator_router
from app.api.trends import router as trends_router

api_router = APIRouter(prefix="/api")

api_router.include_router(simulator_router)
api_router.include_router(quiz_router)
api_router.include_router(parties_router)
api_router.include_router(candidates_router)
api_router.include_router(regions_router)
api_router.include_router(auth_router)
api_router.include_router(share_router)
api_router.include_router(trends_router)
