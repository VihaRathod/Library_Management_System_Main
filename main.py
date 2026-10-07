from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.settings import settings

from middleware.auth_middleware import AuthMiddleware
from middleware.rate_limit import RateLimitMiddleware

from routers.reports import router as reports_router
from routers.auth import router as auth_router
from routers.books import router as books_router
from routers.courses import router as courses_router
from routers.loans import router as loans_router
from routers.receipt import router as receipt_router
from routers.author import router as author_router
from scheduler.scheduler import (
    start_scheduler,
    stop_scheduler
)
from routers.user import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Start scheduler
    start_scheduler()

    yield

    # Stop scheduler
    stop_scheduler()


app = FastAPI(
    lifespan=lifespan
)


# Authentication middleware
app.add_middleware(
    AuthMiddleware
)


# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_limit=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
    auth_requests_limit=settings.auth_rate_limit_requests,
    auth_window_seconds=settings.auth_rate_limit_window_seconds
)


app.include_router(auth_router)
app.include_router(books_router)
app.include_router(courses_router)
app.include_router(loans_router)
app.include_router(receipt_router)
app.include_router(reports_router)
app.include_router(author_router)
app.include_router(users_router)