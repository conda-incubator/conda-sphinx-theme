from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ._version import __version__

if TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx


def set_config_defaults(app: Sphinx) -> None:
    """Set default logo in theme options."""
    app.builder.theme_options = theme = getattr(app.builder, "theme_options") or {}

    # Default github_url
    theme["github_url"] = github_url = theme.get("github_url") or "https://github.com/conda/conda"

    # Default zulip_url
    theme["zulip_url"] = zulip_url = theme.get("zulip_url") or "https://conda.zulipchat.com"

    # Default discourse_url
    theme["discourse_url"] = discourse_url = theme.get("discourse_url") or "https://conda.discourse.group/"

    # Default icon_links
    theme["icon_links"] = icon_links = theme.get("icon_links") or []
    icon_links.extend(
        (
            {
                "name": "Zulip",
                "url": zulip_url,
                "icon": "_static/zulip_logo.svg",
                "type": "local",
            },
            {
                "name": "Discourse",
                "url": discourse_url,
                "icon": "fa-brands fa-discourse",
                "type": "fontawesome",
            },
        )
    )

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
