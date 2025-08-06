
# references:
#   - https://favicon.io
#   - https://realfavicongenerator.net

import argparse
import os
from pathlib import Path

import yaml

TEMPLATE_FILE = "template.html"
STYLE_FILE = "style.css"
ASSETS_DIR = "assets"
DEFAULT_OUTPUT_DIR = "docs"

FAVICONS = {
    "pmb": f"{ASSETS_DIR}/p_favicon.png",
    "work": f"{ASSETS_DIR}/a_favicon.png",
    "other": f"{ASSETS_DIR}/o_favicon.png",
}

VALID_CATEGORIES = ["pmb", "work", "other"]


def load_template():
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(f"Template file '{TEMPLATE_FILE}' not found.")
    with open(TEMPLATE_FILE, "r") as f:
        return f.read()


def ensure_style_linked(output_dir):
    dest = Path(output_dir) / "style.css"
    try:
        if not dest.exists():
            os.symlink(os.path.abspath(STYLE_FILE), dest)
    except OSError:
        import shutil

        shutil.copyfile(STYLE_FILE, dest)


def sanitize_filename(title):
    return title.lower().replace(" ", "_")


def generate_html(title, category, output_dir, force=False):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_style_linked(output_dir)

    template = load_template()
    favicon = FAVICONS.get(category, FAVICONS["other"])
    safe_title = sanitize_filename(title)
    output_path = output_dir / f"{safe_title}.html"

    if output_path.exists() and not force:
        print(f"⚠️ Skipping '{title}': {output_path} already exists (use --force to overwrite)")
        return

    html_content = (
        template.replace("{{ TITLE }}", title).replace("{{ CATEGORY }}", category).replace("{{ FAVICON }}", favicon)
    )

    with open(output_path, "w") as f:
        f.write(html_content)

    print(f"✅ Generated: {output_path}")


def from_yaml(config_path, output_dir, force):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    for entry in config:
        title = entry.get("title", "Untitled")
        category = entry.get("category", "o").lower()
        if category not in VALID_CATEGORIES:
            print(f"⚠️ Skipping '{title}': invalid category '{category}'")
            continue
        generate_html(title, category, output_dir, force)


def interactive_mode(output_dir, force):
    title = input("Enter tab title: ").strip()
    category = input("Category (pmb / work / other): ").strip().lower()
    if category not in VALID_CATEGORIES:
        print(f"⚠️ Invalid category '{category}'")
        return
    generate_html(title, category, output_dir, force)


def main():
    parser = argparse.ArgumentParser(description="Generate browser tab pages.")
    parser.add_argument("--config", help="Path to YAML config file")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output folder")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    if args.config:
        from_yaml(args.config, args.output_dir, args.force)
    else:
        interactive_mode(args.output_dir, args.force)


if __name__ == "__main__":
    main()
