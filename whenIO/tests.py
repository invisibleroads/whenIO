'Tests for whenIO'
import datetime
import unittest

import whenIO


timezone = 'US/Eastern'
today = datetime.datetime(2009, 5, 1)
specialPacks = [
    ('tod', 'today',     datetime.datetime(2009, 5, 1)),
    ('tom', 'tomorrow',  datetime.datetime(2009, 5, 2)),
    ('yes', 'yesterday', datetime.datetime(2009, 4, 30)),
    ('mon', 'monday',    datetime.datetime(2009, 5, 4)),
    ('tue', 'tuesday',   datetime.datetime(2009, 5, 5)),
    ('wed', 'wednesday', datetime.datetime(2009, 5, 6)),
    ('thu', 'thursday',  datetime.datetime(2009, 5, 7)),
    ('fri', 'friday',    datetime.datetime(2009, 5, 8)),
    ('sat', 'saturday',  datetime.datetime(2009, 5, 2)),
    ('sun', 'sunday',    datetime.datetime(2009, 5, 3)),
]


class Test(unittest.TestCase):

    def setUp(self):
        self.whenIO = whenIO.WhenIO(timezone, today)

    def test_format(self):
        'Test that formatting works properly'
        def assertFormat(whens, whensString, **kw):
            self.assertEqual(self.whenIO.format(whens, fromUTC=False, **kw), whensString)
            if not hasattr(whens, '__iter__'):
                whens = [whens]
            self.assertEqual(self.whenIO.format([
                self.whenIO._from_local(x) for x in whens
            ], fromUTC=True, **kw), whensString)
        # Test regular dates
        assertFormat(datetime.datetime(2009, 1, 1),         '1/1/2009 12am')
        assertFormat(datetime.datetime(2009, 1, 1, 3),      '1/1/2009 3am')
        assertFormat(datetime.datetime(2009, 1, 1, 15, 15), '1/1/2009 3:15pm')
        # Test multiple dates
        assertFormat([
            datetime.datetime(2000, 1, 1, 0, 0),
            datetime.datetime(2000, 1, 1, 1, 0),
        ], '1/1/2000 12am 1am')
        assertFormat([
            datetime.datetime(2009, 1, 1, 0, 0),
            datetime.datetime(2009, 1, 2, 0, 0),
            datetime.datetime(2009, 1, 3, 0, 0),
        ], '1/1/2009 12am, 1/2/2009 12am, 1/3/2009 12am', separator=', ')
        # Test special dates
        for stringShort, stringLong, date in specialPacks:
            if date == datetime.datetime(2009, 5, 2):
                stringLong = 'tomorrow'
            assertFormat(date, stringLong.title() + ' 12am')
        # Test custom templates
        assertFormat(datetime.datetime(2009, 1, 1), '20090101 12am', dateTemplate='%Y%m%d', withLeadingZero=True)
        # Test edge cases
        self.whenIO.format([None])
        self.whenIO.format([datetime.datetime(2000, 1, 1), None])

    def test_parse(self):
        'Test that parsing works properly'
        def assertParse(whensString, whens):
            if not hasattr(whens, '__iter__'):
                whens = [whens]
            self.assertEqual(self.whenIO.parse(whensString, toUTC=False)[0], whens)
            self.assertEqual(self.whenIO.parse(whensString, toUTC=True)[0], [
                self.whenIO._from_local(x) for x in whens
            ])
        # Test regular dates
        assertParse('12am',            datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('12am text',       datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('5/1',             datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('5/1/09',          datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('5/1/2009',        datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('5/1/2009 3am',    datetime.datetime(2009, 5, 1, 3, 0))
        assertParse('5/1/2009 3:15pm', datetime.datetime(2009, 5, 1, 15, 15))
        # Test multiple dates
        assertParse('yesterday today tomorrow', [
            datetime.datetime(2009, 4, 30, 0, 0),
            datetime.datetime(2009, 5, 1, 0, 0),
            datetime.datetime(2009, 5, 2, 0, 0),
        ])
        # Test special dates
        for stringShort, stringLong, date in specialPacks:
            assertParse(stringShort, datetime.datetime.combine(date, datetime.time(0, 0)))
            assertParse(stringLong, datetime.datetime.combine(date, datetime.time(0, 0)))

    def test_interval(self):
        self.assertEqual('1 week', whenIO.format_interval(whenIO.parse_interval('1 week 1 second')))
        self.assertEqual('2 years', whenIO.format_interval(whenIO.parse_interval('1 year 8 months'), precision=1))
        self.assertEqual('3 months 1 week', whenIO.format_interval(whenIO.parse_interval('3 months 9 days 23 hours'), precision=2))
        self.assertEqual('1 week', whenIO.format_interval(whenIO.parse_interval('200 hours'), precision=1))
        # Test edge cases
        whenIO.parse_interval('xxx hours')
