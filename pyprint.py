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
    "resource",
    type=click.Path(exists=True, dir_okay=True, file_okay=True, readable=True),
    nargs=1,
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Run without actually sending the file(s) to print. This shows the "
    "list of files that would be printed with the current set of options.",
)
@click.option(
    "-h",
    "--include-hidden",
    is_flag=True,
    help="Include hidden files and files in the hidden subdirectories of "
    "RESOURCE, if resource is a directory. If RESOURCE is not a directory, "
    "this option is ignored if given.",
)
@click.option(
    "-p",
    "--printer",
    type=click.STRING,
    help="Name of the printer to which the printing job should be sent. If "
    "not given, the user is given the list of available printers and prompted "
    "to pick one.",
)
@click.option(
    "-r",
    "--regex",
    type=click.STRING,
    default=None,
    show_default=False,
    help="Python regular expression to filter out files to be printed. If "
    "RESOURCE is not a directory, this option is ignored if given.",
)
@click.option(
    "-s",
    "--staple",
    is_flag=True,
    help="Indicates whether to staple each printed document.",
)
@click.version_option(version=__version__, message="%(version)s")
def main(resource, dry_run, include_hidden, printer, regex, staple):
    """
    Print the given RESOURCE, which can be either a file or a directory. If
    RESOURCE is a directory, all files located under that directory are printed
    unless they are filtered (see the regex option for more details).
    """
    # Handle printer
    printers = get_available_printers()
    if len(printers) == 0:
        raise click.ClickException("No printers available. Exiting.")
    elif printer is None:  # prompt for printer if it is not given
        printer = prompt_for_printer(printers)
    elif printer not in printers:  # verify that the printer given is available
        raise click.ClickException(
            f"Printer called '{printer}' is not available."
        )

    # Validate the regex if needed
    file_input = os.path.isfile(resource)
    try:
        if file_input:  # ignore regex if file is given
            regex = None
        if regex is not None:
            regex = re.compile(regex)
    except re.error as err:
        raise click.ClickException(
            f"Regular expression error: {str(err).capitalize()}: '{regex}'."
        )

    # Get the list of files that should be printed
    if file_input:
        to_print = [resource]
    else:
        to_print = files_to_print(resource, regex, include_hidden)
        if len(to_print) == 0:
            raise click.ClickException(
                f"No files matching '{regex}' in '{resource}'."
            )

    # Print the files
    if dry_run:
        _ = build_print_command(printer, staple, to_print)
        click.echo(
            f"The following files would be sent to printer '{printer}':\n"
            "  " + "\n  ".join(to_print)
        )
    else:
        command = build_print_command(printer, staple, to_print)
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, check=True)
        except FileNotFoundError:
            raise click.ClickException(
                "CUPS doesn't seem to be installed: lp unavailable."
            )
        except Exception:
            raise click.ClickException("Unknown error.")


def prompt_for_printer(printers):
    """Prompt the user to select from a list of printers."""
    numbers = list(range(1, len(printers) + 1))
    enum_printers = [f"{i}) {printers[i - 1]}" for i in numbers]
    click.echo("Available printers:\n  " + "\n  ".join(enum_printers))
    printer_number = click.prompt(
        "Printer to use",
        type=click.Choice([str(i) for i in numbers]),
        show_choices=False,
    )
    return printers[int(printer_number) - 1]


def get_available_printers():
    """Get the list of available printers."""
    try:
        pr = subprocess.run(["lpstat", "-a"], check=True, capture_output=True)
        printers = pr.stdout.decode("UTF-8").splitlines()
        printers = [p.split(" ")[0] for p in printers]
    except FileNotFoundError:
        raise click.ClickException(
            "CUPS doesn't seem to be installed: lpstat unavailable."
        )
    except Exception:
        raise click.ClickException("Unknown error.")

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
            if re.search(r"/\.", root) is not None:
                continue
            entries = [e for e in dirs + files if not e.startswith(".")]
        else:
            entries = dirs + files
        for e in entries:
            yield os.path.join(root, e)


def build_print_command(printer, staple, to_print):
    """Build an `lp` print command based on the user input."""
    stapling_option = set_stapling_option(printer, staple)
    command = [
        "lp",
        "-d",
        printer,
        "-o",
        "sides=two-sided-long-edge",
        "-o",
        "media=A4",
        "-o",
        "collate=true",
    ]
    if staple and stapling_option is not None:
        command.extend(["-o", stapling_option])
    command.extend(["--"])
    command.extend(to_print)

    return command


def set_stapling_option(printer, staple):
    """Get the printer-specific name of the option for staping and set it."""
    pattern = re.compile(r"staple", flags=re.IGNORECASE)
    try:
        pr = subprocess.run(
            ["lpoptions", "-p", printer, "-l"], check=True, capture_output=True
        )
    except FileNotFoundError:
        raise click.ClickException(
            "CUPS doesn't seem to be installed: lpoptions unavailable."
        )
    except Exception:
        raise click.ClickException("Unknown error.")
    options = pr.stdout.decode("UTF-8").splitlines()
    stapling = [opt for opt in options if pattern.search(opt) is not None]

    if not staple and not stapling:
        return None
    elif staple and not stapling:
        raise click.ClickException(
            f"Printer '{printer}' has no stapling functionality."
        )
    name = stapling[0].split("/")[0]  # stapling option name
    values = stapling[0].split(":")[1]  # possible values for the option

    # Set the stapling option to the desired value
    if staple:  # `stapling` is True at this point
        pattern = re.compile(r"(?<!\*)\S*left\S*", flags=re.IGNORECASE)
        target_value = pattern.search(values).group(0)
    else:
        target_value = "None"

    return f"{name}={target_value}"


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
