"""Tests for scripts/check-recipes.py, run as a command on a throwaway repository folder."""

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check-recipes.py"

VALID_RECIPE = textwrap.dedent(
    '''\
    name = "Disk space"
    description = "Checks the free space."
    author = "Jonathan Fontes"
    category = "System"
    command = "df -h /"
    every = 60
    '''
)


class CheckRecipesTest(unittest.TestCase):
    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name)
        (self.root / "recipes").mkdir()

    def tearDown(self):
        self._folder.cleanup()

    def write(self, relative_path, text=VALID_RECIPE):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def check(self):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root)],
            capture_output=True,
            text=True,
        )

    def assertFailsWith(self, result, message):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)

    def test_valid_recipes_pass(self):
        self.write("recipes/disk-space.toml")
        self.write("recipes/website-is-up.toml", VALID_RECIPE.replace("Disk space", "Website is up"))

        result = self.check()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "2 Recipes checked, no problems.\n")

    def test_a_toml_file_outside_recipes_fails(self):
        self.write("disk-space.toml")

        self.assertFailsWith(
            self.check(), "disk-space.toml: a Recipe must be directly inside recipes/"
        )

    def test_a_toml_file_in_a_subfolder_of_recipes_fails(self):
        self.write("recipes/monitoring/disk-space.toml")

        self.assertFailsWith(
            self.check(),
            "recipes/monitoring/disk-space.toml: a Recipe must be directly inside recipes/",
        )

    def test_a_file_name_that_is_not_a_kebab_case_slug_fails(self):
        for file_name in ["Disk-Space.toml", "disk_space.toml", "disk--space.toml", "-disk.toml"]:
            with self.subTest(file_name=file_name):
                self.write(f"recipes/{file_name}")

                self.assertFailsWith(
                    self.check(),
                    f"recipes/{file_name}: the file name must be a slug in kebab-case,"
                    " like disk-space.toml",
                )

                (self.root / "recipes" / file_name).unlink()

    def test_a_missing_required_key_fails(self):
        for key in ["description", "author", "category"]:
            with self.subTest(key=key):
                recipe = "\n".join(
                    line for line in VALID_RECIPE.splitlines() if not line.startswith(key)
                )
                self.write("recipes/disk-space.toml", recipe)

                self.assertFailsWith(
                    self.check(), f"recipes/disk-space.toml: {key} is required and can't be empty"
                )

    def test_an_empty_required_key_fails(self):
        self.write("recipes/disk-space.toml", VALID_RECIPE.replace('"Jonathan Fontes"', '"  "'))

        self.assertFailsWith(
            self.check(), "recipes/disk-space.toml: author is required and can't be empty"
        )

    def test_a_file_that_is_not_valid_toml_fails(self):
        self.write("recipes/disk-space.toml", VALID_RECIPE + "every = \n")

        self.assertFailsWith(self.check(), "recipes/disk-space.toml: not valid TOML")

    def test_a_category_outside_the_fixed_list_fails(self):
        self.write("recipes/disk-space.toml", VALID_RECIPE.replace('"System"', '"system"'))

        self.assertFailsWith(
            self.check(),
            "recipes/disk-space.toml: category must be one of Monitoring, Backups, System,"
            " Development, Maintenance",
        )

    def test_every_category_in_the_fixed_list_passes(self):
        for category in ["Monitoring", "Backups", "System", "Development", "Maintenance"]:
            slug = category.lower()
            recipe = VALID_RECIPE.replace('"System"', f'"{category}"')
            self.write(f"recipes/{slug}.toml", recipe.replace("Disk space", category))

        self.assertEqual(self.check().returncode, 0)

    def test_two_recipes_with_the_same_name_fail(self):
        self.write("recipes/disk-space.toml")
        self.write("recipes/free-disk-space.toml")

        self.assertFailsWith(
            self.check(),
            'recipes/free-disk-space.toml: name "Disk space" is already used by'
            " recipes/disk-space.toml",
        )


if __name__ == "__main__":
    unittest.main()
