"""
Sphinx extension to automatically add version anchors to changelog headings.

This extension finds headings that match version patterns (e.g., "25.5.0 (2025-05-21)")
and automatically assigns them anchor IDs using a configurable format.

Configuration in conf.py:

    # Pattern to match version headings (must have exactly one capture group for the version)
    version_anchor_pattern = r"^(\d+\.\d+(?:\.\d+)?)\s*\(.*?\)$"  # Default

    # Format template for anchor IDs (use {version} as placeholder)
    version_anchor_format = "version-{version}"  # Default

    # Alternative patterns you might want to use:
    # version_anchor_pattern = r"^Version\s+(\d+\.\d+(?:\.\d+)?).*$"  # For "Version 1.2.3" format
    # version_anchor_pattern = r"^Release\s+(\d+\.\d+(?:\.\d+)?)"    # For "Release 1.2.3" format
    # version_anchor_pattern = r"^v?(\d+\.\d+(?:\.\d+)?)"           # For "v1.2.3" or "1.2.3" format

    # Alternative anchor formats you might want to use:
    # version_anchor_format = "v{version}"           # Creates anchors like "v25.5.0"
    # version_anchor_format = "release-{version}"    # Creates anchors like "release-25.5.0"
    # version_anchor_format = "{version}"            # Creates anchors like "25.5.0" (not recommended for HTML4/XHTML)

    # File patterns that indicate changelog files (case-insensitive)
    version_anchor_changelog_files = ["changelog", "release", "history", "news"]  # Default

Example usage:
    If you have a heading like "25.5.0 (2025-05-21)" in a changelog file,
    this extension will automatically create an anchor with ID based on version_anchor_format.
    With the default format "version-{version}", you can link to it with:
    :version:`25.5.0` or :ref:`version-25.5.0` or by URL fragment #version-25.5.0
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from docutils import nodes
from docutils.transforms import Transform

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config


class VersionAnchorTransform(Transform):
    """Transform to add version anchors to changelog headings."""

    default_priority = 500

    def apply(self):
        """Apply the transform to the document."""
        # Only apply to files that look like changelogs
        if not self._is_changelog_file():
            return

        # Get the configuration from app config
        env = self.document.settings.env
        version_pattern_str = env.app.config.version_anchor_pattern
        anchor_format = env.app.config.version_anchor_format
        version_pattern = re.compile(version_pattern_str)

        for node in self.document.traverse(nodes.section):
            title_node = node.next_node(nodes.title)
            if title_node:
                title_text = title_node.astext().strip()
                match = version_pattern.match(title_text)

                if match:
                    version = match.group(1)
                    anchor_id = anchor_format.format(version=version)

                    # Set the section ID
                    node["ids"] = [anchor_id]

                    # Also add it to the document's id mapping
                    self.document.ids[anchor_id] = node

                    # Add to the environment's toctree for proper linking
                    env = self.document.settings.env
                    if hasattr(env, "domaindata") and "std" in env.domaindata:
                        env.domaindata["std"]["labels"][anchor_id] = (
                            env.docname,
                            anchor_id,
                            title_text,
                        )

    def _is_changelog_file(self):
        """Check if this is a changelog-type file."""
        env = self.document.settings.env
        docname = env.docname

        # Get the changelog file patterns from configuration
        changelog_indicators = env.app.config.version_anchor_changelog_files
        return any(indicator in docname.lower() for indicator in changelog_indicators)


def version_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Custom role for referencing version anchors.

    Usage: :version:`25.5.0` will create a reference to the anchor using the configured format
    """
    if options is None:
        options = {}
    if content is None:
        content = []

    version = text.strip()

    # Get the anchor format from the app config
    env = inliner.document.settings.env
    anchor_format = env.app.config.version_anchor_format
    anchor_id = anchor_format.format(version=version)

    # Create a reference node
    ref_node = nodes.reference(
        rawtext,
        version,  # Display text
        refuri=f"#{anchor_id}",
        **options,
    )

    return [ref_node], []


def validate_config(app, config):
    """Validate the configuration values."""
    anchor_format = config.version_anchor_format

    # Check if the format contains the required {version} placeholder
    if "{version}" not in anchor_format:
        raise ValueError(
            f"version_anchor_format must contain '{{version}}' placeholder. "
            f"Got: '{anchor_format}'. "
            f"Example valid formats: 'version-{{version}}', 'v{{version}}', 'release-{{version}}'"
        )

    # Test that the format string is valid by trying to format it
    try:
        test_result = anchor_format.format(version="1.0.0")
        # Additional check: ensure the formatted result is not empty
        if not test_result.strip():
            raise ValueError(
                f"version_anchor_format produces empty anchor IDs. "
                f"Got format: '{anchor_format}'"
            )
    except KeyError as e:
        raise ValueError(
            f"version_anchor_format contains invalid placeholder: {e}. "
            f"Only '{{version}}' is supported. Got: '{anchor_format}'"
        ) from e
    except Exception as e:
        raise ValueError(
            f"version_anchor_format is invalid: {e}. Got: '{anchor_format}'"
        ) from e


def setup(app: Sphinx):
    """Set up the Sphinx extension."""
    app.add_transform(VersionAnchorTransform)

    # Add the custom :version: role
    app.add_role("version", version_role)

    # Add configuration values
    app.add_config_value(
        "version_anchor_pattern",
        r"^(\d+\.\d+(?:\.\d+)?)\s*\(.*?\)$",  # Default pattern
        "env",  # Rebuild environment when this changes
        [str],  # Expected type
    )

    app.add_config_value(
        "version_anchor_format",
        "version-{version}",  # Default format template
        "env",  # Rebuild environment when this changes
        [str],  # Expected type
    )

    app.add_config_value(
        "version_anchor_changelog_files",
        ["changelog", "release", "history", "news"],  # Default file indicators
        "env",  # Rebuild environment when this changes
        [list],  # Expected type
    )

    # Connect the config validation
    app.connect("config-inited", validate_config)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
