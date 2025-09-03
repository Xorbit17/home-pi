from django.http import HttpResponse, FileResponse, HttpResponseServerError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.utils import timezone
from dashboard.models.schedule import Display
from pathlib import Path
from dashboard.models.application import PrerenderedDashboard
from dashboard.models.photos import Variant
from dashboard.constants import IMAGE_DIR
from dashboard.services.select_image import get_variant
from pydantic import BaseModel, ValidationError
from typing import Literal




def _get_file_response(path: str | Path):
    normalisedPath = Path(path)
    if not normalisedPath.exists():
        return HttpResponse(status=404)
    response = FileResponse(open(normalisedPath, "rb"), content_type="image/png")
    response["Cache-Control"] = "no-store"

class IdentityRequestBody(BaseModel):
    mac: str

class DisplayIdentityController(APIView):
    parser_classes = [JSONParser]  # ensure JSON only
    def post(self,request):
        try:
            body = IdentityRequestBody.model_validate(request.data)
        except ValidationError as e:
            return Response(
                {"detail": "Invalid JSON body", "errors": e.errors()},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Display.objects.get(mac=body.mac)
        
        

class ButtonRequestBody(BaseModel):
    button_pressed: Literal["A", "B", "C", "D"]

class DisplayButtonController(APIView):
    permission_classes = [IsAuthenticated]  # BasicAuth via DRF
    parser_classes = [JSONParser]  # ensure JSON only

    def post(self, request):
        display = request.user.display
        display.last_seen = timezone.now()
        display.save(update_fields=["last_seen"])
        try:
            body = ButtonRequestBody.model_validate(request.data)
        except ValidationError as e:
            return Response(
                {"detail": "Invalid JSON body", "errors": e.errors()},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pressed = body.button_pressed
        # Handle

        return Response({"ok": True, "button": pressed}, status=status.HTTP_200_OK)


class DisplayDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        display = request.user.display
        display.last_seen = now
        display.save(update_fields=["last_seen"])
        # Get latest pregenerated dashboad
        try:
            latest = PrerenderedDashboard.objects.latest("created_at")
            if not latest.path:
                raise RuntimeError("Generated dashboard record found but no associated image was generated.")
        except PrerenderedDashboard.DoesNotExist:
            return HttpResponseServerError("No dashboard records exist. Is the generation job running?")
        except RuntimeError as e:
            return HttpResponseServerError(str(e))
        out_path = Path(latest.path)

        response = _get_file_response(out_path)
        if not isinstance(response, FileResponse):
            return response
        # Response is an image
        response["Cache-Control"] = "no-store"
        return response
    
class DisplayVariantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        display = request.user.display
        display.last_seen = now
        display.save(update_fields=["last_seen"])
        try:
            variant = get_variant()
        except:
            return HttpResponseServerError("No variants have been generated. Is the variant creation job running and are source present?")
        if not variant.path:
            return HttpResponseServerError("Variant did not hava path; therefore its generation process failed. Check the variant generation job logs.")
        response = _get_file_response(variant.path)
        if not isinstance(response, FileResponse):
            return response
        # Response is an image
        response["Cache-Control"] = "no-store"
        return response
        