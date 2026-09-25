import json
from pathlib import Path
from urllib.parse import urlparse

from rest_framework import serializers

from .media import all_media_usage, attach_media_file
from .models import (
    LIBRARY_MARKER,
    Client,
    Department,
    FAQ,
    HomepageContent,
    Inquiry,
    MediaAsset,
    Product,
    Project,
    Service,
    Slide,
    TeamMember,
    Testimonial,
    validate_image_file,
)


def absolute_file_url(request, file_field, fallback=""):
    if file_field:
        url = file_field.url
        if request:
            return request.build_absolute_uri(url)
        return url
    if isinstance(fallback, str) and fallback.startswith(LIBRARY_MARKER):
        return ""
    return fallback or ""


def cms_image(**kwargs):
    kwargs.setdefault("required", False)
    kwargs.setdefault("allow_null", True)
    validators = list(kwargs.pop("validators", []))
    if validate_image_file not in validators:
        validators.append(validate_image_file)
    return serializers.ImageField(validators=validators, **kwargs)


class MediaAttachMixin:
    media_source_map = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.media_source_map:
            self.fields[name] = serializers.IntegerField(
                write_only=True, required=False, allow_null=True
            )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        for source in self.media_source_map:
            pk = attrs.get(source)
            if not pk:
                continue
            if not MediaAsset.objects.filter(pk=pk).exists():
                raise serializers.ValidationError({source: "Select a valid media image."})
        return attrs

    def create(self, validated_data):
        attachments = self._pop_media_attachments(validated_data)
        instance = super().create(validated_data)
        if attachments:
            self._apply_media_attachments(instance, attachments)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        attachments = self._pop_media_attachments(validated_data)
        for _source, (file_field, fallback_field) in self.media_source_map.items():
            if validated_data.get(file_field):
                setattr(instance, fallback_field, "")
        instance = super().update(instance, validated_data)
        if attachments:
            self._apply_media_attachments(instance, attachments)
            instance.save()
        return instance

    def _pop_media_attachments(self, validated_data):
        found = []
        for source, dest in self.media_source_map.items():
            pk = validated_data.pop(source, None)
            if validated_data.get(dest[0]):
                continue
            if pk:
                found.append((dest, pk))
        return found

    def _apply_media_attachments(self, instance, attachments):
        errors = {}
        for (file_field, fallback_field), pk in attachments:
            try:
                asset = MediaAsset.objects.get(pk=pk)
            except MediaAsset.DoesNotExist:
                errors[file_field] = "Select a valid media image."
                continue
            attach_media_file(instance, file_field, fallback_field, asset)
        if errors:
            raise serializers.ValidationError(errors)


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    in_use = serializers.SerializerMethodField()
    used_by = serializers.SerializerMethodField()
    file = cms_image(required=False, write_only=True)

    class Meta:
        model = MediaAsset
        fields = (
            "id",
            "name",
            "original_name",
            "file",
            "url",
            "in_use",
            "used_by",
            "created_at",
        )
        extra_kwargs = {
            "file": {"write_only": True},
            "original_name": {"read_only": True},
            "created_at": {"read_only": True},
            "name": {"required": False, "allow_blank": True},
        }

    def get_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.file)

    def get_used_by(self, obj):
        mapping = self.context.get("usage_map")
        if mapping is None:
            mapping = all_media_usage()
            self.context["usage_map"] = mapping
        return mapping.get(obj.pk, [])

    def get_in_use(self, obj):
        return bool(self.get_used_by(obj))

    def validate_name(self, value):
        return (value or "").strip()

    def validate(self, attrs):
        if self.instance is None and not attrs.get("file"):
            raise serializers.ValidationError({"file": "Choose an image to upload."})
        return attrs

    def create(self, validated_data):
        upload = validated_data.get("file")
        if upload:
            filename = Path(upload.name).name
            validated_data["original_name"] = filename
            if not validated_data.get("name"):
                validated_data["name"] = Path(filename).stem
        return super().create(validated_data)

    def update(self, instance, validated_data):
        upload = validated_data.get("file")
        if upload:
            if instance.file:
                instance.file.delete(save=False)
            filename = Path(upload.name).name
            validated_data["original_name"] = filename
            if not validated_data.get("name") and not instance.name:
                validated_data["name"] = Path(filename).stem
        return super().update(instance, validated_data)


class InquirySerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=2, max_length=120)
    message = serializers.CharField(min_length=10, max_length=5000)
    service = serializers.CharField(max_length=80)

    class Meta:
        model = Inquiry
        fields = ("name", "email", "service", "message")

    def validate_service(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Please select a service.")
        published = list(
            Service.objects.filter(is_active=True).values_list("name", flat=True)
        )
        allowed = published or [choice[0] for choice in Inquiry.SERVICE_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError("Select a valid service.")
        return value


class AdminInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ("id", "name", "email", "service", "message", "created_at")
        read_only_fields = fields


from django.contrib.auth import get_user_model

User = get_user_model()


class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "is_superuser", "last_login")
        read_only_fields = fields


class LooseJSONField(serializers.JSONField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError("Enter valid structured data.") from exc
        return super().to_internal_value(data)


class FeaturesField(serializers.ListField):
    child = serializers.CharField(max_length=300, allow_blank=False)

    def to_internal_value(self, data):
        return super().to_internal_value(self._coerce_list(data))

    def to_representation(self, data):
        return super().to_representation(self._coerce_list(data))

    def _coerce_list(self, data):
        if data in (None, ""):
            return []
        if isinstance(data, str):
            return self._parse_string(data)
        if isinstance(data, (list, tuple)):
            if len(data) == 1 and isinstance(data[0], str):
                parsed = self._try_parse_json_list(data[0])
                if parsed is not None:
                    return parsed
            return list(data)
        return data

    def _parse_string(self, value):
        parsed = self._try_parse_json_list(value)
        if parsed is not None:
            return parsed
        return [part.strip() for part in value.split("\n") if part.strip()]

    def _try_parse_json_list(self, value):
        value = (value or "").strip()
        if not value.startswith("["):
            return None
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, list) else None


def clean_href(value):
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith("/") or value.startswith("#"):
        if any(char.isspace() for char in value):
            raise serializers.ValidationError("Enter a valid URL or site path.")
        return value
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    raise serializers.ValidationError("Enter a valid URL or site path.")


class CatalogWriteMixin:
    required_when_active = {}
    sort_order = serializers.IntegerField(min_value=0, required=False)
    is_active = serializers.BooleanField(required=False)

    def validate_sort_order(self, value):
        if value is None:
            return 0
        if value < 0:
            raise serializers.ValidationError("Display order cannot be negative.")
        return int(value)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        is_active = attrs.get("is_active", getattr(self.instance, "is_active", True))
        if not is_active:
            return attrs
        errors = {}
        for field, message in self.required_when_active.items():
            if field in attrs:
                value = attrs[field]
            elif self.instance is not None:
                value = getattr(self.instance, field, "")
            else:
                value = ""
            if not str(value or "").strip():
                errors[field] = message
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class SlideSerializer(CatalogWriteMixin, MediaAttachMixin, serializers.ModelSerializer):
    required_when_active = {"headline": "Enter a headline before publishing."}
    media_source_map = {"image_from_media": ("image", "image_fallback")}
    image_url = serializers.SerializerMethodField()
    image = cms_image()

    class Meta:
        model = Slide
        fields = (
            "id",
            "name",
            "headline",
            "accent",
            "description",
            "image",
            "image_url",
            "primary_cta_label",
            "primary_cta_href",
            "secondary_cta_label",
            "secondary_cta_href",
            "is_active",
            "sort_order",
        )
        extra_kwargs = {"image": {"write_only": True}}

    def get_image_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a slide title.")
        return value

    def validate_primary_cta_href(self, value):
        return clean_href(value)

    def validate_secondary_cta_href(self, value):
        return clean_href(value)


class PublicSlideSerializer(serializers.ModelSerializer):
    tag = serializers.CharField(source="name")
    image = serializers.SerializerMethodField()
    primary_cta = serializers.SerializerMethodField()
    secondary_cta = serializers.SerializerMethodField()

    class Meta:
        model = Slide
        fields = (
            "id",
            "tag",
            "headline",
            "accent",
            "description",
            "image",
            "primary_cta",
            "secondary_cta",
            "sort_order",
        )

    def get_image(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def get_primary_cta(self, obj):
        return {"label": obj.primary_cta_label, "href": obj.primary_cta_href}

    def get_secondary_cta(self, obj):
        return {"label": obj.secondary_cta_label, "href": obj.secondary_cta_href}


class ProjectSerializer(CatalogWriteMixin, MediaAttachMixin, serializers.ModelSerializer):
    media_source_map = {
        "image_from_media": ("image", "image_fallback"),
        "logo_from_media": ("logo", "logo_fallback"),
        "related_image_from_media": ("related_image", "related_image_fallback"),
    }
    image_url = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    related_image_url = serializers.SerializerMethodField()
    image = cms_image()
    logo = cms_image()
    related_image = cms_image()
    features = FeaturesField(required=False)
    url = serializers.URLField(required=False, allow_blank=True, default="")

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "category",
            "url",
            "features",
            "image",
            "image_url",
            "logo",
            "logo_url",
            "related_name",
            "related_role",
            "related_image",
            "related_image_url",
            "is_active",
            "sort_order",
        )
        extra_kwargs = {
            "image": {"write_only": True},
            "logo": {"write_only": True},
            "related_image": {"write_only": True},
        }

    def get_image_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def get_logo_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.logo, obj.logo_fallback)

    def get_related_image_url(self, obj):
        return absolute_file_url(
            self.context.get("request"),
            obj.related_image,
            obj.related_image_fallback,
        )

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a project title.")
        return value

    def validate_features(self, value):
        cleaned = [item.strip() for item in value if str(item).strip()]
        return cleaned[:24]


class PublicProjectSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="name")
    subtitle = serializers.CharField(source="description")
    image = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    link = serializers.CharField(source="url")
    supervisor = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "subtitle",
            "category",
            "features",
            "image",
            "logo",
            "link",
            "supervisor",
            "partner",
            "organization",
            "sort_order",
        )

    def _related(self, obj):
        name = obj.related_name
        if not name:
            return None
        return {
            "name": name,
            "role": obj.related_role,
            "image": absolute_file_url(
                self.context.get("request"),
                obj.related_image,
                obj.related_image_fallback,
            ),
        }

    def get_image(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def get_logo(self, obj):
        return absolute_file_url(self.context.get("request"), obj.logo, obj.logo_fallback)

    def get_supervisor(self, obj):
        if obj.category != Project.CATEGORY_OWN:
            return None
        related = self._related(obj)
        if related and not related.get("role"):
            related["role"] = "Supervisor"
        return related

    def get_partner(self, obj):
        if obj.category != Project.CATEGORY_PARTNERSHIP:
            return None
        return self._related(obj)

    def get_organization(self, obj):
        if obj.category != Project.CATEGORY_CLIENT:
            return None
        return self._related(obj)


class ServiceSerializer(CatalogWriteMixin, MediaAttachMixin, serializers.ModelSerializer):
    media_source_map = {"image_from_media": ("image", "image_fallback")}
    image_url = serializers.SerializerMethodField()
    image = cms_image()
    content = FeaturesField(required=False)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "content",
            "image",
            "image_url",
            "is_active",
            "sort_order",
        )
        extra_kwargs = {"image": {"write_only": True}}

    def get_image_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a service title.")
        return value


class PublicServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    content = FeaturesField(read_only=True)

    class Meta:
        model = Service
        fields = ("id", "name", "description", "content", "image", "sort_order")

    def get_image(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)


class TeamMemberSerializer(CatalogWriteMixin, MediaAttachMixin, serializers.ModelSerializer):
    media_source_map = {"image_from_media": ("image", "image_fallback")}
    image_url = serializers.SerializerMethodField()
    image = cms_image()
    email = serializers.EmailField(required=False, allow_blank=True)
    experience = serializers.IntegerField(min_value=0, required=False)
    projects = serializers.IntegerField(min_value=0, required=False)
    expertise = FeaturesField(required=False)
    department_roles = FeaturesField(required=False)
    department_productions = FeaturesField(required=False)

    class Meta:
        model = TeamMember
        fields = (
            "id",
            "name",
            "role",
            "email",
            "bio",
            "image",
            "image_url",
            "experience",
            "projects",
            "expertise",
            "department_name",
            "department_description",
            "department_roles",
            "department_productions",
            "is_active",
            "sort_order",
        )
        extra_kwargs = {"image": {"write_only": True}}

    def get_image_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a member name.")
        return value


class PublicTeamMemberSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    expertise = FeaturesField(read_only=True)
    department = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = (
            "id",
            "name",
            "role",
            "email",
            "bio",
            "image",
            "experience",
            "projects",
            "expertise",
            "department",
            "sort_order",
        )

    def get_image(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def get_department(self, obj):
        if not obj.department_name and not obj.department_description:
            return None
        return {
            "name": obj.department_name,
            "description": obj.department_description,
            "roles": obj.department_roles or [],
            "productions": obj.department_productions or [],
        }


class ProductSerializer(CatalogWriteMixin, MediaAttachMixin, serializers.ModelSerializer):
    media_source_map = {
        "image_from_media": ("image", "image_fallback"),
        "screen_image_from_media": ("screen_image", "screen_image_fallback"),
    }
    image_url = serializers.SerializerMethodField()
    screen_image_url = serializers.SerializerMethodField()
    image = cms_image()
    screen_image = cms_image()
    features = FeaturesField(required=False)
    url = serializers.URLField(required=False, allow_blank=True, default="")

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "url",
            "features",
            "image",
            "image_url",
            "screen_image",
            "screen_image_url",
            "is_active",
            "sort_order",
        )
        extra_kwargs = {
            "image": {"write_only": True},
            "screen_image": {"write_only": True},
        }

    def get_image_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def get_screen_image_url(self, obj):
        return absolute_file_url(
            self.context.get("request"), obj.screen_image, obj.screen_image_fallback
        )

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a product title.")
        return value


class PublicProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="name")
    image = serializers.SerializerMethodField()
    imageScreen = serializers.SerializerMethodField()
    features = FeaturesField(read_only=True)

    class Meta:
        model = Product
        fields = ("id", "title", "description", "url", "features", "image", "imageScreen", "sort_order")

    def get_image(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def get_imageScreen(self, obj):
        return absolute_file_url(
            self.context.get("request"), obj.screen_image, obj.screen_image_fallback
        )


class DepartmentSerializer(CatalogWriteMixin, MediaAttachMixin, serializers.ModelSerializer):
    media_source_map = {
        "icon_from_media": ("icon", "icon_fallback"),
        "director_image_from_media": ("director_image", "director_image_fallback"),
    }
    icon_url = serializers.SerializerMethodField()
    director_image_url = serializers.SerializerMethodField()
    icon = cms_image()
    director_image = cms_image()
    roles = FeaturesField(required=False)
    productions = FeaturesField(required=False)

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
            "description",
            "icon",
            "icon_url",
            "director_name",
            "director_image",
            "director_image_url",
            "roles",
            "productions",
            "is_active",
            "sort_order",
        )
        extra_kwargs = {
            "icon": {"write_only": True},
            "director_image": {"write_only": True},
        }

    def get_icon_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.icon, obj.icon_fallback)

    def get_director_image_url(self, obj):
        return absolute_file_url(
            self.context.get("request"), obj.director_image, obj.director_image_fallback
        )

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a department name.")
        return value


class PublicDepartmentSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    director = serializers.SerializerMethodField()
    roles = FeaturesField(read_only=True)
    productions = FeaturesField(read_only=True)

    class Meta:
        model = Department
        fields = ("id", "name", "description", "icon", "director", "roles", "productions", "sort_order")

    def get_icon(self, obj):
        return absolute_file_url(self.context.get("request"), obj.icon, obj.icon_fallback)

    def get_director(self, obj):
        photo = absolute_file_url(
            self.context.get("request"), obj.director_image, obj.director_image_fallback
        )
        if not obj.director_name and not photo:
            return None
        return {"name": obj.director_name, "photo": photo}


class TestimonialSerializer(CatalogWriteMixin, MediaAttachMixin, serializers.ModelSerializer):
    required_when_active = {"quote": "Enter a testimonial before publishing."}
    media_source_map = {"image_from_media": ("image", "image_fallback")}
    image_url = serializers.SerializerMethodField()
    image = cms_image()

    class Meta:
        model = Testimonial
        fields = (
            "id",
            "name",
            "role",
            "quote",
            "image",
            "image_url",
            "is_active",
            "sort_order",
        )
        extra_kwargs = {"image": {"write_only": True}}

    def get_image_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a client or person name.")
        return value

    def validate_quote(self, value):
        return (value or "").strip()


class PublicTestimonialSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = ("id", "name", "role", "avatar", "quote", "sort_order")

    def get_avatar(self, obj):
        return absolute_file_url(self.context.get("request"), obj.image, obj.image_fallback)


class FAQSerializer(CatalogWriteMixin, serializers.ModelSerializer):
    required_when_active = {"answer": "Enter an answer before publishing."}

    class Meta:
        model = FAQ
        fields = ("id", "name", "answer", "is_active", "sort_order")

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a question.")
        return value

    def validate_answer(self, value):
        return (value or "").strip()


class PublicFAQSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source="name")

    class Meta:
        model = FAQ
        fields = ("id", "question", "answer", "sort_order")


class ClientSerializer(CatalogWriteMixin, MediaAttachMixin, serializers.ModelSerializer):
    media_source_map = {"logo_from_media": ("logo", "logo_fallback")}
    logo_url = serializers.SerializerMethodField()
    logo = cms_image()
    url = serializers.URLField(required=False, allow_blank=True, default="")

    class Meta:
        model = Client
        fields = ("id", "name", "url", "logo", "logo_url", "is_active", "sort_order")
        extra_kwargs = {"logo": {"write_only": True}}

    def get_logo_url(self, obj):
        return absolute_file_url(self.context.get("request"), obj.logo, obj.logo_fallback)

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Enter a client name.")
        return value


class PublicClientSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ("id", "name", "logo", "url", "sort_order")

    def get_logo(self, obj):
        return absolute_file_url(self.context.get("request"), obj.logo, obj.logo_fallback)


def _clean_stat(item):
    if not isinstance(item, dict):
        return None
    label = str(item.get("label") or "").strip()
    if not label:
        return None
    try:
        value = int(item.get("value") or 0)
    except (TypeError, ValueError):
        value = 0
    return {
        "value": value,
        "suffix": str(item.get("suffix") or ""),
        "label": label,
        "description": str(item.get("description") or ""),
        "featured": bool(item.get("featured")),
    }


def _clean_named_items(items, title_key, extra_keys):
    cleaned = []
    if not isinstance(items, list):
        return cleaned
    for item in items:
        if not isinstance(item, dict):
            continue
        title = str(item.get(title_key) or "").strip()
        if not title:
            continue
        row = {title_key: title}
        for key in extra_keys:
            row[key] = str(item.get(key) or "")
        cleaned.append(row)
    return cleaned


def _clean_method_steps(items):
    cleaned = []
    if not isinstance(items, list):
        return cleaned
    for item in items:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        desc = str(item.get("desc") or "").strip()
        raw_points = item.get("points") or []
        if isinstance(raw_points, str):
            points = [part.strip() for part in raw_points.splitlines() if part.strip()]
        elif isinstance(raw_points, list):
            points = [str(part).strip() for part in raw_points if str(part).strip()]
        else:
            points = []
        cleaned.append({"title": title, "desc": desc, "points": points})
    return cleaned


class HomepageSerializer(MediaAttachMixin, serializers.ModelSerializer):
    media_source_map = {
        "about_image_from_media": ("about_image", "about_image_fallback"),
        "why_image_from_media": ("why_image", "why_image_fallback"),
    }
    about_image_url = serializers.SerializerMethodField()
    why_image_url = serializers.SerializerMethodField()
    about_image = cms_image()
    why_image = cms_image()
    stats = LooseJSONField(required=False)
    about_highlights = LooseJSONField(required=False)
    why_items = LooseJSONField(required=False)
    method_steps = LooseJSONField(required=False)
    expertise_items = LooseJSONField(required=False)

    class Meta:
        model = HomepageContent
        fields = (
            "stats",
            "about_eyebrow",
            "about_title",
            "about_highlight",
            "about_body",
            "about_image",
            "about_image_url",
            "about_cta_label",
            "about_cta_href",
            "about_badge_value",
            "about_badge_label",
            "about_highlights",
            "why_eyebrow",
            "why_title",
            "why_highlight",
            "why_subtitle",
            "why_image",
            "why_image_url",
            "why_items",
            "method_eyebrow",
            "method_title",
            "method_highlight",
            "method_subtitle",
            "method_steps",
            "expertise_eyebrow",
            "expertise_title",
            "expertise_highlight",
            "expertise_subtitle",
            "expertise_items",
        )
        extra_kwargs = {
            "about_image": {"write_only": True},
            "why_image": {"write_only": True},
        }

    def get_about_image_url(self, obj):
        return absolute_file_url(
            self.context.get("request"), obj.about_image, obj.about_image_fallback
        )

    def get_why_image_url(self, obj):
        return absolute_file_url(
            self.context.get("request"), obj.why_image, obj.why_image_fallback
        )

    def validate_stats(self, value):
        if not value:
            return []
        return [row for row in (_clean_stat(item) for item in value) if row]

    def validate_about_highlights(self, value):
        return _clean_named_items(value or [], "label", ["text"])

    def validate_why_items(self, value):
        return _clean_named_items(value or [], "title", ["description", "icon"])

    def validate_method_steps(self, value):
        return _clean_method_steps(value or [])

    def validate_expertise_items(self, value):
        return _clean_named_items(value or [], "title", ["description", "icon"])

    def validate_about_cta_href(self, value):
        return clean_href(value)


class PublicHomepageSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    why = serializers.SerializerMethodField()
    methodology = serializers.SerializerMethodField()
    expertise = serializers.SerializerMethodField()

    class Meta:
        model = HomepageContent
        fields = ("stats", "about", "why", "methodology", "expertise")

    def get_stats(self, obj):
        return [row for row in (_clean_stat(item) for item in (obj.stats or [])) if row]

    def get_about(self, obj):
        request = self.context.get("request")
        return {
            "eyebrow": obj.about_eyebrow,
            "title": obj.about_title,
            "highlight": obj.about_highlight,
            "body": obj.about_body,
            "image": absolute_file_url(request, obj.about_image, obj.about_image_fallback),
            "cta_label": obj.about_cta_label,
            "cta_href": obj.about_cta_href or "/contact",
            "badge_value": obj.about_badge_value,
            "badge_label": obj.about_badge_label,
            "highlights": _clean_named_items(obj.about_highlights or [], "label", ["text"]),
        }

    def get_why(self, obj):
        request = self.context.get("request")
        return {
            "eyebrow": obj.why_eyebrow,
            "title": obj.why_title,
            "highlight": obj.why_highlight,
            "subtitle": obj.why_subtitle,
            "image": absolute_file_url(request, obj.why_image, obj.why_image_fallback),
            "items": _clean_named_items(obj.why_items or [], "title", ["description", "icon"]),
        }

    def get_methodology(self, obj):
        return {
            "eyebrow": obj.method_eyebrow,
            "title": obj.method_title,
            "highlight": obj.method_highlight,
            "subtitle": obj.method_subtitle,
            "steps": _clean_method_steps(obj.method_steps or []),
        }

    def get_expertise(self, obj):
        return {
            "eyebrow": obj.expertise_eyebrow,
            "title": obj.expertise_title,
            "highlight": obj.expertise_highlight,
            "subtitle": obj.expertise_subtitle,
            "items": _clean_named_items(
                obj.expertise_items or [], "title", ["description", "icon"]
            ),
        }
