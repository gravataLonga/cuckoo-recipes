#!/usr/bin/env python3
"""Checks the rules a Recipe must follow in this repository.

Usage: python3 scripts/check-recipes.py [repository folder]

Needs Python 3.11 or later (tomllib) and nothing else.
Prints one line per problem, "<file>: <rule>", and exits with 1 when there is any.
"""

import re
import sys
from pathlib import Path

if sys.version_info < (3, 11):
    sys.exit("check-recipes.py needs Python 3.11 or later, for tomllib.")

import tomllib

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REQUIRED_KEYS = ["description", "author", "category"]
CATEGORIES = ["Monitoring", "Backups", "System", "Development", "Maintenance"]


def toml_files(root):
    """Every .toml file in the repository, outside .git, as paths relative to root."""
    return sorted(
        path.relative_to(root)
        for path in root.rglob("*.toml")
        if ".git" not in path.relative_to(root).parts
    )


def read_recipe(root, path):
    """The problems of one file directly inside recipes/, and its keys when it reads."""
    problems = []

    if not SLUG.match(path.stem):
        problems.append(f"{path}: the file name must be a slug in kebab-case, like disk-space.toml")

    try:
        recipe = tomllib.loads((root / path).read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
        return problems + [f"{path}: not valid TOML ({error})"], None

    for key in REQUIRED_KEYS:
        value = recipe.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{path}: {key} is required and can't be empty")

    category = recipe.get("category")
    if isinstance(category, str) and category.strip() and category not in CATEGORIES:
        problems.append(f"{path}: category must be one of {', '.join(CATEGORIES)}")

    return problems, recipe


def main(arguments):
    root = Path(arguments[0] if arguments else ".")
    problems = []
    recipes = []
    paths_by_name = {}

    for path in toml_files(root):
        if path.parent != Path("recipes"):
            problems.append(f"{path}: a Recipe must be directly inside recipes/")
            continue
        recipes.append(path)
        recipe_problems, recipe = read_recipe(root, path)
        problems += recipe_problems

        name = recipe.get("name") if recipe else None
        if isinstance(name, str):
            if name in paths_by_name:
                problems.append(
                    f'{path}: name "{name}" is already used by {paths_by_name[name]}'
                )
            else:
                paths_by_name[name] = path

    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(f"{len(problems)} {'problem' if len(problems) == 1 else 'problems'} found.", file=sys.stderr)
        return 1

    print(f"{len(recipes)} Recipes checked, no problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
