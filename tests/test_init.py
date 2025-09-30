"""
Tests for the main conda_sphinx_theme module.
"""

import os


def test_module_imports():
    """Test that the main module can be imported without errors."""
    import conda_sphinx_theme
    
    # Test that the module has expected attributes
    assert hasattr(conda_sphinx_theme, '__version__')
    
    # Test that the version is a string
    assert isinstance(conda_sphinx_theme.__version__, str)
    
    # Test that version is not empty
    assert len(conda_sphinx_theme.__version__) > 0


def test_get_html_theme_path():
    """Test the get_html_theme_path function."""
    import conda_sphinx_theme
    
    # The function should return the path to the theme directory
    theme_path = conda_sphinx_theme.get_html_theme_path()
    
    # Should return a list containing one path
    assert isinstance(theme_path, list)
    assert len(theme_path) == 1
    
    # The path should exist
    assert os.path.exists(theme_path[0])
    
    # The path should contain the theme files
    theme_dir = theme_path[0]
    assert os.path.exists(os.path.join(theme_dir, 'conda_sphinx_theme'))
