#!/usr/bin/env python

import calendar
import os
import re
import time
from datetime import datetime


def in_purge_window(target, base, now=time.time(), percent=0.1):
    """Return whether the target timestamp is in the "purge window" of the base
    timestamp.  The target timestamp is within the purge window if it is less
    than ``percent`` older than base.

    :param target: Target time that is being tested for purgeability
    :param base: Base time to compare target to
    :param now: Used for calculating ages; defaults to now
    :param percent: Percentage of the age of base to use for the purge window
    :returns: Boolean signifying whether target is in the purge window

    Simple example:

    >>> in_purge_window(4,5,20)
    True
    >>> in_purge_window(4,9,20)
    False

    A more real world example:

    >>> import datetime
    >>> import calendar
    >>> def time_to_timestamp(time):
    ...   return calendar.timegm(time.utctimetuple())
    ...
    >>> now = datetime.datetime(2012, 12, 1)
    >>> base = datetime.datetime(2012, 7, 1)
    >>> target = datetime.datetime(2012, 5, 1)
    >>> for var in ['now', 'base', 'target']:
    ...     locals()[var] = time_to_timestamp(locals()[var])
    ...
    >>> in_purge_window(target, base, now)
    False
    >>> now = time_to_timestamp(datetime.datetime(2014, 12, 1))
    >>> in_purge_window(target, base, now)
    True

    """

    # This code assumes that base is older than now
    assert now > base
    return base > target > (base - percent * (now - base))


def get_purgeables(items, now=time.time()):
    """Given a collection items and their timestamps, return which ones should
    be purged.  An item is considered purgeable if it, along with other items,
    are in the purge window of an item.  If multiple items are within another
    item's purge window, the oldest of these items is kept and the rest are
    purged.  items does not need to be sorted, it will be sorted by their
    timestamps.

    :param items: A dictionary of items and their timestamps
    :returns: The list of items considered purgeable

    >>> from datetime import datetime, timedelta
    >>> import calendar
    >>> def time_to_timestamp(time):
    ...   return calendar.timegm(time.utctimetuple())
    ...
    >>> items = {}
    >>> for i in range(0,100):
    ...     timestamp = time_to_timestamp(datetime.now() - timedelta(days=i))
    ...     items['item{}'.format(i)] = timestamp
    ...
    >>> len(get_purgeables(items))
    60
    """

    # Sort the items dictionary by the timestamp values
    sorted_items = [ (k,v) for k,v in items.items() ]
    sorted_items = sorted(sorted_items, lambda x,y: cmp(x[1], y[1]))

    remove = []
    current = 0

    # The -2 is to make sure we never remove the last item
    while current < len(items) - 2:

        # Look two items ahead of current
        keeper = current + 2
        purgeable = current + 1

        # If the keeper is within the purge window, then so is the purgeable.
        # We want to keep the older of the two (keeper), so add the purgeable
        # to the list of items to remove.
        while keeper < len(items) and in_purge_window(sorted_items[current][1], sorted_items[keeper][1], now):
            # Remove the item directly before the one that is in the purge
            # window (the newer one).
            remove.append(sorted_items[purgeable][0])
            keeper += 1
            purgeable += 1

        # Out of the loop, keeper is out of the purge window, so current should
        # be the last item item that was kept.
        current = keeper - 1

    return remove


def find_datetime(string):
    """Given a string, see if there's a timestamp that can be extracted

    :param string: The string which may contain a timestamp
    :returns: Any datetime found in the string

    >>> find_datetime('somefile-1969-07-20.txt')
    datetime.datetime(1969, 7, 20, 0, 0)
    """

    regexs = [
        re.compile('(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})'),
        re.compile('(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{1,2}):(?P<minute>\d{2}):(?P<second>\d{2})'),
        re.compile('(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})_(?P<hour>\d{2})_(?P<minute>\d{2})_(?P<second>\d{2})'),
        re.compile('(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'),
        re.compile('(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})'),
    ]

    for regex in regexs:
        match = regex.search(string)
        if match:
            datedata = match.groupdict()

            # Convert the strings to ints
            datedata = dict( [ (k, int(v)) for k,v in datedata.iteritems() ] )

            # The replace is because only sometimes do we have hour/min/sec
            dt = datetime(datedata['year'], datedata['month'],
                          datedata['day']).replace(**datedata)

            #return calendar.timegm(dt.timetuple())
            return dt

    return None


def main():

    import argparse

    parser = argparse.ArgumentParser(description='Purges logs in the specified directory.')
    parser.add_argument("-d", "--directory", nargs=1, action="store",
                        help='Specifies the directory to work in.', type=str)
    parser.add_argument("-n", "--noop", action="store_const", const=True,
                        help='No operation. Does not apply any changes.',
                        default=False)
    # -y for "yes" -f because it mimics rm's behavior
    parser.add_argument("-y", "-f", action="store_const", const=True,
                        help='Does not prompt for deletion.',
                        default=False)

    args = parser.parse_args()

    if args.directory == None:
        parser.print_help()
        quit()

    if args.noop and args.y:
        print "Cannot have -f and -n at the same time. Try again."
        quit()

    # Find dates in the filenames of all the files in the given directory
    files = os.listdir(args.directory[0])
    files_dates = { f: find_datetime(f) for f in files }

    # Ignore files with incomprehensible dates
    for k, v in files_dates.items():
        if v is None:
            files_dates.pop(k)

    files_timestamps = { f: calendar.timegm(date.utctimetuple()) for f, date in files_dates.items() }

    # Get the dates that need removing
    files_to_remove = get_purgeables(files_timestamps)

    # Print out which ones will be removed
    for file_, date in files_dates.items():
        print '{} - {} {}'.format(file_, date, file_ in files_to_remove)

    cont = None
    # No operation
    if args.noop == True:
        cont = False
    # Force operation, do not prompt for input
    if args.y == True:
        cont = True
    # If neither was specified
    if cont == None:
        cont = raw_input('Continue [y/N]')
        if cont[0].lower() == 'y':
            cont = True
        else:
            cont = False

    if cont:
        for r in remove:
            os.remove(os.path.join(args.directory[0], dates_files[r]))


if __name__ == '__main__':
    main()
