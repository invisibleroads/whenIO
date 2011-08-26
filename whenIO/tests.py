'Tests for whenIO'
import datetime
import unittest

import whenIO


offsetMinutes = 240
localToday = datetime.datetime(2009, 5, 1)
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
        self.whenIO = whenIO.WhenIO(offsetMinutes=offsetMinutes, localToday=localToday)

    def test_format(self):
        'Test that formatting works properly'
        def assertFormat(whens, whensString, **kw):
            self.assertEqual(self.whenIO.format(whens, fromUTC=False, **kw), whensString)
            if not hasattr(whens, '__iter__'):
                whens = [whens]
            self.assertEqual(self.whenIO.format([x + datetime.timedelta(minutes=offsetMinutes) for x in whens], fromUTC=True, **kw), whensString)
        # Test regular dates
        assertFormat(datetime.datetime(2009, 1, 1),         '01/01/2009 12am')
        assertFormat(datetime.datetime(2009, 1, 1, 3),      '01/01/2009 3am')
        assertFormat(datetime.datetime(2009, 1, 1, 15, 15), '01/01/2009 3:15pm')
        # Test multiple dates
        assertFormat([
            datetime.datetime(2000, 1, 1, 0, 0),
            datetime.datetime(2000, 1, 1, 1, 0),
        ], '01/01/2000 12am 1am')
        assertFormat([
            datetime.datetime(2009, 1, 1, 0, 0),
            datetime.datetime(2009, 1, 2, 0, 0),
            datetime.datetime(2009, 1, 3, 0, 0),
        ], '01/01/2009 12am, 01/02/2009 12am, 01/03/2009 12am', separator=', ')
        # Test special dates
        for stringShort, stringLong, date in specialPacks:
            if date == datetime.datetime(2009, 5, 2):
                stringLong = 'tomorrow'
            assertFormat(date, stringLong.title() + ' 12am')
        # Test custom templates
        assertFormat(datetime.datetime(2009, 1, 1), 'Thursday 20090101 12am', dateTemplate='%A %Y%m%d')
        assertFormat(datetime.datetime(2009, 5, 1), 'Today 20090501 12am', dateTemplate_=' %Y%m%d')
        # Test other input
        assertFormat([], '')

    def test_parse(self):
        'Test that parsing works properly'
        def assertParse(whensString, whens):
            if not hasattr(whens, '__iter__'):
                whens = [whens]
            self.assertEqual(self.whenIO.parse(whensString, toUTC=False)[0], whens)
            self.assertEqual(self.whenIO.parse(whensString, toUTC=True)[0], [x + datetime.timedelta(minutes=offsetMinutes) for x in whens])
        # Test regular dates
        assertParse('12am',             datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('12am text',             datetime.datetime(2009, 5, 1, 0, 0))
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

    def test_offset(self):
        'Test that we can format and parse offset properly'
        # Format
        self.assertEqual(self.whenIO.format_offset(), '-0400 UTC')
        self.assertEqual(whenIO.format_offset(-765), '+1245 UTC')
        self.assertEqual(whenIO.format_offset(-540), '+0900 UTC')
        self.assertEqual(whenIO.format_offset(-390), '+0630 UTC')
        self.assertEqual(whenIO.format_offset(-270), '+0430 UTC')
        self.assertEqual(whenIO.format_offset(   0), '+0000 UTC')
        self.assertEqual(whenIO.format_offset(+240), '-0400 UTC')
        self.assertEqual(whenIO.format_offset(+270), '-0430 UTC')
        self.assertEqual(whenIO.format_offset(+360), '-0600 UTC')
        # Parse
        self.assertEqual(whenIO.parse_offset('')[0], None)
        self.assertEqual(whenIO.parse_offset('+1245 UTC')[0], -765)
        self.assertEqual(whenIO.parse_offset('+0900 UTC')[0], -540)
        self.assertEqual(whenIO.parse_offset('+0630 UTC')[0], -390)
        self.assertEqual(whenIO.parse_offset('+0430 UTC')[0], -270)
        self.assertEqual(whenIO.parse_offset('+0000 UTC')[0],    0)
        self.assertEqual(whenIO.parse_offset('-0400 UTC')[0], +240)
        self.assertEqual(whenIO.parse_offset('-0430 UTC')[0], +270)
        self.assertEqual(whenIO.parse_offset('-0600 UTC')[0], +360)

    def test_interval(self):
        self.assertEqual('7 days', whenIO.format_interval(whenIO.parse_interval('1 week 1 second')))
        self.assertEqual('2 years', whenIO.format_interval(whenIO.parse_interval('1 year 8 months'), precision=1))
        self.assertEqual('3 months 10 days', whenIO.format_interval(whenIO.parse_interval('3 months 9 days 23 hours'), precision=2))
        self.assertEqual('8 days 8 hours', whenIO.format_interval(whenIO.parse_interval('200 hours')))
