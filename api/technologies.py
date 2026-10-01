from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.text import slugify

from .models import Technology

# name, simple-icons slug. Logo files live in frontend/public/tech/.
CATALOG = (
    ("React", "react"),
    ("Next.js", "nextdotjs"),
    ("Vue.js", "vuedotjs"),
    ("Angular", "angular"),
    ("Svelte", "svelte"),
    ("TypeScript", "typescript"),
    ("JavaScript", "javascript"),
    ("HTML5", "html5"),
    ("CSS", "css"),
    ("Tailwind CSS", "tailwindcss"),
    ("Bootstrap", "bootstrap"),
    ("Django", "django"),
    ("Python", "python"),
    ("Node.js", "nodedotjs"),
    ("Express", "express"),
    ("NestJS", "nestjs"),
    ("Laravel", "laravel"),
    ("PHP", "php"),
    ("FastAPI", "fastapi"),
    ("Flask", "flask"),
    ("Ruby on Rails", "rubyonrails"),
    (".NET", "dotnet"),
    ("Java", "openjdk"),
    ("Spring", "spring"),
    ("Go", "go"),
    ("Rust", "rust"),
    ("C++", "cplusplus"),
    ("Flutter", "flutter"),
    ("Swift", "swift"),
    ("Kotlin", "kotlin"),
    ("React Native", "react"),
    ("PostgreSQL", "postgresql"),
    ("MySQL", "mysql"),
    ("MongoDB", "mongodb"),
    ("Redis", "redis"),
    ("SQLite", "sqlite"),
    ("Firebase", "firebase"),
    ("Supabase", "supabase"),
    ("Prisma", "prisma"),
    ("Docker", "docker"),
    ("Kubernetes", "kubernetes"),
    ("AWS", "amazonwebservices"),
    ("Nginx", "nginx"),
    ("Vercel", "vercel"),
    ("Git", "git"),
    ("GitHub", "github"),
    ("Linux", "linux"),
    ("GraphQL", "graphql"),
    ("Redux", "redux"),
    ("Vite", "vite"),
    ("Webpack", "webpack"),
    ("Three.js", "threedotjs"),
    ("Electron", "electron"),
    ("jQuery", "jquery"),
    ("Figma", "figma"),
    ("WordPress", "wordpress"),
    ("Shopify", "shopify"),
    ("Stripe", "stripe"),
    ("TensorFlow", "tensorflow"),
    ("Pandas", "pandas"),
    ("NumPy", "numpy"),
)

CATALOG_LOGOS = {name.casefold(): f"/tech/{icon}.svg" for name, icon in CATALOG}

# Compact keys (letters and digits only) for common short names.
ALIASES = {
    "react": "React",
    "reactjs": "React",
    "reactnative": "React Native",
    "next": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "django": "Django",
    "node": "Node.js",
    "nodejs": "Node.js",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "golang": "Go",
    "go": "Go",
    "rails": "Ruby on Rails",
    "ror": "Ruby on Rails",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "dotnet": ".NET",
    "nestjs": "NestJS",
    "fastapi": "FastAPI",
    "graphql": "GraphQL",
    "sqlite": "SQLite",
    "mysql": "MySQL",
    "redux": "Redux",
    "threejs": "Three.js",
    "cpp": "C++",
    "cplusplus": "C++",
}


def _compact(name):
    return "".join(char for char in name.casefold() if char.isalnum())


def canonical_name(name):
    cleaned = " ".join(str(name or "").split())
    if not cleaned:
        return ""
    return ALIASES.get(_compact(cleaned), cleaned)


def catalog_logo(name):
    return CATALOG_LOGOS.get(canonical_name(name).casefold(), "")


def _unique_slug(name):
    base = (slugify(name) or "tech")[:70]
    slug = base
    number = 2
    while Technology.objects.filter(slug=slug).exists():
        slug = f"{base}-{number}"[:80]
        number += 1
    return slug


def ensure_technology_catalog():
    existing = {tech.name.casefold(): tech for tech in Technology.objects.all()}
    for name, icon in CATALOG:
        logo = f"/tech/{icon}.svg"
        current = existing.get(name.casefold())
        if current:
            if not current.logo:
                current.logo = logo
                current.save(update_fields=["logo"])
            continue
        try:
            Technology.objects.create(name=name, slug=_unique_slug(name), logo=logo)
        except IntegrityError:
            continue


def remember_technology(name, logo=""):
    display = canonical_name(name)
    if not display:
        return None
    chosen_logo = (logo or "").strip() or catalog_logo(display)
    now = timezone.now()
    with transaction.atomic():
        tech = Technology.objects.filter(name__iexact=display).first()
        if tech is None:
            try:
                return Technology.objects.create(
                    name=display,
                    slug=_unique_slug(display),
                    logo=chosen_logo,
                    last_used_at=now,
                )
            except IntegrityError:
                tech = Technology.objects.filter(name__iexact=display).first()
                if tech is None:
                    raise
        updates = ["last_used_at"]
        tech.last_used_at = now
        if chosen_logo and not tech.logo:
            tech.logo = chosen_logo
            updates.append("logo")
        tech.save(update_fields=updates)
        return tech


def present_stack(items):
    if not isinstance(items, list):
        return []
    result = []
    seen = set()
    for item in items:
        if isinstance(item, dict):
            raw_name = item.get("name") or ""
            logo = str(item.get("logo") or "").strip()
        else:
            raw_name = item
            logo = ""
        name = canonical_name(raw_name)
        if not name or name.casefold() in seen:
            continue
        if not logo:
            logo = catalog_logo(name)
        result.append({"name": name, "logo": logo})
        seen.add(name.casefold())
    return result


def stack_names(items):
    return [item["name"] for item in present_stack(items)]
