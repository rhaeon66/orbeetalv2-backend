from pathlib import Path
import uuid

from django.core.exceptions import ValidationError
from django.db import models


def _media_upload(folder, filename):
    ext = Path(filename).suffix.lower() or ".bin"
    return f"{folder}/{uuid.uuid4().hex}{ext}"


def slide_upload(instance, filename):
    return _media_upload("slides", filename)


def project_image_upload(instance, filename):
    return _media_upload("projects", filename)


def project_logo_upload(instance, filename):
    return _media_upload("projects/logos", filename)


def project_related_upload(instance, filename):
    return _media_upload("projects/related", filename)


def service_upload(instance, filename):
    return _media_upload("services", filename)


def team_upload(instance, filename):
    return _media_upload("team", filename)


def testimonial_upload(instance, filename):
    return _media_upload("testimonials", filename)


def product_image_upload(instance, filename):
    return _media_upload("products", filename)


def product_screen_upload(instance, filename):
    return _media_upload("products/screens", filename)


def department_icon_upload(instance, filename):
    return _media_upload("departments", filename)


def department_director_upload(instance, filename):
    return _media_upload("departments/directors", filename)


def client_logo_upload(instance, filename):
    return _media_upload("clients", filename)


def homepage_about_upload(instance, filename):
    return _media_upload("homepage/about", filename)


def homepage_why_upload(instance, filename):
    return _media_upload("homepage/why", filename)


def media_library_upload(instance, filename):
    return _media_upload("library", filename)


def validate_image_file(file):
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    suffix = Path(file.name).suffix.lower()
    if suffix not in allowed:
        raise ValidationError("Use a JPG, PNG, WEBP, or GIF image.")
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Image must be 5MB or smaller.")


class Inquiry(models.Model):
    SERVICE_CHOICES = [
        ("Software Development", "Software Development"),
        ("Web Development", "Web Development"),
        ("Mobile App Development", "Mobile App Development"),
        ("AI Solutions", "AI Solutions"),
        ("Cyber Security", "Cyber Security"),
        ("Digital Marketing", "Digital Marketing"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    service = models.CharField(max_length=80)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "inquiries"

    def __str__(self):
        return f"{self.name} — {self.service}"


class CatalogItem(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class Slide(CatalogItem):
    headline = models.CharField(max_length=255, blank=True)
    accent = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to=slide_upload,
        blank=True,
        validators=[validate_image_file],
    )
    image_fallback = models.CharField(max_length=500, blank=True)
    primary_cta_label = models.CharField(max_length=120, blank=True)
    primary_cta_href = models.CharField(max_length=500, blank=True)
    secondary_cta_label = models.CharField(max_length=120, blank=True)
    secondary_cta_href = models.CharField(max_length=500, blank=True)


class Project(CatalogItem):
    CATEGORY_OWN = "own"
    CATEGORY_PARTNERSHIP = "partnership"
    CATEGORY_CLIENT = "client"
    CATEGORY_CHOICES = [
        (CATEGORY_OWN, "Own Products"),
        (CATEGORY_PARTNERSHIP, "Partnerships"),
        (CATEGORY_CLIENT, "Client Projects"),
    ]

    description = models.CharField(max_length=500, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_CLIENT,
    )
    url = models.URLField(blank=True)
    features = models.JSONField(default=list, blank=True)
    image = models.ImageField(
        upload_to=project_image_upload,
        blank=True,
        validators=[validate_image_file],
    )
    image_fallback = models.CharField(max_length=500, blank=True)
    logo = models.ImageField(
        upload_to=project_logo_upload,
        blank=True,
        validators=[validate_image_file],
    )
    logo_fallback = models.CharField(max_length=500, blank=True)
    related_name = models.CharField(max_length=255, blank=True)
    related_role = models.CharField(max_length=120, blank=True)
    related_image = models.ImageField(
        upload_to=project_related_upload,
        blank=True,
        validators=[validate_image_file],
    )
    related_image_fallback = models.CharField(max_length=500, blank=True)


class Service(CatalogItem):
    description = models.TextField(blank=True)
    content = models.JSONField(default=list, blank=True)
    image = models.ImageField(
        upload_to=service_upload,
        blank=True,
        validators=[validate_image_file],
    )
    image_fallback = models.CharField(max_length=500, blank=True)


class Product(CatalogItem):
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    features = models.JSONField(default=list, blank=True)
    image = models.ImageField(
        upload_to=product_image_upload,
        blank=True,
        validators=[validate_image_file],
    )
    image_fallback = models.CharField(max_length=500, blank=True)
    screen_image = models.ImageField(
        upload_to=product_screen_upload,
        blank=True,
        validators=[validate_image_file],
    )
    screen_image_fallback = models.CharField(max_length=500, blank=True)


class TeamMember(CatalogItem):
    role = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(
        upload_to=team_upload,
        blank=True,
        validators=[validate_image_file],
    )
    image_fallback = models.CharField(max_length=500, blank=True)
    experience = models.PositiveIntegerField(default=0)
    projects = models.PositiveIntegerField(default=0)
    expertise = models.JSONField(default=list, blank=True)
    department_name = models.CharField(max_length=120, blank=True)
    department_description = models.TextField(blank=True)
    department_roles = models.JSONField(default=list, blank=True)
    department_productions = models.JSONField(default=list, blank=True)

    class Meta(CatalogItem.Meta):
        verbose_name = "team member"
        verbose_name_plural = "team members"


class Department(CatalogItem):
    description = models.TextField(blank=True)
    icon = models.ImageField(
        upload_to=department_icon_upload,
        blank=True,
        validators=[validate_image_file],
    )
    icon_fallback = models.CharField(max_length=500, blank=True)
    director_name = models.CharField(max_length=120, blank=True)
    director_image = models.ImageField(
        upload_to=department_director_upload,
        blank=True,
        validators=[validate_image_file],
    )
    director_image_fallback = models.CharField(max_length=500, blank=True)
    roles = models.JSONField(default=list, blank=True)
    productions = models.JSONField(default=list, blank=True)


class Testimonial(CatalogItem):
    role = models.CharField(max_length=160, blank=True)
    quote = models.TextField(blank=True)
    image = models.ImageField(
        upload_to=testimonial_upload,
        blank=True,
        validators=[validate_image_file],
    )
    image_fallback = models.CharField(max_length=500, blank=True)


class FAQ(CatalogItem):
    answer = models.TextField(blank=True)

    class Meta(CatalogItem.Meta):
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"


class Client(CatalogItem):
    url = models.URLField(blank=True)
    logo = models.ImageField(
        upload_to=client_logo_upload,
        blank=True,
        validators=[validate_image_file],
    )
    logo_fallback = models.CharField(max_length=500, blank=True)


class HomepageContent(models.Model):
    stats = models.JSONField(default=list, blank=True)
    about_eyebrow = models.CharField(max_length=120, blank=True)
    about_title = models.CharField(max_length=255, blank=True)
    about_highlight = models.CharField(max_length=255, blank=True)
    about_body = models.TextField(blank=True)
    about_image = models.ImageField(
        upload_to=homepage_about_upload,
        blank=True,
        validators=[validate_image_file],
    )
    about_image_fallback = models.CharField(max_length=500, blank=True)
    about_cta_label = models.CharField(max_length=120, blank=True)
    about_cta_href = models.CharField(max_length=500, blank=True)
    about_badge_value = models.CharField(max_length=80, blank=True)
    about_badge_label = models.CharField(max_length=160, blank=True)
    about_highlights = models.JSONField(default=list, blank=True)
    why_eyebrow = models.CharField(max_length=120, blank=True)
    why_title = models.CharField(max_length=255, blank=True)
    why_highlight = models.CharField(max_length=255, blank=True)
    why_subtitle = models.TextField(blank=True)
    why_image = models.ImageField(
        upload_to=homepage_why_upload,
        blank=True,
        validators=[validate_image_file],
    )
    why_image_fallback = models.CharField(max_length=500, blank=True)
    why_items = models.JSONField(default=list, blank=True)
    method_eyebrow = models.CharField(max_length=120, blank=True)
    method_title = models.CharField(max_length=255, blank=True)
    method_highlight = models.CharField(max_length=255, blank=True)
    method_subtitle = models.TextField(blank=True)
    method_steps = models.JSONField(default=list, blank=True)
    expertise_eyebrow = models.CharField(max_length=120, blank=True)
    expertise_title = models.CharField(max_length=255, blank=True)
    expertise_highlight = models.CharField(max_length=255, blank=True)
    expertise_subtitle = models.TextField(blank=True)
    expertise_items = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "homepage content"
        verbose_name_plural = "homepage content"

    def __str__(self):
        return "Homepage"


LIBRARY_MARKER = "library:"


class MediaAsset(models.Model):
    name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255, blank=True)
    file = models.ImageField(
        upload_to=media_library_upload,
        validators=[validate_image_file],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.name

    @property
    def marker(self):
        return f"{LIBRARY_MARKER}{self.pk}"
