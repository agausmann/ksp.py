"""Calculator for in-game time and durations."""

from functools import total_ordering
from typing import Union

Number = Union[float, int]

SECONDS_PER_MINUTE = 60.0
MINUTES_PER_HOUR = 60.0
HOURS_PER_DAY = 6.0
# This is the length of the full orbit of Kerbin, but it appears that
# the "year" in timestamps is exactly 426 days.
# HOURS_PER_YEAR = 2556.5
DAYS_PER_YEAR = 426.0

SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
SECONDS_PER_DAY = SECONDS_PER_HOUR * HOURS_PER_DAY
SECONDS_PER_YEAR = SECONDS_PER_DAY * DAYS_PER_YEAR


@total_ordering
class Duration:
    """A span of in-game time.

    Example use case: Calculating the required orbital periods for a CommNet
    relay constellation deployment.

    - Goal: 6 evenly-spaced relay satellites at an 8,000 Mm circular orbit
      around Kerbol.

    - Approximate orbital period for target orbit: 201d 4h 28m 20s (grabbed
      from an ingame maneuver)

    - Approach: Bring satellites into an orbit with periapsis at 8,000 Mm and
      an orbital period that is 7/6 times the orbital period of target orbit.
      Every time the deployment craft completes 1 orbit, it has lagged behind
      the circular orbit by 1/6 of the orbital period.

    - Each time the craft reaches periapsis, detach a satellite and have it
      burn retrograde until the target orbital period is reached.

    To calculate the orbital period of the deployment craft:

    >>> relay_orbital_period = Duration(
    ...     days=201, hours=4, minutes=28, seconds=20,
    ... )
    >>> offset_orbital_period = relay_orbital_period * 7 / 6
    >>> offset_orbital_period
    235d 2h 13m 3s
    """

    _seconds: float

    def __init__(
            self,
            years: Number=0.0,
            days: Number=0.0,
            hours: Number=0.0,
            minutes: Number=0.0,
            seconds: Number=0.0
    ):
        """Create a duration from any number of different time units.

        Can be initialized with time in years, days, hours, minutes, and
        seconds using the respective keyword arguments. If multiple arguments
        are provided, then the resulting duration will be their sum.

        After computing the total duration, if the duration is negative, a
        ValueError will be raised.
        """
        self._seconds = (
            SECONDS_PER_YEAR * years
            + SECONDS_PER_DAY * days
            + SECONDS_PER_HOUR * hours
            + SECONDS_PER_MINUTE * minutes
            + seconds
        )
        if self._seconds < 0.0:
            raise ValueError('Duration can not be negative')

    @property
    def as_seconds(self) -> float:
        """The total length of the duration in seconds,
        including fractional seconds."""
        return self._seconds

    @property
    def as_minutes(self) -> float:
        """The total length of the duration in minutes,
        including fractional minutes."""
        return self._seconds / SECONDS_PER_MINUTE

    @property
    def as_hours(self) -> float:
        """The total length of the duration in hours,
        including fractional hours."""
        return self._seconds / SECONDS_PER_HOUR

    @property
    def as_days(self) -> float:
        """The total length of the duration in days,
        including fractional days."""
        return self._seconds / SECONDS_PER_DAY

    @property
    def as_years(self) -> float:
        """The total length of the duration in years,
        including fractional years."""
        return self._seconds / SECONDS_PER_YEAR

    @property
    def timestamp_seconds(self) -> int:
        """The number of whole seconds since the last whole minute.

        This does not return the total length of the duration in seconds;
        the returned number always represents a fractional portion of a minute
        (i.e., it is less than 60 seconds).
        """
        return int(self.as_seconds % SECONDS_PER_MINUTE)

    @property
    def timestamp_minutes(self) -> int:
        """The number of whole minutes since the last whole hour.

        This does not return the total length of the duration in minutes;
        the returned number always represents a fractional portion of an hour
        (i.e., it is less than 60 minutes).
        """
        return int(self.as_minutes % MINUTES_PER_HOUR)

    @property
    def timestamp_hours(self) -> int:
        """The number of whole hours since the last whole day.

        This does not return the total length of the duration in hours;
        the returned number always represents a fractional portion of a day
        (i.e., it is less than 6 hours).
        """
        return int(self.as_hours % HOURS_PER_DAY)

    @property
    def timestamp_days(self) -> int:
        """The number of whole days since the last whole year.

        This does not return the total length of the duration in days;
        the returned number always represents a fractional portion of a day
        (i.e., it is less than 426 days).
        """
        return int(self.as_days % DAYS_PER_YEAR)
    
    @property
    def timestamp_years(self) -> int:
        """The number of whole years contained in this duration."""
        return int(self.as_years)



    def __add__(self, rhs: 'Duration') -> 'Duration':
        """The sum of the lengths of the two durations."""
        return Duration(seconds=self._seconds + rhs._seconds)

    def __sub__(self, rhs: 'Duration') -> 'Duration':
        """The difference in length between the two durations.

        Note: This will raise a ValueError if rhs > self.
        """
        return Duration(seconds=self._seconds - rhs._seconds)

    def __mul__(self, rhs: Number) -> 'Duration':
        """A scaled duration created by multiplying this duration by the given
        amount."""
        return Duration(seconds=self._seconds * rhs)

    def __truediv__(self, rhs: Number) -> 'Duration':
        """A scaled duration created by dividing this duration by the given
        amount."""
        return Duration(seconds=self._seconds / rhs)

    def __eq__(self, rhs: 'Duration') -> bool:
        return self._seconds == rhs._seconds

    def __lt__(self, rhs: 'Duration') -> bool:
        return self._seconds < rhs._seconds

    def __repr__(self):
        if self.timestamp_years > 0:
            return '{}y {}d {}h {}m {}s'.format(
                self.timestamp_years,
                self.timestamp_days,
                self.timestamp_hours,
                self.timestamp_minutes,
                self.timestamp_seconds,
            )
        if self.timestamp_days > 0:
            return '{}d {}h {}m {}s'.format(
                self.timestamp_days,
                self.timestamp_hours,
                self.timestamp_minutes,
                self.timestamp_seconds,
            )
        elif self.timestamp_hours > 0:
            return '{}h {}m {}s'.format(
                self.timestamp_hours,
                self.timestamp_minutes,
                self.timestamp_seconds,
            )
        elif self.timestamp_minutes > 0:
            return '{}m {}s'.format(
                self.timestamp_minutes,
                self.timestamp_seconds,
            )
        else:
            return '{}s'.format(
                self.timestamp_seconds,
            )
