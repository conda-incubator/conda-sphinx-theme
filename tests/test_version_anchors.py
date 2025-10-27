"""
Tests for the Version Anchors Sphinx extension.

This module contains comprehensive tests for the version_anchors extension
that automatically adds version anchors to changelog headings.
"""

import re
import pytest


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


def test_transform_apply_with_version_heading(mocker):
    """Test the transform apply method with a version heading."""
    from conda_sphinx_theme.version_anchors import (
        VersionAnchorTransform,
        DEFAULT_VERSION_PATTERN,
        DEFAULT_ANCHOR_FORMAT,
        DEFAULT_CHANGELOG_FILES,
    )
    from docutils import nodes

    # Create a document with a section containing a version heading
    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"  # Must be a string for docutils
    document.settings.env = mocker.Mock()
    document.settings.env.docname = "changelog"
    document.settings.env.app = mocker.Mock()
    document.settings.env.app.config = mocker.Mock()
    document.settings.env.app.config.version_anchor_pattern = DEFAULT_VERSION_PATTERN
    document.settings.env.app.config.version_anchor_format = DEFAULT_ANCHOR_FORMAT
    document.settings.env.app.config.version_anchor_changelog_files = (
        DEFAULT_CHANGELOG_FILES
    )
    document.settings.env.domaindata = {"std": {"labels": {}}}
    document.ids = {}

    # Create a section with a title
    section = nodes.section()
    title = nodes.title(text="1.2.3 (2025-01-24)")
    section.append(title)

    # Mock traverse to return our section
    document.traverse = mocker.Mock(return_value=[section])

    # Create and apply the transform
    transform = VersionAnchorTransform(document)
    transform.apply()

    # Verify the anchor was created
    assert section["ids"] == ["version-1.2.3"]
    assert "version-1.2.3" in document.ids
    assert document.ids["version-1.2.3"] == section
    assert "version-1.2.3" in document.settings.env.domaindata["std"]["labels"]


def test_transform_apply_non_changelog_file(mocker):
    """Test that transform doesn't apply to non-changelog files."""
    from conda_sphinx_theme.version_anchors import (
        VersionAnchorTransform,
        DEFAULT_CHANGELOG_FILES,
    )

    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"  # Must be a string for docutils
    document.settings.env = mocker.Mock()
    document.settings.env.docname = "api"  # Not a changelog
    document.settings.env.app = mocker.Mock()
    document.settings.env.app.config = mocker.Mock()
    document.settings.env.app.config.version_anchor_changelog_files = (
        DEFAULT_CHANGELOG_FILES
    )

    # Mock traverse - should not be called
    document.traverse = mocker.Mock()

    transform = VersionAnchorTransform(document)
    transform.apply()

    # Verify traverse was not called
    document.traverse.assert_not_called()


def test_transform_apply_non_version_heading(mocker):
    """Test that transform ignores non-version headings."""
    from conda_sphinx_theme.version_anchors import (
        VersionAnchorTransform,
        DEFAULT_VERSION_PATTERN,
        DEFAULT_ANCHOR_FORMAT,
        DEFAULT_CHANGELOG_FILES,
    )
    from docutils import nodes

    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"  # Must be a string for docutils
    document.settings.env = mocker.Mock()
    document.settings.env.docname = "changelog"
    document.settings.env.app = mocker.Mock()
    document.settings.env.app.config = mocker.Mock()
    document.settings.env.app.config.version_anchor_pattern = DEFAULT_VERSION_PATTERN
    document.settings.env.app.config.version_anchor_format = DEFAULT_ANCHOR_FORMAT
    document.settings.env.app.config.version_anchor_changelog_files = (
        DEFAULT_CHANGELOG_FILES
    )
    document.ids = {}

    # Create a section with a non-version title
    section = nodes.section()
    title = nodes.title(text="Introduction")
    section.append(title)

    document.traverse = mocker.Mock(return_value=[section])

    transform = VersionAnchorTransform(document)
    transform.apply()

    # Verify no anchor was created
    assert "ids" not in section or section.get("ids", []) == []
    assert len(document.ids) == 0


def test_version_role(mocker):
    """Test the custom version role."""
    from conda_sphinx_theme.version_anchors import version_role, DEFAULT_ANCHOR_FORMAT
    from docutils import nodes

    # Mock inliner and document
    inliner = mocker.Mock()
    inliner.document = mocker.Mock()
    inliner.document.settings = mocker.Mock()
    inliner.document.settings.env = mocker.Mock()
    inliner.document.settings.env.app = mocker.Mock()
    inliner.document.settings.env.app.config = mocker.Mock()
    inliner.document.settings.env.app.config.version_anchor_format = (
        DEFAULT_ANCHOR_FORMAT
    )

    # Call the role
    result_nodes, messages = version_role(
        name="version",
        rawtext=":version:`1.2.3`",
        text="1.2.3",
        lineno=1,
        inliner=inliner,
    )

    # Verify the result
    assert len(result_nodes) == 1
    assert isinstance(result_nodes[0], nodes.reference)
    assert result_nodes[0].astext() == "1.2.3"
    assert result_nodes[0]["refuri"] == "#version-1.2.3"
    assert messages == []


def test_config_validation_empty_result(mocker):
    """Test configuration validation with format that produces empty results."""
    from conda_sphinx_theme.version_anchors import validate_config

    app = mocker.Mock()
    config = mocker.Mock()
    config.version_anchor_format = "   {version}   "  # Valid but might be problematic

    # This should pass - spaces are allowed
    validate_config(app, config)
