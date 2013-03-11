'Methods for formatting and parsing friendly timestamps'
import datetime
import pytz
from tzlocal import get_localzone


__all__ = [
    'WhenIO',
    'format_interval',
    'parse_interval',
]
_indexByWeekday = {
    'mon': 0, 'monday': 0,
    'tue': 1, 'tuesday': 1,
    'wed': 2, 'wednesday': 2,
    'thu': 3, 'thursday': 3,
    'fri': 4, 'friday': 4,
    'sat': 5, 'saturday': 5,
    'sun': 6, 'sunday': 6,
}
_dateTemplates = '%m/%d/%Y', '%m/%d/%y', '%m/%d'
_timeTemplates = '%I%p', '%I:%M%p'
_unitLimits = [
    ('microseconds', 1000000),
    ('seconds', 60),
    ('minutes', 60),
    ('hours', 24),
    ('days', 7),
    ('weeks', 4),
    ('months', 12),
    ('years', None),
]


class WhenIO(object):
    'Convenience class for formatting and parsing friendly timestamps'

    def __init__(self, timezone=None, today=None):
        """
        Set user-specific parameters.
        timezone    Set timezone as returned by jstz, e.g US/Eastern.
        today       Set reference date to parse special terms, e.g. Today.
        """
        self._tz = get_localzone() if not timezone else pytz.timezone(timezone)
        utcnow = datetime.datetime.utcnow()
        self._today = today.date() if today else self._to_local(utcnow).date()
        self._tomorrow = self._today + datetime.timedelta(days=1)
        self._yesterday = self._today + datetime.timedelta(days=-1)

    def format(self, whens, dateTemplate=_dateTemplates[0], dateTemplate_='', withLeadingZero=False, previousDate=None, withStartDate=True, fromUTC=True, separator=' '):
        """
        Format whens into strings.
        whens                 A timestamp or list of timestamps
        dateTemplate          Template when date is more than a week from today
        dateTemplate_         Template when date is less than a week from today
        withLeadingZero=True  Prepend leading zero
        withStartDate=True    Prepend start date
        fromUTC=True          Convert to local time before formatting
        """
        if not isinstance(whens, list):
            whens = [whens]
        if fromUTC:
            whens = map(self._to_local, whens)
        whens = sorted(whens)
        strings = []
        previousDate = None if withStartDate else whens[0].date()
        for when in whens:
            if when is None:
                continue
            if when.date() == previousDate:
                string = self.format_time(when, withLeadingZero)
            else:
                string = '%s %s' % (
                    self.format_date(when, dateTemplate, dateTemplate_, withLeadingZero),
                    self.format_time(when, withLeadingZero))
            strings.append(string)
            previousDate = when.date()
        return separator.join(strings)

    def format_date(self, date, dateTemplate=_dateTemplates[0], dateTemplate_='', withLeadingZero=False):
        """
        Format date into string.
        dateTemplate          Template when date is more than a week from today
        dateTemplate_         Template when date is less than a week from today
        withLeadingZero=True  Prepend leading zero
        """
        if isinstance(date, datetime.datetime):
            date = date.date()
        if not withLeadingZero:
            dateTemplate = dateTemplate.replace('%', '%-')
            dateTemplate_ = dateTemplate_.replace('%', '%-')
        dateString = date.strftime(dateTemplate_) if dateTemplate_ else ''
        # Format special
        if date == self._today:
            return 'Today' + dateString
        elif date == self._tomorrow:
            return 'Tomorrow' + dateString
        elif date == self._yesterday:
            return 'Yesterday' + dateString
        # Format weekday
        differenceInDays = (date - self._today).days
        if differenceInDays <= 7 and differenceInDays > 0:
            return date.strftime('%A') + dateString
        return date.strftime(dateTemplate)

    def format_time(self, time, withLeadingZero=False):
        'Format time into string'
        if isinstance(time, datetime.datetime):
            time = time.time()
        timeTemplate = _timeTemplates[1] if time.minute else _timeTemplates[0]
        if not withLeadingZero:
            timeTemplate = timeTemplate.replace('%', '%-')
        return time.strftime(timeTemplate).lower()

    def parse(self, whensString, toUTC=True):
        """
        Parse whens from strings.
        whensString  A string of timestamps
        toUTC=True   Convert whens to UTC after parsing
        toUTC=False  Parse whens without conversion
        """
        whens, terms = [], []
        for term in whensString.split():
            # Try to parse the term as a date
            date = self.parse_date(term)
            if date is not None:
                if date not in whens:
                    whens.append(date)
                continue  # pragma: no cover
            # Try to parse the term as a time
            time = self.parse_time(term)
            if time is not None:
                oldWhen = whens[-1] if whens else None
                newWhen = self._combine_date_time(oldWhen, time)
                # If oldWhen already has a time or we have no whens, append newWhen
                if isinstance(oldWhen, datetime.datetime) or not whens:
                    whens.append(newWhen)
                # If oldWhen did not have a time, replace oldWhen
                else:
                    whens[-1] = newWhen
                continue
            # If it is neither a date nor a time, save it
            if term not in terms:
                terms.append(term)
        # Make sure every when has a time
        for whenIndex, when in enumerate(whens):
            if not isinstance(when, datetime.datetime):
                whens[whenIndex] = self._combine_date_time(when, whenTime=None)
        if toUTC:
            whens = map(self._from_local, whens)
        return sorted(whens), terms

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
        elif dateString in _indexByWeekday:
            difference = _indexByWeekday[dateString] - self._today.weekday()
            if difference <= 0:
                difference += 7
            return self._today + datetime.timedelta(days=difference)
        # Parse date
        for template in _dateTemplates:
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
        for template in _timeTemplates:
            try:
                time = datetime.datetime.strptime(timeString, template).time()
            except (ValueError, TypeError):
                pass
            else:
                return time

    # Helpers

    def _combine_date_time(self, whenDate, whenTime=None):
        'Create when from date and time, assuming where necessary'
        # If both terms are present, combine them
        if whenTime is not None and whenDate:
            return datetime.datetime.combine(whenDate, whenTime)
        # If only the time is present,
        if whenTime is not None:
            return datetime.datetime.combine(self._today, whenTime)
        # If only the date is present,
        if whenDate:
            return datetime.datetime.combine(whenDate, datetime.time(0, 0))

    def _from_local(self, when):
        'Convert local time into UTC'
        if when:
            return self._tz.localize(when).astimezone(pytz.utc).replace(tzinfo=None)

    def _to_local(self, when):
        'Convert UTC into local time '
        if when:
            return pytz.utc.localize(when).astimezone(self._tz).replace(tzinfo=None)


def format_interval(rdelta, precision=0):
    'Format a relativedelta object rounded to the given precision'
    packs = []
    valueByUnit = _serialize_relativedelta(rdelta)
    unitLimitsReversed = list(reversed(_unitLimits))
    precisionIndex = 0
    for unitIndex, (unit, limit) in enumerate(unitLimitsReversed):
        value = valueByUnit.get(unit)
        if not value:
            if packs:
                break
            continue  # pragma: no cover
        packs.append([value, unit])
        precisionIndex += 1
        if precision and precisionIndex >= precision:
            # Look at the next value and round up if necessary
            nextUnit, nextLimit = unitLimitsReversed[unitIndex + 1]
            nextValue = valueByUnit.get(nextUnit, 0)
            if nextValue > nextLimit / 2:
                packs[-1][0] += 1
            break
    # Format terms with appropriate plurality
    return ' '.join('%i %s' % (value, unit if abs(value) != 1 else unit[:-1]) for value, unit in packs)


def parse_interval(text):
    'Parse a relativedelta object from a string'
    from dateutil.relativedelta import relativedelta
    units = ['years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds']
    terms = text.split()
    valueByUnit = {}
    for termIndex, term in enumerate(terms[1:], 1):
        if not term.endswith('s'):
            term += 's'
        if term in units:
            try:
                value = int(terms[termIndex - 1])
            except ValueError:
                continue
            valueByUnit[term] = value
    return relativedelta(**valueByUnit)


def _serialize_relativedelta(rdelta):
    'Use larger units when possible and introduce new units'
    valueByUnit = {}
    for index, (unit, limit) in enumerate(_unitLimits):
        try:
            value = valueByUnit.get(unit, 0) + getattr(rdelta, unit)
        except AttributeError:
            continue
        if limit and value >= limit:
            nextUnit = _unitLimits[index + 1][0]
            nextValue = valueByUnit.get(nextUnit, 0)
            valueByUnit[nextUnit] = nextValue + value / limit
            value = value % limit
        if value:
            valueByUnit[unit] = value
    return valueByUnit
