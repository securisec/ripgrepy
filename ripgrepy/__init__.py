from __future__ import annotations
import os
from shutil import which
from subprocess import getoutput
from json import dumps, loads
from functools import wraps
from timeit import default_timer
from pkg_resources import get_distribution
import logging

__version__ = get_distribution("ripgrepy").version


def _logger(func):
    """
    Logger decorator
    """

    @wraps(func)
    def l(*args, **kwargs):
        try:
            start = default_timer()
            o = func(*args, **kwargs)
            end = default_timer()
            rt = str(round(end - start, 4)) + " seconds"
            logging.debug(f"{func.__name__} runtime {rt}")
            return o
        except:
            logging.exception("")
            raise

    return l


class RipGrepNotFound(Exception):
    pass


class RipGrepOut(object):
    def __init__(self, _output, command):
        self._output = _output
        self.command = command

    @property
    @_logger
    def as_dict(self) -> list:
        """
        Returns an array of objects with the match. The objects include
        file path, line number and matched value. This is in addition to the
        --json that can be passed to ripgrep and is designed for simple ripgrep use

        :return: Array of matched objects
        :rtype: list

        The following is an example of the dict output.

        >>> [{'data': {'absolute_offset': 12,
        >>>   'line_number': 3,
        >>>   'lines': {'text': 'teststring\\n'},
        >>>   'path': {'text': '/tmp/test/test.lol'},
        >>>   'submatches': [{'end': 4, 'match': {'text': 'test'}, 'start': 0}]},
        >>> 'type': 'match'}]
        """
        if "--json" not in self.command:
            raise TypeError("To use as_dict, use the json() method")
        out = self._output.splitlines()
        holder = []
        for line in out:
            data = loads(line)
            if data["type"] == "match":
                holder.append(data)
        return holder

    @property
    @_logger
    def as_json(self) -> str:
        """
        Returns the output as a JSON object. This is in addition to the
        --json that can be passed to ripgrep and is designed for simple ripgrep use

        :return: JSON object
        :rtype: str
        """
        if "--json" not in self.command:
            raise TypeError("To use as_dict, use the json() method")
        out = self._output.splitlines()
        holder = []
        for line in out:
            data = loads(line)
            if data["type"] == "match":
                holder.append(data)
        return dumps(holder)

    @property
    @_logger
    def as_string(self) -> str:
        """
        Returns stdout from ripgrep

        :return: Stdout of ripgrep
        :rtype: str
        """
        return self._output

    def __repr__(self):
        return str(self._output)


class Ripgrepy(object):
    """
    The main class for Ripgrepy.

    :param regex_pattern: A regular expression used for searching
    :type regex_pattern: str
    :param path: A file or directory to search. Directories are searched
           recursively. Paths specified explicitly on the command line
           override glob and ignore rules
    :type path: str
    :param rg_path: Path to ripgrep. Defaults to $PATH
    :type rg_path: str
    :raises RipGrepNotFound: Error if path to ripgrep could not be resolved
    """

    def __init__(self, regex_pattern: str, path: str, rg_path: str = "rg"):
        self.regex_pattern = f'"{regex_pattern}"'
        self.path = os.path.expanduser(path)
        self._output = None
        self._rg_path = rg_path
        #: The ripgreg command that will be executed
        self.command = [self._rg_path]

        if which(self._rg_path) is None:
            raise RipGrepNotFound("ripgrep not found")

        # short syntax mapping
        #: Short syntax for byte_offset
        self.b = self.byte_offset
        #: Short syntax for case_sensitive
        self.s = self.case_sensitive
        #: Short syntax for encoding
        self.E = self.encoding
        #: Short syntax for file
        self.f = self.file
        #: Short syntax for files_with_matches
        self.l = self.files_with_matches
        #: Short syntax for fixed_strings
        self.F = self.fixed_strings
        #: Short syntax for follow
        self.L = self.follow
        #: Short syntax for glob
        self.g = self.glob
        #: Short syntax for ignore_case
        self.i = self.ignore_case
        #: Short syntax for invert_match
        self.v = self.invert_match
        #: Short syntax for line_number
        self.n = self.line_number
        #: Short syntax for after_context
        self.A = self.after_context
        #: Short syntax for before_context
        self.B = self.before_context
        #: Short syntax for context
        self.C = self.context
        #: Short syntax for line_regexp
        self.x = self.line_regexp
        #: Short syntax for max_columns
        self.M = self.max_columns
        #: Short syntax for max_count
        self.m = self.max_count
        #: Short syntax for multiline
        self.U = self.multiline
        #: Short syntax for no_filename
        self.I = self.no_filename
        #: Short syntax for no_line_number
        self.N = self.no_line_number
        #: Short syntax for only_matching
        self.o = self.only_matching
        #: Short syntax for pcre2
        self.P = self.pcre2
        #: Short syntax for pretty
        self.p = self.pretty
        #: Short syntax for quite
        self.q = self.quite
        #: Short syntax for regexp
        self.e = self.regexp
        #: Short syntax for replace
        self.r = self.replace
        #: Short syntax for search_zip
        self.z = self.search_zip
        #: Short syntax for smart_case
        self.S = self.smart_case
        #: Short syntax for text
        self.a = self.text
        #: Short syntax for threads
        self.j = self.threads
        #: Short syntax for type_not
        self.T = self.type_not
        #: Short syntax for unrestricted
        self.u = self.unrestricted
        #: Short syntax for with_filename
        self.H = self.with_filename
        #: Short syntax for word_regexp
        self.w = self.word_regexp
        #: Alias to run
        self.run_rg = self.run

    @_logger
    def run(self) -> RipgrepOut:
        """
        Returns an instace of the Ripgrepy object

        :return: self
        :rtype: RipgrepOut
        """
        self.command.append(self.regex_pattern)
        self.command.append(self.path)
        self.command = " ".join(self.command)
        self._output = getoutput(self.command)
        return RipGrepOut(self._output, self.command)

    @_logger
    def error_msg(self) -> Ripgrepy:
        """
        Returns any stderr that was generated

        :return: String of error
        :rtype: Ripgrepy
        """
        return self.error

    @_logger
    def after_context(self, number: int) -> Ripgrepy:
        """
        Show NUM lines after each match.

        This overrides the --context flag.

        :param number: Number of lines to show
        :type number: int
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--after-context {number}")
        return self

    @_logger
    def before_context(self, number: int) -> Ripgrepy:
        """
        Show NUM lines before each match.

        This overrides the --context flag.

        :param number: Number of lines to show
        :type number: int
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--before-context {number}")
        return self

    @_logger
    def context(self, number: int) -> Ripgrepy:
        """
        Show NUM lines before and after each match. This is equivalent to
        providing both the -B/--before-context and -A/--after-context flags
        with the same value.

        This overrides both the -B/--before-context and -A/--after-context
        flags.


        :param number: Number of lines to show
        :type number: int
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--context {number}")
        return self

    @_logger
    def binary(self) -> Ripgrepy:
        """
        Enabling this flag will cause ripgrep to search binary files. By
        default, ripgrep attempts to automatically skip binary files in
        order to improve the relevance of results and make the search
        faster.

        Binary files are heuristically detected based on whether they
        contain a NUL byte or not. By default (without this flag set), once
        a NUL byte is seen, ripgrep will stop searching the file. Usually,
        NUL bytes occur in the beginning of most binary files. If a NUL
        byte occurs after a match, then ripgrep will still stop searching
        the rest of the file, but a warning will be printed.

        In contrast, when this flag is provided, ripgrep will continue
        searching a file even if a NUL byte is found. In particular, if a
        NUL byte is found then ripgrep will continue searching until either
        a match is found or the end of the file is reached, whichever comes
        sooner. If a match is found, then ripgrep will stop and print a
        warning saying that the search stopped prematurely.

        If you want ripgrep to search a file without any special NUL byte
        handling at all (and potentially print binary data to stdout), then
        you should use the -a/--text flag.

        The --binary flag is a flag for controlling ripgrep's automatic
        filtering mechanism. As such, it does not need to be used when
        searching a file explicitly or when searching stdin. That is, it is
        only applicable when recursively searching a directory.

        Note that when the -u/--unrestricted flag is provided for a third
        time, then this flag is automatically enabled.

        This flag can be disabled with --no-binary. It overrides the
        -a/--text flag.
        """
        self.command.append("--binary")
        return self

    @_logger
    def auto_hybrid_regex(self) -> Ripgrepy:
        """
        When this flag is used, ripgrep will dynamically choose between
        supported regex engines depending on the features used in a
        pattern. When ripgrep chooses a regex engine, it applies that
        choice for every regex provided to ripgrep (e.g., via multiple
        -e/--regexp or -f/--file flags).

        As an example of how this flag might behave, ripgrep will attempt
        to use its default finite automata based regex engine whenever the
        pattern can be successfully compiled with that regex engine. If
        PCRE2 is enabled and if the pattern given could not be compiled
        with the default regex engine, then PCRE2 will be automatically
        used for searching. If PCRE2 isn't available, then this flag has no
        effect because there is only one regex engine to choose from.

        In the future, ripgrep may adjust its heuristics for how it decides
        which regex engine to use. In general, the heuristics will be
        limited to a static analysis of the patterns, and not to any
        specific runtime behavior observed while searching files.

        The primary downside of using this flag is that it may not always
        be obvious which regex engine ripgrep uses, and thus, the match
        semantics or performance profile of ripgrep may subtly and
        unexpectedly change. However, in many cases, all regex engines will
        agree on what constitutes a match and it can be nice to
        transparently support more advanced regex features like look-around
        and backreferences without explicitly needing to enable them.

        This flag can be disabled with --no-auto-hybrid-regex.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--auto-hybrid-regex")
        return self

    @_logger
    def block_buffered(self) -> Ripgrepy:
        """
        When enabled, ripgrep will use block buffering. That is, whenever a
        matching line is found, it will be written to an in-memory buffer
        and will not be written to stdout until the buffer reaches a
        certain size. This is the default when ripgrep's stdout is
        redirected to a pipeline or a file. When ripgrep's stdout is
        connected to a terminal, line buffering will be used. Forcing block
        buffering can be useful when dumping a large amount of contents to
        a terminal.

        Forceful block buffering can be disabled with --no-block-buffered.
        Note that using --no-block-buffered causes ripgrep to revert to its
        default behavior of automatically detecting the buffering strategy.
        To force line buffering, use the --line-buffered flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--block-buffered")
        return self

    @_logger
    def byte_offset(self) -> Ripgrepy:
        """
        Print the 0-based byte offset within the input file before each
        line of output. If -o (--only-matching) is specified, print the
        offset of the matching part itself.

        If ripgrep does transcoding, then the byte offset is in terms of
        the the result of transcoding and not the original data. This
        applies similarly to another transformation on the source, such as
        decompression or a --pre filter. Note that when the PCRE2 regex
        engine is used, then UTF-8 transcoding is done by default.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--byte-offset")
        return self

    @_logger
    def case_sensitive(self) -> Ripgrepy:
        """
        Search case sensitively.

        This overrides the -i/--ignore-case and -S/--smart-case flags.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--case-sensitive")
        return self

    @_logger
    def count_matches(self) -> Ripgrepy:
        """
        This flag suppresses normal output and shows the number of
        individual matches of the given patterns for each file searched.
        Each file containing matches has its path and match count printed
        on each line. Note that this reports the total number of individual
        matches and not the number of lines that match.

        If only one file is given to ripgrep, then only the count is
        printed if there is a match. The --with-filename flag can be used
        to force printing the file path in this case.

        This overrides the --count flag. Note that when --count is combined
        with --only-matching, then ripgrep behaves as if --count-matches
        was given.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--count-matches")
        return self

    @_logger
    def crlf(self) -> Ripgrepy:
        """
        When enabled, ripgrep will treat CRLF (\\r\\n) as a line terminator
        instead of just \\n.

        Principally, this permits $ in regex patterns to match just before
        CRLF instead of just before LF. The underlying regex engine may not
        support this natively, so ripgrep will translate all instances of $
        to (?:\\r??$). This may produce slightly different than desired
        match offsets. It is intended as a work-around until the regex
        engine supports this natively.

        CRLF support can be disabled with --no-crlf.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--crlf")
        return self

    @_logger
    def debug(self) -> Ripgrepy:
        """
        Show debug messages. Please use this when filing a bug report.

        The --debug flag is generally useful for figuring out why ripgrep
        skipped searching a particular file. The debug messages should
        mention all files skipped and why they were skipped.

        To get even more debug output, use the --trace flag, which implies
        --debug along with additional trace data. With --trace, the output
        could be quite large and is generally more useful for development.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--debug")
        return self

    @_logger
    def dfa_size_limit(self, num_suffix: int) -> Ripgrepy:
        """
        The upper size limit of the regex DFA. The default limit is 10M.
        This should only be changed on very large regex inputs where the
        (slower) fallback regex engine may otherwise be used if the limit
        is reached.

        The argument accepts the same size suffixes as allowed in with the
        --max-filesize flag.

        :param num_suffix: size suffixes
        :type num_suffix: int
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--dfa-size-limit "{num_suffix}"')
        return self

    @_logger
    def encoding(self, encoding: str) -> Ripgrepy:
        """
        Specify the text encoding that ripgrep will use on all files
        searched. The default value is auto, which will cause ripgrep to do
        a best effort automatic detection of encoding on a per-file basis.
        Automatic detection in this case only applies to files that begin
        with a UTF-8 or UTF-16 byte-order mark (BOM). No other automatic
        detection is performed. One can also specify none which will then
        completely disable BOM sniffing and always result in searching the
        raw bytes, including a BOM if it's present, regardless of its
        encoding.

        Other supported values can be found in the list of labels here:
        https://encoding.spec.whatwg.org/#concept-encoding-get

        For more details on encoding and how ripgrep deals with it, see
        GUIDE.md.

        This flag can be disabled with --no-encoding.

        :param encoding: encoding
        :type encoding: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--encoding "{encoding}"')
        return self

    @_logger
    def file(self, pattern: str) -> Ripgrepy:
        """
        Search for patterns from the given file, with one pattern per line.
        When this flag is used multiple times or in combination with the
        -e/--regexp flag, then all patterns provided are searched. Empty
        pattern lines will match all input lines, and the newline is not
        counted as part of the pattern.

        A line is printed if and only if it matches at least one of the
        patterns.

        :param pattern: pattern
        :type pattern: str
        :return: [description]
        :rtype: Ripgrepy
        """
        self.command.append(f'--file "{pattern}"')
        return self

    @_logger
    def files(self) -> Ripgrepy:
        """
        Print each file that would be searched without actually performing
        the search. This is useful to determine whether a particular file
        is being searched or not.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--files")
        return self

    @_logger
    def files_with_matches(self) -> Ripgrepy:
        """
        Only print the paths with at least one match.

        This overrides --files-without-match.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--files-with-matches")
        return self

    @_logger
    def files_without_match(self) -> Ripgrepy:
        """
        Only print the paths that contain zero matches. This
        inverts/negates the --files-with-matches flag.

        This overrides --files-with-matches.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--files-without-match")
        return self

    @_logger
    def fixed_strings(self) -> Ripgrepy:
        """
        Treat the pattern as a literal string instead of a regular
        expression. When this flag is used, special regular expression meta
        characters such as .(){}*+ do not need to be escaped.

        This flag can be disabled with --no-fixed-strings.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--fixed-strings")
        return self

    @_logger
    def follow(self) -> Ripgrepy:
        """
        When this flag is enabled, ripgrep will follow symbolic links while
        traversing directories. This is disabled by default. Note that
        ripgrep will check for symbolic link loops and report errors if it
        finds one.

        This flag can be disabled with --no-follow.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--follow")
        return self

    @_logger
    def glob(self, glob_pattern: str) -> Ripgrepy:
        """
        Include or exclude files and directories for searching that match
        the given glob. This always overrides any other ignore logic.
        Multiple glob flags may be used. Globbing rules match .gitignore
        globs. Precede a glob with a ! to exclude it.

        :param glob_pattern: Glob pattern
        :type glob_pattern: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--glob "{glob_pattern}"')
        return self

    @_logger
    def hidden(self) -> Ripgrepy:
        """
        Search hidden files and directories. By default, hidden files and
        directories are skipped. Note that if a hidden file or a directory
        is whitelisted in an ignore file, then it will be searched even if
        this flag isn't provided.

        This flag can be disabled with --no-hidden.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--hidden")
        return self

    @_logger
    def iglob(self, glob_pattern: str) -> Ripgrepy:
        """
        Include or exclude files and directories for searching that match
        the given glob. This always overrides any other ignore logic.
        Multiple glob flags may be used. Globbing rules match .gitignore
        globs. Precede a glob with a ! to exclude it. Globs are matched
        case insensitively.

        :param glob_pattern: Glob pattern
        :type glob_pattern: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--iglob "{glob_pattern}"')
        return self

    @_logger
    def ignore_case(self) -> Ripgrepy:
        """
        When this flag is provided, the given patterns will be searched
        case insensitively. The case insensitivity rules used by ripgrep
        conform to Unicode's "simple" case folding rules.

        This flag overrides -s/--case-sensitive and -S/--smart-case.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--ignore-case")
        return self

    @_logger
    def ignore_file(self, path: str) -> Ripgrepy:
        """
        Specifies a path to one or more .gitignore format rules files.
        These patterns are applied after the patterns found in .gitignore
        and .ignore are applied and are matched relative to the current
        working directory. Multiple additional ignore files can be
        specified by using the --ignore-file flag several times. When
        specifying multiple ignore files, earlier files have lower
        precedence than later files.

        If you are looking for a way to include or exclude files and
        directories directly on the command line, then used -g instead.

        :param path: File path
        :type path: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--ignore-file "{path}"')
        return self

    @_logger
    def ignore_file_case_insensitive(self) -> Ripgrepy:
        """
        Process ignore files (.gitignore, .ignore, etc.) case
        insensitively. Note that this comes with a performance penalty and
        is most useful on case insensitive file systems (such as Windows).

        This flag can be disabled with the
        --no-ignore-file-case-insensitive flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--ignore-file-case-insensitive")
        return self

    @_logger
    def invert_match(self) -> Ripgrepy:
        """
        Invert matching. Show lines that do not match the given patterns.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--invert-match")
        return self

    @_logger
    def json(self) -> Ripgrepy:
        """
        Enable printing results in a JSON Lines format.

        When this flag is provided, ripgrep will emit a sequence of
        messages, each encoded as a JSON object, where there are five
        different message types:

        begin - A message that indicates a file is being searched and
        contains at least one match.

        end - A message the indicates a file is done being searched. This
        message also include summary statistics about the search for a
        particular file.

        match - A message that indicates a match was found. This includes
        the text and offsets of the match.

        context - A message that indicates a contextual line was found.
        This includes the text of the line, along with any match
        information if the search was inverted.

        summary - The final message emitted by ripgrep that contains
        summary statistics about the search across all files.

        Since file paths or the contents of files are not guaranteed to be
        valid UTF-8 and JSON itself must be representable by a Unicode
        encoding, ripgrep will emit all data elements as objects with one
        of two keys: text or bytes.  text is a normal JSON string when the
        data is valid UTF-8 while bytes is the base64 encoded contents of
        the data.

        The JSON Lines format is only supported for showing search results.
        It cannot be used with other flags that emit other types of output,
        such as --files, --files-with-matches, --files-without-match,
        --count or --count-matches. ripgrep will report an error if any of
        the aforementioned flags are used in concert with --json.

        Other flags that control aspects of the standard output such as
        --only-matching, --heading, --replace, --max-columns, etc., have no
        effect when --json is set.

        A more complete description of the JSON format used can be found
        `here: <https://docs.rs/grep-printer/*/grep_printer/struct.JSON.html>__`

        The JSON Lines format can be disabled with --no-json.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--json")
        return self

    @_logger
    def line_buffered(self) -> Ripgrepy:
        """
        When enabled, ripgrep will use line buffering. That is, whenever a
        matching line is found, it will be flushed to stdout immediately.
        This is the default when ripgrep's stdout is connected to a
        terminal, but otherwise, ripgrep will use block buffering, which is
        typically faster. This flag forces ripgrep to use line buffering
        even if it would otherwise use block buffering. This is typically
        useful in shell pipelines, e.g., tail -f something.log | rg foo
        --line-buffered | rg bar.

        Forceful line buffering can be disabled with --no-line-buffered.
        Note that using --no-line-buffered causes ripgrep to revert to its
        default behavior of automatically detecting the buffering strategy.
        To force block buffering, use the --block-buffered flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--line-buffered")
        return self

    @_logger
    def line_number(self) -> Ripgrepy:
        """
        Show line numbers (1-based). This is enabled by default when
        searching in a terminal.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--line-number")
        return self

    @_logger
    def line_regexp(self) -> Ripgrepy:
        """
        Only show matches surrounded by line boundaries. This is equivalent
        to putting ^...$ around all of the search patterns. In other words,
        this only prints lines where the entire line participates in a
        match.

        This overrides the --word-regexp flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--line-regexp")
        return self

    @_logger
    def max_columns(self, num: int) -> Ripgrepy:
        """
        Don't print lines longer than this limit in bytes. Longer lines are
        omitted, and only the number of matches in that line is printed.

        When this flag is omitted or is set to 0, then it has no effect.

        :param num: Number of columns
        :type num: int
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--max-columns {num}")
        return self

    @_logger
    def max_columns_preview(self) -> Ripgrepy:
        """
        When the --max-columns flag is used, ripgrep will by default
        completely replace any line that is too long with a message
        indicating that a matching line was removed. When this flag is
        combined with --max-columns, a preview of the line (corresponding
        to the limit size) is shown instead, where the part of the line
        exceeding the limit is not shown.

        If the --max-columns flag is not set, then this has no effect.

        This flag can be disabled with --no-max-columns-preview.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--max-columns-preview")
        return self

    @_logger
    def max_count(self, num: int) -> Ripgrepy:
        """
        Limit the number of matching lines per file searched to NUM.

        :param num: Number
        :type num: int
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--max-count {num}")
        return self

    @_logger
    def max_depth(self, num: int) -> Ripgrepy:
        """
        Limit the depth of directory traversal to NUM levels beyond the
        paths given. A value of zero only searches the explicitly given
        paths themselves.

        For example, rg --max-depth 0 dir/ is a no-op because dir/ will not
        be descended into.  rg --max-depth 1 dir/ will search only the
        direct children of dir.

        :param num: Number
        :type num: int
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--max-depth {num}")
        return self

    @_logger
    def max_filesize(self, num_suffix: str) -> Ripgrepy:
        """
        Ignore files larger than NUM in size. This does not apply to
        directories.

        The input format accepts suffixes of K, M or G which correspond to
        kilobytes, megabytes and gigabytes, respectively. If no suffix is
        provided the input is treated as bytes.

        Examples: --max-filesize 50K or --max-filesize 80M

        :param num_suffix: number plus suffic
        :type num_suffix: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--max-filesize "{num_suffix}"')
        return self

    @_logger
    def mmap(self) -> Ripgrepy:
        """
        Search using memory maps when possible. This is enabled by default
        when ripgrep thinks it will be faster.

        Memory map searching doesn't currently support all options, so if
        an incompatible option (e.g., --context) is given with --mmap, then
        memory maps will not be used.

        Note that ripgrep may abort unexpectedly when --mmap if it searches
        a file that is simultaneously truncated.

        This flag overrides --no-mmap.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--mmap")
        return self

    @_logger
    def multiline(self) -> Ripgrepy:
        """
        Enable matching across multiple lines.

        When multiline mode is enabled, ripgrep will lift the restriction
        that a match cannot include a line terminator. For example, when
        multiline mode is not enabled (the default), then the regex \p{any}
        will match any Unicode codepoint other than \\n. Similarly, the
        regex \\n is explicitly forbidden, and if you try to use it, ripgrep
        will return an error. However, when multiline mode is enabled,
        \p{any} will match any Unicode codepoint, including \\n, and regexes
        like \\n are permitted.

        An important caveat is that multiline mode does not change the
        match semantics of .. Namely, in most regex matchers, a .  will by
        default match any character other than \\n, and this is true in
        ripgrep as well. In order to make .  match \\n, you must enable the
        "dot all" flag inside the regex. For example, both (?s).  and
        (?s:.)  have the same semantics, where .  will match any character,
        including \\n. Alternatively, the --multiline-dotall flag may be
        passed to make the "dot all" behavior the default. This flag only
        applies when multiline search is enabled.

        There is no limit on the number of the lines that a single match
        can span.

        WARNING: Because of how the underlying regex engine works,
        multiline searches may be slower than normal line-oriented
        searches, and they may also use more memory. In particular, when
        multiline mode is enabled, ripgrep requires that each file it
        searches is laid out contiguously in memory (either by reading it
        onto the heap or by memory-mapping it). Things that cannot be
        memory-mapped (such as stdin) will be consumed until EOF before
        searching can begin. In general, ripgrep will only do these things
        when necessary. Specifically, if the --multiline flag is provided
        but the regex does not contain patterns that would match \\n
        characters, then ripgrep will automatically avoid reading each file
        into memory before searching it. Nevertheless, if you only care
        about matches spanning at most one line, then it is always better
        to disable multiline mode.

        This flag can be disabled with --no-multiline.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--multiline")
        return self

    @_logger
    def multiline_dotall(self) -> Ripgrepy:
        """
        This flag enables "dot all" in your regex pattern, which causes .
        to match newlines when multiline searching is enabled. This flag
        has no effect if multiline searching isn't enabled with the
        --multiline flag.

        Normally, a .  will match any character except newlines. While this
        behavior typically isn't relevant for line-oriented matching (since
        matches can span at most one line), this can be useful when
        searching with the -U/--multiline flag. By default, the multiline
        mode runs without this flag.

        This flag is generally intended to be used in an alias or your
        ripgrep config file if you prefer "dot all" semantics by default.
        Note that regardless of whether this flag is used, "dot all"
        semantics can still be controlled via inline flags in the regex
        pattern itself, e.g., (?s:.)  always enables "dot all" whereas
        (?-s:.)  always disables "dot all".

        This flag can be disabled with --no-multiline-dotall.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--multiline-dotall")
        return self

    @_logger
    def no_config(self) -> Ripgrepy:
        """
        Never read configuration files. When this flag is present, ripgrep
        will not respect the RIPGREP_CONFIG_PATH environment variable.

        If ripgrep ever grows a feature to automatically read configuration
        files in pre-defined locations, then this flag will also disable
        that behavior as well.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-config")
        return self

    @_logger
    def no_filename(self) -> Ripgrepy:
        """
        Never print the file path with the matched lines. This is the
        default when ripgrep is explicitly instructed to search one file or
        stdin.

        This flag overrides --with-filename.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-filename")
        return self

    @_logger
    def no_heading(self) -> Ripgrepy:
        """
        Don't group matches by each file. If --no-heading is provided in
        addition to the -H/--with-filename flag, then file paths will be
        printed as a prefix for every matched line. This is the default
        mode when not printing to a terminal.

        This overrides the --heading flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-heading")
        return self

    @_logger
    def no_ignore(self) -> Ripgrepy:
        """
        Don't respect ignore files (.gitignore, .ignore, etc.). This
        implies --no-ignore-parent, --no-ignore-dot and --no-ignore-vcs.

        This flag can be disabled with the --ignore flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-ignore")
        return self

    @_logger
    def no_ignore_dot(self) -> Ripgrepy:
        """
        Don't respect .ignore files.

        This flag can be disabled with the --ignore-dot flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-ignore-dot")
        return self

    @_logger
    def no_ignore_global(self) -> Ripgrepy:
        """
        Don't respect ignore files that come from "global" sources such as
        git's core.excludesFile configuration option (which defaults to
        $HOME/.config/git/ignore).

        This flag can be disabled with the --ignore-global flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-ignore-global")
        return self

    @_logger
    def no_ignore_messages(self) -> Ripgrepy:
        """
        Suppresses all error messages related to parsing ignore files such
        as .ignore or .gitignore.

        This flag can be disabled with the --ignore-messages flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-ignore-messages")
        return self

    @_logger
    def no_ignore_parent(self) -> Ripgrepy:
        """
        Don't respect ignore files (.gitignore, .ignore, etc.) in parent
        directories.

        This flag can be disabled with the --ignore-parent flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-ignore-parent")
        return self

    @_logger
    def no_ignore_vcs(self) -> Ripgrepy:
        """
        Don't respect version control ignore files (.gitignore, etc.). This
        implies --no-ignore-parent for VCS files. Note that .ignore files
        will continue to be respected.

        This flag can be disabled with the --ignore-vcs flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-ignore-vcs")
        return self

    @_logger
    def no_line_number(self) -> Ripgrepy:
        """
        Suppress line numbers. This is enabled by default when not
        searching in a terminal.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-line-number")
        return self

    @_logger
    def no_messages(self) -> Ripgrepy:
        """
        Suppress all error messages related to opening and reading files.
        Error messages related to the syntax of the pattern given are still
        shown.

        This flag can be disabled with the --messages flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-messages")
        return self

    @_logger
    def no_mmap(self) -> Ripgrepy:
        """
        Never use memory maps, even when they might be faster.

        This flag overrides --mmap.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-mmap")
        return self

    @_logger
    def no_pcre2_unicode(self) -> Ripgrepy:
        """
        When PCRE2 matching is enabled, this flag will disable Unicode
        mode, which is otherwise enabled by default. If PCRE2 matching is
        not enabled, then this flag has no effect.

        When PCRE2's Unicode mode is enabled, several different types of
        patterns become Unicode aware. This includes \\b, \B, \w, \W, \d,
        \D, \s and \S. Similarly, the .  meta character will match any
        Unicode codepoint instead of any byte. Caseless matching will also
        use Unicode simple case folding instead of ASCII-only case
        insensitivity.

        Unicode mode in PCRE2 represents a critical trade off in the user
        experience of ripgrep. In particular, unlike the default regex
        engine, PCRE2 does not support the ability to search possibly
        invalid UTF-8 with Unicode features enabled. Instead, PCRE2
        requires that everything it searches when Unicode mode is enabled
        is valid UTF-8. (Or valid UTF-16/UTF-32, but for the purposes of
        ripgrep, we only discuss UTF-8.) This means that if you have
        PCRE2's Unicode mode enabled and you attempt to search invalid
        UTF-8, then the search for that file will halt and print an error.
        For this reason, when PCRE2's Unicode mode is enabled, ripgrep will
        automatically "fix" invalid UTF-8 sequences by replacing them with
        the Unicode replacement codepoint.

        If you would rather see the encoding errors surfaced by PCRE2 when
        Unicode mode is enabled, then pass the --no-encoding flag to
        disable all transcoding.

        Related flags: --pcre2

        This flag can be disabled with --pcre2-unicode.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-pcre2-unicode")
        return self

    @_logger
    def null(self) -> Ripgrepy:
        """
        Whenever a file path is printed, follow it with a NUL byte. This
        includes printing file paths before matches, and when printing a
        list of matching files such as with --count, --files-with-matches
        and --files. This option is useful for use with xargs.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--null")
        return self

    @_logger
    def null_data(self) -> Ripgrepy:
        """
        Enabling this option causes ripgrep to use NUL as a line terminator
        instead of the default of \\n.

        This is useful when searching large binary files that would
        otherwise have very long lines if \\n were used as the line
        terminator. In particular, ripgrep requires that, at a minimum,
        each line must fit into memory. Using NUL instead can be a useful
        stopgap to keep memory requirements low and avoid OOM (out of
        memory) conditions.

        This is also useful for processing NUL delimited data, such as that
        emitted when using ripgrep's -0/--null flag or find's --print0
        flag.

        Using this flag implies -a/--text.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--null-data")
        return self

    @_logger
    def one_file_system(self) -> Ripgrepy:
        """
        When enabled, ripgrep will not cross file system boundaries
        relative to where the search started from.

        Note that this applies to each path argument given to ripgrep. For
        example, in the command rg --one-file-system /foo/bar /quux/baz,
        ripgrep will search both /foo/bar and /quux/baz even if they are on
        different file systems, but will not cross a file system boundary
        when traversing each path's directory tree.

        This is similar to find's -xdev or -mount flag.

        This flag can be disabled with --no-one-file-system.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--one-file-system")
        return self

    @_logger
    def only_matching(self) -> Ripgrepy:
        """
        Print only the matched (non-empty) parts of a matching line, with
        each such part on a separate output line.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--only-matching")
        return self

    @_logger
    def passthru(self) -> Ripgrepy:
        """
        Print both matching and non-matching lines.

        Another way to achieve a similar effect is by modifying your
        pattern to match the empty string. For example, if you are
        searching using rg foo then using rg "^|foo" instead will emit
        every line in every file searched, but only occurrences of foo will
        be highlighted. This flag enables the same behavior without needing
        to modify the pattern.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--passthru")
        return self

    @_logger
    def path_seprator(self, separator: str) -> Ripgrepy:
        """
        Set the path separator to use when printing file paths. This
        defaults to your platform's path separator, which is / on Unix and
        \ on Windows. This flag is intended for overriding the default when
        the environment demands it (e.g., cygwin). A path separator is
        limited to a single byte.

        :param separator: separator
        :type separator: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--path-separator "{separator}"')
        return self

    @_logger
    def pcre2(self) -> Ripgrepy:
        """
        When this flag is present, ripgrep will use the PCRE2 regex engine
        instead of its default regex engine.

        This is generally useful when you want to use features such as
        look-around or backreferences.

        Note that PCRE2 is an optional ripgrep feature. If PCRE2 wasn't
        included in your build of ripgrep, then using this flag will result
        in ripgrep printing an error message and exiting.

        Related flags: --no-pcre2-unicode

        This flag can be disabled with --no-pcre2.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--pcre2")
        return self

    @_logger
    def pcre2_version(self) -> Ripgrepy:
        """
        When this flag is present, ripgrep will print the version of PCRE2
        in use, along with other information, and then exit. If PCRE2 is
        not available, then ripgrep will print an error message and exit
        with an error code.

        :return: self
        :rtype: Ripgrepy
        """
        self.regex_pattern = ""
        self.command.append("--pcre2-version")
        return self

    @_logger
    def pre(self, command: str) -> Ripgrepy:
        """
        For each input FILE, search the standard output of COMMAND FILE
        rather than the contents of FILE. This option expects the COMMAND
        program to either be an absolute path or to be available in your
        PATH. Either an empty string COMMAND or the --no-pre flag will
        disable this behavior.

        WARNING: When this flag is set, ripgrep will unconditionally spawn a
        process for every file that is searched. Therefore, this can incur an
        unnecessarily large performance penalty if you don't otherwise need the
        flexibility offered by this flag. One possible mitigation to this is to use
        the '--pre-glob' flag to limit which files a preprocessor is run with.

        A preprocessor is not run when ripgrep is searching stdin.

        When searching over sets of files that may require one of several
        decoders as preprocessors, COMMAND should be a wrapper program or
        script which first classifies FILE based on magic numbers/content
        or based on the FILE name and then dispatches to an appropriate
        preprocessor. Each COMMAND also has its standard input connected to
        FILE for convenience.

        For example, a shell script for COMMAND might look like:

        >>>    case "$1" in
        >>>    *.pdf)
        >>>        exec pdftotext "$1" -
        >>>        ;;
        >>>    *)
        >>>        case $(file "$1") in
        >>>        *Zstandard*)
        >>>            exec pzstd -cdq
        >>>            ;;
        >>>        *)
        >>>            exec cat
        >>>            ;;
        >>>        esac
        >>>        ;;
        >>>    esac

        The above script uses pdftotext to convert a PDF file to plain
        text. For all other files, the script uses the file utility to
        sniff the type of the file based on its contents. If it is a
        compressed file in the Zstandard format, then pzstd is used to
        decompress the contents to stdout.

        This overrides the -z/--search-zip flag.

        :param command: command to execute
        :type command: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--pre "{command}"')
        return self

    @_logger
    def pre_glob(self, glob: str) -> Ripgrepy:
        """
        This flag works in conjunction with the --pre flag. Namely, when
        one or more --pre-glob flags are given, then only files that match
        the given set of globs will be handed to the command specified by
        the --pre flag. Any non-matching files will be searched without
        using the preprocessor command.

        This flag is useful when searching many files with the --pre flag.
        Namely, it permits the ability to avoid process overhead for files
        that don't need preprocessing. For example, given the following
        shell script, pre-pdftotext:

        >>>    #!/bin/sh
        >>>    pdftotext "$1" -

        then it is possible to use --pre pre-pdftotext --pre-glob '\*.pdf'
        to make it so ripgrep only executes the pre-pdftotext command on
        files with a .pdf extension.

        Multiple --pre-glob flags may be used. Globbing rules match
        .gitignore globs. Precede a glob with a ! to exclude it.

        This flag has no effect if the --pre flag is not used.

        :param glob: Glob pattern
        :type glob: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--pre-glob "{glob}"')
        return self

    @_logger
    def pretty(self) -> Ripgrepy:
        """
        This is a convenience alias for --color always --heading
        --line-number. This flag is useful when you still want pretty
        output even if you're piping ripgrep to another program or file.
        For example: rg -p foo | less -R.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--pretty")
        return self

    @_logger
    def quite(self) -> Ripgrepy:
        """
        Do not print anything to stdout. If a match is found in a file,
        then ripgrep will stop searching. This is useful when ripgrep is
        used only for its exit code (which will be an error if no matches
        are found).

        When --files is used, then ripgrep will stop finding files after
        finding the first file that matches all ignore rules.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--quite")
        return self

    @_logger
    def regex_size_limit(self, num_suffix: str) -> Ripgrepy:
        """
        The upper size limit of the compiled regex. The default limit is
        10M.

        The argument accepts the same size suffixes as allowed in the
        --max-filesize flag.

        :param num_suffix: Number + suffix
        :type num_suffix: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--regex-size-limit "{num_suffix}"')
        return self

    @_logger
    def regexp(self, pattern: str) -> Ripgrepy:
        """
        A pattern to search for. This option can be provided multiple
        times, where all patterns given are searched. Lines matching at
        least one of the provided patterns are printed. This flag can also
        be used when searching for patterns that start with a dash.

        For example, to search for the literal -foo, you can use this flag:

            rg -e -foo

        You can also use the special -- delimiter to indicate that no more
        flags will be provided. Namely, the following is equivalent to the
        above:

            rg -- -foo

        :param pattern: Regex pattern
        :type pattern: str
        :return: self
        :rtype: Ripgrepy
        """
        self.regex_pattern = ""
        self.command.append(f'--regexp "{pattern}"')
        return self

    @_logger
    def replace(self, replacement_text: str) -> Ripgrepy:
        """
        Replace every match with the text given when printing results.
        Neither this flag nor any other ripgrep flag will modify your
        files.

        Capture group indices (e.g., $5) and names (e.g., $foo) are
        supported in the replacement string.

        Note that the replacement by default replaces each match, and NOT
        the entire line. To replace the entire line, you should match the
        entire line.

        This flag can be used with the -o/--only-matching flag.

        :param replacement_text: Replacement text. Groups are supported
        :type replacement_text: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--replace '{replacement_text}'")
        return self

    @_logger
    def search_zip(self) -> Ripgrepy:
        """
        Search in compressed files. Currently gzip, bzip2, xz, LZ4, LZMA,
        Brotli and Zstd files are supported. This option expects the
        decompression binaries to be available in your PATH.

        This flag can be disabled with --no-search-zip.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--search-zip")
        return self

    @_logger
    def smart_case(self) -> Ripgrepy:
        """
        Searches case insensitively if the pattern is all lowercase. Search
        case sensitively otherwise.

        This overrides the -s/--case-sensitive and -i/--ignore-case flags.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--smart-case")
        return self

    @_logger
    def sort(self, sort_by: str) -> Ripgrepy:
        """
        This flag enables sorting of results in ascending order. The
        possible values for this flag are:

            path        Sort by file path.
            modified    Sort by the last modified time on a file.
            accessed    Sort by the last accessed time on a file.
            created     Sort by the creation time on a file.
            none        Do not sort results.

        If the sorting criteria isn't available on your system (for
        example, creation time is not available on ext4 file systems), then
        ripgrep will attempt to detect this and print an error without
        searching any results. Otherwise, the sort order is unspecified.

        To sort results in reverse or descending order, use the --sortr
        flag. Also, this flag overrides --sortr.

        Note that sorting results currently always forces ripgrep to
        abandon parallelism and run in a single thread.

        :param sort_by: Sort by path, modified, accessed, created, none
        :type sort_by: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--sort "{sort_by}"')
        return self

    @_logger
    def sortr(self, sort_by: str) -> Ripgrepy:
        """
        This flag enables sorting of results in descending order. The
        possible values for this flag are:

            path        Sort by file path.
            modified    Sort by the last modified time on a file.
            accessed    Sort by the last accessed time on a file.
            created     Sort by the creation time on a file.
            none        Do not sort results.

        If the sorting criteria isn't available on your system (for
        example, creation time is not available on ext4 file systems), then
        ripgrep will attempt to detect this and print an error without
        searching any results. Otherwise, the sort order is unspecified.

        To sort results in ascending order, use the --sort flag. Also, this
        flag overrides --sort.

        Note that sorting results currently always forces ripgrep to
        abandon parallelism and run in a single thread.

        :param sort_by: Sort desending by. Valid options are accessed, modified, path, created, none
        :type sort_by: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--sortr "{sort_by}"')
        return self

    @_logger
    def stats(self) -> Ripgrepy:
        """
        Print aggregate statistics about this ripgrep search. When this
        flag is present, ripgrep will print the following stats to stdout
        at the end of the search: number of matched lines, number of files
        with matches, number of files searched, and the time taken for the
        entire search to complete.

        This set of aggregate statistics may expand over time.

        Note that this flag has no effect if --files, --files-with-matches
        or --files-without-match is passed.

        This flag can be disabled with --no-stats.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--stats")
        return self

    @_logger
    def text(self) -> Ripgrepy:
        """
        Search binary files as if they were text. When this flag is
        present, ripgrep's binary file detection is disabled. This means
        that when a binary file is searched, its contents may be printed if
        there is a match. This may cause escape codes to be printed that
        alter the behavior of your terminal.

        When binary file detection is enabled it is imperfect. In general,
        it uses a simple heuristic. If a NUL byte is seen during search,
        then the file is considered binary and search stops (unless this
        flag is present). Alternatively, if the --binary flag is used, then
        ripgrep will only quit when it sees a NUL byte after it sees a
        match (or searches the entire file).

        This flag can be disabled with --no-text. It overrides the --binary
        flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--text")
        return self

    @_logger
    def threads(self, num: int) -> Ripgrepy:
        """
        The approximate number of threads to use. A value of 0 (which is
        the default) causes ripgrep to choose the thread count using
        heuristics.

        :param num: Number of threads
        :type num: int
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--threads {num}")
        return self

    @_logger
    def trim(self) -> Ripgrepy:
        """
        When set, all ASCII whitespace at the beginning of each line
        printed will be trimmed.

        This flag can be disabled with --no-trim.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--trim")
        return self

    @_logger
    def type_(self, type_pattern: str) -> Ripgrepy:
        """
        Only search files matching TYPE. Multiple type flags may be
        provided. Use the --type-list flag to list all available types.

        :param type_pattern: Type pattern
        :type type_pattern: str
        :return: [description]
        :rtype: Ripgrepy
        """
        self.command.append(f'--type "{type_pattern}"')
        return self

    @_logger
    def type_add(self, type_spec: str) -> Ripgrepy:
        """
        Add a new glob for a particular file type. Only one glob can be
        added at a time. Multiple --type-add flags can be provided. Unless
        --type-clear is used, globs are added to any existing globs defined
        inside of ripgrep.

        Note that this MUST be passed to every invocation of ripgrep. Type
        settings are NOT persisted.

        Example:

        >>>    rg --type-add 'foo:*.foo' -tfoo PATTERN.

        --type-add can also be used to include rules from other types with
        the special include directive. The include directive permits
        specifying one or more other type names (separated by a comma) that
        have been defined and its rules will automatically be imported into
        the type specified. For example, to create a type called src that
        matches C++, Python and Markdown files, one can use:

        >>>    --type-add 'src:include:cpp,py,md'

        Additional glob rules can still be added to the src type by using
        the --type-add flag again:

        >>>    --type-add 'src:include:cpp,py,md' --type-add 'src:*.foo'

        Note that type names must consist only of Unicode letters or
        numbers. Punctuation characters are not allowed.

        :param type_spec: Type spec
        :type type_spec: str
        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f'--type-add "{type_spec}"')
        return self

    @_logger
    def type_clear(self) -> Ripgrepy:
        """
        Clear the file type globs previously defined for TYPE. This only
        clears the default type definitions that are found inside of
        ripgrep.

        Note that this MUST be passed to every invocation of ripgrep. Type
        settings are NOT persisted.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--type-clear")
        return self

    @_logger
    def type_list(self) -> Ripgrepy:
        """
        Show all supported file types and their corresponding globs.

        :return: self
        :rtype: Ripgrepy
        """
        self.regex_pattern = ""
        self.path = ""
        self.command.append("--type-list")
        return self

    @_logger
    def type_not(self, type_pattern: str) -> Ripgrepy:
        """
        Do not search files matching TYPE. Multiple type-not flags may be
        provided. Use the --type-list flag to list all available types

        :param type_pattern: Type pattern
        :type type_pattern: str
        :return: [description]
        :rtype: Ripgrepy
        """
        self.command.append(f'--type-not "{type_pattern}"')
        return self

    @_logger
    def unrestricted(self) -> Ripgrepy:
        """
        Reduce the level of "smart" searching. A single -u won't respect
        .gitignore (etc.) files. Two -u flags will additionally search
        hidden files and directories. Three -u flags will additionally
        search binary files.

        rg -uuu is roughly equivalent to grep -r.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--unrestricted")
        return self

    @_logger
    def vimgrep(self) -> Ripgrepy:
        """
        Show results with every match on its own line, including line
        numbers and column numbers. With this option, a line with more than
        one match will be printed more than once.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--vimgrep")
        return self

    @_logger
    def with_filename(self) -> Ripgrepy:
        """
        Display the file path for matches. This is the default when more
        than one file is searched. If --heading is enabled (the default
        when printing to a terminal), the file path will be shown above
        clusters of matches from each file; otherwise, the file name will
        be shown as a prefix for each matched line.

        This flag overrides --no-filename.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--with-filename")
        return self

    @_logger
    def word_regexp(self) -> Ripgrepy:
        """
        Only show matches surrounded by word boundaries. This is roughly
        equivalent to putting \\b before and after all of the search
        patterns.

        This overrides the --line-regexp flag.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--word-regexp")
        return self

    ### Options for version 12 of ripgrep
    @_logger
    def no_unicode(self) -> Ripgrepy:
        """
        By default, ripgrep will enable "Unicode mode" in all of its
        regexes. This has a number of consequences:

        ·   . will only match valid UTF-8 encoded scalar values.

        ·   Classes like \w, \s, \d are all Unicode aware and much bigger
            than their ASCII only versions.

        ·   Case insensitive matching will use Unicode case folding.

        ·   A large array of classes like \p{Emoji} are available.

        ·   Word boundaries (\\b and \B) use the Unicode definition of a
            word character.

            In some cases it can be desirable to turn these things off. The
            --no-unicode flag will do exactly that.

            For PCRE2 specifically, Unicode mode represents a critical
            trade off in the user experience of ripgrep. In particular,
            unlike the default regex engine, PCRE2 does not support the
            ability to search possibly invalid UTF-8 with Unicode features
            enabled. Instead, PCRE2 requires that everything it searches
            when Unicode mode is enabled is valid UTF-8. (Or valid
            UTF-16/UTF-32, but for the purposes of ripgrep, we only discuss
            UTF-8.) This means that if you have PCRE2's Unicode mode
            enabled and you attempt to search invalid UTF-8, then the
            search for that file will halt and print an error. For this
            reason, when PCRE2's Unicode mode is enabled, ripgrep will
            automatically "fix" invalid UTF-8 sequences by replacing them
            with the Unicode replacement codepoint. This penalty does not
            occur when using the default regex engine.

            If you would rather see the encoding errors surfaced by PCRE2
            when Unicode mode is enabled, then pass the --no-encoding flag
            to disable all transcoding.

            The --no-unicode flag can be disabled with --unicode. Note that
            --no-pcre2-unicode and --pcre2-unicode are aliases for
            --no-unicode and --unicode, respectively.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append("--no-unicode")
        return self

    @_logger
    def engine(self, engine: str) -> Ripgrepy:
        """
        Specify which regular expression engine to use. When you choose a
        regex engine, it applies that choice for every regex provided to
        ripgrep (e.g., via multiple -e/--regexp or -f/--file flags).

        Accepted values are default, pcre2, or auto.

        The default value is default, which is the fastest and should be
        good for most use cases. The pcre2 engine is generally useful when
        you want to use features such as look-around or backreferences.
        auto will dynamically choose between supported regex engines
        depending on the features used in a pattern on a best effort basis.

        Note that the pcre2 engine is an optional ripgrep feature. If PCRE2
        wasn't including in your build of ripgrep, then using this flag
        will result in ripgrep printing an error message and exiting.

        This overrides previous uses of --pcre2 and --auto-hybrid-regex
        flags.

        :return: self
        :rtype: Ripgrepy
        """
        self.command.append(f"--engine {engine}")
        return self
