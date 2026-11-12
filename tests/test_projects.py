"""
Tests for the project list and the generated projects page.
"""

from __future__ import annotations

import json
import logging

import pytest


def make_app(mocker, theme_options=None):
    app = mocker.Mock()
    app.builder = mocker.Mock()
    app.builder.theme_options = {} if theme_options is None else theme_options
    return app


def make_app_with_builder(mocker, theme_options=None, found_docs=()):
    app = mocker.Mock()
    app.builder.theme_options = {} if theme_options is None else theme_options
    app.builder.env.found_docs = set(found_docs)
    return app


def test_projects_shipped_list(mocker):
    """The shipped list is valid and its markers drive the navbar split."""
    from conda_sphinx_theme import set_config_defaults

    app = make_app(mocker)
    set_config_defaults(app)

    theme = app.builder.theme_options
    projects = theme["projects"]
    assert projects
    assert all(entry.get("name") and entry.get("docs") for entry in projects)
    assert len({entry["name"] for entry in projects}) == len(projects)

    # The inline entries are the leading run: at least one tab, and the marker
    # stops at the first unmarked entry.
    inline = theme["projects_inline"]
    assert inline > 0
    assert all(entry.get("inline") for entry in projects[:inline])
    assert not any(entry.get("inline") for entry in projects[inline:])


def test_projects_json_is_packaged():
    """The shipped list is valid JSON and is declared as package data."""
    from pathlib import Path

    import tomllib

    import conda_sphinx_theme

    root = Path(conda_sphinx_theme.__file__).parent
    assert json.loads((root / "projects.json").read_text())

    config = tomllib.loads((root.parent / "pyproject.toml").read_text())
    package_data = config["tool"]["setuptools"]["package-data"]["conda_sphinx_theme"]
    assert "projects.json" in package_data


def test_projects_page_enabled_by_default(mocker):
    """The projects page is generated unless it is turned off."""
    from conda_sphinx_theme import set_config_defaults

    app = make_app(mocker)
    set_config_defaults(app)

    assert app.builder.theme_options["projects_page"] is True


@pytest.mark.parametrize("value", [False, "false", "0", "no", "off"])
def test_projects_page_disabled(mocker, value):
    """Any falsy spelling of projects_page disables the page."""
    from conda_sphinx_theme import set_config_defaults

    app = make_app(mocker, {"projects_page": value})
    set_config_defaults(app)

    assert app.builder.theme_options["projects_page"] is False


def test_projects_defaults_to_shipped_list(mocker):
    """An empty projects option means "use the shipped list"."""
    from conda_sphinx_theme import set_config_defaults

    app = make_app(mocker, {"projects": ""})
    set_config_defaults(app)

    assert app.builder.theme_options["projects"][0]["name"] == "conda"


def test_projects_override_replaces_default(mocker):
    """A project can supply its own list, even an empty one."""
    from conda_sphinx_theme import set_config_defaults

    custom = [{"name": "myproject", "docs": "https://example.com", "inline": True}]
    app = make_app(mocker, {"projects": custom})
    set_config_defaults(app)

    assert app.builder.theme_options["projects"] == custom
    assert app.builder.theme_options["projects_inline"] == 1


@pytest.mark.parametrize(
    "projects,expected",
    [
        pytest.param(
            [
                {"name": "a", "docs": "https://a.example"},
                {"name": "b", "docs": "https://b.example"},
            ],
            0,
            id="no-markers",
        ),
        pytest.param(
            [
                {"name": "a", "docs": "https://a.example", "inline": True},
                {"name": "b", "docs": "https://b.example"},
            ],
            1,
            id="one-marker",
        ),
        pytest.param(
            [
                {"name": "a", "docs": "https://a.example", "inline": True},
                {"name": "b", "docs": "https://b.example", "inline": True},
            ],
            2,
            id="all-markers",
        ),
        pytest.param(
            [
                {"name": "a", "docs": "https://a.example", "inline": True},
                {"name": "b", "docs": "https://b.example"},
                {"name": "c", "docs": "https://c.example", "inline": True},
            ],
            1,
            id="stray-marker",
        ),
    ],
)
def test_projects_inline_derivation(mocker, projects, expected):
    """The navbar split is the run of leading entries marked inline."""
    from conda_sphinx_theme import set_config_defaults

    app = make_app(mocker, {"projects": projects})
    set_config_defaults(app)

    assert app.builder.theme_options["projects_inline"] == expected


def test_projects_stray_marker_warns(mocker, caplog):
    """A marker after a gap is ignored with a warning naming the entry."""
    from conda_sphinx_theme import set_config_defaults

    projects = [
        {"name": "a", "docs": "https://a.example", "inline": True},
        {"name": "b", "docs": "https://b.example"},
        {"name": "c", "docs": "https://c.example", "inline": True},
    ]
    app = make_app(mocker, {"projects": projects})

    with caplog.at_level(logging.WARNING, logger="conda_sphinx_theme"):
        set_config_defaults(app)

    assert "'c'" in caplog.text or "c" in caplog.text


@pytest.mark.parametrize(
    "entry",
    [
        pytest.param({"docs": "https://a.example"}, id="missing-name"),
        pytest.param({"name": "a"}, id="missing-docs"),
        pytest.param("not-a-dict", id="not-a-dict"),
    ],
)
def test_projects_invalid_entry_raises(mocker, entry):
    """Malformed entries fail the build with a clear message."""
    from conda_sphinx_theme import set_config_defaults

    app = make_app(mocker, {"projects": [entry]})

    with pytest.raises(ValueError, match="name"):
        set_config_defaults(app)


def test_projects_filter_script_registered(mocker):
    """The navbar filter needs its client-side script."""
    from conda_sphinx_theme import set_config_defaults

    app = make_app(mocker)
    set_config_defaults(app)

    assert (
        mocker.call(
            "js/projects-filter.js",
        )
        in app.add_js_file.call_args_list
    )


def test_get_projects_page(mocker):
    """The generated page carries the flag the templates use."""
    from conda_sphinx_theme import get_projects_page

    app = make_app_with_builder(mocker, {"projects_page": True})

    pages = list(get_projects_page(app))

    assert len(pages) == 1
    pagename, context, template = pages[0]
    assert pagename == "projects"
    assert template == "projects.html"
    assert context["conda_page"] == "projects"
    assert context["title"] == "Projects"


def test_get_projects_page_disabled(mocker):
    """No page is generated when projects_page is off."""
    from conda_sphinx_theme import get_projects_page

    app = make_app_with_builder(mocker, {"projects_page": False})

    assert list(get_projects_page(app)) == []


def test_get_projects_page_skips_existing_document(mocker):
    """An authored document named projects wins over the generated page."""
    from conda_sphinx_theme import get_projects_page

    app = make_app_with_builder(
        mocker, {"projects_page": True}, found_docs=("projects",)
    )

    assert list(get_projects_page(app)) == []
