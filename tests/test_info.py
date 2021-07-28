from datetime import datetime, timedelta
import os.path

import pytest
from idelib.importer import importFile
from endaq.ide import info


@pytest.fixture
def dataset():
    with importFile(os.path.join("tests", "test.ide")) as ds:
        yield ds


class TestTimeParse:
    """ Test the time parsing function.
    """
    def test_parse_time(self):
        """ Test basic handling of non-strings. """
        assert info.parse_time(None) is None
        assert info.parse_time("") is None
        assert info.parse_time(42) == 42
        with pytest.raises(TypeError):
            info.parse_time([1])


    def test_parse_time_str(self):
        """ Test time string parsing. """
        assert info.parse_time("11") == 11 * 10**6
        assert info.parse_time("22:11") == 1331000000
        assert info.parse_time("3:22:11") == 12131000000
        assert info.parse_time("1d 3:22:11") == 98531000000
        with pytest.raises(ValueError):
            info.parse_time("bogus")


    def test_parse_time_datetime(self):
        """ Test `datetime.datetime` and `datetime.timedelta` parsing. """
        t1 = datetime(2021, 7, 8, 11, 28, 40, 800752)
        t2 = datetime(2021, 7, 7, 0, 0)
        td = timedelta(days=1, seconds=2345, microseconds=6789)

        assert info.parse_time(td) == td.total_seconds() * 10**6
        assert info.parse_time(t1 - t2) == 127720.800752 * 10**6
        assert info.parse_time(t1, t2) == 127720.800752 * 10**6


class TestChannelTableFormatting:
    """ Test the individual column value formatting functions.
    """
    def test_format_channel_id(self, dataset):
        assert info.format_channel_id(dataset.channels[59]) == '59.*'
        assert info.format_channel_id(dataset.channels[59][0]) == '59.0'

        assert info.format_channel_id(None) == "None"


    def test_format_timedelta(self):
        # Note: only the start of strings is checked in order to avoid
        # differences in selected number of significant digits
        td = timedelta(seconds=0)
        assert info.format_timedelta(td).startswith('00:00.')

        td = timedelta(seconds=1623430749.8969631)
        assert info.format_timedelta(td).startswith('18789d 16:59:09.')

        # Number instead of timedelta. Unlikely but not not impossible.
        assert info.format_timedelta(100000000).startswith('01:40.')
        assert info.format_timedelta(None) == "None"


    def test_format_timestamp(self):
        for i in range(0, 10000, 123):
            assert info.format_timestamp(i).startswith(str(i))
            assert info.format_timestamp(str(i)).startswith(str(i))

        assert info.format_timestamp('bogus') == 'bogus'
        assert info.format_timestamp(None) == "None"


class TestChannelTable:
    """ Test the "channel table" generating functionality
    """
    def test_get_channel_table(self, dataset):
        # TODO: Implement additional get_channel_table() tests?
        ct = info.get_channel_table(dataset)

        assert len(ct.data) == len(dataset.getPlots()), \
               "Length of table's data did not match number of subchannels in IDE"


    def test_channel_table_ranges(self, dataset):
        # Exclude channels with extremely low sample rates
        # TODO: change acceptable delta based on sample rate
        MIN_RATE = 10  # Hz

        # Test with a specified start
        ct1 = info.get_channel_table(dataset, start="2s")
        for n, t in enumerate(ct1.data['start']):
            if ct1.data['rate'][n] < MIN_RATE:
                continue
            assert pytest.approx(t / 10**6, 2), f"{ct1.data['channel'][n]}"

        # Test with a specified end
        ct2 = info.get_channel_table(dataset, end="10s")
        for n, t in enumerate(ct2.data['end']):
            if ct1.data['rate'][n] < MIN_RATE:
                continue
            assert pytest.approx(t / 10**6, 10), f"{ct2.data['channel'][n]}"

        # Test with both start and end specified
        ct3 = info.get_channel_table(dataset, start="2s", end="10s")
        assert list(ct3.data['start']) == list(ct1.data['start'])
        assert list(ct3.data['end']) == list(ct2.data['end'])
