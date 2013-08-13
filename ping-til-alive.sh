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
   -t      Timeout in seconds (0 for no timeout, default: $DEFAULT_TIMEOUT)
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


# Stores the result of ping, 300 signifies first run and no sleep
result=300

# Ping til response
start=$(date +"%s")
while [ $result -ne 0 ]; do

  now=$(date +"%s")
  elapsed=$((now - start))

  # Remaining time, could be infinite (no timeout)
  if [ $timeout -ne 0 ]; then
    remaining=$((timeout - elapsed))
  else
    if [ $(locale charmap) == "UTF-8" ]; then
      remaining=∞
    else
      remaining=Inf
    fi
  fi

  v Elapsed time: $elapsed - Remaining time: $remaining

  # Timeout if need be
  if [ $timeout -ne 0 ] && [ $remaining -lt 1 ]; then
    echo "Timed out."
    exit 1
  fi

  # Pause between pings, but not the first time through
  if [ $result -ne 300 ]; then
    sleep 1
  fi

  v Pinging $host

  # Temporarily allow errors in commands
  set +e
  ping -c 1 $host 2> /dev/null 1>/dev/null
  result=$?
  set -e

  v Result: $result
done
