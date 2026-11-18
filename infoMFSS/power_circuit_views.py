from __future__ import annotations

from dataclasses import asdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.views.generic import TemplateView

from infoMFSS.power_circuit import SchemaUnavailableError, list_schemas, read_schema


class PowerCircuitView(LoginRequiredMixin, TemplateView):
    template_name = "infoMFSS/power_circuit.html"


class PrivateSchemaView(LoginRequiredMixin, View):
    """Prevent caches from retaining both JSON responses and login redirects."""

    http_method_names = ["get", "head", "options"]

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        response = super().dispatch(request, *args, **kwargs)
        response["Cache-Control"] = "private, no-store"
        return response


class PowerCircuitCatalogView(PrivateSchemaView):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"schemas": [asdict(entry) for entry in list_schemas()]})


class PowerCircuitSchemaView(PrivateSchemaView):
    def get(self, request: HttpRequest, mine_dir: str, filename: str) -> JsonResponse:
        try:
            schema = read_schema(mine_dir, filename)
        except SchemaUnavailableError as error:
            raise Http404("Схема не найдена") from error
        return JsonResponse(schema)
