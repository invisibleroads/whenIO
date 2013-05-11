1.5
---
- Added unit abbreviations and letters to parse_duration(), format_duration()
- Added control over rounding behavior to format_duration()

1.4
---
- Added forceDate to format(), format_date()
- Replaced withStartDate to omitStartDate

1.3
---
- Changed constructor to use timezones from pytz and tzlocal
- Added weeks to format_duration()
- Added withLeadingZero to format(), format_date(), format_time()
- Added withStartDate to format()
- Removed parse_offset(), format_offset()

1.2
---
- Removed python-dateutil==1.5 requirement
- Restored test coverage to 100%

1.1
---
- Added format_duration() for formatting relativedelta objects
- Added parse_duration() for parsing text into relativedelta objects

1.0
---
- Expanded test coverage to 100%
