#!/bin/sh

# ocf-tester doesn't support testing of Python scripts
# so this is a simple wrapper

python docker-container "$@"
exit $?
