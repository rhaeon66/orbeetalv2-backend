import base64
import html
import re
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from PIL import Image as PILImage

from .models import Project

DESIGN_PATH = Path(__file__).resolve().parents[2] / "portfolio.html"
SITE_ORIGIN = "https://orbeetal.com"

CATEGORY_LABELS = {
    Project.CATEGORY_OWN: "Own Product",
    Project.CATEGORY_PARTNERSHIP: "Partnership",
    Project.CATEGORY_CLIENT: "Client Project",
}

CATEGORY_CTA = {
    Project.CATEGORY_OWN: "Explore Product →",
    Project.CATEGORY_PARTNERSHIP: "Explore Project →",
    Project.CATEGORY_CLIENT: "View Live Project →",
}

CATEGORY_ACCENT = {
    Project.CATEGORY_OWN: "accent-blue",
    Project.CATEGORY_PARTNERSHIP: "accent-lime",
    Project.CATEGORY_CLIENT: "accent-cyan",
}

TAG_CLASSES = ("tag-one", "tag-two", "tag-three")

EXTRA_CSS = """
    .visual-grid,
    .visual-orbit {
      z-index: 2;
    }

    .visual-core,
    .floating-tag {
      z-index: 3;
    }

    .visual-photo {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      z-index: 0;
    }

    .visual-photo-veil {
      position: absolute;
      inset: 0;
      z-index: 1;
      background:
        linear-gradient(
          180deg,
          rgba(7, 26, 43, 0.28),
          rgba(7, 26, 43, 0.78)
        );
    }

    .project-link.is-disabled {
      pointer-events: none;
      opacity: 0.55;
    }

    @media print {
      .navbar {
        position: static;
      }

      .nav-links,
      .nav-cta,
      .portfolio-controls {
        display: none;
      }

      .project {
        animation: none;
        opacity: 1;
        transform: none;
        break-inside: avoid;
      }

      .project.hidden {
        display: grid !important;
      }
    }
"""


def _public_dir():
    return Path(getattr(settings, "FRONTEND_PUBLIC", settings.BASE_DIR.parent / "frontend" / "public"))


def resolve_project_image(project):
    if project.image:
        path = Path(project.image.path)
        if path.exists() and path.suffix.lower() != ".svg":
            return path
    fallback = (project.image_fallback or "").strip()
    if not fallback or fallback.startswith("library:"):
        return None
    if fallback.startswith("http://") or fallback.startswith("https://"):
        marker = "/media/"
        if marker in fallback:
            rel = fallback.split(marker, 1)[1]
            path = Path(settings.MEDIA_ROOT) / rel
            if path.exists() and path.suffix.lower() != ".svg":
                return path
        return None
    if fallback.startswith("/media/"):
        path = Path(settings.MEDIA_ROOT) / fallback[len("/media/") :]
    elif fallback.startswith("media/"):
        path = Path(settings.MEDIA_ROOT) / fallback[len("media/") :]
    else:
        path = _public_dir() / fallback.lstrip("/")
    if path.exists() and path.suffix.lower() != ".svg":
        return path
    return None


def _escape(value):
    return html.escape(str(value or "").strip(), quote=True)


def _feature_list(raw):
    if not isinstance(raw, list):
        return []
    items = []
    for item in raw:
        text = str(item).strip() if item is not None else ""
        if text:
            items.append(text)
    return items


def active_projects():
    return list(Project.objects.filter(is_active=True).order_by("sort_order", "id"))


def project_features(project):
    return _feature_list(project.features)


def _initials(name):
    parts = [part for part in re.split(r"\W+", name or "") if part]
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    if parts:
        return parts[0][:3].upper()
    return "OR"


def _image_data_uri(path):
    try:
        with PILImage.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((960, 960), PILImage.Resampling.LANCZOS)
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=80, optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return ""


def _design_parts():
    if not DESIGN_PATH.exists():
        raise FileNotFoundError("portfolio.html design file is missing.")
    text = DESIGN_PATH.read_text(encoding="utf-8")
    style_match = re.search(r"<style>(.*?)</style>", text, re.S)
    script_match = re.search(r"<script>(.*?)</script>", text, re.S)
    if not style_match:
        raise ValueError("portfolio.html is missing its stylesheet.")
    return style_match.group(1), script_match.group(1) if script_match else ""


def _meta_items(projects):
    categories = {project.category for project in projects}
    live = sum(1 for project in projects if (project.url or "").strip())
    items = [
        (str(len(projects)), "Projects"),
        (str(len(categories) or 3), "Project Types"),
    ]
    if live:
        items.append((str(live), "Live Sites"))
    else:
        items.append(("3", "Categories"))
    return items


def _render_project(project, index, featured_id):
    category = project.category or Project.CATEGORY_CLIENT
    features = _feature_list(project.features)
    tags = features[:3]
    image_uri = ""
    image_path = resolve_project_image(project)
    if image_path:
        image_uri = _image_data_uri(image_path)

    featured_class = " featured" if project.id == featured_id else ""
    accent = CATEGORY_ACCENT.get(category, "accent-blue")
    label = CATEGORY_LABELS.get(category, "Client Project")
    url = (project.url or "").strip()
    cta = CATEGORY_CTA.get(category, "Explore Project →")
    if url and category != Project.CATEGORY_CLIENT:
        cta = "View Live Project →"
    number = f"{index:02d}"
    initials = _initials(project.name)

    photo_html = ""
    if image_uri:
        photo_html = (
            f'<img class="visual-photo" src="{image_uri}" alt="" />'
            '<div class="visual-photo-veil"></div>'
        )

    tags_html = "\n".join(
        f'<div class="floating-tag {TAG_CLASSES[i]}">{_escape(tag)}</div>'
        for i, tag in enumerate(tags)
    )

    features_html = ""
    if features:
        chips = "\n".join(f'<span class="feature">{_escape(item)}</span>' for item in features)
        features_html = f'<div class="features">{chips}</div>'

    if url:
        link_html = (
            f'<a href="{_escape(url)}" target="_blank" rel="noopener noreferrer" '
            f'class="project-link">{_escape(cta)}</a>'
        )
    else:
        link_html = f'<span class="project-link is-disabled">{_escape(cta)}</span>'

    core_html = f'<div class="visual-core">{_escape(initials)}</div>'

    return f"""
      <article
        class="project{featured_class} {accent}"
        data-category="{_escape(category)}">

        <div class="project-visual">
          {photo_html}
          <div class="visual-grid"></div>
          <div class="visual-orbit"></div>
          {core_html}
          {tags_html}
        </div>

        <div class="project-content">
          <div class="project-category">{_escape(label)}</div>
          <h2>{_escape(project.name)}</h2>
          <p class="project-description">{_escape(project.description)}</p>
          {features_html}
          <div class="project-footer">
            {link_html}
            <span class="project-number">{number}</span>
          </div>
        </div>
      </article>
    """


def build_portfolio_html():
    style, script = _design_parts()
    projects = active_projects()
    featured = next(
        (project for project in projects if project.category == Project.CATEGORY_OWN),
        projects[0] if projects else None,
    )
    featured_id = featured.id if featured else None
    cards = "\n".join(
        _render_project(project, index, featured_id)
        for index, project in enumerate(projects, start=1)
    )
    empty_display = "block" if not projects else "none"
    empty_copy = (
        "No published projects yet."
        if not projects
        else "No projects found in this category."
    )
    meta_html = "\n".join(
        f'<div class="meta-item"><strong>{_escape(value)}</strong> {_escape(label)}</div>'
        for value, label in _meta_items(projects)
    )
    year = timezone.now().year

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Orbeetal — Portfolio</title>
  <style>
{style}
{EXTRA_CSS}
  </style>
</head>
<body>
  <header class="navbar">
    <div class="nav-inner">
      <a href="{SITE_ORIGIN}/" class="logo">
        <div class="logo-mark">O</div>
        <span>Orbeetal</span>
      </a>
      <nav class="nav-links">
        <a href="{SITE_ORIGIN}/">Home</a>
        <a href="{SITE_ORIGIN}/about">About Us</a>
        <a href="{SITE_ORIGIN}/services">Services</a>
        <a href="{SITE_ORIGIN}/portfolio" class="active">Portfolio</a>
        <a href="{SITE_ORIGIN}/faq">FAQ</a>
        <a href="{SITE_ORIGIN}/contact">Contact</a>
      </nav>
      <a href="{SITE_ORIGIN}/contact" class="nav-cta">Get a Quote →</a>
    </div>
  </header>

  <section class="hero">
    <div class="hero-content">
      <div class="eyebrow">
        <span class="eyebrow-dot"></span>
        Our Work
      </div>
      <h1>
        Digital products
        <span>built for real impact.</span>
      </h1>
      <p class="hero-description">
        Explore products, partnerships, and client projects we've
        designed and developed across education, business operations,
        AI, cloud, digital platforms, and more.
      </p>
      <div class="hero-meta">
        {meta_html}
      </div>
    </div>
  </section>

  <section class="portfolio-controls">
    <div class="controls-inner">
      <div class="filter-label">Explore our work</div>
      <div class="filters">
        <button class="filter-btn active" data-filter="all">All</button>
        <button class="filter-btn" data-filter="own">Own Products</button>
        <button class="filter-btn" data-filter="partnership">Partnerships</button>
        <button class="filter-btn" data-filter="client">Client Projects</button>
      </div>
    </div>
  </section>

  <main class="portfolio">
    <div class="project-grid">
      {cards}
    </div>
    <div class="empty" style="display:{empty_display}">{_escape(empty_copy)}</div>
  </main>

  <section class="final-cta">
    <div class="eyebrow">
      <span class="eyebrow-dot"></span>
      Start a Project
    </div>
    <h2>
      Have an idea?
      <span>Let's build it.</span>
    </h2>
    <p>
      Tell us what you're trying to build and let's turn the
      idea into a reliable digital product.
    </p>
    <a href="{SITE_ORIGIN}/contact" class="cta-button">Get a Quote →</a>
  </section>

  <footer>
    <div class="footer-inner">
      <div class="logo">
        <div class="logo-mark">O</div>
        <span>Orbeetal</span>
      </div>
      <div class="footer-copy">© {year} Orbeetal. All rights reserved.</div>
      <div class="footer-links">
        <a href="{SITE_ORIGIN}/contact">Privacy</a>
        <a href="{SITE_ORIGIN}/contact">Terms</a>
        <a href="{SITE_ORIGIN}/contact">Contact</a>
      </div>
    </div>
  </footer>

  <script>
{script}
  </script>
</body>
</html>
""".encode("utf-8")
