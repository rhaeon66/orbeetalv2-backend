from io import BytesIO
from pathlib import Path

from django.conf import settings
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from .models import Product, Project
from .portfolio import resolve_project_image

PAGE_W, PAGE_H = landscape(A4)
NAVY = HexColor("#12344D")
CYAN = HexColor("#27BFC7")
LIME = HexColor("#96D83A")
INK = HexColor("#102C40")
MUTED = HexColor("#5E8294")
PAPER = HexColor("#F4FBFE")
GRID = HexColor("#D7EEF6")
ACCENT = HexColor("#5B4DFF")
CARD = HexColor("#E7F4FA")

KIND_LABELS = {
    "project": "PROJECT",
    "product": "PRODUCT",
    "running": "RUNNING",
    "upcoming": "UPCOMING",
}


def _ids(raw):
    if not isinstance(raw, list):
        return []
    chosen = []
    for item in raw:
        try:
            chosen.append(int(item))
        except (TypeError, ValueError):
            continue
    return chosen


def _lines(items):
    if not isinstance(items, list):
        return []
    return [str(item).strip() for item in items if str(item).strip()]


def _wrap(text, font, size, width):
    words = str(text or "").split()
    if not words:
        return []
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if stringWidth(trial, font, size) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _public_dir():
    return Path(getattr(settings, "FRONTEND_PUBLIC", settings.BASE_DIR.parent / "frontend" / "public"))


def _stored_path(file_field, fallback):
    if file_field:
        path = Path(file_field.path)
        if path.exists() and path.suffix.lower() != ".svg":
            return path
    fallback = (fallback or "").strip()
    if not fallback or fallback.startswith("library:"):
        return None
    if fallback.startswith("http://") or fallback.startswith("https://"):
        marker = "/media/"
        if marker not in fallback:
            return None
        fallback = "/media/" + fallback.split(marker, 1)[1]
    if fallback.startswith("/media/"):
        path = Path(settings.MEDIA_ROOT) / fallback[len("/media/") :]
    elif fallback.startswith("media/"):
        path = Path(settings.MEDIA_ROOT) / fallback[len("media/") :]
    else:
        path = _public_dir() / fallback.lstrip("/")
    if path.exists() and path.suffix.lower() != ".svg":
        return path
    return None


def _product_cover(product):
    return _stored_path(product.screen_image, product.screen_image_fallback) or _stored_path(
        product.image, product.image_fallback
    )


def _logo_path():
    logo = _public_dir() / "logo.png"
    return logo if logo.exists() else None


def _draw_grid(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setStrokeColor(GRID)
    c.setLineWidth(0.4)
    x = 0
    while x <= PAGE_W:
        c.line(x, 0, x, PAGE_H)
        x += 14 * mm
    y = 0
    while y <= PAGE_H:
        c.line(0, y, PAGE_W, y)
        y += 14 * mm


def _draw_logo(c, x, y, height=11 * mm):
    path = _logo_path()
    if not path:
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y, "Orbeetal")
        return
    image = ImageReader(str(path))
    iw, ih = image.getSize()
    width = height * (iw / ih)
    c.drawImage(image, x, y, width=width, height=height, mask="auto")


def _draw_cover_art(c):
    scale = 1.35
    box_w = 72 * mm
    box_h = 78 * mm
    c.saveState()
    c.translate(PAGE_W - 20 * mm - (box_w + 8 * mm) * scale, 26 * mm)
    c.scale(scale, scale)
    _paint_cover_art(c, 0, 0, box_w, box_h)
    c.restoreState()


def _paint_cover_art(c, x, y, w, h):
    c.setFillColor(HexColor("#D7F3F6"))
    c.circle(x + w * 0.72, y + h * 0.78, 7 * mm, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.roundRect(x, y + 8 * mm, w, h * 0.72, 8 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.roundRect(x + 8 * mm, y + h * 0.62, 28 * mm, 16 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.roundRect(x + 14 * mm, y + 28 * mm, 42 * mm, 26 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#1177C8"))
    c.rect(x + 18 * mm, y + 40 * mm, 16 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(LIME)
    c.circle(x + 44 * mm, y + 36 * mm, 5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.circle(x + w * 0.5, y + 16 * mm, 11 * mm, fill=1, stroke=0)
    c.setStrokeColor(white)
    c.setLineWidth(1.6)
    c.roundRect(x + w * 0.5 - 6 * mm, y + 12 * mm, 12 * mm, 8 * mm, 1.5 * mm, fill=0, stroke=1)
    c.setFillColor(LIME)
    for dot_x, dot_y in (
        (x - 8 * mm, y + 24 * mm),
        (x + w + 6 * mm, y + 46 * mm),
        (x + w - 4 * mm, y + h + 6 * mm),
        (x + 10 * mm, y + h + 2 * mm),
    ):
        c.circle(dot_x, dot_y, 1.3 * mm, fill=1, stroke=0)


def _draw_cover(c):
    _draw_grid(c)
    _draw_logo(c, 18 * mm, PAGE_H - 28 * mm, 12 * mm)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 34)
    c.drawString(18 * mm, PAGE_H - 58 * mm, "COMPANY")
    c.drawString(18 * mm, PAGE_H - 74 * mm, "PORTFOLIO")
    label = "www.orbeetal.com"
    c.setFont("Helvetica", 10)
    text_w = stringWidth(label, "Helvetica", 10)
    pill_w = text_w + 12 * mm
    pill_h = 8 * mm
    pill_x = 18 * mm
    pill_y = PAGE_H - 92 * mm
    c.setFillColor(NAVY)
    c.roundRect(pill_x, pill_y, pill_w, pill_h, 4 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.drawString(pill_x + 6 * mm, pill_y + 2.6 * mm, label)
    _draw_cover_art(c)


def _draw_image(c, path, x, y, width, height):
    c.setFillColor(CARD)
    c.roundRect(x, y, width, height, 3 * mm, fill=1, stroke=0)
    if not path:
        return
    try:
        image = ImageReader(str(path))
        iw, ih = image.getSize()
    except Exception:
        return
    scale = min(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(
        image,
        x + (width - dw) / 2,
        y + (height - dh) / 2,
        width=dw,
        height=dh,
        mask="auto",
        preserveAspectRatio=True,
        anchor="c",
    )


def _draw_item(c, kind, number, name, project_type, image_path, features, stack, url):
    _draw_grid(c)
    _draw_logo(c, 16 * mm, PAGE_H - 22 * mm, 9 * mm)
    label = KIND_LABELS[kind]
    type_name = (project_type or "General").upper()
    heading = f"{label} {number:02d} - {type_name}"
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(16 * mm, PAGE_H - 40 * mm, heading[:72])
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 20)
    name_lines = _wrap(name, "Helvetica-Bold", 20, PAGE_W - 32 * mm)[:2]
    y = PAGE_H - 52 * mm
    for line in name_lines:
        c.drawString(16 * mm, y, line)
        y -= 8 * mm

    margin = 16 * mm
    gap = 8 * mm
    stack_lines = _wrap(", ".join(stack), "Helvetica", 10, PAGE_W - 2 * margin)[:3] if stack else []
    url_block = 10 * mm if url else 0
    stack_block = (7 * mm + 5 * mm * len(stack_lines)) if stack_lines else 0
    footer = 12 * mm + url_block + stack_block
    text_min = 96 * mm
    max_w = PAGE_W - margin - gap - text_min - margin
    max_h = max(48 * mm, y - gap - footer)
    image_h = min(max_h, max_w * 9 / 16)
    image_w = image_h * 16 / 9
    image_x = margin
    image_y = y - gap - image_h
    _draw_image(c, image_path, image_x, image_y, image_w, image_h)

    text_x = image_x + image_w + gap
    text_w = PAGE_W - text_x - margin
    cursor = y - gap
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(text_x, cursor, "Features")
    cursor -= 6 * mm
    c.setFont("Helvetica", 10)
    shown = features[:8] or ["—"]
    for feature in shown:
        for line in _wrap(feature, "Helvetica", 10, text_w - 6 * mm)[:2]:
            if cursor < image_y:
                break
            c.setFillColor(CYAN)
            c.circle(text_x + 1.4 * mm, cursor + 1.2 * mm, 1.1 * mm, fill=1, stroke=0)
            c.setFillColor(INK)
            c.drawString(text_x + 5 * mm, cursor, line)
            cursor -= 5 * mm
        cursor -= 1 * mm

    if stack_lines:
        cursor = 12 * mm + url_block + 5 * mm * len(stack_lines)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, cursor, "Stack / tools")
        cursor -= 6 * mm
        c.setFillColor(INK)
        c.setFont("Helvetica", 10)
        for line in stack_lines:
            c.drawString(margin, cursor, line)
            cursor -= 5 * mm

    if url:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 11)
        label_w = stringWidth(url, "Helvetica-Bold", 11)
        c.drawString((PAGE_W - label_w) / 2, 12 * mm, url[:90])


def build_portfolio_pdf(project_ids, product_ids):
    projects = {
        project.id: project
        for project in Project.objects.filter(id__in=_ids(project_ids))
    }
    products = {
        product.id: product
        for product in Product.objects.filter(id__in=_ids(product_ids))
    }
    ordered_projects = sorted(projects.values(), key=lambda item: (item.sort_order, item.id))
    ordered_products = sorted(products.values(), key=lambda item: (item.sort_order, item.id))
    groups = [
        ("project", [item for item in ordered_projects if item.status == Project.STATUS_FINISHED]),
        ("product", ordered_products),
        ("running", [item for item in ordered_projects if item.status == Project.STATUS_RUNNING]),
        ("upcoming", [item for item in ordered_projects if item.status == Project.STATUS_UPCOMING]),
    ]
    pages = []
    for kind, rows in groups:
        for index, row in enumerate(rows, start=1):
            if kind == "product":
                image = _product_cover(row)
                type_name = row.project_type
            else:
                image = resolve_project_image(row)
                type_name = row.project_type
            pages.append(
                {
                    "kind": kind,
                    "number": index,
                    "name": row.name,
                    "project_type": type_name,
                    "image_path": image,
                    "features": _lines(row.features),
                    "stack": _lines(row.stack),
                    "url": row.url or "",
                }
            )
    if not pages:
        raise ValueError("Select at least one project or product.")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    pdf.setTitle("Orbeetal Company Portfolio")
    _draw_cover(pdf)
    pdf.showPage()
    for page in pages:
        _draw_item(pdf, **page)
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()
