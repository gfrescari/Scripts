import subprocess
import sys


def list_zip_files(zip_file: str) -> list[str]:
    """Return lines from `unzip -l` output."""
    result = subprocess.run(
        ["unzip", "-l", zip_file],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.splitlines()


def filter_files(lines: list[str], patterns: list[str]) -> list[str]:
    """Filter filenames matching any of the given patterns."""
    files = [None]  # index 0 intentionally unused
    patterns = [p.lower() for p in patterns]

    for line in lines:
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue

        filename = parts[3]

        if any(p in filename.lower() for p in patterns):
            files.append(filename)

    return files


def print_files(files: list[str]) -> None:
    """Print files as: <index>. <filename>"""
    for i in range(1, len(files)):
        print(f"{i}. {files[i]}")


def prompt_for_index(max_index: int) -> int:
    """Prompt user for a valid file index."""
    while True:
        try:
            choice = int(input(f"\nEnter file index to extract (1-{max_index}): "))
            if 1 <= choice <= max_index:
                return choice
            print("Index out of range.")
        except ValueError:
            print("Please enter a valid number.")


def extract_file(zip_file: str, filename: str) -> None:
    """Extract a single file from the zip."""
    subprocess.run(
        ["unzip", zip_file, filename],
        check=True
    )
    print(f"\nExtracted: {filename}")


def main() -> None:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <zipfile> <pattern1> [pattern2 ...]")
        sys.exit(1)

    zip_file = sys.argv[1]
    patterns = sys.argv[2:]

    lines = list_zip_files(zip_file)
    files = filter_files(lines, patterns)

    if len(files) == 1:
        print("No matching files found.")
        sys.exit(0)

    print_files(files)

    index = prompt_for_index(len(files) - 1)
    extract_file(zip_file, files[index])


if __name__ == "__main__":
    main()
