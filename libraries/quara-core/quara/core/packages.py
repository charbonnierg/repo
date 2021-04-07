"""
Utilities to parse versions.
"""
import pkg_resources


def get_version(package_name: str) -> str:
    """Get a version from a package name."""
    return pkg_resources.get_distribution(package_name).version
