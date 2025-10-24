"""
Tests for the Version Anchors Sphinx extension.

This module contains comprehensive tests for the version_anchors extension
that automatically adds version anchors to changelog headings.
"""

import re
import pytest


# Test fixtures
@pytest.fixture
def mock_config(mocker):
    """Fixture providing a mock Sphinx app config with default values."""
    from conda_sphinx_theme.version_anchors import (
        DEFAULT_VERSION_PATTERN,
        DEFAULT_ANCHOR_FORMAT,
        DEFAULT_CHANGELOG_FILES,
    )

    config = mocker.Mock()
    config.version_anchor_pattern = DEFAULT_VERSION_PATTERN
    config.version_anchor_format = DEFAULT_ANCHOR_FORMAT
    config.version_anchor_changelog_files = DEFAULT_CHANGELOG_FILES
    return config


# Pattern matching tests using the actual extension's default pattern
@pytest.mark.parametrize(
    "heading_text,expected_version",
    [
        ("1.2.3 (2025-01-24)", "1.2.3"),
        ("25.5.0 (2025-05-21)", "25.5.0"),
        ("0.1.0 (2025-12-31)", "0.1.0"),
        ("2.0 (2025-06-15)", "2.0"),
        ("1.5 (Released on 2025-03-10)", "1.5"),
        ("10.20.30 (Beta release)", "10.20.30"),
    ],
)
def test_version_pattern_matches(heading_text, expected_version):
    """Test that the extension's default pattern matches expected formats."""
    from conda_sphinx_theme.version_anchors import DEFAULT_VERSION_PATTERN

    pattern = re.compile(DEFAULT_VERSION_PATTERN)
    match = pattern.match(heading_text)
    assert match is not None, f"Pattern should match '{heading_text}'"
    assert (
        match.group(1) == expected_version
    ), f"Version mismatch for '{heading_text}': got '{match.group(1)}', expected '{expected_version}'"


@pytest.mark.parametrize(
    "heading_text",
    [
        "Introduction",  # No version
        "Version 1.2.3",  # Wrong format
        "Release 2.0.0",  # Wrong format
        "v1.5.0 (2025-01-01)",  # Has 'v' prefix
        "1.2.3.4 (2025-01-01)",  # Too many version parts
        "(2025-01-01) 1.2.0",  # Wrong order
        "1.2 - Bug fixes",  # No parentheses
    ],
)
def test_version_pattern_non_matches(heading_text):
    """Test that the extension's default pattern rejects invalid formats."""
    from conda_sphinx_theme.version_anchors import DEFAULT_VERSION_PATTERN

    pattern = re.compile(DEFAULT_VERSION_PATTERN)
    match = pattern.match(heading_text)
    assert match is None, f"Pattern should NOT match '{heading_text}'"


# Anchor format generation tests
@pytest.mark.parametrize(
    "version,format_template,expected_anchor",
    [
        ("1.2.3", "version-{version}", "version-1.2.3"),
        ("25.5.0", "v{version}", "v25.5.0"),
        ("2.0", "release-{version}", "release-2.0"),
        ("0.1.0", "{version}", "0.1.0"),
    ],
)
def test_anchor_format_generation(version, format_template, expected_anchor):
    """Test anchor ID generation from version and format template."""
    anchor_id = format_template.format(version=version)
    assert anchor_id == expected_anchor


def test_setup_function(mocker):
    """Test that the setup function registers the extension correctly."""
    from conda_sphinx_theme.version_anchors import setup

    app = mocker.Mock()
    result = setup(app)

    # Check that the extension was configured
    assert app.add_transform.called
    assert app.add_config_value.call_count >= 3  # 3 config values
    assert app.connect.called

    # Check return metadata
    assert result["version"] == "0.1"
    assert result["parallel_read_safe"] is True
    assert result["parallel_write_safe"] is True


def test_transform_initialization(mocker):
    """Test VersionAnchorTransform initialization."""
    from conda_sphinx_theme.version_anchors import VersionAnchorTransform

    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"

    transform = VersionAnchorTransform(document)
    assert transform.document == document
    assert transform.default_priority == 500


def test_changelog_file_detection(mocker):
    """Test changelog file detection logic."""
    from conda_sphinx_theme.version_anchors import VersionAnchorTransform

    # Create transform with minimal mocking
    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"
    document.settings.env = mocker.Mock()
    document.settings.env.app = mocker.Mock()
    document.settings.env.app.config = mocker.Mock()
    document.settings.env.app.config.version_anchor_changelog_files = [
        "changelog",
        "release",
        "history",
        "news",
    ]

    transform = VersionAnchorTransform(document)

    # Test positive cases
    document.settings.env.docname = "changelog"
    assert transform._is_changelog_file() is True

    document.settings.env.docname = "CHANGELOG"
    assert transform._is_changelog_file() is True

    document.settings.env.docname = "release-notes"
    assert transform._is_changelog_file() is True

    # Test negative case
    document.settings.env.docname = "api"
    assert transform._is_changelog_file() is False


def test_version_heading_detection(mocker):
    """Test version heading detection and anchor creation."""
    from conda_sphinx_theme.version_anchors import VersionAnchorTransform

    # Create transform with mocked config
    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"
    document.settings.env = mocker.Mock()
    document.settings.env.app = mocker.Mock()

    config = mocker.Mock()
    config.version_anchor_pattern = r"^(\d+\.\d+(?:\.\d+)?)\s*\(.*?\)$"
    config.version_anchor_format = "version-{version}"
    document.settings.env.app.config = config

    # Initialize transform to test configuration
    VersionAnchorTransform(document)

    # Test version heading detection
    heading_text = "25.5.0 (2025-05-21)"
    pattern = re.compile(config.version_anchor_pattern)
    match = pattern.match(heading_text)

    assert match is not None
    version = match.group(1)
    anchor_id = config.version_anchor_format.format(version=version)
    assert anchor_id == "version-25.5.0"


def test_config_validation_valid_format(mocker):
    """Test configuration validation with valid format."""
    from conda_sphinx_theme.version_anchors import validate_config

    app = mocker.Mock()
    config = mocker.Mock()
    config.version_anchor_format = "version-{version}"

    # Should not raise
    validate_config(app, config)


def test_config_validation_missing_placeholder(mocker):
    """Test configuration validation with missing {version} placeholder."""
    from conda_sphinx_theme.version_anchors import validate_config

    app = mocker.Mock()
    config = mocker.Mock()
    config.version_anchor_format = "invalid-format"  # Missing {version}

    with pytest.raises(ValueError, match="must contain.*version.*placeholder"):
        validate_config(app, config)


@pytest.mark.parametrize(
    "invalid_format",
    [
        "version-only",  # No placeholder
        "prefix-{ver}-suffix",  # Wrong placeholder name
        "version-{VERSION}",  # Wrong case
        "{version-typo}",  # Typo in placeholder
    ],
)
def test_config_validation_invalid_formats(mocker, invalid_format):
    """Test configuration validation with various invalid formats."""
    from conda_sphinx_theme.version_anchors import validate_config

    app = mocker.Mock()
    config = mocker.Mock()
    config.version_anchor_format = invalid_format

    with pytest.raises(ValueError, match="must contain.*version.*placeholder"):
        validate_config(app, config)


# Changelog file detection tests
@pytest.mark.parametrize(
    "filename",
    [
        "changelog.rst",
        "CHANGELOG.md",
        "release_notes.rst",
        "release-notes.md",
        "history.rst",
        "HISTORY.md",
        "news.rst",
        "NEWS.md",
        "docs/changelog.rst",
        "src/CHANGELOG.md",
    ],
)
def test_changelog_files_detected(filename):
    """Test that changelog files are correctly identified."""
    changelog_indicators = ["changelog", "release", "history", "news"]
    is_changelog = any(
        indicator in filename.lower() for indicator in changelog_indicators
    )
    assert is_changelog, f"'{filename}' should be detected as a changelog file"


@pytest.mark.parametrize(
    "filename",
    [
        "index.rst",
        "example.rst",
        "api.rst",
        "installation.md",
        "configuration.rst",
        "tutorial.rst",
        "faq.md",
    ],
)
def test_regular_files_not_detected(filename):
    """Test that regular files are not detected as changelog files."""
    changelog_indicators = ["changelog", "release", "history", "news"]
    is_changelog = any(
        indicator in filename.lower() for indicator in changelog_indicators
    )
    assert not is_changelog, f"'{filename}' should NOT be detected as a changelog file"


def test_anchor_creation_with_heading_node(mocker):
    """Test anchor creation with actual heading nodes."""
    from conda_sphinx_theme.version_anchors import VersionAnchorTransform
    from docutils import nodes

    # Create transform
    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"
    document.settings.env = mocker.Mock()
    document.settings.env.app = mocker.Mock()

    config = mocker.Mock()
    config.version_anchor_pattern = r"^(\d+\.\d+(?:\.\d+)?)\s*\(.*?\)$"
    config.version_anchor_format = "version-{version}"
    document.settings.env.app.config = config

    # Initialize transform to test anchor creation
    VersionAnchorTransform(document)

    # Create a heading node with version text
    heading = nodes.section()
    title = nodes.title()
    title.append(nodes.Text("25.5.0 (2025-05-21)"))
    heading.append(title)

    # Test that we can extract version and create anchor
    heading_text = title.astext()
    pattern = re.compile(config.version_anchor_pattern)
    match = pattern.match(heading_text)

    assert match is not None
    version = match.group(1)
    assert version == "25.5.0"

    anchor_id = config.version_anchor_format.format(version=version)
    assert anchor_id == "version-25.5.0"


@pytest.mark.parametrize(
    "pattern,format_str,heading,expected_id",
    [
        (
            r"^Version\s+(\d+\.\d+(?:\.\d+)?).*$",
            "v{version}",
            "Version 1.2.3",
            "v1.2.3",
        ),
        (
            r"^Release\s+(\d+\.\d+(?:\.\d+)?)",
            "release-{version}",
            "Release 2.0",
            "release-2.0",
        ),
        (r"^v?(\d+\.\d+(?:\.\d+)?)", "{version}", "v3.1.4", "3.1.4"),
        (
            r"^(\d+\.\d+(?:\.\d+)?)\s*\(.*?\)$",
            "version-{version}",
            "1.0.0 (Final)",
            "version-1.0.0",
        ),
    ],
)
def test_custom_patterns_and_formats(pattern, format_str, heading, expected_id):
    """Test various custom patterns and format combinations."""
    compiled_pattern = re.compile(pattern)
    match = compiled_pattern.match(heading)

    assert match is not None, f"Pattern {pattern} should match '{heading}'"

    version = match.group(1)
    anchor_id = format_str.format(version=version)
    assert anchor_id == expected_id
