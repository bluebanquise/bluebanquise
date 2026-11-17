#!/usr/bin/env python3
"""
check_duplicated_files.py: check that every copy of a duplicated WebUI file is identical.

Some files are duplicated on purpose in the WebUI packs (no shared library: each pack works on its
own). Each copy starts with this header, listing every copy, including itself:

  DUPLICATED FILE: any change made to this file must be made identically in every copy below.
  Copies:
    collections/management/roles/bluebanquise_supervision/files/lib/webui_auth.py
    collections/management/roles/bluebanquise_federator/files/lib/webui_auth.py

The header is in a comment of the file language (# , // , /* * , {# #}), the check ignores these
comment characters.

For each file holding this header, the check fails when:
  - the file does not list itself (a path is misspelled, or the file was copied and not listed),
  - a listed copy does not exist,
  - a listed copy is not byte-identical to the file.
Identical copies have identical headers, so all copies list the same copies.

bulma.min.css is a vendor file, kept untouched (no header): every file named bulma.min.css must be
identical to the others, so all packs use the same Bulma version.

Run from the root of the repository:
  python3 resources/workflow/check_duplicated_files.py
Exit code 0 when everything is fine, 1 otherwise (each problem is printed).
"""

import os
import sys

# Folder searched, relative to the root of the repository
SEARCHED_FOLDER = 'collections'

MARKER = 'DUPLICATED FILE:'

# Vendor files without header, compared by name
SAME_NAME_FILES = ['bulma.min.css']

# The header must be at the top of the file
HEADER_LINES = 10


def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


def read_lines(path):
    """Lines of a text file, or [] for a file that is not text (images, archives...)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except UnicodeDecodeError:
        return []


def clean(line):
    """A header line without its comment characters: '#   a/b.py' -> 'a/b.py'."""
    return line.strip().lstrip('#/*{').strip()


def listed_copies(lines):
    """Paths listed after 'Copies:', until the first line that is not a path of the searched
    folder. None when the file has no header at its top."""
    top = [clean(line) for line in lines[:HEADER_LINES]]
    if not any(line.startswith(MARKER) for line in top):
        return None
    if 'Copies:' not in top:
        return []
    copies = []
    for line in [clean(line) for line in lines[top.index('Copies:') + 1:]]:
        if not line.startswith(SEARCHED_FOLDER + '/') or ' ' in line:
            break
        copies.append(line)
    return copies


def all_files(folder):
    """Every file of the folder and its subfolders, sorted, paths relative to the repository."""
    files = []
    for root, folders, names in os.walk(folder):
        for name in names:
            files.append(os.path.join(root, name))
    return sorted(files)


def main():
    if not os.path.isdir(SEARCHED_FOLDER):
        print('Error: run this script from the root of the repository (no {} folder here)'.format(SEARCHED_FOLDER))
        return 1

    problems = []
    checked = 0

    # 1. Files with a header
    for path in all_files(SEARCHED_FOLDER):
        copies = listed_copies(read_lines(path))
        if copies is None:
            continue
        checked = checked + 1
        print('Checking {} ({} copies listed)'.format(path, len(copies)))
        if len(copies) == 0:
            problems.append('{}: has the {} header, but lists no copy under "Copies:"'.format(path, MARKER))
            continue
        if path not in copies:
            problems.append('{}: does not list itself under "Copies:"'.format(path))
        content = read_bytes(path)
        for copy in copies:
            if copy == path:
                continue
            if not os.path.isfile(copy):
                problems.append('{}: listed copy {} does not exist'.format(path, copy))
            elif read_bytes(copy) != content:
                problems.append('{}: listed copy {} is different (diff {} {})'.format(path, copy, path, copy))

    # 2. Vendor files, by name
    for name in SAME_NAME_FILES:
        paths = [path for path in all_files(SEARCHED_FOLDER) if os.path.basename(path) == name]
        checked = checked + len(paths)
        print('Checking {} ({} files)'.format(name, len(paths)))
        for path in paths[1:]:
            if read_bytes(path) != read_bytes(paths[0]):
                problems.append('{} is different from {} (all {} files must be the same version)'.format(path, paths[0], name))

    print('')
    if len(problems) > 0:
        for problem in problems:
            print('ERROR ' + problem)
        print('{} problem(s). Duplicated files must stay identical: make the same change in every copy.'.format(len(problems)))
        return 1
    print('OK: {} files checked, every copy is identical'.format(checked))
    return 0


if __name__ == '__main__':
    sys.exit(main())
