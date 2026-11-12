try:
    from ._version import version_tuple as version_info, __version__  # noqa: F401  # ty: ignore[unresolved-import]
except ImportError:  # pragma: no cover
    # Version file not generated yet (e.g., in editable install before build)
    __version__ = "0.0.0+unknown"
    version_info = (0, 0, 0)

import json
from pathlib import Path

from sphinx.util import logging

logger = logging.getLogger(__name__)

# theme.conf values arrive as strings, while html_theme_options can supply real
# booleans; these are the spellings that mean False.
FALSE_VALUES = frozenset({"false", "0", "no", "off"})


def set_config_defaults(app):
    """Inject additional default theme options and icon links."""
    try:
        theme = app.builder.theme_options
    except AttributeError:
        theme = None
    if not theme:
        theme = {}

    # Add extra icon links entries if there were shortcuts present
    # See https://github.com/pydata/pydata-sphinx-theme/blob/6b426bb133812c69b33ce88913f8bc018f1bfd02/src/pydata_sphinx_theme/__init__.py#L141-L163
    icon_links = []
    for key, default_url, icon, name in [
        ("zulip_url", "https://conda.zulipchat.com/", "fa-custom fa-zulip", "Zulip"),
    ]:
        # Skip link if URL is falsy
        if url := theme.get(key, default_url):
            icon_links.append(
                {
                    "url": url,
                    "icon": icon,
                    "name": name,
                    "type": "fontawesome",
                },
            )
    theme["icon_links"] = [*icon_links, *(theme.get("icon_links") or [])]

    # Default project list, unless the project supplied one
    projects = theme.get("projects")
    if projects is None or isinstance(projects, str):
        # theme.conf declares this as an empty string, meaning "use the default"
        projects = json.loads((Path(__file__).parent / "projects.json").read_text())
        theme["projects"] = projects
    for entry in projects:
        if (
            not isinstance(entry, dict)
            or not entry.get("name")
            or not entry.get("docs")
        ):
            raise ValueError(
                f"conda-sphinx-theme: invalid project entry {entry!r}, "
                "'name' and 'docs' are required"
            )

    # theme.conf values arrive as strings; normalize so templates and the
    # html-collect-pages hook agree
    theme["projects_page"] = (
        str(theme.get("projects_page", "true")).lower() not in FALSE_VALUES
    )

    # Add custom Zulip icon
    app.add_js_file("js/zulip-icon.js")

    # Filter bar for the project list in the navbar
    app.add_js_file("js/projects-filter.js")

    # Add GoatCounter script
    if goatcounter_url := theme.get("goatcounter_url"):
        app.add_js_file(
            "js/count.js",
            **{"loading_method": "async", "data-goatcounter": goatcounter_url},
        )

    # Default logo
    logo = theme.get("logo", {})
    if "image_dark" not in logo:
        logo["image_dark"] = "_static/conda_logo_full.svg"
    if "image_light" not in logo:
        logo["image_light"] = "_static/conda_logo_full.svg"
    theme["logo"] = logo

    # Default favicon; relies on https://sphinx-favicon.readthedocs.io/en/stable
    favicons = theme.get("favicons", [])
    favicons.append({"href": "favicon.ico", "rel": "icon", "type": "image/svg+xml"})
    theme["favicons"] = favicons

    # Update the HTML theme config
    app.builder.theme_options = theme


def get_projects_page(app):
    """Generate a page listing every documentation site in the project list."""
    builder = app.builder
    if not builder.theme_options.get("projects_page"):
        return
    if "projects" in builder.env.found_docs:
        logger.info(
            "conda-sphinx-theme: not generating a projects page, a document "
            "named 'projects' already exists"
        )
        return
    yield (
        "projects",
        {"conda_page": "projects", "title": "Projects", "parents": []},
        "projects.html",
    )


# For more details, see:
# https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
def setup(app):
    here = Path(__file__).parent.resolve()
    # Include component templates
    app.config.templates_path.append(str(here / "_templates"))
    app.add_html_theme("conda_sphinx_theme", str(here))
    app.connect("builder-inited", set_config_defaults)
    app.connect("html-collect-pages", get_projects_page)
    return {"version": __version__, "parallel_read_safe": True}
