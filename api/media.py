from collections import defaultdict
from pathlib import Path

from django.core.files.base import ContentFile

from .models import (
    LIBRARY_MARKER,
    Client,
    Department,
    HomepageContent,
    MediaAsset,
    Product,
    Project,
    Service,
    Slide,
    TeamMember,
    Testimonial,
)

IMAGE_USAGE = (
    (Slide, "Slide", (("image", "image_fallback"),)),
    (
        Project,
        "Project",
        (
            ("image", "image_fallback"),
            ("logo", "logo_fallback"),
            ("related_image", "related_image_fallback"),
        ),
    ),
    (Service, "Service", (("image", "image_fallback"),)),
    (
        Product,
        "Product",
        (("image", "image_fallback"), ("screen_image", "screen_image_fallback")),
    ),
    (TeamMember, "Team", (("image", "image_fallback"),)),
    (
        Department,
        "Department",
        (("icon", "icon_fallback"), ("director_image", "director_image_fallback")),
    ),
    (Testimonial, "Testimonial", (("image", "image_fallback"),)),
    (Client, "Client", (("logo", "logo_fallback"),)),
    (
        HomepageContent,
        "Homepage",
        (
            ("about_image", "about_image_fallback"),
            ("why_image", "why_image_fallback"),
        ),
    ),
)


def _parse_marker(value):
    if not isinstance(value, str) or not value.startswith(LIBRARY_MARKER):
        return None
    try:
        return int(value.removeprefix(LIBRARY_MARKER))
    except ValueError:
        return None


def all_media_usage():
    usage = defaultdict(list)
    seen = defaultdict(set)
    library_ids = {
        (asset.file.name or "").replace("\\", "/"): asset.pk
        for asset in MediaAsset.objects.exclude(file="")
    }
    for model, label, fields in IMAGE_USAGE:
        for obj in model.objects.all():
            label_text = f"{label}: {obj}"
            for file_field, fallback_field in fields:
                pk = _parse_marker(getattr(obj, fallback_field) or "")
                file_val = getattr(obj, file_field)
                file_name = (getattr(file_val, "name", "") or "").replace("\\", "/")
                if pk is None and file_name:
                    pk = library_ids.get(file_name)
                if pk is None:
                    continue
                if label_text in seen[pk]:
                    continue
                seen[pk].add(label_text)
                usage[pk].append(label_text)
    return usage


def media_usage(asset):
    return all_media_usage().get(asset.pk, [])


def attach_media_file(instance, file_field_name, fallback_field_name, asset):
    if not asset.file:
        raise ValueError("That media item has no file.")
    asset.file.open("rb")
    try:
        payload = asset.file.read()
    finally:
        asset.file.close()
    filename = Path(asset.original_name or asset.file.name).name or "image.jpg"
    field = getattr(instance, file_field_name)
    field.save(filename, ContentFile(payload), save=False)
    setattr(instance, fallback_field_name, asset.marker)
