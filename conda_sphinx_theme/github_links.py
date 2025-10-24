"""
GitHub Links Sphinx Extension

This extension automatically converts GitHub issue and pull request references
into clickable links in changelog files.

Usage:
    Add 'conda_sphinx_theme.github_links' to your extensions list in conf.py:

    extensions = [
        # ... your other extensions
        'conda_sphinx_theme.github_links',
    ]

    Then configure your GitHub repository:

    github_links_repo = "owner/repo"  # Required
    github_links_url = "https://github.com/{repo}/issues/{number}"  # Optional
    github_links_new_tab = False  # Optional
    github_links_pattern = r"\\((?:([^/\\s]+/[^/\\s]+)#)?(\\d+)\\)"  # Optional
    github_links_changelog_files = ["changelog", "release", "history", "news"]  # Optional

The extension will automatically detect changelog files and convert patterns like:
- (#123) → links to your-repo/issues/123
- (owner/repo#456) → links to owner/repo/issues/456
"""

import re
from docutils import nodes
from sphinx.transforms import SphinxTransform
from sphinx.application import Sphinx
from sphinx.config import Config


class GitHubLinkTransform(SphinxTransform):
    """Transform that converts GitHub issue references to clickable links."""

    default_priority = 500  # Run after most other transforms

    def apply(self):
        """Apply the GitHub link transformation to the document."""
        # Only process if this is a changelog file
        if not self._is_changelog_file():
            return

        config = self.app.config

        # Compile the pattern once
        try:
            pattern = re.compile(config.github_links_pattern)
        except re.error as e:
            logger = self.document.settings.env.app.logger
            logger.warning(f"Invalid github_links_pattern: {e}")
            return

        # Find and replace GitHub references in text nodes
        for node in self.document.findall(nodes.Text):
            if pattern.search(node.astext()):
                new_nodes = self._create_github_links(node, pattern, config)
                if new_nodes:
                    # Replace the text node with the new nodes
                    parent = node.parent
                    index = parent.index(node)
                    parent.remove(node)
                    for i, new_node in enumerate(new_nodes):
                        parent.insert(index + i, new_node)

    def _is_changelog_file(self):
        """Check if the current file is a changelog file."""
        if not hasattr(self.document.settings, "env"):
            return False

        docname = self.document.settings.env.docname
        changelog_files = self.app.config.github_links_changelog_files

        return any(indicator in docname.lower() for indicator in changelog_files)

    def _create_github_links(self, text_node, pattern, config):
        """Create new nodes with GitHub links replacing issue references."""
        text = text_node.astext()
        nodes_list = []
        last_end = 0

        for match in pattern.finditer(text):
            # Add text before the match
            if match.start() > last_end:
                nodes_list.append(nodes.Text(text[last_end : match.start()]))

            # Extract repo and issue number
            repo_match = match.group(1)  # owner/repo or None
            issue_number = match.group(2)  # issue number

            # Determine the repository to use
            repo = repo_match or config.github_links_repo

            # Create the GitHub URL
            github_url = config.github_links_url.format(repo=repo, number=issue_number)

            # Create link text (what the user sees)
            if repo_match:
                link_text = f"{repo_match}#{issue_number}"
            else:
                link_text = f"#{issue_number}"

            # Create the reference node (clickable link)
            ref_node = nodes.reference(
                text=link_text,
                refuri=github_url,
            )

            # Add new tab attributes if configured
            if config.github_links_new_tab:
                ref_node["target"] = "_blank"
                ref_node["rel"] = "noopener"

            ref_node.append(nodes.Text(link_text))

            # Add opening parenthesis, link, closing parenthesis
            nodes_list.append(nodes.Text("("))
            nodes_list.append(ref_node)
            nodes_list.append(nodes.Text(")"))

            last_end = match.end()

        # Add remaining text after the last match
        if last_end < len(text):
            nodes_list.append(nodes.Text(text[last_end:]))

        return nodes_list if len(nodes_list) > 1 else None


def validate_config(app: Sphinx, config: Config):
    """Validate the GitHub links configuration."""
    repo = config.github_links_repo

    if not repo:
        raise ValueError(
            "github_links_repo is required when using the GitHub Links extension. "
            "Please set it in your conf.py: github_links_repo = 'owner/repo'"
        )

    if not isinstance(repo, str) or "/" not in repo:
        raise ValueError(
            f"github_links_repo must be in 'owner/repo' format, got: {repo!r}"
        )

    # Basic validation: should have exactly one slash and non-empty parts
    parts = repo.split("/")
    if len(parts) != 2 or not all(part.strip() for part in parts):
        raise ValueError(
            f"github_links_repo must be in 'owner/repo' format, got: {repo!r}"
        )


def setup(app: Sphinx):
    """Set up the Sphinx extension."""
    app.add_transform(GitHubLinkTransform)

    # Add configuration values
    app.add_config_value(
        "github_links_repo",
        None,  # No default, must be set by user
        "env",  # Rebuild environment when this changes
        [str],  # Expected type
    )

    app.add_config_value(
        "github_links_url",
        "https://github.com/{repo}/issues/{number}",  # Default to issues
        "env",
        [str],
    )

    app.add_config_value(
        "github_links_pattern",
        r"\\((?:([^/\\s]+/[^/\\s]+)#)?(\\d+)\\)",  # Default pattern
        "env",
        [str],
    )

    app.add_config_value(
        "github_links_changelog_files",
        ["changelog", "release", "history", "news"],  # Default indicators
        "env",
        [list],
    )

    app.add_config_value(
        "github_links_new_tab",
        False,  # Default: open in same tab
        "env",
        [bool],
    )

    # Connect the config validation
    app.connect("config-inited", validate_config)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
