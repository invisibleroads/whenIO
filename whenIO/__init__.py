'Methods for formatting and parsing friendly timestamps'
import datetime
import pytz
import re
from tzlocal import get_localzone


__all__ = [
    'WhenIO',
    'format_duration',
    'parse_duration',
]
_INDEX_BY_WEEKDAY = {
    'mon': 0, 'monday': 0,
    'tue': 1, 'tuesday': 1,
    'wed': 2, 'wednesday': 2,
    'thu': 3, 'thursday': 3,
    'fri': 4, 'friday': 4,
    'sat': 5, 'saturday': 5,
    'sun': 6, 'sunday': 6,
}
_DATE_TEMPLATES = '%m/%d/%Y', '%m/%d/%y', '%m/%d'
_TIME_TEMPLATES = '%I%p', '%I:%M%p'
_UNIT_LIMITS = [
    ('microseconds', 1000000),
    ('seconds', 60),
    ('minutes', 60),
    ('hours', 24),
    ('days', 7),
    ('weeks', 4),
    ('months', 12),
    ('years', None),
]
_UNIT_WORDS = (
    'year', 'month', 'week', 'day', 'hour', 'minute', 'second', 'microsecond')
_UNIT_ABBREVIATIONS = 'yr', 'mo', 'wk', 'dy', 'hr', 'min', 'sec', 'usec'
_UNIT_LETTERS = 'y', 'l', 'w', 'd', 'h', 'm', 's', 'u'


class WhenIO(object):
    'Convenience class for formatting and parsing friendly timestamps'

    def __init__(
            self, timezone=None, today=None, default_time=datetime.time()):
        """Set user-specific parameters.
        timezone    Set timezone as returned by jstz, e.g US/Eastern.
        today       Set reference date to parse special terms, e.g. Today.
        """
        utcnow = datetime.datetime.utcnow()
        self._tz = get_localzone() if not timezone else pytz.timezone(timezone)
        self._today = today.date() if today else self._to_local(utcnow).date()
        self._tomorrow = self._today + datetime.timedelta(days=1)
        self._yesterday = self._today + datetime.timedelta(days=-1)
        self._default_time = default_time

    def format(
            self, timestamps, dateTemplate=_DATE_TEMPLATES[0],
            withLeadingZero=False, omitStartDate=False, forceDate=False,
            fromUTC=True, separator=' '):
        """Format timestamps into strings.
        timestamps            A timestamp or list of timestamps
        dateTemplate          Template when date is more than a week away
        withLeadingZero=True  Prepend leading zero
        omitStartDate=True    Omit start date
        forceDate=True        Show date even when it is less than a week away
        fromUTC=True          Convert to local time before formatting
        separator=' - '       Specify a custom separator between timestamps
        """
        if not isinstance(timestamps, list):
            timestamps = [timestamps]
        if fromUTC:
            timestamps = map(self._to_local, timestamps)
        timestamps = sorted(filter(lambda _: _, timestamps))
        strings = []
        previousDate = timestamps[0].date() if omitStartDate else None
        for timestamp in timestamps:
            if timestamp.date() == previousDate:
                string = self.format_time(timestamp, withLeadingZero)
            else:
                string = '%s %s' % (
                    self.format_date(
                        timestamp, dateTemplate, withLeadingZero, forceDate),
                    self.format_time(timestamp, withLeadingZero))
            strings.append(string)
            previousDate = timestamp.date()
        return separator.join(strings)

    def format_date(
            self, date, dateTemplate=_DATE_TEMPLATES[0],
            withLeadingZero=False, forceDate=False):
        """Format date into string.
        dateTemplate          Template when date is more than a week away
        withLeadingZero=True  Prepend leading zero
        forceDate=True        Show date even when it is less than a week away
        """
        if isinstance(date, datetime.datetime):
            date = date.date()
        if not withLeadingZero:
            dateTemplate = dateTemplate.replace('%', '%-')
        dateString_ = date.strftime(dateTemplate)
        dateString = ' ' + dateString_ if forceDate else ''
        differenceInDays = (date - self._today).days
        if date == self._today:
            return 'Today' + dateString
        elif date == self._tomorrow:
            return 'Tomorrow' + dateString
        elif date == self._yesterday:
            return 'Yesterday' + dateString
        elif differenceInDays <= 7 and differenceInDays > 0:
            return date.strftime('%A') + dateString
        else:
            return dateString_

    def format_time(self, time, withLeadingZero=False):
        'Format time into string'
        if isinstance(time, datetime.datetime):
            time = time.time()
        if time.minute:
            timeTemplate = _TIME_TEMPLATES[1]
        else:
            timeTemplate = _TIME_TEMPLATES[0]
        if not withLeadingZero:
            timeTemplate = timeTemplate.replace('%', '%-')
        return time.strftime(timeTemplate).lower()

    def parse(self, text, toUTC=True):
        """Parse timestamps from strings.
        text         A string of timestamps
        toUTC=True   Convert timestamps to UTC after parsing
        toUTC=False  Parse timestamps without conversion
        """
        timestamps, scraps = [], []
        for term in text.split():
            # Try to parse the term as a date
            date = self.parse_date(term)
            if date is not None:
                if date not in timestamps:
                    timestamps.append(date)
                continue  # pragma: no cover
            # Try to parse the term as a time
            time = self.parse_time(term)
            if time is not None:
                oldTimestamp = timestamps[-1] if timestamps else None
                newTimestamp = self._combine_date_time(oldTimestamp, time)
                if isinstance(
                        oldTimestamp, datetime.datetime) or not timestamps:
                    timestamps.append(newTimestamp)
                else:
                    timestamps[-1] = newTimestamp
                continue
            # If it is neither a date nor a time, save it
            if term not in scraps:
                scraps.append(term)
        # Make sure every timestamp has a time
        for index, timestamp in enumerate(timestamps):
            if not isinstance(timestamp, datetime.datetime):
                timestamps[index] = self._combine_date_time(timestamp)
        if toUTC:
            timestamps = map(self._from_local, timestamps)
        return sorted(timestamps), scraps

    def parse_date(self, dateString):
        'Parse date from a string'
        dateString = dateString.strip().lower()
        # Look for special terms
        if dateString in ('today', 'tod'):
            return self._today
        elif dateString in ('tomorrow', 'tom'):
            return self._tomorrow
        elif dateString in ('yesterday', 'yes'):
            return self._yesterday
        elif dateString in _INDEX_BY_WEEKDAY:
            difference = _INDEX_BY_WEEKDAY[dateString] - self._today.weekday()
            if difference <= 0:
                difference += 7
            return self._today + datetime.timedelta(days=difference)
        # Parse date
        for template in _DATE_TEMPLATES:
            try:
                date = datetime.datetime.strptime(dateString, template).date()
            except (ValueError, TypeError):
                pass
            else:
                if date.year == 1900:
                    date = date.replace(year=self._today.year)
                return date

    def parse_time(self, timeString):
        'Parse time from a string'
        timeString = timeString.strip().lower()
        # Parse time
        for template in _TIME_TEMPLATES:
            try:
                time = datetime.datetime.strptime(timeString, template).time()
            except (ValueError, TypeError):
                pass
            else:
                return time

    # Helpers

    def _combine_date_time(self, date, time=None):
        'Create timestamp from date and time, assuming where necessary'
        # If both terms are present, combine them
        if time is not None and date:
            return datetime.datetime.combine(date, time)
        # If only the time is present,
        if time is not None:
            return datetime.datetime.combine(self._today, time)
        # If only the date is present,
        if date:
            return datetime.datetime.combine(date, self._default_time)

    def _from_local(self, timestamp):
        'Convert local time into UTC'
        if timestamp:
            return self._tz.localize(
                timestamp).astimezone(pytz.utc).replace(tzinfo=None)

    def _to_local(self, timestamp):
        'Convert UTC into local time '
        if timestamp:
            return pytz.utc.localize(
                timestamp).astimezone(self._tz).replace(tzinfo=None)


def format_duration(rdelta, precision=0, style='words', rounding='ceiling'):
    """Format a relativedelta object rounded to the given precision.

    Set style='abbreviations' to abbreviate units.
    Set style='letters' to abbreviate to one letter.

    Set rounding='floor' to truncate.
    Set rounding='round' to round up.
    """
    packs = []
    valueByUnit = _serialize_relativedelta(rdelta)
    unitLimitsReversed = list(reversed(_UNIT_LIMITS))
    units = {
        'words': _UNIT_WORDS,
        'abbreviations': _UNIT_ABBREVIATIONS,
        'letters': _UNIT_LETTERS,
    }[style]
    get_adjustment = {
        'ceiling': lambda value, limit: 1 if value else 0,
        'floor': lambda value, limit: 0,
        'round': lambda value, limit: 1 if value > limit // 2 else 0,
    }[rounding]
    padding = '' if style == 'letters' else ' '
    precisionIndex = 0
    for unitIndex, (unit, limit) in enumerate(unitLimitsReversed):
        value = valueByUnit.get(unit)
        if not value:
            continue  # pragma: no cover
        packs.append([value, padding + units[unitIndex]])
        precisionIndex += 1
        if precision and precisionIndex >= precision:
            # Look at the next value and adjust if necessary
            nextUnit, nextLimit = unitLimitsReversed[unitIndex + 1]
            nextValue = valueByUnit.get(nextUnit, 0)
            packs[-1][0] += get_adjustment(nextValue, nextLimit)
            break
    # Format terms with appropriate plurality
    return ' '.join('%i%s' % (
        value,
        unit + 's' if len(unit) > 1 and abs(value) != 1 else unit,
    ) for value, unit in packs)


def _serialize_relativedelta(rdelta):
    'Use larger units when possible and introduce new units'
    valueByUnit = {}
    for index, (unit, limit) in enumerate(_UNIT_LIMITS):
        value = valueByUnit.get(unit, 0)
        if unit != 'weeks':
            value += getattr(rdelta, unit, 0)
        if limit and value >= limit:
            nextUnit = _UNIT_LIMITS[index + 1][0]
            nextValue = valueByUnit.get(nextUnit, 0)
            valueByUnit[nextUnit] = nextValue + value // limit
            value = value % limit
        valueByUnit[unit] = value
    return valueByUnit


def parse_duration(text):
    'Parse a relativedelta object from a string'
    from dateutil.relativedelta import relativedelta
    terms = re.sub(r'([0-9])([A-Za-z])', r'\1 \2', text).split()
    valueByUnit = {}
    for termIndex, term in enumerate(terms):
        try:
            nextTerm = terms[termIndex + 1]
        except IndexError:
            break
        try:
            value = int(term)
            unit = _get_unit(nextTerm) + 's'
        except ValueError:
            continue
        if value:  # Ignore zero
            valueByUnit[unit] = value
    if valueByUnit:
        return relativedelta(**valueByUnit)


def _get_unit(term):
    try:
        return _UNIT_WORDS[_UNIT_LETTERS.index(term)]
    except ValueError:
        pass
    term = term.rstrip('s')
    try:
        return _UNIT_WORDS[_UNIT_ABBREVIATIONS.index(term)]
    except ValueError:
        pass
    return _UNIT_WORDS[_UNIT_WORDS.index(term)]
