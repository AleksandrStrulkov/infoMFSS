from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def csrf_failure(request: HttpRequest, reason: str = "") -> HttpResponse:
    """Show a safe recovery page without exposing CSRF rejection details."""
    return render(request, "403_csrf.html", status=403)
