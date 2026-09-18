from django.contrib import admin, messages

from .media import media_usage
from .models import (
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
)

admin.site.site_header = "Orbeetal CMS"
admin.site.site_title = "Orbeetal CMS"
admin.site.index_title = "Website content"


class CatalogAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active", "sort_order")
    ordering = ("sort_order", "id")


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "created_at")
    list_filter = ("service", "created_at")
    search_fields = ("name", "email", "message", "service")
    readonly_fields = ("created_at",)


@admin.register(Slide)
class SlideAdmin(CatalogAdmin):
    list_display = ("name", "headline", "is_active", "sort_order")
    search_fields = ("name", "headline", "accent", "description")


@admin.register(Project)
class ProjectAdmin(CatalogAdmin):
    list_display = ("name", "category", "is_active", "sort_order")
    list_filter = ("is_active", "category")
    search_fields = ("name", "description", "url")


@admin.register(Service)
class ServiceAdmin(CatalogAdmin):
    search_fields = ("name", "description")


@admin.register(Product)
class ProductAdmin(CatalogAdmin):
    search_fields = ("name", "description", "url")


@admin.register(TeamMember)
class TeamMemberAdmin(CatalogAdmin):
    list_display = ("name", "role", "email", "is_active", "sort_order")
    search_fields = ("name", "role", "email", "bio", "department_name")


@admin.register(Department)
class DepartmentAdmin(CatalogAdmin):
    list_display = ("name", "director_name", "is_active", "sort_order")
    search_fields = ("name", "description", "director_name")


@admin.register(Testimonial)
class TestimonialAdmin(CatalogAdmin):
    list_display = ("name", "role", "is_active", "sort_order")
    search_fields = ("name", "role", "quote")


@admin.register(FAQ)
class FAQAdmin(CatalogAdmin):
    search_fields = ("name", "answer")


@admin.register(Client)
class ClientAdmin(CatalogAdmin):
    search_fields = ("name", "url")


@admin.register(HomepageContent)
class HomepageContentAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Stats", {"fields": ("stats",)}),
        (
            "About",
            {
                "fields": (
                    "about_eyebrow",
                    "about_title",
                    "about_highlight",
                    "about_body",
                    "about_image",
                    "about_image_fallback",
                    "about_cta_label",
                    "about_cta_href",
                    "about_badge_value",
                    "about_badge_label",
                    "about_highlights",
                )
            },
        ),
        (
            "Why choose us",
            {
                "fields": (
                    "why_eyebrow",
                    "why_title",
                    "why_highlight",
                    "why_subtitle",
                    "why_image",
                    "why_image_fallback",
                    "why_items",
                )
            },
        ),
        (
            "Methodology",
            {
                "fields": (
                    "method_eyebrow",
                    "method_title",
                    "method_highlight",
                    "method_subtitle",
                    "method_steps",
                )
            },
        ),
        (
            "Expertise",
            {
                "fields": (
                    "expertise_eyebrow",
                    "expertise_title",
                    "expertise_highlight",
                    "expertise_subtitle",
                    "expertise_items",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not HomepageContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("name", "original_name", "created_at")
    search_fields = ("name", "original_name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at", "-id")

    def delete_model(self, request, obj):
        used_by = media_usage(obj)
        if used_by:
            self.message_user(
                request,
                "This image is still used by: " + ", ".join(used_by),
                messages.ERROR,
            )
            return
        if obj.file:
            obj.file.delete(save=False)
        super().delete_model(request, obj)
