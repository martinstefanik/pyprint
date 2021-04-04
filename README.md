# pyprint

A command line tool for sending files to print on a Unix-like operating system such as Linux or macOS. The main purpose of the tool is to allow the user to easily print a large number of files following a certain naming pattern that are located in different directories on the file system. This functionality can essentially be replicated by piping the output of the command line tool such as `find` or `fd` into `lp` with arguments and option names that can be discovered with `lpoptions` and `lpstat`. The names of these options and the names of their valid values are typically dependent on the brand of the printing device. `pyprint` is intended to simplify this process, especially for users not familiar with these commands and/or piping.

`pyprint` is currently not intended to be very customizable. The goal is to provide the most common options with reasonable defaults.

# Installation

The tool can be installed manually using `pip` by downloading/cloning the repo and by running

```bash
pip install --user .
```

inside the directory. The directory can be removed after the installation is complete.

Alternatively, if `git` is installed on the system, `pyprint` can also be installed by running

```bash
pip install --user git+https://github.com/martinstefanik/pyprint
```

In order to remove `pyprint`, simply run

```bash
pip uninstall pyprint
```

`pyprint` requires the `cups` package to be installed on the system. Many Linux distributions comes with `cups` pre-installed, but you might need to install it manually.

# Usage

Details about the usage of the tool can be obtained by running `pyprint --help`. Note in particular the `--dry-run` option which allows the user to test the files filtered out by the regular expression given to the `--regex` option before actually sending the files to print.

An example of a common call is given by

```bash
pyprint --printer HP --sides 2 --staple --regex ".*\.pdf$" ~/Documents/library
```

This prints all the PDF files located in `~/Documents/library` two-sided and stapled from the printer called HP. If HP does not support two-sided print or stapling, a corresponding error is raised.

If the `--printer` option is omitted, the user is shown the list of available printers and is prompted to choose one of them as follows

```bash
Available printers:
  1) HP_LaserJet_office
  2) HP_LaserJet_hall
Printer to use:
```
See [here](https://docs.python.org/3/library/re.html#regular-expression-syntax) for details about Python regular expressions syntax.
