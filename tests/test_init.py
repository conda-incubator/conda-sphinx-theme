"""
Tests for the main conda_sphinx_theme module.
"""


def test_module_imports():
    """Test that the main module can be imported without errors."""
    import conda_sphinx_theme

    # Test that the module has expected attributes
    assert hasattr(conda_sphinx_theme, "__version__")

    # Test that the version is a string
    assert isinstance(conda_sphinx_theme.__version__, str)

    # Test that version is not empty
    assert len(conda_sphinx_theme.__version__) > 0


def test_setup_function(mocker):
    """Test the Sphinx theme setup function."""
    from conda_sphinx_theme import setup

    # Mock the Sphinx app
    app = mocker.Mock()
    app.config = mocker.Mock()
    app.config.templates_path = []

    # Call setup
    result = setup(app)

    # Verify theme was added
    app.add_html_theme.assert_called_once()
    theme_name, theme_path = app.add_html_theme.call_args[0]
    assert theme_name == "conda_sphinx_theme"
    assert "conda_sphinx_theme" in theme_path

    # Verify templates_path was updated
    assert len(app.config.templates_path) == 1
    assert "_templates" in app.config.templates_path[0]

    # Verify builder-inited event was connected
    app.connect.assert_called_once_with("builder-inited", mocker.ANY)

    # Verify return metadata
    assert "version" in result
    assert result["parallel_read_safe"] is True


def test_set_config_defaults_with_goatcounter(mocker):
    """Test set_config_defaults with GoatCounter URL."""
    from conda_sphinx_theme import set_config_defaults

    # Mock app with GoatCounter URL
    app = mocker.Mock()
    app.builder = mocker.Mock()
    app.builder.theme_options = {
        "goatcounter_url": "https://example.goatcounter.com/count"
    }

    # Call the function
    set_config_defaults(app)

    # Verify GoatCounter script was added
    app.add_js_file.assert_called_once()
    call_args = app.add_js_file.call_args
    assert call_args[0][0] == "js/count.js"
    assert call_args[1]["data-goatcounter"] == "https://example.goatcounter.com/count"


def test_set_config_defaults_without_goatcounter(mocker):
    """Test set_config_defaults without GoatCounter URL."""
    from conda_sphinx_theme import set_config_defaults

    # Mock app without GoatCounter URL
    app = mocker.Mock()
    app.builder = mocker.Mock()
    app.builder.theme_options = {}

    # Call the function
    set_config_defaults(app)

    # Verify GoatCounter script was NOT added
    app.add_js_file.assert_not_called()


def test_set_config_defaults_adds_logo(mocker):
    """Test that set_config_defaults adds default logo."""
    from conda_sphinx_theme import set_config_defaults

    app = mocker.Mock()
    app.builder = mocker.Mock()
    app.builder.theme_options = {}

    set_config_defaults(app)

    # Verify logo was set
    logo = app.builder.theme_options["logo"]
    assert logo["image_dark"] == "_static/conda_logo_full.svg"
    assert logo["image_light"] == "_static/conda_logo_full.svg"


def test_set_config_defaults_preserves_existing_logo(mocker):
    """Test that set_config_defaults preserves existing logo settings."""
    from conda_sphinx_theme import set_config_defaults

    app = mocker.Mock()
    app.builder = mocker.Mock()
    app.builder.theme_options = {
        "logo": {
            "image_dark": "custom_dark.svg",
            "image_light": "custom_light.svg",
        }
    }

    set_config_defaults(app)

    # Verify custom logo was preserved
    logo = app.builder.theme_options["logo"]
    assert logo["image_dark"] == "custom_dark.svg"
    assert logo["image_light"] == "custom_light.svg"


def test_set_config_defaults_adds_favicon(mocker):
    """Test that set_config_defaults adds default favicon."""
    from conda_sphinx_theme import set_config_defaults

    app = mocker.Mock()
    app.builder = mocker.Mock()
    app.builder.theme_options = {}

    set_config_defaults(app)

    # Verify favicon was added
    favicons = app.builder.theme_options["favicons"]
    assert len(favicons) == 1
    assert favicons[0]["href"] == "favicon.ico"
    assert favicons[0]["rel"] == "icon"
    assert favicons[0]["type"] == "image/svg+xml"


def test_set_config_defaults_appends_to_existing_favicons(mocker):
    """Test that set_config_defaults appends to existing favicons."""
    from conda_sphinx_theme import set_config_defaults

    app = mocker.Mock()
    app.builder = mocker.Mock()
    app.builder.theme_options = {
        "favicons": [{"href": "custom.png", "rel": "icon", "type": "image/png"}]
    }

    set_config_defaults(app)

    # Verify favicon was appended
    favicons = app.builder.theme_options["favicons"]
    assert len(favicons) == 2
    assert favicons[0]["href"] == "custom.png"
    assert favicons[1]["href"] == "favicon.ico"


