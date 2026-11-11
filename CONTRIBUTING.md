# Contributing a Recipe

Thanks for sharing a Recipe. This page says what a Recipe needs, how to send it, and when it
won't be accepted.

Recipes need Cuckoo 0.2.0 or later.

## How to propose a Recipe

1. Fork this repository.
2. Add one file, `recipes/<slug>.toml`. The slug is the file name and the address of the Recipe
   on the site: lowercase letters, digits and single hyphens, like `disk-space.toml`. No
   subfolders.
3. Open a Pull Request and tick the list in the template.

You don't need git for this. On GitHub, open the `recipes/` folder, choose **Add file** and
**Create new file**, and GitHub makes the fork and the Pull Request for you.

Send one Recipe per Pull Request.

Jonathan reviews every Pull Request and is the only one who merges. A Recipe shows up on
https://cuckoo.jonathan.pt/recipes after it is merged.

## What a Recipe contains

A Recipe is a Cuckoo Job file with a few more keys. On top of `name`, `command` and the schedule
(`every` or `at`), it must have:

| Key           | Required | What it is                                                     |
| ------------- | -------- | -------------------------------------------------------------- |
| `description` | yes      | What it does, when it fails, and which values to change.       |
| `author`      | yes      | Your name, your handle, or both. Free text.                    |
| `category`    | yes      | One of the 5 categories below.                                 |
| `website`     | no       | A link for your name, for example your site or your profile.   |

The 5 categories, written exactly like this: `Monitoring`, `Backups`, `System`, `Development`,
`Maintenance`.

`name` is the title of the Recipe. Two Recipes can't have the same `name`.

## Patterns that work

**Put what people change in `[environment]`, with an example value.** The `command` stays the
same for everyone; people only edit the values.

```toml
name = "Disk space"
description = '''
Checks every hour how much space is free on the startup disk.
Fails when less than MIN_FREE_GB gigabytes are left.
'''
author = "Jonathan Fontes"
website = "https://jonathan.pt"
category = "System"
command = '''
free=$(df -g / | awk 'NR == 2 { print $4 }')
echo "$free GB free, minimum $MIN_FREE_GB GB"
[ "$free" -ge "$MIN_FREE_GB" ]
'''
every = 60

[environment]
MIN_FREE_GB = "20"
```

**Let people write `~` in paths.** `[environment]` values are not expanded by a shell, so turn a
leading `~` into the home folder yourself:

```sh
folder="${FOLDER/#\~/$HOME}"
```

**Make the `command` work in both zsh and bash.** Cuckoo runs it with `zsh -l -c` or `bash -l -c`,
so stick to what both understand.

**Don't use names the shell reserves.** In zsh, `status` is read-only, so `status=$(...)` fails.
Pick another name, like `code` or `result`.

## When a Recipe is not accepted

Jonathan closes the Pull Request, with one sentence saying why, when the Recipe:

- downloads and runs code from elsewhere (`curl … | sh`) or needs `sudo`;
- has a security flaw or puts the system of the person who uses it at risk;
- repeats a Recipe that already exists;
- only works for the person who wrote it;
- needs a paid service without saying so in the `description`.

## Checks on every Pull Request

GitHub Actions runs two checks, and both must pass before a merge:

1. `cuckoo check` from the latest Cuckoo release, on every file in `recipes/`.
2. `scripts/check-recipes.py`, which checks the rules above: the file is directly in `recipes/`,
   the slug, the required keys, the category, and that no two Recipes share a `name`.

To run them yourself before you open the Pull Request:

```sh
/Applications/Cuckoo.app/Contents/Helpers/cuckoo check recipes/*.toml
python3 scripts/check-recipes.py
```

The script needs Python 3.11 or later and nothing else.

The checks don't judge whether a `command` is safe. That is part of the review.

## Changing a Recipe

Changing a Recipe is a new Pull Request, like any other, and the merge is the new approval. Keep
the file name: it is the address of the Recipe. A new file name makes a new address, and the old
one stops working. Deleting the file takes the Recipe off the site.

People who already copied a Recipe keep their copy. Nothing in their Cuckoo updates by itself.

## Licence

This repository is published under the [MIT licence](LICENSE). By opening a Pull Request, you
agree to publish your Recipe under that licence. Your credit stays in `author`, `website` and the
Git history.
