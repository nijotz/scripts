#!/bin/bash
#
# Add red or green leading character depending on if output is stdout or stderr
#
# Stolen from:
# http://stackoverflow.com/questions/6841143/how-to-set-font-color-for-stdout-and-stderr/16178979#16178979
# 
# color()(set -o pipefail;"$@" 2>&1>&3|sed $'s,.*,\e[31m&\e[m,'>&2)3>&1
# 
# set -o pipefail — This is a shell option that preserves the error return code of a command whose output is piped into another command.
# (set -o...) — This is done in a subshell, which is created by the parentheses, so as not to change the pipefail option in the outer shell.
# "$@" — Executes the arguments to the function as a new command. "$@" is equivalent to "$1" "$2" ...
# 2>&1 — Redirects the stderr of the command to stdout so that it becomes sed's stdin.
# >&3 — Shorthand for 1>&3, this redirects stdout to a new temporary file descriptor 3. 3 gets routed back into stdout later.
# sed ... — Because of the redirects above, sed's stdin is the stderr of the executed command. Its function is to surround each line with color codes.
# $'...' A bash construct that causes it to understand backslash-escaped characters
# .* — Matches the entire line.
# \e[31m — The ANSI escape sequence that causes the following characters to be red
# & — The sed replace character that expands to the entire matched string (the entire line in this case).
# \e[m — The ANSI escape sequence that resets the color.
# >&2 — Shorthand for 1>&2, this redirects sed's stdout to stderr.
# 3>&1 — Redirects the temporary file descriptor 3 back into stdout.

(
set -o pipefail
"$@" 2>&1 1>&3 | sed $'s/^/\e[31m!\e[m /' 1>&2
)3>&1 | sed $'s/^/\e[32m*\e[m /'
