from io import BytesIO
from pathlib import Path

from django.conf import settings
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

from .models import Product, Project
from .portfolio import resolve_project_image
from .technologies import present_stack

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 16 * mm

NAVY = HexColor("#0C2F86")
BLUE = HexColor("#1563E8")
FRAME = HexColor("#7EB4EA")
CYAN = HexColor("#2EC4E6")
INK = HexColor("#1A3358")
MUTED = HexColor("#5E7A96")
CARD = HexColor("#F4F8FD")
LINE = HexColor("#D5E4F2")
CONTACT_EMAIL = "support@orbeetal.com"
CONTACT_WEBSITE = "www.orbeetal.com"

FONT = "OrbeetalSans"
FONT_MED = "OrbeetalSans-Medium"
FONT_SEMI = "OrbeetalSans-Semi"
FONT_BOLD = "OrbeetalSans-Bold"

FEATURE_DETAILS = {
    "student management": "Manage student information and records",
    "teacher management": "Handle teacher profiles and assignments",
    "administration management": "Manage institutional operations",
    "exam management": "Create and manage exams and results",
    "class management": "Organize classes, subjects and schedules",
}

_FONTS_READY = False
_SVG_CACHE = {}


def _register_fonts():
    global _FONTS_READY
    if _FONTS_READY:
        return
    root = Path("/usr/share/fonts/truetype/noto")
    pdfmetrics.registerFont(TTFont(FONT, str(root / "NotoSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_MED, str(root / "NotoSans-Medium.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SEMI, str(root / "NotoSans-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, str(root / "NotoSans-Bold.ttf")))
    _FONTS_READY = True


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


def _site_brand():
    from .models import HomepageContent

    email = CONTACT_EMAIL
    website = CONTACT_WEBSITE
    logo = None
    obj = HomepageContent.objects.filter(pk=1).first()
    if obj:
        email = (obj.contact_email or "").strip() or email
        website = (obj.contact_website or "").strip() or website
        if obj.brand_logo:
            path = Path(obj.brand_logo.path)
            if path.exists() and path.suffix.lower() != ".svg":
                logo = path
        if logo is None:
            logo = _stored_path(None, obj.brand_logo_fallback)
    if logo is None:
        logo = _logo_path()
    return logo, website, email


def _hq_path():
    path = _public_dir() / "images" / "portfolio-headquarters.jpg"
    return path if path.exists() else None


def _tech_logo_path(logo):
    logo = (logo or "").strip()
    if not logo.startswith("/tech/"):
        return None
    path = _public_dir() / logo.lstrip("/")
    return path if path.exists() else None


def _http_url(value):
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith("www."):
        return f"https://{value}"
    return ""


def _client_website(name):
    from .models import Client

    name = (name or "").strip()
    if not name:
        return ""
    client = Client.objects.filter(name__iexact=name).exclude(url="").first()
    return _http_url(client.url) if client else ""


def _link_box(c, url, x, y, w, h):
    href = _http_url(url)
    if not href:
        return
    c.linkURL(href, (x, y, x + w, y + h), relative=0, thickness=0)


def _feature_row(feature):
    title = str(feature or "").strip()
    detail = FEATURE_DETAILS.get(title.casefold(), "")
    return title, detail


def _logo_width(height, path=None):
    path = path or _logo_path()
    if not path:
        return 28 * mm
    image = ImageReader(str(path))
    iw, ih = image.getSize()
    return height * (iw / max(ih, 1))


def _draw_logo(c, x, y, height=10 * mm, path=None):
    path = path or _logo_path()
    width = _logo_width(height, path)
    if not path:
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 13)
        c.drawString(x, y, "Orbeetal")
        return width
    c.drawImage(str(path), x, y, width=width, height=height, mask="auto")
    return width


def _image_size(path):
    try:
        image = ImageReader(str(path))
        return image.getSize()
    except Exception:
        return None


def _draw_image_contained(c, path, x, y, width, height, radius=4 * mm, cover=False):
    c.saveState()
    clip = c.beginPath()
    clip.roundRect(x, y, width, height, radius)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColor(HexColor("#EAF3FB"))
    c.rect(x, y, width, height, fill=1, stroke=0)
    if path:
        size = _image_size(path)
        if size:
            iw, ih = size
            scale = max(width / iw, height / ih) if cover else min(width / iw, height / ih)
            dw, dh = iw * scale, ih * scale
            c.drawImage(
                str(path),
                x + (width - dw) / 2,
                y + (height - dh) / 2,
                width=dw,
                height=dh,
                mask="auto",
                preserveAspectRatio=True,
                anchor="c",
            )
    c.restoreState()


def _draw_image_cover(c, path, x, y, width, height):
    size = _image_size(path)
    if not size:
        return
    iw, ih = size
    scale = max(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(
        str(path),
        x + (width - dw) / 2,
        y + (height - dh) / 2,
        width=dw,
        height=dh,
        mask="auto",
    )


def _clip_circle(c, cx, cy, radius):
    path = c.beginPath()
    path.circle(cx, cy, radius)
    c.clipPath(path, stroke=0, fill=0)


def _draw_svg(c, path, x, y, size):
    key = str(path)
    drawing = _SVG_CACHE.get(key)
    if drawing is None:
        drawing = svg2rlg(key)
        _SVG_CACHE[key] = drawing
    if drawing is None:
        return False
    c.saveState()
    scale = size / max(drawing.width, drawing.height)
    c.translate(x, y)
    c.scale(scale, scale)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()
    return True


def _dots(c, x, y, cols, rows, gap, color):
    c.setFillColor(color)
    for row in range(rows):
        for col in range(cols):
            c.circle(x + col * gap, y + row * gap, 0.45, fill=1, stroke=0)


def _mini_globe(c, x, y):
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.6)
    c.circle(x, y, 1.35 * mm, fill=0, stroke=1)
    c.ellipse(x - 0.55 * mm, y - 1.35 * mm, x + 0.55 * mm, y + 1.35 * mm, fill=0, stroke=1)
    c.line(x - 1.35 * mm, y, x + 1.35 * mm, y)


def _mini_mail(c, x, y):
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.6)
    c.rect(x, y, 3.1 * mm, 2.2 * mm, fill=0, stroke=1)
    c.line(x, y + 2.2 * mm, x + 1.55 * mm, y + 1.05 * mm)
    c.line(x + 3.1 * mm, y + 2.2 * mm, x + 1.55 * mm, y + 1.05 * mm)


def _footer(c, page_number):
    _logo, website, email = _site_brand()
    y = 9.5 * mm
    _mini_globe(c, MARGIN + 1.3 * mm, y + 1.15 * mm)
    c.setFillColor(MUTED)
    c.setFont(FONT, 8)
    c.drawString(MARGIN + 3.6 * mm, y, website)
    email_x = MARGIN + 54 * mm
    _mini_mail(c, email_x, y)
    c.setFillColor(MUTED)
    c.drawString(email_x + 4.2 * mm, y, email)
    label = f"Page {page_number:02d}"
    c.setFont(FONT_MED, 8)
    label_w = stringWidth(label, FONT_MED, 8)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(PAGE_W - MARGIN - 28 * mm, y + 1.2 * mm, PAGE_W - MARGIN - label_w - 3 * mm, y + 1.2 * mm)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MARGIN, y, label)


def _header_project(c):
    logo, _website, _email = _site_brand()
    height = 8.6 * mm
    y = PAGE_H - MARGIN - height
    _draw_logo(c, PAGE_W - MARGIN - _logo_width(height, logo), y, height, logo)


def _feature_icon(c, cx, cy, kind=0):
    c.setFillColor(BLUE)
    c.circle(cx, cy, 1.15 * mm, fill=1, stroke=0)


def _link_icon(c, x, y):
    c.setStrokeColor(BLUE)
    c.setFillColor(BLUE)
    c.setLineWidth(0.8)
    c.roundRect(x, y, 3.1 * mm, 3.1 * mm, 0.5 * mm, fill=0, stroke=1)
    c.line(x + 1.3 * mm, y + 1.5 * mm, x + 2.5 * mm, y + 2.5 * mm)
    c.line(x + 1.7 * mm, y + 2.5 * mm, x + 2.5 * mm, y + 2.5 * mm)
    c.line(x + 2.5 * mm, y + 1.7 * mm, x + 2.5 * mm, y + 2.5 * mm)


def _draw_background(c):
    c.saveState()
    clip = c.beginPath()
    clip.rect(0, 0, PAGE_W, PAGE_H)
    c.clipPath(clip, stroke=0, fill=0)
    c.linearGradient(
        0,
        PAGE_H,
        PAGE_W,
        0,
        [HexColor("#F7FBFF"), HexColor("#E4F3FC"), HexColor("#C5E2F6")],
        positions=[0, 0.48, 1],
    )
    c.restoreState()


def _cover_service_icon(c, x, y, kind):
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.7)
    if kind == 0:
        c.circle(x, y, 12, fill=0, stroke=1)
        c.line(x - 12, y, x + 12, y)
        c.arc(x - 7, y - 12, x + 7, y + 12, 90, 180)
        c.arc(x - 7, y - 12, x + 7, y + 12, 270, 180)
    elif kind == 1:
        c.roundRect(x - 12, y - 8, 24, 16, 3, fill=0, stroke=1)
        c.line(x - 6, y - 12, x + 6, y - 12)
        c.line(x, y - 8, x, y - 12)
    elif kind == 2:
        c.circle(x, y, 11, fill=0, stroke=1)
        c.circle(x - 4, y + 3, 2, fill=0, stroke=1)
        c.circle(x + 4, y - 3, 2, fill=0, stroke=1)
        c.line(x - 2, y + 2, x + 2, y - 2)
    elif kind == 3:
        c.circle(x - 5, y + 4, 5, fill=0, stroke=1)
        c.circle(x + 6, y - 4, 5, fill=0, stroke=1)
        c.line(x - 1, y + 1, x + 2, y - 2)
    else:
        c.arc(x - 13, y - 4, x - 1, y + 8, 0, 180)
        c.arc(x - 5, y - 5, x + 9, y + 9, 0, 180)
        c.line(x - 13, y - 4, x + 9, y - 4)


def _draw_cover(c):
    width, height = PAGE_W, PAGE_H
    c.setFillColor(HexColor("#F7FBFF"))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(HexColor("#E8F4FF"))
    c.circle(width * 0.69, height * 0.72, 220, fill=1, stroke=0)
    c.setFillColor(HexColor("#DCEEFF"))
    c.circle(width * 0.83, height * 0.58, 175, fill=1, stroke=0)

    c.setFillColor(BLUE)
    shape = c.beginPath()
    shape.moveTo(width * 0.69, 0)
    shape.curveTo(width * 0.78, 80, width * 0.84, 145, width, 205)
    shape.lineTo(width, 0)
    shape.close()
    c.drawPath(shape, fill=1, stroke=0)

    logo, website, email = _site_brand()
    logo_h = 11 * mm
    _draw_logo(c, 45, height - 58, logo_h, logo)
    c.setFillColor(NAVY)
    c.setFont("Helvetica", 9)
    nav_x = width - 250
    for index, item in enumerate(["Innovate", "Build", "Solve", "Grow"]):
        c.drawString(nav_x, height - 42, item)
        nav_x += stringWidth(item, "Helvetica", 9) + 18
        if index < 3:
            c.setFillColor(BLUE)
            c.drawString(nav_x - 9, height - 42, "•")
            c.setFillColor(NAVY)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(45, height - 118, "T E C H N O L O G Y   F O R   A   B E T T E R   T O M O R R O W")
    c.setFont("Helvetica-Bold", 42)
    c.drawString(45, height - 172, "COMPANY")
    c.setFillColor(BLUE)
    c.drawString(45, height - 216, "PORTFOLIO")
    c.setFillColor(BLUE)
    c.rect(45, height - 239, 65, 4, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica", 10.5)
    for index, line in enumerate(
        [
            "Orbeetal is a technology company building modern web solutions,",
            "software products and AI-powered applications to solve real-world",
            "problems.",
        ]
    ):
        c.drawString(45, height - 270 - index * 15, line)

    photo_x, photo_y, photo_r = 610, 365, 150
    c.setFillColor(HexColor("#B9DFFF"))
    c.circle(photo_x, photo_y, photo_r, fill=1, stroke=0)
    hq = _hq_path()
    if hq:
        c.saveState()
        _clip_circle(c, photo_x, photo_y, photo_r)
        _draw_image_cover(c, hq, photo_x - photo_r, photo_y - photo_r, photo_r * 2, photo_r * 2)
        c.restoreState()

    c.setFillColor(BLUE)
    for row in range(5):
        for col in range(5):
            c.circle(410 + col * 7, 360 + row * 7, 1, fill=1, stroke=0)

    c.setFillColor(BLUE)
    c.circle(745, 110, 75, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(707, 120, "Ideas")
    c.setFillColor(CYAN)
    c.drawString(707, 97, "into Impact")
    c.setFillColor(CYAN)
    c.rect(707, 83, 45, 3, fill=1, stroke=0)

    services = [
        ("Web", "Development"),
        ("Software", "Development"),
        ("AI / ML", "Solutions"),
        ("UI/UX", "Design"),
        ("Cloud", "Solutions"),
    ]
    card_x = 45
    for index, (first, second) in enumerate(services):
        c.setFillColor(white)
        c.setStrokeColor(HexColor("#CFE2F5"))
        c.setLineWidth(1)
        c.roundRect(card_x, 58, 100, 78, 10, fill=1, stroke=1)
        _cover_service_icon(c, card_x + 50, 110, index)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7.8)
        c.drawCentredString(card_x + 50, 82, first)
        c.drawCentredString(card_x + 50, 70, second)
        card_x += 108

    c.setFillColor(NAVY)
    c.setFont("Helvetica", 8)
    c.drawString(45, 24, website)
    c.setStrokeColor(HexColor("#9BBFE8"))
    c.setLineWidth(1)
    c.line(205, 22, 205, 34)
    c.drawString(225, 24, email)
    c.setStrokeColor(HexColor("#A9C8E9"))
    c.line(width - 155, 28, width - 95, 28)
    c.setFillColor(MUTED)
    c.drawRightString(width - 45, 24, "Page 01")


def _section_box(c, x, y, w, h):
    c.setFillColor(HexColor("#F4F8FD"))
    c.setStrokeColor(FRAME)
    c.setLineWidth(1.2)
    c.roundRect(x, y, w, h, 3 * mm, fill=1, stroke=1)


def _stack_badges(c, stack, x, y, max_w):
    items = []
    for item in (stack or [])[:3]:
        name = item.get("name") or ""
        if not name:
            continue
        logo = _tech_logo_path(item.get("logo"))
        label_w = stringWidth(name, FONT_MED, 7.5)
        badge_w = 6.2 * mm + (4.6 * mm if logo else 0) + label_w
        items.append((item, logo, badge_w))
    if not items:
        return y
    rows = [[]]
    row_width = 0
    for entry in items:
        badge_w = entry[2]
        if rows[-1] and row_width + badge_w > max_w:
            rows.append([entry])
            row_width = badge_w + 1.8 * mm
        else:
            rows[-1].append(entry)
            row_width += badge_w + 1.8 * mm
    box_top = y + 4.6 * mm
    box_bottom = y - 8 * mm - (len(rows) - 1) * 8.4 * mm - 4.2 * mm
    _section_box(c, x - 3 * mm, box_bottom, max_w + 5 * mm, box_top - box_bottom)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 11)
    c.drawString(x, y, "Technology Stack")
    row_y = y - 8 * mm
    for row in rows:
        cursor = x
        for item, logo, badge_w in row:
            name = item.get("name") or ""
            c.setFillColor(white)
            c.setStrokeColor(LINE)
            c.setLineWidth(0.7)
            c.roundRect(cursor, row_y - 1.5 * mm, badge_w, 6.6 * mm, 3.2 * mm, fill=1, stroke=1)
            if logo:
                _draw_svg(c, logo, cursor + 1.5 * mm, row_y - 0.15 * mm, 3.8 * mm)
                text_x = cursor + 6 * mm
            else:
                text_x = cursor + 2.2 * mm
            c.setFillColor(INK)
            c.setFont(FONT_MED, 7.5)
            c.drawString(text_x, row_y + 0.55 * mm, name)
            cursor += badge_w + 1.8 * mm
        row_y -= 8.4 * mm
    return box_bottom


def _draw_photo(c, image_path, x, y, w, h):
    radius = 4 * mm
    _draw_image_contained(c, image_path, x, y, w, h, radius)
    c.setStrokeColor(FRAME)
    c.setLineWidth(1.2)
    c.roundRect(x, y, w, h, radius, fill=0, stroke=1)


def _draw_project(c, page, page_number):
    _draw_background(c)
    _header_project(c)

    logo, _website, _email = _site_brand()
    logo_w = _logo_width(8.6 * mm, logo)
    title_w = PAGE_W - 2 * MARGIN - logo_w - 8 * mm
    content_w = PAGE_W - 2 * MARGIN
    title_y = PAGE_H - 23 * mm
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 20)
    for line in _wrap(page["name"], FONT_BOLD, 20, title_w)[:2]:
        c.drawString(MARGIN, title_y, line)
        title_y -= 8 * mm

    if page.get("description"):
        c.setFillColor(INK)
        c.setFont(FONT, 9)
        title_y -= 1 * mm
        for line in _wrap(page["description"], FONT, 9, content_w)[:2]:
            c.drawString(MARGIN, title_y, line)
            title_y -= 4.2 * mm

    gap = 6 * mm
    photo_x = MARGIN
    photo_top = title_y - 5 * mm
    content_bottom = 16 * mm
    full_w = PAGE_W - 2 * MARGIN - 76 * mm - gap
    full_h = max(40 * mm, photo_top - content_bottom)
    photo_w = full_w
    photo_h = photo_w * 9 / 16
    if photo_h > full_h:
        photo_h = full_h
        photo_w = photo_h * 16 / 9
    photo_y = photo_top - photo_h
    _draw_photo(c, page.get("image_path"), photo_x, photo_y, photo_w, photo_h)

    right_x = photo_x + photo_w + gap
    right_w = PAGE_W - MARGIN - right_x
    heading_pad = 5.6 * mm
    heading_drop = 9.2 * mm
    cursor = photo_top - heading_pad
    features = page.get("features") or []
    shown = features[:5]
    feature_drop = 0
    for feature in shown:
        _, detail = _feature_row(feature)
        feature_drop += 13 * mm if detail else 10.5 * mm
    if shown:
        box_top = photo_top
        box_bottom = cursor - heading_drop - feature_drop + 2.5 * mm
        _section_box(c, right_x - 3 * mm, box_bottom, right_w + 5 * mm, box_top - box_bottom)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 14)
    c.drawString(right_x, cursor, "Key Features")
    cursor -= heading_drop
    for index, feature in enumerate(shown):
        title, detail = _feature_row(feature)
        _feature_icon(c, right_x + 1.6 * mm, cursor + 3.2 * mm, index)
        c.setFillColor(NAVY)
        c.setFont(FONT_SEMI, 10)
        feature_title = _wrap(title, FONT_SEMI, 10, right_w - 8 * mm)[:1]
        c.drawString(right_x + 5.2 * mm, cursor + 1.8 * mm, feature_title[0] if feature_title else "")
        if detail:
            c.setFillColor(MUTED)
            c.setFont(FONT, 9)
            detail_line = _wrap(detail, FONT, 9, right_w - 8 * mm)[:1]
            if detail_line:
                c.drawString(right_x + 5.2 * mm, cursor - 2.8 * mm, detail_line[0])
            cursor -= 13 * mm
        else:
            cursor -= 10.5 * mm
    cursor -= 5.2 * mm
    _stack_badges(c, page.get("stack") or [], right_x, cursor, right_w)

    blocks = []
    if page.get("client_name"):
        blocks.append(
            {
                "label": "Client / Organization",
                "value": page["client_name"],
                "extra": page.get("client_role") or "",
                "kind": "org",
                "href": page.get("client_url") or "",
            }
        )
    if page.get("url"):
        blocks.append(
            {
                "label": "Live Project",
                "value": page["url"],
                "extra": "link",
                "kind": "link",
                "href": page["url"],
            }
        )
    info_x = photo_x + 3 * mm
    info_w = photo_w - 14 * mm
    info_y = content_bottom + max(0, len(blocks[:2]) - 1) * 18 * mm
    for block in blocks[:2]:
        label = block["label"]
        value = block["value"]
        extra = block["extra"]
        kind = block["kind"]
        box_x = photo_x
        box_y = info_y - 1.5 * mm
        box_w = photo_w
        box_h = 14 * mm
        _section_box(c, box_x, box_y, box_w, box_h)
        c.setFillColor(HexColor("#E7F1FB"))
        c.circle(info_x + 3.2 * mm, info_y + 6 * mm, 3.6 * mm, fill=1, stroke=0)
        if kind == "link":
            _link_icon(c, info_x + 1.7 * mm, info_y + 4.6 * mm)
        else:
            c.setFillColor(BLUE)
            c.roundRect(info_x + 1.6 * mm, info_y + 4.4 * mm, 3.2 * mm, 2.6 * mm, 0.4 * mm, fill=1, stroke=0)
            c.setFillColor(white)
            c.circle(info_x + 3.2 * mm, info_y + 6.6 * mm, 0.65 * mm, fill=1, stroke=0)
        text_x = info_x + 8.4 * mm
        c.setFillColor(MUTED)
        c.setFont(FONT_MED, 6.5)
        c.drawString(text_x, info_y + 8.6 * mm, label)
        if extra == "link":
            c.setFillColor(BLUE)
            c.setFont(FONT_MED, 7.5)
            url = value
            while url and stringWidth(url, FONT_MED, 7.5) > info_w:
                url = url[:-1]
            if url != value:
                url = url[:-1] + "…"
            c.drawString(text_x, info_y + 4.4 * mm, url)
        else:
            c.setFillColor(NAVY)
            c.setFont(FONT_BOLD, 8)
            shown = _wrap(value, FONT_BOLD, 8, info_w)[:1]
            if shown:
                c.drawString(text_x, info_y + 4.8 * mm, shown[0])
            if extra:
                c.setFillColor(MUTED)
                c.setFont(FONT, 6.5)
                role = _wrap(extra, FONT, 6.5, info_w)[:1]
                if role:
                    c.drawString(text_x, info_y + 1.6 * mm, role[0])
        _link_box(c, block.get("href"), box_x, box_y, box_w, box_h)
        info_y -= 16 * mm
    _footer(c, page_number)


def build_portfolio_pdf(project_ids, product_ids):
    _register_fonts()
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
                client_name = ""
                client_role = ""
            else:
                image = resolve_project_image(row)
                client_name = row.related_name or ""
                client_role = row.related_role or ""
            pages.append(
                {
                    "kind": kind,
                    "number": index,
                    "name": row.name,
                    "description": row.description or "",
                    "image_path": image,
                    "features": _lines(row.features),
                    "stack": present_stack(row.stack)[:3],
                    "url": row.url or "",
                    "client_name": client_name,
                    "client_role": client_role,
                    "client_url": _client_website(client_name),
                }
            )
    if not pages:
        raise ValueError("Select at least one project or product.")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    pdf.setTitle("Orbeetal Company Portfolio")
    _draw_cover(pdf)
    pdf.showPage()
    for offset, page in enumerate(pages, start=2):
        _draw_project(pdf, page, offset)
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()
