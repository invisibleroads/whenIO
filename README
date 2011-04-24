WhenIO
======
Here are some methods for formatting and parsing friendly timestamps.


Installation
------------
::

    easy_install -U whenIO


Usage
-----
::

    >>> import whenIO
    >>> import datetime
    >>> w = whenIO.WhenIO(minutesOffset=240)

    >>> w.format(datetime.datetime.utcnow(), fromUTC=False)
    'Today 5:15pm'
    >>> w.format(datetime.datetime.utcnow(), fromUTC=True)
    'Today 1:15pm'
    >>> w.format(datetime.datetime.utcnow(), dateTemplate_=' %m/%d/%Y', fromUTC=True)
    'Today 04/24/2011 1:15pm'
    >>> w.format([datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 1, 0)], fromUTC=False)
    '01/01/2000 12am 1am'

    >>> w.parse('10am', toUTC=False)
    ([datetime.datetime(2011, 4, 24, 10, 0)], [])
    >>> w.parse('today 10am', toUTC=False)
    ([datetime.datetime(2011, 4, 24, 10, 0)], [])
    >>> w.parse('today 10am', toUTC=True)
    ([datetime.datetime(2011, 4, 24, 14, 0)], [])
    >>> w.parse('tom 8pm', toUTC=True)
    ([datetime.datetime(2011, 4, 26, 0, 0)], [])
    >>> w.parse('Monday 8:10pm tag1 tag2', toUTC=True)
    ([datetime.datetime(2011, 4, 26, 0, 10)], ['tag1', 'tag2'])

    >>> w.format_offset()
    '-0400 UTC'
    >>> whenIO.format_offset(-540)
    '+0900 UTC'
    >>> whenIO.parse_offset('-0400 UTC')
    (240, '')
