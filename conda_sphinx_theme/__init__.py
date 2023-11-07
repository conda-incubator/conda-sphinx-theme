from ._version import version_info, __version__  # noqa: F401

from pathlib import Path


def set_config_defaults(app):
    """Set default logo in theme options."""
    try:
        theme = app.builder.theme_options
    except AttributeError:
        theme = None
    if not theme:
        theme = {}

    # Default logo
    logo = theme.get("logo", {})
    if "image_dark" not in logo:
        logo["image_dark"] = "_static/conda_logo_full.svg"
    if "image_light" not in logo:
        logo["image_light"] = "_static/conda_logo_full.svg"
    theme["logo"] = logo

    # Default favicon; relies on https://sphinx-favicon.readthedocs.io/en/stable
    favicons = theme.get("favicons", [])
    favicons.append(
        {"href": "favicon.ico", "rel": "icon", "type": "image/svg+xml"}
    )
    theme["favicons"] = favicons

    # Update the HTML theme config
    app.builder.theme_options = theme


def get_html_theme_path():
    """Return list of HTML theme paths."""
    return [str(Path(__file__).parent.parent.resolve())]


# For more details, see:
# https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
def setup(app):
    here = Path(__file__).parent.resolve()
    # Include component templates
    app.config.templates_path.append(str(here / "_templates"))
    app.add_html_theme("conda_sphinx_theme", str(here))
    app.connect("builder-inited", set_config_defaults)
    return {'version': __version__, 'parallel_read_safe': True}
