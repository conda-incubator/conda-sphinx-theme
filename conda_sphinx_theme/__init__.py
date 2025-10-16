from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ._version import __version__

if TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx


def set_config_defaults(app: Sphinx) -> None:
    """Set default theme options."""
    # Get theme options
    app.builder.theme_options = theme = {
        **app.builder.theme.get_options(),  # theme.conf
        **app.builder.theme_options,  # conf.py's html_theme_options
    }

    # Add custom icons
    app.add_js_file("js/custom-icons.js")

    # Add icon links based on configured URLs
    # Note: Since we insert at the beginning, we add the links in reverse order
    theme["icon_links"] = icon_links = theme.get("icon_links") or []
    for key, name, icon, type in (
        ("discourse_url", "Discourse", "fa-brands fa-discourse", "fontawesome"),
        ("zulip_url", "Zulip", "fa-custom fa-zulip", "fontawesome"),
    ):
        if url := theme.get(key):
            icon_links.insert(0, {
                "name": name,
                "url": url,
                "icon": icon,
                "type": type,
            })

    # Add GoatCounter script
    if goatcounter_url := theme.get("goatcounter_url"):
        app.add_js_file(
            "js/count.js",
            **{"loading_method": "async", "data-goatcounter": goatcounter_url},
        )

    # Default logo
    theme["logo"] = logo = theme.get("logo") or {}
    logo.setdefault("image_dark", "_static/conda_logo_full.svg")
    logo.setdefault("image_light", "_static/conda_logo_full.svg")

    # Default favicon; relies on https://sphinx-favicon.readthedocs.io/en/stable
    theme["favicons"] = favicons = theme.get("favicons") or []
    favicons.append({"href": "favicon.ico", "rel": "icon", "type": "image/svg+xml"})


def get_html_theme_path() -> list[str]:
    """Return list of HTML theme paths."""
    return [str(Path(__file__).parent.parent.resolve())]


# For more details, see:
# https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
def setup(app: Sphinx) -> dict[str, Any]:
    here = Path(__file__).parent.resolve()
    # Include component templates
    app.config.templates_path.append(str(here / "_templates"))
    app.add_html_theme("conda_sphinx_theme", str(here))
    app.connect("builder-inited", set_config_defaults)
    return {"version": __version__, "parallel_read_safe": True}
