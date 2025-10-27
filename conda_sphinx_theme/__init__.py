from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydata_sphinx_theme.utils import get_theme_options_dict

try:
    from ._version import version_tuple as version_info, __version__  # noqa: F401  # ty: ignore[unresolved-import]
except ImportError:  # pragma: no cover
    # Version file not generated yet (e.g., in editable install before build)
    __version__ = "0.0.0+unknown"
    version_info = (0, 0, 0)

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def set_config_defaults(app: Sphinx) -> None:
    """Set default theme options."""
    # Get theme options
    theme = get_theme_options_dict(app)

    # Add icon links based on configured URLs
    # Note: Since we insert at the beginning, we add the links in reverse order
    theme["icon_links"] = icon_links = theme.get("icon_links") or []
    add_custom_icons = False
    for key, default_url, name, icon, type in (
        ("discourse_url", "https://conda.discourse.group/", "Discourse", "fa-brands fa-discourse", "fontawesome"),
        ("zulip_url", "https://conda.zulipchat.com/", "Zulip", "fa-custom fa-zulip", "fontawesome"),
    ):
        if url := theme.get(key, default_url):
            icon_links.insert(0, {
                "name": name,
                "url": url,
                "icon": icon,
                "type": type,
            })
            add_custom_icons |= "fa-custom" in icon

    # Add custom icons
    if add_custom_icons:
        app.add_js_file("js/custom-icons.js")

    # Add GoatCounter script
    if goatcounter_url := theme.get("goatcounter_url"):
        app.add_js_file(
            "js/count.js",
            loading_method="async",
            **{"data-goatcounter": goatcounter_url},
        )

    # Default logo
    theme["logo"] = logo = theme.get("logo") or {}
    logo.setdefault("image_dark", "_static/conda_logo_full.svg")
    logo.setdefault("image_light", "_static/conda_logo_full.svg")

    # Default favicon; relies on https://sphinx-favicon.readthedocs.io/en/stable
    theme["favicons"] = favicons = theme.get("favicons") or []
    favicons.append({"href": "favicon.ico", "rel": "icon", "type": "image/svg+xml"})


# For more details, see:
# https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
def setup(app):
    here = Path(__file__).parent.resolve()
    # Include component templates
    app.config.templates_path.append(str(here / "_templates"))
    app.add_html_theme("conda_sphinx_theme", str(here))
    app.connect("builder-inited", set_config_defaults)
    return {"version": __version__, "parallel_read_safe": True}
