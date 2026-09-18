from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from PIL import Image as PILImage
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.pdfgen import canvas as pdfcanvas

from .models import HomepageContent, Project, Service, Testimonial
from .portfolio import active_projects, project_features, resolve_project_image

PAGE_W, PAGE_H = A4

NAVY = HexColor("#12344D")
CYAN = HexColor("#27BFC7")
LIME = HexColor("#96D83A")
PAPER = HexColor("#C8E5F1")
CARD = HexColor("#E7F4FA")
CARD_ALT = HexColor("#D7EEF5")
INK = HexColor("#102C40")
MUTED = HexColor("#63869A")
SOFT = HexColor("#9BB6C4")
NAVY_DEEP = HexColor("#0C2838")

COMPANY = {
    "name": "Orbeetal",
    "tagline": "Digital products built for real impact.",
    "origin": "https://www.orbeetal.com",
    "email": "support@orbeetal.com",
    "phone": "+88 01627480049",
    "location": "Dhaka, Bangladesh",
    "member": "BASIS Member",
    "linkedin": "https://www.linkedin.com/company/orbeetal/",
    "mission": (
        "To engineer digital products that elevate businesses above the "
        "competition - combining technical precision, creative excellence, "
        "and strategic thinking to deliver measurable impact."
    ),
    "vision": (
        "To become the most trusted technology partner for ambitious businesses "
        "in South Asia and beyond - known for our integrity, innovation, and "
        "the lasting success of our clients."
    ),
}

WHY_POINTS = [
    ("01", "One accountable technology partner", "Strategy, design, engineering and growth in a single team."),
    ("02", "Product-focused engineering", "We build durable products, not one-off deliverables."),
    ("03", "Design + development under one roof", "Interface, architecture and delivery stay aligned."),
    ("04", "Business-oriented solutions", "Every build is measured against a commercial outcome."),
    ("05", "Long-term technical support", "Maintenance and iteration after launch, not just handover."),
]

INDUSTRY_RULES = [
    (("news", "reporter", "media", "journal"), "Media"),
    (("july", "heroes"), "Civic & public memory"),
    (("education", "school", "learning", "exam", "student"), "Education"),
    (("plant", "agricultur", "farm", "grow"), "Agriculture"),
    (("book", "order", "inventory", "commerce", "shop"), "Business"),
    (("burial", "cemetery", "funeral"), "Community services"),
    (("hvac", "filter", "cleanroom", "air"), "HVAC & Engineering"),
    (("academy", "training", "certif", "cloudx"), "Training & Development"),
]

CATEGORY_COPY = {
    Project.CATEGORY_OWN: (
        "Our products",
        "Products built and owned by Orbeetal.",
    ),
    Project.CATEGORY_PARTNERSHIP: (
        "Partnerships",
        "Products developed together with our partners.",
    ),
    Project.CATEGORY_CLIENT: (
        "Client projects",
        "Technology delivered for organisations and businesses.",
    ),
}

ACCENTS = (CYAN, LIME, NAVY)


def _plain(value):
    return " ".join(str(value or "").split())


def _safe(value):
    text = (
        _plain(value)
        .replace("—", "-")
        .replace("–", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _generated_on():
    return timezone.now()


def _public_dir():
    return Path(getattr(settings, "FRONTEND_PUBLIC", settings.BASE_DIR.parent / "frontend" / "public"))


def _homepage():
    return HomepageContent.objects.first()


def _about_copy():
    page = _homepage()
    body = _plain(getattr(page, "about_body", ""))
    return body or (
        "Orbeetal is a forward-thinking software company based in Dhaka, Bangladesh. "
        "We specialise in web and mobile development, AI-powered systems and "
        "cybersecurity, helping businesses compete and grow."
    )


def _pretty_stat_label(label):
    low = (label or "").lower()
    if "client" in low:
        return "Clients"
    if "active" in low:
        return "Active"
    if "project" in low:
        return "Projects"
    return label


def _stats():
    page = _homepage()
    raw = getattr(page, "stats", None) or []
    items = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        value = str(item.get("value", "")).strip()
        suffix = str(item.get("suffix", "")).strip()
        label = str(item.get("label", "")).strip()
        if value and label:
            items.append((f"{value}{suffix}", _pretty_stat_label(label)))
        if len(items) == 3:
            break
    return items or [("50+", "Clients"), ("120+", "Projects"), ("15+", "Active")]


def _styles():
    return {
        "kicker": ParagraphStyle(
            "Kicker",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=CYAN,
            spaceAfter=4,
        ),
        "display": ParagraphStyle(
            "Display",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=NAVY,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=INK,
            spaceAfter=6,
        ),
        "muted": ParagraphStyle(
            "Muted",
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=MUTED,
        ),
        "card_title": ParagraphStyle(
            "CardTitle",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=NAVY,
        ),
        "card_body": ParagraphStyle(
            "CardBody",
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=INK,
        ),
        "label": ParagraphStyle(
            "Label",
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9,
            textColor=CYAN,
        ),
        "quote": ParagraphStyle(
            "Quote",
            fontName="Helvetica-Oblique",
            fontSize=13,
            leading=18,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "quote_small": ParagraphStyle(
            "QuoteSmall",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=12,
            textColor=INK,
        ),
        "center_name": ParagraphStyle(
            "CenterName",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "center_role": ParagraphStyle(
            "CenterRole",
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "why_title": ParagraphStyle(
            "WhyTitle",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=NAVY,
        ),
        "link": ParagraphStyle(
            "Link",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=CYAN,
        ),
        "right_num": ParagraphStyle(
            "RightNum",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=SOFT,
            alignment=TA_RIGHT,
        ),
    }


def _para(text, style, width):
    paragraph = Paragraph(_safe(text), style)
    w, h = paragraph.wrap(width, 800)
    return paragraph, w, h


def _draw_para(canv, text, style, x, y_top, width):
    paragraph, _, h = _para(text, style, width)
    paragraph.drawOn(canv, x, y_top - h)
    return h


def _jpeg_cover(path, width_pt, height_pt):
    if not path:
        return None
    try:
        with PILImage.open(path) as source:
            image = source.convert("RGB")
            target_ratio = width_pt / height_pt
            src_ratio = image.width / max(image.height, 1)
            if src_ratio > target_ratio:
                new_w = max(int(image.height * target_ratio), 1)
                left = (image.width - new_w) // 2
                image = image.crop((left, 0, left + new_w, image.height))
            else:
                new_h = max(int(image.width / target_ratio), 1)
                top = (image.height - new_h) // 2
                image = image.crop((0, top, image.width, top + new_h))
            image = image.resize(
                (max(int(width_pt * 2), 1), max(int(height_pt * 2), 1)),
                PILImage.Resampling.LANCZOS,
            )
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=82, optimize=True)
            return buffer.getvalue()
    except Exception:
        return None


def _reader(data):
    if not data:
        return None
    return ImageReader(BytesIO(data))


def _clip_round(canv, x, y, w, h, radius=10):
    path = canv.beginPath()
    path.roundRect(x, y, w, h, radius)
    canv.clipPath(path, stroke=0, fill=0)


def _draw_photo(canv, data, x, y, w, h, radius=10):
    reader = _reader(data)
    if not reader:
        canv.setFillColor(NAVY)
        canv.roundRect(x, y, w, h, radius, fill=1, stroke=0)
        return
    canv.saveState()
    _clip_round(canv, x, y, w, h, radius)
    canv.drawImage(reader, x, y, w, h, mask="auto")
    canv.restoreState()


def _industry_for(project):
    hay = " ".join(
        [
            project.name or "",
            project.description or "",
            " ".join(project_features(project)),
        ]
    ).lower()
    for needles, label in INDUSTRY_RULES:
        if any(needle in hay for needle in needles):
            return label
    return "Digital products"


def _industries(projects):
    seen = []
    for project in projects:
        label = _industry_for(project)
        if label not in seen:
            seen.append(label)
    return seen


def _find_named(projects, *needles):
    for needle in needles:
        for project in projects:
            if needle.lower() in (project.name or "").lower():
                return project
    return None


def _chunk(items, size):
    return [items[index : index + size] for index in range(0, len(items), size)]


def _short_caps(project, limit=3):
    labels = []
    for item in project_features(project):
        text = _plain(item).rstrip(".")
        if len(text) > 36:
            text = text[:34].rsplit(" ", 1)[0]
        if text:
            labels.append(text)
        if len(labels) == limit:
            break
    return labels


def _service_caps(service, limit=3):
    raw = service.content if isinstance(service.content, list) else []
    labels = []
    for item in raw:
        text = _plain(item).rstrip(".")
        low = text.lower()
        if " like " in low:
            text = text.split(" like ", 1)[-1]
            text = text.replace(" and ", ", ")
        elif low.startswith("end-to-end") and " from " in low:
            text = text.split(" from ", 1)[0].strip()
        else:
            for sep in (" for ", " to ", " that "):
                if sep.strip() in f" {low} ":
                    left = text.split(sep.strip(), 1)[0].strip()
                    if len(left) >= 12:
                        text = left
                        break
        if len(text) > 40:
            text = " ".join(text.split()[:5])
        if text:
            labels.append(text)
        if len(labels) == limit:
            break
    return labels


def _initials(name):
    parts = [part for part in (name or "").split() if part]
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return (parts[0][:2] if parts else "OR").upper()


# ---------------------------------------------------------------------------
# Decorative drawing
# ---------------------------------------------------------------------------

def _draw_mark(canv, x, y, size=12 * mm, fill=LIME, glyph="O"):
    canv.setFillColor(fill)
    canv.roundRect(x, y, size, size, size * 0.22, fill=1, stroke=0)
    canv.setFillColor(NAVY)
    canv.setFont("Helvetica-Bold", size * 0.52)
    canv.drawCentredString(x + size / 2, y + size * 0.28, glyph)


def _draw_abstract(canv, cx, cy):
    canv.saveState()
    canv.setStrokeColor(Color(0.15, 0.75, 0.78, alpha=0.35))
    canv.setLineWidth(1.1)
    for radius in (38 * mm, 52 * mm, 68 * mm):
        canv.circle(cx, cy, radius, fill=0, stroke=1)
    canv.setFillColor(Color(0.15, 0.75, 0.78, alpha=0.08))
    canv.circle(cx, cy, 28 * mm, fill=1, stroke=0)
    canv.setFillColor(LIME)
    canv.circle(cx, cy, 7 * mm, fill=1, stroke=0)
    canv.setFillColor(NAVY)
    canv.setFont("Helvetica-Bold", 11)
    canv.drawCentredString(cx, cy - 3.5, "O")

    canv.setFillColor(Color(0.59, 0.85, 0.23, alpha=0.9))
    nodes = [
        (cx + 46 * mm, cy + 18 * mm, 5.5 * mm),
        (cx - 40 * mm, cy + 32 * mm, 4 * mm),
        (cx + 22 * mm, cy - 44 * mm, 6 * mm),
        (cx - 48 * mm, cy - 10 * mm, 3.5 * mm),
        (cx + 54 * mm, cy - 22 * mm, 3 * mm),
    ]
    canv.setStrokeColor(Color(0.59, 0.85, 0.23, alpha=0.55))
    canv.setLineWidth(0.8)
    for x, y, _r in nodes:
        canv.line(cx, cy, x, y)
    for x, y, radius in nodes:
        canv.setFillColor(CYAN if radius > 4.5 * mm else LIME)
        canv.circle(x, y, radius, fill=1, stroke=0)

    canv.setFillColor(Color(1, 1, 1, alpha=0.18))
    for col in range(-4, 5):
        for row in range(-4, 5):
            if col * col + row * row in (0, 1):
                continue
            canv.circle(cx + col * 9 * mm, cy + row * 9 * mm, 0.7 * mm, fill=1, stroke=0)
    canv.restoreState()


def _draw_inner_chrome(canv, _doc):
    canv.saveState()
    canv.setFillColor(PAPER)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canv.setFillColor(CYAN)
    canv.rect(0, PAGE_H - 5.5 * mm, PAGE_W, 5.5 * mm, fill=1, stroke=0)
    canv.setFillColor(LIME)
    canv.rect(0, 0, 6 * mm, PAGE_H, fill=1, stroke=0)
    canv.setFillColor(NAVY)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawString(16 * mm, PAGE_H - 13 * mm, "ORBEETAL")
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 8)
    canv.drawRightString(PAGE_W - 14 * mm, PAGE_H - 13 * mm, "Company Portfolio")
    canv.setStrokeColor(CYAN)
    canv.setLineWidth(0.8)
    canv.line(16 * mm, PAGE_H - 16 * mm, PAGE_W - 14 * mm, PAGE_H - 16 * mm)
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 7.5)
    canv.drawString(16 * mm, 8 * mm, COMPANY["origin"].replace("https://", ""))
    canv.setFillColor(NAVY)
    canv.circle(PAGE_W - 18 * mm, 9.5 * mm, 6.2 * mm, fill=1, stroke=0)
    canv.setFillColor(white)
    canv.setFont("Helvetica-Bold", 7)
    canv.drawCentredString(PAGE_W - 18 * mm, 7.8 * mm, f"{canv.getPageNumber():02d}")
    canv.restoreState()


def _draw_cover(canv, _doc):
    stats = _stats()
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canv.setFillColor(LIME)
    canv.rect(0, 0, 8 * mm, PAGE_H, fill=1, stroke=0)
    canv.setFillColor(CYAN)
    canv.rect(8 * mm, PAGE_H - 7 * mm, PAGE_W - 8 * mm, 7 * mm, fill=1, stroke=0)
    _draw_abstract(canv, PAGE_W * 0.72, PAGE_H * 0.46)

    canv.setFillColor(CYAN)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawString(
        22 * mm,
        PAGE_H - 28 * mm,
        f"{COMPANY['member'].upper()}  ·  {COMPANY['location'].upper()}",
    )
    canv.setFillColor(Color(1, 1, 1, alpha=0.7))
    canv.setFont("Helvetica", 8)
    canv.drawRightString(PAGE_W - 18 * mm, PAGE_H - 28 * mm, _generated_on().strftime("%B %Y"))

    _draw_mark(canv, 22 * mm, PAGE_H - 58 * mm, 14 * mm)
    canv.setFillColor(white)
    canv.setFont("Helvetica-Bold", 28)
    canv.drawString(40 * mm, PAGE_H - 53 * mm, "ORBEETAL")

    canv.setFillColor(CYAN)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawString(22 * mm, PAGE_H - 74 * mm, "COMPANY PORTFOLIO")

    canv.setFillColor(white)
    canv.setFont("Helvetica-Bold", 26)
    canv.drawString(22 * mm, PAGE_H - 96 * mm, "Digital products")
    canv.setFillColor(LIME)
    canv.drawString(22 * mm, PAGE_H - 108 * mm, "built for real impact.")

    canv.setStrokeColor(CYAN)
    canv.setLineWidth(2)
    canv.line(22 * mm, PAGE_H - 118 * mm, 78 * mm, PAGE_H - 118 * mm)

    y = 38 * mm
    canv.setStrokeColor(Color(0.15, 0.75, 0.78, alpha=0.5))
    canv.setLineWidth(0.6)
    canv.line(22 * mm, y + 28 * mm, PAGE_W - 18 * mm, y + 28 * mm)
    slot = 48 * mm
    for index, (value, label) in enumerate(stats[:3]):
        x = 22 * mm + index * slot
        canv.setFillColor(LIME if index == 1 else white)
        canv.setFont("Helvetica-Bold", 20)
        canv.drawString(x, y + 10 * mm, value)
        canv.setFillColor(CYAN)
        canv.setFont("Helvetica", 8)
        canv.drawString(x, y + 3 * mm, label.upper())
    canv.restoreState()


def _draw_cta_chrome(canv, _doc):
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canv.setFillColor(LIME)
    canv.rect(0, 0, 8 * mm, PAGE_H, fill=1, stroke=0)
    canv.setFillColor(CYAN)
    canv.rect(8 * mm, PAGE_H - 7 * mm, PAGE_W - 8 * mm, 7 * mm, fill=1, stroke=0)
    _draw_abstract(canv, PAGE_W * 0.78, PAGE_H * 0.22)

    canv.setFillColor(CYAN)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawString(22 * mm, PAGE_H - 28 * mm, "START A PROJECT")

    canv.setFillColor(white)
    canv.setFont("Helvetica-Bold", 28)
    canv.drawString(22 * mm, PAGE_H - 52 * mm, "Let's build something")
    canv.setFillColor(LIME)
    canv.drawString(22 * mm, PAGE_H - 66 * mm, "that matters.")

    canv.setFillColor(Color(1, 1, 1, alpha=0.88))
    canv.setFont("Helvetica", 11)
    canv.drawString(22 * mm, PAGE_H - 84 * mm, "A single partner for strategy,")
    canv.drawString(22 * mm, PAGE_H - 91 * mm, "design, engineering and growth.")

    canv.setStrokeColor(CYAN)
    canv.setLineWidth(1.4)
    canv.line(22 * mm, PAGE_H - 104 * mm, 92 * mm, PAGE_H - 104 * mm)

    lines = [
        COMPANY["location"],
        COMPANY["email"],
        COMPANY["phone"],
        COMPANY["origin"].replace("https://", ""),
    ]
    y = PAGE_H - 124 * mm
    canv.setFillColor(white)
    canv.setFont("Helvetica", 11)
    for line in lines:
        canv.drawString(22 * mm, y, line)
        y -= 8 * mm

    canv.setFillColor(CYAN)
    canv.roundRect(22 * mm, 58 * mm, 42 * mm, 11 * mm, 5.5, fill=1, stroke=0)
    canv.setFillColor(NAVY)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawCentredString(43 * mm, 61.5 * mm, "LinkedIn")
    canv.linkURL(COMPANY["linkedin"], (22 * mm, 58 * mm, 64 * mm, 69 * mm), relative=0, thickness=0)
    canv.setStrokeColor(LIME)
    canv.setLineWidth(1.2)
    canv.roundRect(68 * mm, 58 * mm, 42 * mm, 11 * mm, 5.5, fill=0, stroke=1)
    canv.setFillColor(LIME)
    canv.drawCentredString(89 * mm, 61.5 * mm, "Visit website")
    canv.linkURL(COMPANY["origin"], (68 * mm, 58 * mm, 110 * mm, 69 * mm), relative=0, thickness=0)
    canv.linkURL(f"mailto:{COMPANY['email']}", (22 * mm, PAGE_H - 140 * mm, 90 * mm, PAGE_H - 128 * mm), relative=0, thickness=0)

    canv.setFillColor(white)
    canv.roundRect(PAGE_W - 58 * mm, PAGE_H - 152 * mm, 40 * mm, 40 * mm, 8, fill=1, stroke=0)
    qr = QrCodeWidget(COMPANY["origin"])
    qr.barFillColor = NAVY
    qr.barStrokeColor = NAVY
    bounds = qr.getBounds()
    qw, qh = bounds[2] - bounds[0], bounds[3] - bounds[1]
    size = 32 * mm
    drawing = Drawing(size, size, transform=[size / qw, 0, 0, size / qh, 0, 0])
    drawing.add(qr)
    drawing.drawOn(canv, PAGE_W - 54 * mm, PAGE_H - 148 * mm)

    canv.setFillColor(Color(1, 1, 1, alpha=0.7))
    canv.setFont("Helvetica", 7)
    canv.drawString(PAGE_W - 54 * mm, PAGE_H - 158 * mm, "Scan to visit")

    _draw_mark(canv, 22 * mm, 26 * mm, 11 * mm)
    canv.setFillColor(white)
    canv.setFont("Helvetica-Bold", 16)
    canv.drawString(36 * mm, 28.5 * mm, "ORBEETAL")
    canv.restoreState()


# ---------------------------------------------------------------------------
# Flowables
# ---------------------------------------------------------------------------

class SectionHead(Flowable):
    def __init__(self, kicker, title, width, subtitle=""):
        super().__init__()
        self.kicker = kicker
        self.title = title
        self.subtitle = subtitle
        self._w = width
        styles = _styles()
        self._bits = []
        self._h = 2
        para, _, h = _para(kicker.upper(), styles["kicker"], width)
        self._bits.append((para, h))
        self._h += h + 2
        para, _, h = _para(title, styles["display"], width)
        self._bits.append((para, h))
        self._h += h
        if subtitle:
            para, _, h = _para(subtitle, styles["muted"], width)
            self._bits.append((para, h))
            self._h += h + 4
        else:
            self._h += 6

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        y = self._h
        for para, h in self._bits:
            y -= h
            para.drawOn(self.canv, 0, y)
            y -= 2
        self.canv.setFillColor(CYAN)
        self.canv.rect(0, 0, 18 * mm, 1.6, fill=1, stroke=0)


class StatRow(Flowable):
    def __init__(self, width, height=28 * mm):
        super().__init__()
        self._w = width
        self._h = height
        self.items = _stats()[:3]

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        if not self.items:
            return
        gap = 5 * mm
        card_w = (self._w - gap * (len(self.items) - 1)) / len(self.items)
        for index, (value, label) in enumerate(self.items):
            x = index * (card_w + gap)
            self.canv.setFillColor(NAVY if index == 1 else CARD)
            self.canv.roundRect(x, 0, card_w, self._h, 8, fill=1, stroke=0)
            self.canv.setFillColor(LIME if index == 1 else CYAN)
            self.canv.roundRect(x, self._h - 4, 16 * mm, 4, 2, fill=1, stroke=0)
            self.canv.setFillColor(white if index == 1 else NAVY)
            self.canv.setFont("Helvetica-Bold", 18)
            self.canv.drawString(x + 8, 12 * mm, value)
            self.canv.setFillColor(CYAN if index == 1 else MUTED)
            self.canv.setFont("Helvetica", 8)
            self.canv.drawString(x + 8, 6 * mm, label.upper())


class SplitCards(Flowable):
    def __init__(self, left_title, left_body, right_title, right_body, width, height=48 * mm):
        super().__init__()
        self.left_title = left_title
        self.left_body = left_body
        self.right_title = right_title
        self.right_body = right_body
        self._w = width
        self._h = height

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        styles = _styles()
        gap = 5 * mm
        card_w = (self._w - gap) / 2
        for index, (title, body) in enumerate(
            ((self.left_title, self.left_body), (self.right_title, self.right_body))
        ):
            x = index * (card_w + gap)
            self.canv.setFillColor(CARD)
            self.canv.roundRect(x, 0, card_w, self._h, 10, fill=1, stroke=0)
            self.canv.setFillColor(LIME if index else CYAN)
            self.canv.rect(x, 8, 3.2, self._h - 16, fill=1, stroke=0)
            _draw_para(self.canv, title.upper(), styles["label"], x + 10, self._h - 8, card_w - 16)
            _draw_para(self.canv, body, styles["card_body"], x + 10, self._h - 18, card_w - 18)


class PhotoBand(Flowable):
    def __init__(self, width, height=52 * mm):
        super().__init__()
        self._w = width
        self._h = height
        path = _public_dir() / "images" / "teams-1.png"
        self.data = _jpeg_cover(path if path.exists() else None, width, height)

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        _draw_photo(self.canv, self.data, 0, 0, self._w, self._h, 12)
        self.canv.setFillColor(LIME)
        self.canv.circle(18 * mm, 12 * mm, 7 * mm, fill=1, stroke=0)
        self.canv.setFillColor(CYAN)
        self.canv.circle(self._w - 16 * mm, self._h - 12 * mm, 5 * mm, fill=1, stroke=0)


class ServiceGrid(Flowable):
    def __init__(self, services, width):
        super().__init__()
        self.services = services[:6]
        self._w = width
        self.rows = max((len(self.services) + 1) // 2, 1)
        self.card_h = 72 * mm
        self._h = self.rows * self.card_h + (self.rows - 1) * 5 * mm

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        styles = _styles()
        gap = 5 * mm
        card_w = (self._w - gap) / 2
        for index, service in enumerate(self.services):
            col = index % 2
            row = index // 2
            x = col * (card_w + gap)
            y = self._h - (row + 1) * self.card_h - row * gap
            accent = ACCENTS[index % 3]
            self.canv.setFillColor(CARD if index % 2 == 0 else CARD_ALT)
            self.canv.roundRect(x, y, card_w, self.card_h, 10, fill=1, stroke=0)
            self.canv.setFillColor(accent)
            self.canv.roundRect(x, y + 8, 3.4, self.card_h - 16, 1.6, fill=1, stroke=0)
            self.canv.setFillColor(NAVY)
            self.canv.circle(x + 16 * mm, y + self.card_h - 14 * mm, 7 * mm, fill=1, stroke=0)
            self.canv.setFillColor(LIME if accent == NAVY else accent)
            self.canv.setFont("Helvetica-Bold", 8)
            self.canv.drawCentredString(
                x + 16 * mm, y + self.card_h - 16 * mm, f"{index + 1:02d}"
            )
            _draw_para(
                self.canv,
                service.name,
                styles["card_title"],
                x + 26 * mm,
                y + self.card_h - 8 * mm,
                card_w - 32 * mm,
            )
            _draw_para(
                self.canv,
                service.description or "",
                styles["card_body"],
                x + 10,
                y + self.card_h - 24 * mm,
                card_w - 18,
            )
            caps = _service_caps(service)
            cy = y + 24 * mm
            for cap in caps:
                self.canv.setFillColor(accent)
                self.canv.circle(x + 12, cy - 2, 1.5, fill=1, stroke=0)
                used = _draw_para(
                    self.canv,
                    cap,
                    styles["card_body"],
                    x + 16,
                    cy + 6,
                    card_w - 26,
                )
                cy -= max(used, 5 * mm)


class FeaturedSpread(Flowable):
    def __init__(self, projects, width):
        super().__init__()
        self.projects = [item for item in projects if item]
        self._w = width
        self.top_h = 90 * mm
        self.wide_h = 88 * mm
        self._h = self.top_h + 5 * mm + self.wide_h

    def wrap(self, *_args):
        return self._w, self._h

    def _card(self, project, x, y, w, h, accent):
        styles = _styles()
        path = resolve_project_image(project) if project else None
        data = _jpeg_cover(path, w, h)
        _draw_photo(self.canv, data, x, y, w, h, 12)
        self.canv.setFillColor(Color(0.07, 0.16, 0.24, alpha=0.18))
        self.canv.roundRect(x, y, w, h, 12, fill=1, stroke=0)
        self.canv.saveState()
        path = self.canv.beginPath()
        path.roundRect(x, y, w, h, 12)
        self.canv.clipPath(path, stroke=0, fill=0)
        self.canv.setFillColor(Color(0.07, 0.16, 0.24, alpha=0.78))
        self.canv.rect(x, y, w, 22 * mm, fill=1, stroke=0)
        self.canv.restoreState()
        self.canv.setFillColor(accent)
        self.canv.roundRect(x + 10, y + 8, 16, 4, 2, fill=1, stroke=0)
        name = project.name if project else ""
        _draw_para(self.canv, name, ParagraphStyle(
            "FeatName",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=white,
        ), x + 10, y + 20 * mm, w - 20)

    def draw(self):
        gap = 5 * mm
        half = (self._w - gap) / 2
        top_y = self.wide_h + gap
        left = self.projects[0] if self.projects else None
        right = self.projects[1] if len(self.projects) > 1 else None
        wide = self.projects[2] if len(self.projects) > 2 else left
        self._card(left, 0, top_y, half, self.top_h, CYAN)
        self._card(right, half + gap, top_y, half, self.top_h, LIME)
        self._card(wide, 0, 0, self._w, self.wide_h, CYAN)


class ProjectCard(Flowable):
    def __init__(self, project, index, width, height, accent=CYAN):
        super().__init__()
        self.project = project
        self.index = index
        self.accent = accent
        self._w = width
        self._h = height
        path = resolve_project_image(project)
        self.photo = _jpeg_cover(path, width, height * 0.58)

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        styles = _styles()
        self.canv.setFillColor(CARD)
        self.canv.roundRect(0, 0, self._w, self._h, 12, fill=1, stroke=0)
        photo_h = self._h * 0.56
        _draw_photo(self.canv, self.photo, 0, self._h - photo_h, self._w, photo_h, 12)
        self.canv.setFillColor(CARD)
        self.canv.rect(0, self._h - photo_h - 1, self._w, 14, fill=1, stroke=0)
        self.canv.setFillColor(self.accent)
        self.canv.roundRect(8, self._h - 18, 22, 10, 5, fill=1, stroke=0)
        self.canv.setFillColor(NAVY)
        self.canv.setFont("Helvetica-Bold", 7)
        self.canv.drawCentredString(19, self._h - 15.2, f"{self.index:02d}")

        y = self._h - photo_h - 6
        used = _draw_para(self.canv, self.project.name, styles["card_title"], 8, y, self._w - 16)
        y -= used + 2
        used = _draw_para(
            self.canv,
            self.project.description or "",
            styles["muted"],
            8,
            y,
            self._w - 16,
        )
        y -= used + 6
        self.canv.setFillColor(MUTED)
        self.canv.setFont("Helvetica-Bold", 6.5)
        self.canv.drawString(8, y, "INDUSTRY")
        y -= 9
        self.canv.setFillColor(NAVY)
        self.canv.setFont("Helvetica", 8)
        self.canv.drawString(8, y, _industry_for(self.project))
        y -= 12
        caps = "  ·  ".join(_short_caps(self.project))
        if caps:
            self.canv.setFillColor(MUTED)
            self.canv.setFont("Helvetica-Bold", 6.5)
            self.canv.drawString(8, y, "CAPABILITIES")
            y -= 10
            _draw_para(self.canv, caps, styles["card_body"], 8, y + 8, self._w - 16)
        url = _plain(self.project.url)
        if url:
            self.canv.setFillColor(CYAN)
            self.canv.setFont("Helvetica-Bold", 7.5)
            self.canv.drawRightString(self._w - 10, 8, "Visit project  >")
            self.canv.linkURL(url, (self._w - 52, 4, self._w - 6, 16), relative=1, thickness=0)


class CardPair(Flowable):
    def __init__(self, left, right, width, height):
        super().__init__()
        self.left = left
        self.right = right
        self._w = width
        self._h = height

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        gap = 5 * mm
        card_w = (self._w - gap) / 2
        self.left._w = card_w
        self.right._w = card_w
        self.left.canv = self.canv
        self.left.wrap(card_w, self._h)
        self.left.drawOn(self.canv, 0, 0)
        self.right.canv = self.canv
        self.right.wrap(card_w, self._h)
        self.right.drawOn(self.canv, card_w + gap, 0)


class IndustryGrid(Flowable):
    def __init__(self, labels, width):
        super().__init__()
        self.labels = labels[:8]
        self._w = width
        self.rows = max((len(self.labels) + 1) // 2, 1)
        self.card_h = 32 * mm
        self._h = self.rows * self.card_h + max(self.rows - 1, 0) * 4 * mm

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        gap = 4 * mm
        card_w = (self._w - gap) / 2
        for index, label in enumerate(self.labels):
            col = index % 2
            row = index // 2
            x = col * (card_w + gap)
            y = self._h - (row + 1) * self.card_h - row * gap
            self.canv.setFillColor(NAVY if index % 2 else CARD)
            self.canv.roundRect(x, y, card_w, self.card_h, 10, fill=1, stroke=0)
            self.canv.setFillColor(LIME if index % 2 else CYAN)
            self.canv.circle(x + 14 * mm, y + self.card_h / 2, 4.2 * mm, fill=1, stroke=0)
            self.canv.setFillColor(white if index % 2 else NAVY)
            self.canv.setFont("Helvetica-Bold", 11)
            self.canv.drawString(x + 24 * mm, y + self.card_h / 2 - 4, label)


class TestimonialHero(Flowable):
    def __init__(self, item, width, height=88 * mm):
        super().__init__()
        self.item = item
        self._w = width
        self._h = height

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        styles = _styles()
        self.canv.setFillColor(NAVY)
        self.canv.roundRect(0, 0, self._w, self._h, 14, fill=1, stroke=0)
        self.canv.setFillColor(LIME)
        self.canv.setFont("Helvetica-Bold", 28)
        self.canv.drawString(12, self._h - 22, '"')
        quote = _plain(self.item.quote)
        _draw_para(
            self.canv,
            f'"{quote}"',
            ParagraphStyle(
                "HeroQuote",
                fontName="Helvetica-Oblique",
                fontSize=11,
                leading=15,
                textColor=white,
                alignment=TA_CENTER,
            ),
            16,
            self._h - 18,
            self._w - 32,
        )
        self.canv.setFillColor(CYAN)
        self.canv.setFont("Helvetica-Bold", 9)
        self.canv.drawCentredString(self._w / 2, 22, self.item.name)
        self.canv.setFillColor(Color(1, 1, 1, alpha=0.7))
        self.canv.setFont("Helvetica", 8)
        self.canv.drawCentredString(self._w / 2, 12, _plain(self.item.role))
        self.canv.setFillColor(LIME)
        self.canv.circle(self._w / 2 - 10, 4, 2.1, fill=1, stroke=0)
        self.canv.setFillColor(CYAN)
        self.canv.roundRect(self._w / 2 - 5, 3, 10, 2.2, 1.1, fill=1, stroke=0)
        self.canv.setStrokeColor(CYAN)
        self.canv.setLineWidth(0.8)
        self.canv.circle(self._w / 2 + 10, 4, 2.1, fill=0, stroke=1)


class TestimonialRow(Flowable):
    def __init__(self, items, width, height=50 * mm):
        super().__init__()
        self.items = items
        self._w = width
        self._h = height

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        styles = _styles()
        if not self.items:
            return
        gap = 5 * mm
        card_w = (self._w - gap * (len(self.items) - 1)) / len(self.items)
        for index, item in enumerate(self.items):
            x = index * (card_w + gap)
            self.canv.setFillColor(CARD)
            self.canv.roundRect(x, 0, card_w, self._h, 10, fill=1, stroke=0)
            quote = _plain(item.quote)
            if len(quote) > 180:
                quote = quote[:177].rsplit(" ", 1)[0] + "..."
            _draw_para(self.canv, f'"{quote}"', styles["quote_small"], x + 8, self._h - 8, card_w - 16)
            self.canv.setFillColor(NAVY)
            self.canv.setFont("Helvetica-Bold", 7.5)
            self.canv.drawString(x + 8, 12, item.name)
            self.canv.setFillColor(MUTED)
            self.canv.setFont("Helvetica", 6.5)
            self.canv.drawString(x + 8, 4, _plain(item.role)[:42])


class WhyList(Flowable):
    def __init__(self, width):
        super().__init__()
        self.points = WHY_POINTS
        self._w = width
        self.row_h = 34 * mm
        self._h = len(self.points) * self.row_h + (len(self.points) - 1) * 3 * mm

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        styles = _styles()
        for index, (number, title, body) in enumerate(self.points):
            y = self._h - (index + 1) * self.row_h - index * 3 * mm
            self.canv.setFillColor(CARD if index % 2 == 0 else CARD_ALT)
            self.canv.roundRect(0, y, self._w, self.row_h, 10, fill=1, stroke=0)
            self.canv.setFillColor(NAVY)
            self.canv.circle(16 * mm, y + self.row_h / 2, 8 * mm, fill=1, stroke=0)
            self.canv.setFillColor(LIME if index % 2 else CYAN)
            self.canv.setFont("Helvetica-Bold", 8)
            self.canv.drawCentredString(16 * mm, y + self.row_h / 2 - 3, number)
            _draw_para(self.canv, title, styles["why_title"], 30 * mm, y + self.row_h - 7, self._w - 36 * mm)
            _draw_para(self.canv, body, styles["muted"], 30 * mm, y + self.row_h - 16, self._w - 36 * mm)


class EmptyNote(Flowable):
    def __init__(self, text, width, height=20 * mm):
        super().__init__()
        self.text = text
        self._w = width
        self._h = height

    def wrap(self, *_args):
        return self._w, self._h

    def draw(self):
        styles = _styles()
        _draw_para(self.canv, self.text, styles["muted"], 0, self._h - 4, self._w)


# ---------------------------------------------------------------------------
# Story
# ---------------------------------------------------------------------------

def _content_width():
    return PAGE_W - 30 * mm


def _own_and_partner_page(styles, own, partners, width):
    bits = []
    running = 1
    if own:
        title, intro = CATEGORY_COPY[Project.CATEGORY_OWN]
        bits.append(SectionHead("Portfolio", title, width, intro))
        bits.append(Spacer(1, 4 * mm))
        for project in own:
            bits.append(ProjectCard(project, running, width, 92 * mm, CYAN))
            bits.append(Spacer(1, 4 * mm))
            running += 1
    if partners:
        title, intro = CATEGORY_COPY[Project.CATEGORY_PARTNERSHIP]
        bits.append(SectionHead("Portfolio", title, width, intro))
        bits.append(Spacer(1, 4 * mm))
        for project in partners:
            bits.append(ProjectCard(project, running, width, 92 * mm, LIME))
            bits.append(Spacer(1, 4 * mm))
            running += 1
    return bits, running


def _client_pages(clients, start_index, width):
    pages = []
    index = start_index
    for group in _chunk(clients, 4):
        bits = [
            SectionHead(
                "Portfolio",
                "Client projects",
                width,
                "Technology delivered for organisations and businesses.",
            ),
            Spacer(1, 3 * mm),
        ]
        rows = _chunk(group, 2)
        for row in rows:
            height = 102 * mm
            if len(row) == 1:
                bits.append(ProjectCard(row[0], index, width, height, CYAN))
                index += 1
            else:
                left = ProjectCard(row[0], index, (width - 5 * mm) / 2, height, CYAN)
                right = ProjectCard(row[1], index + 1, (width - 5 * mm) / 2, height, LIME)
                bits.append(CardPair(left, right, width, height))
                index += 2
            bits.append(Spacer(1, 4 * mm))
        pages.append(bits)
    return pages


def build_portfolio_pdf():
    projects = active_projects()
    services = list(Service.objects.filter(is_active=True).order_by("sort_order", "id"))
    quotes = list(Testimonial.objects.filter(is_active=True).order_by("sort_order", "id")[:3])
    own = [item for item in projects if item.category == Project.CATEGORY_OWN]
    partners = [item for item in projects if item.category == Project.CATEGORY_PARTNERSHIP]
    clients = [item for item in projects if item.category == Project.CATEGORY_CLIENT]
    width = _content_width()
    styles = _styles()

    buffer = BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        title="Orbeetal - Company Portfolio",
        author="Orbeetal",
        subject="Orbeetal company portfolio",
        creator="Orbeetal CMS",
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
    )
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, 0, 0, 0, 0, id="cover")
    inner_frame = Frame(
        16 * mm,
        16 * mm,
        width,
        PAGE_H - 34 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="inner",
    )
    cta_frame = Frame(0, 0, PAGE_W, PAGE_H, 0, 0, 0, 0, id="cta")
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[cover_frame], onPage=_draw_cover),
            PageTemplate(id="inner", frames=[inner_frame], onPage=_draw_inner_chrome),
            PageTemplate(id="cta", frames=[cta_frame], onPage=_draw_cta_chrome),
        ]
    )

    story = [Spacer(1, 1), NextPageTemplate("inner"), PageBreak()]

    story.append(SectionHead(
        "About Orbeetal",
        "We build technology that moves businesses forward.",
        width,
    ))
    story.append(Paragraph(_safe(_about_copy()), styles["body"]))
    story.append(Spacer(1, 4 * mm))
    story.append(StatRow(width))
    story.append(Spacer(1, 5 * mm))
    story.append(SplitCards("Mission", COMPANY["mission"], "Vision", COMPANY["vision"], width))
    story.append(Spacer(1, 6 * mm))
    story.append(PhotoBand(width, 72 * mm))

    story.append(PageBreak())
    story.append(SectionHead(
        "What we do",
        "Capabilities, under one team.",
        width,
        "Strategy, design, engineering and growth as a single accountable partner.",
    ))
    story.append(Spacer(1, 3 * mm))
    if services:
        story.append(ServiceGrid(services, width))
    else:
        story.append(EmptyNote("No published services yet.", width))

    featured = [
        _find_named(projects, "Munabooks"),
        _find_named(projects, "RUET", "Reporters"),
        _find_named(projects, "Plant Paradise"),
    ]
    featured = [item for item in featured if item] or projects[:3]
    story.append(PageBreak())
    story.append(SectionHead(
        "Selected work",
        "Digital products across multiple industries.",
        width,
    ))
    story.append(Spacer(1, 3 * mm))
    if featured:
        story.append(FeaturedSpread(featured, width))
    else:
        story.append(EmptyNote("No published projects yet.", width))

    if own or partners:
        story.append(PageBreak())
        bits, running = _own_and_partner_page(styles, own, partners, width)
        story.extend(bits)
    else:
        running = 1

    for page in _client_pages(clients, running, width):
        story.append(PageBreak())
        story.extend(page)

    industries = _industries(projects)
    story.append(PageBreak())
    story.append(SectionHead(
        "Expertise",
        "Industries we serve.",
        width,
        "Derived from products and client work currently in this portfolio.",
    ))
    story.append(Spacer(1, 4 * mm))
    if industries:
        story.append(IndustryGrid(industries, width))
        story.append(Spacer(1, 8 * mm))
        story.append(PhotoBand(width, 52 * mm))
    else:
        story.append(EmptyNote("Industries will appear as projects are published.", width))

    if quotes:
        story.append(PageBreak())
        story.append(SectionHead("Client stories", "Work that earns trust.", width))
        story.append(Spacer(1, 4 * mm))
        story.append(TestimonialHero(quotes[0], width))
        if quotes[1:]:
            story.append(Spacer(1, 5 * mm))
            story.append(TestimonialRow(quotes[1:], width))

    story.append(PageBreak())
    story.append(SectionHead(
        "Why Orbeetal",
        "A partner built for lasting products.",
        width,
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(WhyList(width))

    story.append(NextPageTemplate("cta"))
    story.append(PageBreak())
    story.append(Spacer(1, 1))

    doc.build(story, canvasmaker=pdfcanvas.Canvas)
    return buffer.getvalue()
