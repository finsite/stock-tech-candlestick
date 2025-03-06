import sys

from packaging.version import Version


def next_version(current: str, part: str) -> str:
    """
    Increment a version.

    Args:
        current (str): The current version string. Must be in the format
            'major.minor.patch'.
        part (str): The part of the version to increment ('major', 'minor', or
            'patch').

    Returns:
        str: A new version string with the specified part incremented.
    """
    v = Version(current)
    if part == "major":
        # Increment the major version (e.g. 0.1.0 -> 1.0.0)
        # The major version is incremented by setting the minor and patch
        # versions to 0
        return f"{v.major + 1}.0.0"
    elif part == "minor":
        # Increment the minor version (e.g. 0.1.0 -> 0.2.0)
        # The minor version is incremented by setting the patch version to 0
        return f"{v.major}.{v.minor + 1}.0"
    elif part == "patch":
        # Increment the patch version (e.g. 0.1.0 -> 0.1.1)
        return f"{v.major}.{v.minor}.{v.micro + 1}"
    else:
        raise ValueError(
            f"Invalid part '{part}'. Must be one of 'major', 'minor', or 'patch'."
        )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python setup.py <current_version> <major|minor|patch>")
        sys.exit(1)
    current_version, part = sys.argv[1], sys.argv[2]
    try:
        print(next_version(current_version, part))
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
