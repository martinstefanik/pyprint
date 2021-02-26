#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print all files satisfying a pattern."""

import os
import re
import subprocess

import click

__version__ = "1.0.0"


@click.command()
@click.argument(
    "dir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True),
    nargs=1,
)
@click.option(
    "-p",
    "--pattern",
    type=click.STRING,
    help="Python regular expression to filter out files to be printed.",
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Run without actually sending the files to print. This shows the list "
    "of files that would be printed with the current set of options.",
)
@click.option(
    "-h",
    "--include-hidden",
    is_flag=True,
    help="Include hidden files and files in a hidden subdirectories of DIR.",
)
@click.version_option(version=__version__, message="%(version)s")
def main(dir, pattern, dry_run, include_hidden):
    """Print all files located in DIR."""
    pattern = re.compile(pattern)
    to_print = files_to_print(dir, pattern, include_hidden)
    if dry_run:
        print("The following files would be sent to print:")
        print("  " + "\n  ".join(to_print))
    else:
        for f in to_print:
            subprocess.run(
                [
                    "lp",
                    "-d",
                    "p-hg-g-53-1",
                    "-o",
                    "sides=two-sided-long-edge",
                    "-o",
                    "media=A4",
                    "-o",
                    "collate=true",
                    "-o",
                    "HPStaplerOptions=1StapleLeft",
                    f,
                ],
                stdout=subprocess.DEVNULL,
            )


def files_to_print(dir, pattern, include_hidden):
    """Get a list of files in a directory whose names conform to a pattern."""
    to_print = []
    for f in files(dir, include_hidden):
        if os.path.isfile(f) and pattern.search(f):
            to_print.append(f)
    return to_print


def files(dir, include_hidden):
    """Generate files and directories located under a given directory."""
    for root, dirs, files in os.walk(dir):
        if not include_hidden:
            if re.search(r"\.(?!/|$).*", root) is not None:
                continue
            entries = [e for e in dirs + files if not e.startswith(".")]
        else:
            entries = dirs + files
        for e in entries:
            yield os.path.join(root, e)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
