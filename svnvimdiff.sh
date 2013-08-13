#!/bin/sh

# This allows: svn diff --diff-cmd=/path/to/svnvimdiff.sh
# Subversion provides the paths we need as the sixth and seventh parameters

`which vimdiff` -R ${6} ${7}
