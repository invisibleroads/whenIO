whenIO
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
    >>> w = whenIO.WhenIO(timezone='US/Eastern')

    >>> w.format(datetime.datetime.now(), fromUTC=False)
    'Today 2:30pm'
    >>> w.format(datetime.datetime.utcnow())
    'Today 2:30pm'
    >>> w.format(datetime.datetime.utcnow(), forceDate=True)
    'Today 3/10/2013 2:30pm'
    >>> date1 = datetime.datetime(2000, 1, 1, 0, 0)
    >>> date2 = datetime.datetime(2000, 1, 1, 1, 0)
    >>> w.format([date1, date2], fromUTC=False)
    '1/1/2000 12am 1am'

    >>> w.parse('10am', toUTC=False)[0]
    [datetime.datetime(2013, 3, 10, 10, 0)]
    >>> w.parse('today 10am', toUTC=False)[0]
    [datetime.datetime(2013, 3, 10, 10, 0)]
    >>> w.parse('tom 8pm', toUTC=False)[0]
    [datetime.datetime(2013, 3, 11, 20, 0)]
    >>> w.parse('mon 10am 12pm', toUTC=False)[0]
    [datetime.datetime(2013, 3, 11, 10, 0), 
     datetime.datetime(2013, 3, 11, 12, 0)]

    >>> rdelta = whenIO.parse_interval('2 years 7 months 1 second')
    >>> whenIO.format_interval(rdelta, precision=1)
    '3 years'
    >>> whenIO.format_interval(rdelta, precision=2)
    '2 years 7 months'
