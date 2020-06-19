import os
import os.path
import pathlib
import sys
from contextlib import contextmanager
from datetime import datetime
from distutils.filelist import glob_to_re
from distutils.text_file import TextFile
from glob import glob
from zipfile import ZipFile

"""
    This Script collects all the source files
    and packages them into a .zip file
"""

OUTPUT_DIR = "dist"
MANIFEST_FILE = "MANIFEST.in"
SOURCE_DIRECTORY = pathlib.Path(os.getcwd()).resolve(True)


@contextmanager
def cd(directory):
    """Change the current working directory, temporarily.
    Use as a context manager: with cd(d): ...
    """
    old_dir = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old_dir)


def warning(message):
    print(message, file=sys.stderr)


class Failure(Exception):
    """An expected failure (as opposed to a bug in this script)."""


def _glob_to_regexp(pat):
    """Compile a glob pattern into a regexp.
    We need to do this because fnmatch allows * to match /, which we
    don't want.  E.g. a MANIFEST.in exclude of 'dirname/*css' should
    match 'dirname/foo.css' but not 'dirname/subdir/bar.css'.
    """
    return glob_to_re(pat)


def _get_ignore_from_manifest_lines(lines):
    """Gather the various ignore patterns from a MANIFEST.in.
    'lines' should be a list of strings with comments removed
    and continuation lines joined.
    Returns a list of standard ignore patterns and a list of regular
    expressions to ignore.
    """
    ignore = []
    ignore_regexps = []
    included_regexps = []
    included_files = []
    for line in lines:
        try:
            cmd, rest = line.split(None, 1)
        except ValueError:
            # no whitespace, so not interesting
            continue

        for part in rest.split():
            # distutils enforces these warnings on Windows only
            if part.startswith("/"):
                warning(
                    "ERROR: Leading slashes are not allowed in MANIFEST.in on Windows: {}".format(part)  # noqa
                )
            if part.endswith("/"):
                warning(
                    "ERROR: Trailing slashes are not allowed in MANIFEST.in on Windows: {}".format(part)  # noqa
                )
        if cmd == "exclude":
            # An exclude of 'dirname/*css' can match 'dirname/foo.css'
            # but not 'dirname/subdir/bar.css'.  We need a regular
            # expression for that, since fnmatch doesn't pay attention to
            # directory separators.
            for pat in rest.split():
                if "*" in pat or "?" in pat or "[!" in pat:
                    ignore_regexps.append(_glob_to_regexp(pat))
                else:
                    ignore.append(pat)
        elif cmd == "include":
            for pat in rest.split():
                if "*" in pat or "?" in pat or "[!" in pat:
                    included_regexps.append(_glob_to_regexp(pat))
                else:
                    included_files.append(pat)
        elif cmd == "global-exclude":
            ignore.extend(rest.split())
        elif cmd == "recursive-include":
            try:
                dirname, patterns = rest.split(None, 1)
            except ValueError:
                warning(
                    "You have a wrong line in MANIFEST.in: %r\n"
                    "'recursive-include' expects <dir> <pattern1> "
                    "<pattern2> ..." % line
                )
                continue
            dirname = dirname.rstrip(os.path.sep)
            for pattern in patterns.split():
                if pattern.startswith("*"):
                    if len(pattern) == 1:
                        included_regexps.append(dirname + "/**")
                    else:
                        included_regexps.append(dirname + "/**/" + pattern)
                else:
                    # 'recursive-exclude plone metadata.xml' should
                    # exclude plone/metadata.xml and
                    # plone/*/metadata.xml, where * can be any number
                    # of sub directories.  We could use a regexp, but
                    # two ignores seems easier.
                    included_regexps.append(dirname + os.path.sep + pattern)
                    included_regexps.append(dirname + "/**/" + pattern)
        elif cmd == "recursive-exclude":
            try:
                dirname, patterns = rest.split(None, 1)
            except ValueError:
                # Wrong MANIFEST.in line.
                warning(
                    "You have a wrong line in MANIFEST.in: %r\n"
                    "'recursive-exclude' expects <dir> <pattern1> "
                    "<pattern2> ..." % line
                )
                continue
            # Strip path separator for clarity.
            dirname = dirname.rstrip(os.path.sep)
            for pattern in patterns.split():
                if pattern.startswith("*"):
                    if len(pattern) == 1:
                        ignore.append(dirname + "/**")
                    else:
                        ignore.append(dirname + "/**/" + pattern)
                else:
                    # 'recursive-exclude plone metadata.xml' should
                    # exclude plone/metadata.xml and
                    # plone/*/metadata.xml, where * can be any number
                    # of sub directories.  We could use a regexp, but
                    # two ignores seems easier.
                    ignore.append(dirname + os.path.sep + pattern)
                    ignore.append(dirname + os.path.sep + "*" + os.path.sep + pattern)  # noqa
        elif cmd == "prune":
            # rest is considered to be a directory name.  It should
            # not contain a path separator, as it actually has no
            # effect in that case, but that could differ per python
            # version.  We strip it here to avoid double separators.
            # XXX: mg: I'm not 100% sure the above is correct, AFAICS
            # all pythons from 2.6 complain if the path has a leading or
            # trailing slash -- on Windows, that is.
            rest = rest.rstrip("/\\")
            ignore.append(rest)
            ignore.append(rest + os.path.sep + "*")
    return ignore, ignore_regexps, included_regexps, included_files


def _get_ignore_from_manifest(filename):
    """Gather the various ignore patterns from a MANIFEST.in.
    Returns a list of standard ignore patterns and a list of regular
    expressions to ignore.
    """

    class MyTextFile(TextFile):
        def error(self, msg, line=None):  # pragma: nocover
            # (this is never called by TextFile in current versions of CPython)
            raise Failure(self.gen_error(msg, line))

        def warn(self, msg, line=None):
            warning(self.gen_error(msg, line))

    # with cd(SOURCE_DIRECTORY):
    template = MyTextFile(
        SOURCE_DIRECTORY.joinpath(filename),
        strip_comments=True,
        skip_blanks=True,
        join_lines=True,
        lstrip_ws=True,
        rstrip_ws=True,
        collapse_join=True,
    )

    try:
        lines = template.readlines()
    finally:
        template.close()
    return _get_ignore_from_manifest_lines(lines)


def _read_tree(included_glob, included_files, excluded_glob, excluded_files):
    included_glob_files = []
    excluded_glob_files = []

    def _read_from_root_dir(_lst):
        _res = []
        with cd(SOURCE_DIRECTORY):
            for glob_ in _lst:
                for x in glob(glob_, recursive=True):
                    _res.append(SOURCE_DIRECTORY.joinpath(x))
        return _res

    if len(included_glob) > 0:
        included_glob_files.extend(_read_from_root_dir(included_glob))

    if len(included_files) > 0:
        included_glob_files.extend(_read_from_root_dir(included_files))

    if len(excluded_glob) > 0:
        excluded_glob_files.extend(_read_from_root_dir(excluded_glob))

    if len(excluded_files) > 0:
        excluded_glob_files.extend(_read_from_root_dir(excluded_files))

    # filter included directories
    filtered_included_glob_files = list(
        filter(lambda x: not x.is_dir(), included_glob_files)
    )
    filtered_excluded_glob_files = list(
        filter(lambda x: not x.is_dir(), excluded_glob_files)
    )

    filtered_files_set = set(filtered_included_glob_files) - set(
        filtered_excluded_glob_files
    )

    return list(filtered_files_set)


def _zip_files(file_paths):
    output_filename = (
        "zenteach-build-" + str(datetime.timestamp(datetime.now())) + ".zip"
    )
    pathlib.Path(OUTPUT_DIR).mkdir(exist_ok=True)

    with cd(SOURCE_DIRECTORY):
        with ZipFile(OUTPUT_DIR + "/" + output_filename, "w") as zip:
            for _file in file_paths:
                relative_to_root = _file.relative_to(SOURCE_DIRECTORY)
                zip.write(relative_to_root)
    return output_filename


def package():
    (
        ignored_files,
        ignore_regex,
        included_regexp,
        included_files,
    ) = _get_ignore_from_manifest(MANIFEST_FILE)

    filter_files = _read_tree(
        included_regexp, included_files, ignore_regex, ignored_files
    )

    return _zip_files(filter_files)


if __name__ == "__main__":
    # sys.exit(package())
    sys.stdout.write(package())
