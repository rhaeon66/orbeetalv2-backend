from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from rest_framework import status
from rest_framework.response import Response

from .media import media_usage
from .models import (
    Client,
    Department,
    FAQ,
    HomepageContent,
    MediaAsset,
    Product,
    Project,
    Service,
    Slide,
    TeamMember,
    Testimonial,
)
from .permissions import IsStaffUser
from .serializers import (
    ClientSerializer,
    DepartmentSerializer,
    FAQSerializer,
    HomepageSerializer,
    MediaAssetSerializer,
    ProductSerializer,
    ProjectSerializer,
    PublicClientSerializer,
    PublicDepartmentSerializer,
    PublicFAQSerializer,
    PublicHomepageSerializer,
    PublicProductSerializer,
    PublicProjectSerializer,
    PublicServiceSerializer,
    PublicSlideSerializer,
    PublicTeamMemberSerializer,
    PublicTestimonialSerializer,
    ServiceSerializer,
    SlideSerializer,
    TeamMemberSerializer,
    TestimonialSerializer,
)


class PublicSlideList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicSlideSerializer
    pagination_class = None
    queryset = Slide.objects.filter(is_active=True)


class PublicProjectList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicProjectSerializer
    pagination_class = None
    queryset = Project.objects.filter(is_active=True)


class PublicServiceList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicServiceSerializer
    pagination_class = None
    queryset = Service.objects.filter(is_active=True)


class PublicTeamMemberList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicTeamMemberSerializer
    pagination_class = None
    queryset = TeamMember.objects.filter(is_active=True)


class PublicTestimonialList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicTestimonialSerializer
    pagination_class = None
    queryset = Testimonial.objects.filter(is_active=True)


class PublicFAQList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicFAQSerializer
    pagination_class = None
    queryset = FAQ.objects.filter(is_active=True)


class PublicProductList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicProductSerializer
    pagination_class = None
    queryset = Product.objects.filter(is_active=True)


class PublicDepartmentList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentSerializer
    pagination_class = None
    queryset = Department.objects.filter(is_active=True)


class AdminSlideListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = SlideSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = Slide.objects.all()


class AdminSlideDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = SlideSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Slide.objects.all()


class AdminProjectListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ProjectSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = Project.objects.all()


class AdminProjectDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ProjectSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Project.objects.all()


class AdminServiceListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ServiceSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = Service.objects.all()


class AdminServiceDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ServiceSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Service.objects.all()


class AdminTeamMemberListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = TeamMemberSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = TeamMember.objects.all()


class AdminTeamMemberDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = TeamMemberSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = TeamMember.objects.all()


class AdminTestimonialListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = TestimonialSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = Testimonial.objects.all()


class AdminTestimonialDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = TestimonialSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Testimonial.objects.all()


class AdminFAQListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = FAQSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = FAQ.objects.all()


class AdminFAQDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = FAQSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = FAQ.objects.all()


class AdminProductListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = Product.objects.all()


class AdminProductDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Product.objects.all()


class AdminDepartmentListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = DepartmentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = Department.objects.all()


class AdminDepartmentDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = DepartmentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Department.objects.all()


def _homepage():
    obj, _created = HomepageContent.objects.get_or_create(pk=1)
    return obj


class PublicClientList(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicClientSerializer
    pagination_class = None
    queryset = Client.objects.filter(is_active=True)


class PublicHomepage(RetrieveAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicHomepageSerializer

    def get_object(self):
        return _homepage()


class AdminClientListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ClientSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = Client.objects.all()


class AdminClientDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ClientSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Client.objects.all()


class AdminHomepage(RetrieveUpdateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = HomepageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return _homepage()


class AdminMediaListCreate(ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = MediaAssetSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None
    queryset = MediaAsset.objects.all()


class AdminMediaDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = MediaAssetSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = MediaAsset.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        used_by = media_usage(instance)
        if used_by:
            return Response(
                {
                    "detail": "This image is still used by: " + ", ".join(used_by),
                    "used_by": used_by,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if instance.file:
            instance.file.delete(save=False)
        return super().destroy(request, *args, **kwargs)
