from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Client,
    Department,
    FAQ,
    Inquiry,
    Product,
    Project,
    Service,
    Slide,
    TeamMember,
    Testimonial,
)
from .permissions import IsStaffUser
from .portfolio_export import build_portfolio_pdf
from .serializers import (
    AdminInquirySerializer,
    InquirySerializer,
    StaffUserSerializer,
    absolute_file_url,
)


class BinaryFileRenderer(BaseRenderer):
    media_type = "application/octet-stream"
    format = "bin"
    charset = None
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        if isinstance(data, str):
            return data.encode("utf-8")
        return b""


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"ok": True, "service": "orbeetal-backend"})


@method_decorator(csrf_exempt, name="dispatch")
class ContactView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"ok": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {
                "ok": True,
                "message": "Thank you. We received your inquiry and will get back to you shortly.",
            },
            status=status.HTTP_201_CREATED,
        )


class DashboardView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        recent_projects = [
            {
                "id": project.id,
                "name": project.name,
                "category": project.get_category_display(),
                "is_active": project.is_active,
                "image_url": absolute_file_url(
                    request, project.image, project.image_fallback
                ),
            }
            for project in Project.objects.order_by("-id")[:8]
        ]
        return Response(
            {
                "projects": Project.objects.filter(is_active=True).count(),
                "services": Service.objects.filter(is_active=True).count(),
                "team_members": TeamMember.objects.filter(is_active=True).count(),
                "testimonials": Testimonial.objects.filter(is_active=True).count(),
                "faqs": FAQ.objects.filter(is_active=True).count(),
                "slides": Slide.objects.filter(is_active=True).count(),
                "products": Product.objects.filter(is_active=True).count(),
                "departments": Department.objects.filter(is_active=True).count(),
                "clients": Client.objects.filter(is_active=True).count(),
                "inquiries": Inquiry.objects.count(),
                "recent_projects": recent_projects,
            }
        )


class AdminInquiryList(ListAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = AdminInquirySerializer
    pagination_class = None
    queryset = Inquiry.objects.all()


class AdminInquiryDetail(RetrieveDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = AdminInquirySerializer
    queryset = Inquiry.objects.all()


class AdminUserList(ListAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = StaffUserSerializer
    pagination_class = None
    queryset = get_user_model().objects.filter(is_staff=True).order_by("username")


class AdminPortfolioDownload(APIView):
    permission_classes = [IsStaffUser]
    renderer_classes = [JSONRenderer, BinaryFileRenderer]

    def get(self, request):
        payload = build_portfolio_pdf()
        stamp = timezone.now().date().isoformat()
        response = HttpResponse(payload, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="orbeetal-portfolio-{stamp}.pdf"'
        )
        response["Cache-Control"] = "no-store"
        return response
