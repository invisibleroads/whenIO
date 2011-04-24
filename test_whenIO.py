'Tests for whenIO'
import datetime
import unittest

import whenIO


# Setup
minutesOffset = 240
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


class TestWhenIO(unittest.TestCase):

    def setUp(self):
        self.whenIO = whenIO.WhenIO(minutesOffset=minutesOffset, localToday=localToday)

    def test_format(self):
        'Test that formatting works properly'
        def assertFormat(whens, whensString, **kw):
            if not hasattr(whens, '__iter__'):
                whens = [whens]
            self.assertEqual(self.whenIO.format(whens, fromUTC=False, **kw), whensString)
            self.assertEqual(self.whenIO.format([x + datetime.timedelta(minutes=minutesOffset) for x in whens], fromUTC=True, **kw), whensString)
        # Test regular dates
        assertFormat(datetime.datetime(2009, 1, 1),         '01/01/2009 12am')
        assertFormat(datetime.datetime(2009, 1, 1, 3),      '01/01/2009 3am')
        assertFormat(datetime.datetime(2009, 1, 1, 15, 15), '01/01/2009 3:15pm')
        # Test multiple dates
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

    def test_parse(self):
        'Test that parsing works properly'
        def assertParse(whensString, whens):
            if not hasattr(whens, '__iter__'):
                whens = [whens]
            self.assertEqual(self.whenIO.parse(whensString, toUTC=False)[0], whens)
            self.assertEqual(self.whenIO.parse(whensString, toUTC=True)[0], [x + datetime.timedelta(minutes=minutesOffset) for x in whens])
        # Test regular dates
        assertParse('5/1',             datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('5/1/09',          datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('5/1/2009',        datetime.datetime(2009, 5, 1, 0, 0))
        assertParse('5/1/2009 3am',    datetime.datetime(2009, 5, 1, 3, 0))
        assertParse('5/1/2009 3:15pm', datetime.datetime(2009, 5, 1, 15, 15))
        # Test multiple dates
        assertParse('yesterday today tomorrow',     [
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
        assert whenIO.format_offset(-765) == '+1245 UTC'
        assert whenIO.format_offset(-540) == '+0900 UTC'
        assert whenIO.format_offset(-390) == '+0630 UTC'
        assert whenIO.format_offset(-270) == '+0430 UTC'
        assert whenIO.format_offset(   0) == '+0000 UTC'
        assert whenIO.format_offset(+240) == '-0400 UTC'
        assert whenIO.format_offset(+270) == '-0430 UTC'
        assert whenIO.format_offset(+360) == '-0600 UTC'
        # Parse
        assert whenIO.parse_offset('+1245 UTC')[0] == -765
        assert whenIO.parse_offset('+0900 UTC')[0] == -540
        assert whenIO.parse_offset('+0630 UTC')[0] == -390
        assert whenIO.parse_offset('+0430 UTC')[0] == -270
        assert whenIO.parse_offset('+0000 UTC')[0] ==    0
        assert whenIO.parse_offset('-0400 UTC')[0] == +240
        assert whenIO.parse_offset('-0430 UTC')[0] == +270
        assert whenIO.parse_offset('-0600 UTC')[0] == +360
