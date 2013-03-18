1.4
---
- Added forceDate to format(), format_date()
- Replaced withStartDate to omitStartDate

1.3
---
- Changed constructor to use timezones from pytz and tzlocal
- Added weeks to format_interval()
- Added withLeadingZero to format(), format_date(), format_time()
- Added withStartDate to format()
- Removed parse_offset(), format_offset()

1.2
---
- Removed python-dateutil==1.5 requirement
- Restored test coverage to 100%

1.1
---
- Added format_interval() for formatting relativedelta objects
- Added parse_interval() for parsing text into relativedelta objects

1.0
---
- Expanded test coverage to 100%
