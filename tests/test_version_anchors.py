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


def test_changelog_file_detection(mocker):
    """Test changelog file detection logic."""
    from conda_sphinx_theme.version_anchors import (
        VersionAnchorTransform,
        DEFAULT_CHANGELOG_FILES,
    )

    # Create transform with minimal mocking
    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"
    document.settings.env = mocker.Mock()
    document.settings.env.app = mocker.Mock()
    document.settings.env.app.config = mocker.Mock()
    document.settings.env.app.config.version_anchor_changelog_files = (
        DEFAULT_CHANGELOG_FILES
    )

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

