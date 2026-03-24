try:
    from ._version import version_tuple as version_info, __version__  # noqa: F401  # ty: ignore[unresolved-import]
except ImportError:
    # Version file not generated yet (e.g., in editable install before build)
    __version__ = "0.0.0+unknown"
    version_info = (0, 0, 0)

from pathlib import Path


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
    for key, default_url, name, icon in [
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

    # Add custom Zulip icon
    app.add_js_file("js/zulip-icon.js")

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


# For more details, see:
# https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
def setup(app):
    here = Path(__file__).parent.resolve()
    # Include component templates
    app.config.templates_path.append(str(here / "_templates"))
    app.add_html_theme("conda_sphinx_theme", str(here))
    app.connect("builder-inited", set_config_defaults)
    return {"version": __version__, "parallel_read_safe": True}
