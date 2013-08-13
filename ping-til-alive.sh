#!/bin/bash

# exit on error
set -e


# Usage
function usage {
cat << EOF
usage: $0 [options] IP/HOSTNAME

Wait for a network device to respond.

OPTIONS:
   -h      Help
   -r      Ignore inability to resolve hostnames
   -t      Timeout in seconds (default $DEFAULT_TIMEOUT)
   -v      Verbose
EOF
}

# If verbose is enabled echo the given message
function v {
  if [ $verbose -ne 0 ]
  then
    echo $*
  fi
}

# Parse options and args
DEFAULT_TIMEOUT=10
host=
timeout=$DEFAULT_TIMEOUT
verbose=0

while getopts "ht:v" option
do
  case $option in
    h)
      usage
      exit
      ;;
    t)
      timeout=$OPTARG
      ;;
    v)
      verbose=1
      ;;
  esac
done

shift $(($OPTIND - 1))
host=$1

if [ -z $host ]
then
  echo "A host is required"
  usage
  exit 1
fi

# Ping til response
start=$(date +"%s")
result=1
while [ $result -ne 0 ]; do

  now=$(date +"%s")
  elapsed=$((now - start))
  remaining=$((timeout - elapsed))
  v Remaining time: $remaining

  if [ $remaining -lt 1 ]; then
    echo "Timed out."
    exit 1
  fi

  sleep 1

  v Pinging $host

  # Temporarily allow errors in commands
  set +e
  ping -c 1 $host 2> /dev/null 1>/dev/null
  result=$?
  set -e

  v Result: $result
done
