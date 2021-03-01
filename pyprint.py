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
@click.option(
    "-p",
    "--printer",
    type=click.STRING,
    prompt="Printer to be used",
    help="Name of the printer that should be used.",
)
@click.option(
    "-r",
    "--regex",
    type=click.STRING,
    default=None,
    show_default=False,
    help="Python regular expression to filter out files to be printed.",
)
@click.version_option(version=__version__, message="%(version)s")
def main(dir, dry_run, include_hidden, printer, regex):
    """
    Print all files located under DIR. Files without read permission and files
    in directories without read permission are automatically ignored.
    """
    # Verify that the printer given is available
    printers = get_available_printers()
    if printer not in printers:
        raise click.ClickException(f"Printer not available: {printer}.")

    # Validate the regex
    try:
        if regex is not None:
            regex = re.compile(regex)
    except re.error as err:
        raise click.ClickException(
            f"Regular expression error: {str(err).capitalize()}: '{regex}'."
        )

    to_print = files_to_print(dir, regex, include_hidden)
    if dry_run:
        if len(to_print) == 0:
            click.echo(f"No files matching '{regex}' in '{dir}'.")
        else:
            print(
                f"The following files would be sent to printer '{printer}':\n"
                "  " + "\n  ".join(to_print)
            )
    else:
        try:
            subprocess.run(
                [
                    "lp",
                    "-d",
                    printer,
                    "-o",
                    "sides=two-sided-long-edge",
                    "-o",
                    "media=A4",
                    "-o",
                    "collate=true",
                    "-o",
                    "HPStaplerOptions=1StapleLeft",
                    "--",
                ]
                + to_print,
                stdout=subprocess.DEVNULL,
                check=True,
            )
        except Exception:
            click.echo("Printing failed")


def get_available_printers():
    """Get the list of available printers."""
    try:
        pr = subprocess.run(["lpstat", "-a"], check=True, capture_output=True)
        printers = pr.stdout.decode("UTF-8").splitlines()
        printers = [p.split(" ")[0] for p in printers]
    except subprocess.CalledProcessError:
        click.ClickException("Shell command error.")

    return printers


def files_to_print(dir, regex, include_hidden):
    """Get a list of files in a directory whose names conform to a regex."""
    if regex is not None:
        to_print = []
        for f in files(dir, include_hidden):
            if os.path.isfile(f) and regex.search(f):
                to_print.append(f)
    else:
        to_print = list(files(dir, include_hidden))

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
