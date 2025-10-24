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


