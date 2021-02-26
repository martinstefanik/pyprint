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
@click.version_option(version=__version__, message="%(version)s")
def main(dir, pattern):
    """Print all files located in DIR."""
    pattern = re.compile(pattern)
    to_print = files_to_print(dir, pattern)
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


def files_to_print(dir, pattern):
    """Get a list of files in a directory whose names conform to a pattern."""
    to_print = []
    for f in files(dir):
        if os.path.isfile(f) and pattern.search(f):
            to_print.append(f)
    return to_print


def files(dir):
    """Generate all files and directories located under a given directory."""
    for root, dirs, files in os.walk(dir):
        for f in dirs + files:
            yield os.path.join(root, f)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
