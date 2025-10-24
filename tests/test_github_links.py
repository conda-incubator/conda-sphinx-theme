"""
Tests for the GitHub Links Sphinx extension.

This module contains comprehensive tests for the github_links extension,
separate from the lightweight config validation that runs on every build.
"""

import re
import pytest


# Test fixtures
@pytest.fixture
def github_pattern():
    """Fixture providing the compiled regex pattern."""
    return re.compile("\\((?:([^/\\s]+/[^/\\s]+)#|#)(\\d+)\\)")


@pytest.fixture
def mock_config(mocker):
    """Fixture providing a mock Sphinx app config."""
    config = mocker.Mock()
    config.github_links_repo = "conda/conda"
    config.github_links_url = "https://github.com/{repo}/issues/{number}"
    config.github_links_pattern = "\\((?:([^/\\s]+/[^/\\s]+)#|#)(\\d+)\\)"
    config.github_links_changelog_files = ["changelog", "release", "history", "news"]
    config.github_links_new_tab = False
    return config


# Pattern matching tests
@pytest.mark.parametrize("test_input,expected_repo,expected_number", [
    ("(#42)", None, "42"),
    ("(#1)", None, "1"), 
    ("(#1234)", None, "1234"),
    ("(conda/conda#789)", "conda/conda", "789"),
    ("(myorg/myproject#55)", "myorg/myproject", "55"),
    ("(conda-incubator/conda-sphinx-theme#999)", "conda-incubator/conda-sphinx-theme", "999"),
])
def test_pattern_matches(github_pattern, test_input, expected_repo, expected_number):
    """Test the default pattern matches expected formats."""
    match = github_pattern.search(test_input)
    assert match is not None, f"Pattern should match '{test_input}'"
    assert len(match.groups()) == 2, f"Pattern should have 2 capture groups for '{test_input}'"

    actual_repo, actual_number = match.groups()
    assert actual_repo == expected_repo, (
        f"Repo mismatch for '{test_input}': got '{actual_repo}', expected '{expected_repo}'"
    )
    assert actual_number == expected_number, (
        f"Number mismatch for '{test_input}': got '{actual_number}', expected '{expected_number}'"
    )


@pytest.mark.parametrize("test_input", [
    "(#)",  # No number
    "(123)",  # No hash - should require # or repo#
    "(abc#123)",  # Invalid repo format (no slash)
    "(#abc)",  # Non-numeric issue number  
    "123",  # No parentheses
    "(owner/#123)",  # Empty repo name part
    "(#123#456)",  # Multiple hashes
    "#123",  # No parentheses
    "()",  # Empty parentheses
])
def test_pattern_non_matches(github_pattern, test_input):
    """Test that the pattern correctly rejects invalid formats."""
    match = github_pattern.search(test_input)
    assert match is None, f"Pattern should NOT match invalid format '{test_input}'"


@pytest.mark.parametrize("test_input,expected_link_text,expected_final_format", [
    ("(#123)", "#123", "(<link>#123</link>)"),
    ("(conda/conda#456)", "conda/conda#456", "(<link>conda/conda#456</link>)"),
    ("(owner/repo#789)", "owner/repo#789", "(<link>owner/repo#789</link>)"),
])
def test_link_text_formatting(github_pattern, test_input, expected_link_text, expected_final_format):
    """Test that link text excludes parentheses but includes issue reference."""
    match = github_pattern.search(test_input)
    assert match is not None, f"Pattern should match '{test_input}'"

    # Simulate the link text creation logic from the extension
    repo_match = match.group(1)
    number = match.group(2)

    if repo_match:
        link_text = f"{repo_match}#{number}"
    else:
        link_text = f"#{number}"

    assert link_text == expected_link_text, (
        f"Link text for '{test_input}': got '{link_text}', expected '{expected_link_text}'"
    )

    # Verify the format contains the link text as expected in the final format
    assert link_text in expected_final_format, (
        f"Format verification for '{test_input}': expected '{link_text}' to be in '{expected_final_format}'"
    )


# URL generation tests
@pytest.mark.parametrize("repo_from_match,issue_number,config_repo,expected_url", [
    (None, "42", "myorg/myproject", "https://github.com/myorg/myproject/issues/42"),
    ("conda/conda", "789", "myorg/myproject", "https://github.com/conda/conda/issues/789"),
    ("different/repo", "123", "default/repo", "https://github.com/different/repo/issues/123"),
])
def test_url_generation(repo_from_match, issue_number, config_repo, expected_url):
    """Test URL generation for various configurations."""
    # Determine which repo to use (match repo takes precedence)
    repo = repo_from_match or config_repo
    url = f"https://github.com/{repo}/issues/{issue_number}"

    assert url == expected_url, f"URL mismatch: got '{url}', expected '{expected_url}'"


@pytest.mark.parametrize("template,repo,number,expected", [
    ("https://github.com/{repo}/pull/{number}", "owner/repo", "123", "https://github.com/owner/repo/pull/123"),
    ("https://git.example.com/{repo}/issues/{number}", "org/project", "456", "https://git.example.com/org/project/issues/456"),
])
def test_custom_url_template(template, repo, number, expected):
    """Test that custom URL templates work."""
    result = template.format(repo=repo, number=number)
    assert result == expected


# Configuration validation tests
@pytest.mark.parametrize("repo", [
    "conda/conda",
    "owner/repo", 
    "conda-incubator/conda-sphinx-theme",
    "my-org/my-project",
    "123/456",  # Numbers are valid in GitHub usernames/repos
])
def test_valid_repo_formats(mocker, repo):
    """Test that valid repository formats are accepted."""
    from conda_sphinx_theme.github_links import validate_config

    config = mocker.Mock()
    config.github_links_repo = repo
    
    app = mocker.Mock()
    # Should not raise any exception
    validate_config(app, config)


@pytest.mark.parametrize("repo", [
    "",  # Empty
    "repo",  # Missing owner
    "owner/",  # Missing repo
    "/repo",  # Missing owner
    "owner repo",  # Space instead of slash
    "owner\\repo",  # Wrong separator
    None,  # None value
])
def test_invalid_repo_formats(mocker, repo):
    """Test that invalid repository formats are rejected."""
    from conda_sphinx_theme.github_links import validate_config

    config = mocker.Mock()
    config.github_links_repo = repo
    
    app = mocker.Mock()
    with pytest.raises(ValueError):
        validate_config(app, config)


# Changelog detection tests  
@pytest.fixture
def changelog_indicators():
    """Fixture providing changelog indicators."""
    return ["changelog", "release", "history", "news"]


@pytest.mark.parametrize("filename", [
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
])
def test_changelog_files_detected(changelog_indicators, filename):
    """Test that changelog files are correctly identified."""
    is_changelog = any(
        indicator in filename.lower() for indicator in changelog_indicators
    )
    assert is_changelog, f"'{filename}' should be detected as a changelog file"


@pytest.mark.parametrize("filename", [
    "index.rst",
    "example.rst",
    "api.rst", 
    "installation.md",
    "configuration.rst",
    "tutorial.rst",
    "faq.md",
])
def test_regular_files_not_detected(changelog_indicators, filename):
    """Test that regular files are not detected as changelog files."""
    is_changelog = any(
        indicator in filename.lower() for indicator in changelog_indicators
    )
    assert not is_changelog, f"'{filename}' should NOT be detected as a changelog file"


# Integration tests for the actual Sphinx extension
def test_setup_function(mocker):
    """Test that the setup function registers the extension correctly."""
    from conda_sphinx_theme.github_links import setup
    
    app = mocker.Mock()
    result = setup(app)
    
    # Check that the extension was configured
    assert app.add_transform.called
    assert app.add_config_value.call_count >= 5  # 5 config values
    assert app.connect.called
    
    # Check return metadata
    assert result["version"] == "0.1"
    assert result["parallel_read_safe"] is True
    assert result["parallel_write_safe"] is True


def test_create_github_links_method(mocker):
    """Test GitHub link creation logic directly."""
    from conda_sphinx_theme.github_links import GitHubLinkTransform
    from docutils import nodes
    
    # Create a minimal transform instance
    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"
    transform = GitHubLinkTransform(document)
    
    # Create pattern and mock config
    pattern = re.compile("\\((?:([^/\\s]+/[^/\\s]+)#|#)(\\d+)\\)")
    config = mocker.Mock()
    config.github_links_repo = "conda/conda"
    config.github_links_url = "https://github.com/{repo}/issues/{number}"
    config.github_links_new_tab = False
    
    # Test link creation
    test_text = nodes.Text("Fixed issue (#123)")
    result_nodes = transform._create_github_links(test_text, pattern, config)
    
    assert result_nodes is not None
    assert len(result_nodes) >= 3  # Should have text + link + text components
    
    # Check that a reference node was created
    ref_nodes = [n for n in result_nodes if isinstance(n, nodes.reference)]
    assert len(ref_nodes) == 1
    assert ref_nodes[0].get('refuri') == "https://github.com/conda/conda/issues/123"


def test_changelog_file_detection(mocker):
    """Test changelog file detection logic directly."""
    from conda_sphinx_theme.github_links import GitHubLinkTransform
    
    # Create transform with minimal mocking
    document = mocker.Mock()
    document.settings = mocker.Mock()
    document.settings.language_code = "en"
    document.settings.env = mocker.Mock()
    document.settings.env.app = mocker.Mock()
    document.settings.env.app.config = mocker.Mock()
    document.settings.env.app.config.github_links_changelog_files = ["changelog", "release", "history", "news"]
    
    transform = GitHubLinkTransform(document)
    
    # Test positive case
    document.settings.env.docname = "changelog"
    assert transform._is_changelog_file() is True
    
    # Test negative case  
    document.settings.env.docname = "api"
    assert transform._is_changelog_file() is False
    
    # Test case insensitive
    document.settings.env.docname = "CHANGELOG"
    assert transform._is_changelog_file() is True


def test_validate_config_function(mocker):
    """Test configuration validation function."""
    from conda_sphinx_theme.github_links import validate_config
    
    # Test valid config
    app = mocker.Mock()
    config = mocker.Mock()
    config.github_links_repo = "conda/conda"
    
    # Should not raise
    validate_config(app, config)
    
    # Test missing config
    config.github_links_repo = None
    with pytest.raises(ValueError, match="required"):
        validate_config(app, config)
    
    # Test invalid format
    config.github_links_repo = "invalid-repo"
    with pytest.raises(ValueError, match="owner/repo"):
        validate_config(app, config)


def test_github_link_creation_with_repo_override(mocker):
    """Test link creation when text includes repo override."""
    from conda_sphinx_theme.github_links import GitHubLinkTransform
    from docutils import nodes
    
    # Set up transform
    document = mocker.Mock()
    document.settings = mocker.Mock() 
    document.settings.language_code = "en"
    transform = GitHubLinkTransform(document)
    
    # Create pattern and config
    pattern = re.compile("\\((?:([^/\\s]+/[^/\\s]+)#|#)(\\d+)\\)")
    config = mocker.Mock()
    config.github_links_repo = "default/repo"
    config.github_links_url = "https://github.com/{repo}/issues/{number}"
    config.github_links_new_tab = True
    
    # Test with repo override
    test_text = nodes.Text("See issue (conda/conda#456)")
    result_nodes = transform._create_github_links(test_text, pattern, config)
    
    assert result_nodes is not None
    ref_nodes = [n for n in result_nodes if isinstance(n, nodes.reference)]
    assert len(ref_nodes) == 1
    assert ref_nodes[0].get('refuri') == "https://github.com/conda/conda/issues/456"
    assert ref_nodes[0].astext() == "conda/conda#456"
    
        # Check new tab attributes
    assert ref_nodes[0].get('target') == "_blank"
    assert ref_nodes[0].get('rel') == "noopener"
    """Test the regex pattern matching functionality."""

    @pytest.fixture
    def pattern(self):
        """Fixture providing the compiled regex pattern."""
        return re.compile("\\((?:([^/\\s]+/[^/\\s]+)#|#)(\\d+)\\)")

    @pytest.mark.parametrize("test_input,expected_repo,expected_number", [
        ("(#42)", None, "42"),
        ("(#1)", None, "1"),
        ("(#1234)", None, "1234"),
        ("(conda/conda#789)", "conda/conda", "789"),
        ("(myorg/myproject#55)", "myorg/myproject", "55"),
        ("(conda-incubator/conda-sphinx-theme#999)", "conda-incubator/conda-sphinx-theme", "999"),
    ])
    def test_default_pattern(self, pattern, test_input, expected_repo, expected_number):
        """Test the default pattern matches expected formats."""
        match = pattern.search(test_input)
        assert match is not None, f"Pattern should match '{test_input}'"
        assert len(match.groups()) == 2, f"Pattern should have 2 capture groups for '{test_input}'"

        actual_repo, actual_number = match.groups()
        assert actual_repo == expected_repo, (
            f"Repo mismatch for '{test_input}': got '{actual_repo}', expected '{expected_repo}'"
        )
        assert actual_number == expected_number, (
            f"Number mismatch for '{test_input}': got '{actual_number}', expected '{expected_number}'"
        )

    @pytest.mark.parametrize("test_input", [
        "(#)",  # No number
        "(123)",  # No hash - should require # or repo#
        "(abc#123)",  # Invalid repo format (no slash)
        "(#abc)",  # Non-numeric issue number  
        "123",  # No parentheses
        "(owner/#123)",  # Empty repo name part
        "(#123#456)",  # Multiple hashes
        "#123",  # No parentheses
        "()",  # Empty parentheses
    ])
    def test_pattern_non_matches(self, pattern, test_input):
        """Test that the pattern correctly rejects invalid formats."""
        match = pattern.search(test_input)
        assert match is None, f"Pattern should NOT match invalid format '{test_input}'"

    @pytest.mark.parametrize("test_input,expected_link_text,expected_final_format", [
        ("(#123)", "#123", "(<link>#123</link>)"),
        ("(conda/conda#456)", "conda/conda#456", "(<link>conda/conda#456</link>)"),
        ("(owner/repo#789)", "owner/repo#789", "(<link>owner/repo#789</link>)"),
    ])
    def test_link_text_formatting(self, pattern, test_input, expected_link_text, expected_final_format):
        """Test that link text excludes parentheses but includes issue reference."""
        match = pattern.search(test_input)
        assert match is not None, f"Pattern should match '{test_input}'"

        # Simulate the link text creation logic from the extension
        repo_match = match.group(1)
        number = match.group(2)

        if repo_match:
            link_text = f"{repo_match}#{number}"
        else:
            link_text = f"#{number}"

        assert link_text == expected_link_text, (
            f"Link text for '{test_input}': got '{link_text}', expected '{expected_link_text}'"
        )

        # Verify the format contains the link text as expected in the final format
        assert link_text in expected_final_format, (
            f"Format verification for '{test_input}': expected '{link_text}' to be in '{expected_final_format}'"
        )
