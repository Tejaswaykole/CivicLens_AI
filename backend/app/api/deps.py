"""Shared route dependencies."""

from fastapi import Query

from app.schemas.common import PageParams


def pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)
