from datetime import datetime, timedelta
import os.path
import unittest

from idelib.importer import importFile
from endaq.ide import info


IDE_FILENAME = os.path.join(os.path.dirname(__file__), "test.ide")


class TimeParseTest(unittest.TestCase):
    """ Test the time parsing function.
    """
    def test_parse_time(self):
        """ Test basic handling of non-strings. """
        self.assertEqual(info.parse_time(None), None)
        self.assertEqual(info.parse_time(""), None)
        self.assertEqual(info.parse_time(42), 42)
        self.assertRaises(TypeError, lambda *x: info.parse_time([1]),
                          "parse_time() accepted a bad type (list)")


    def test_parse_time_str(self):
        """ Test time string parsing. """
        self.assertEqual(info.parse_time("42"), 42 * 10**6)
        self.assertEqual(info.parse_time("22:11"), 1331000000)
        self.assertEqual(info.parse_time("3:22:11"), 1511000000)
        self.assertEqual(info.parse_time("1d 3:22:11"), 1535000000)
        self.assertRaises(ValueError, lambda *x: info.parse_time("bogus"),
                          "parse_time() accepted a bad string")


    def test_parse_time_datetime(self):
        """ Test `datetime.datetime` and `datetime.timedelta` parsing. """
        t1 = datetime(2021, 7, 8, 11, 28, 40, 800752)
        t2 = datetime(2021, 7, 7, 0, 0)
        td = timedelta(days=1, seconds=2345, microseconds=6789)

        self.assertEqual(info.parse_time(td), td.total_seconds() * 10**6)
        self.assertEqual(info.parse_time(t1 - t2), 127720.800752 * 10**6)
        self.assertEqual(info.parse_time(t1, t2), 127720.800752 * 10**6)


class ChannelTableFormattingTests(unittest.TestCase):
    """ Test the individual column value formatting functions.
    """

    def test_format_channel_id(self):
        dataset = importFile(IDE_FILENAME)
        self.assertEqual(info.format_channel_id(dataset.channels[59]), '59.*')
        self.assertEqual(info.format_channel_id(dataset.channels[59][0]), '59.0')

        self.assertEqual(info.format_channel_id(None), "None")


    def test_format_timedelta(self):
        # Note: only the start of strings is checked in order to avoid
        # differences in selected number of significant digits
        td = timedelta(seconds=0)
        self.assertTrue(info.format_timedelta(td).startswith('00:00.'))

        td = timedelta(seconds=1623430749.8969631)
        self.assertTrue(info.format_timedelta(td).startswith('18789d 16:59:09.'))

        # Number instead of timedelta. Unlikely but not not impossible.
        self.assertTrue(info.format_timedelta(100000000).startswith('01:40.'))
        self.assertEqual(info.format_timedelta(None), "None")


    def test_format_timestamp(self):
        for i in range(0, 10000, 123):
            self.assertTrue(info.format_timestamp(i).startswith(str(i)))
            self.assertTrue(info.format_timestamp(str(i)).startswith(str(i)))

        self.assertEqual(info.format_timestamp('bogus'), 'bogus')
        self.assertEqual(info.format_timestamp(None), "None")


class ChannelTableTests(unittest.TestCase):
    """ Test the "channel table" generating functionality
    """
    def setUp(self):
        self.dataset = importFile(IDE_FILENAME)

    def test_get_channel_table(self):
        # TODO: Implement additional get_channel_table() tests?
        ct = info.get_channel_table(self.dataset)

        self.assertEqual(len(ct.data), len(self.dataset.getPlots()),
                         "Length of table's data did not match number of subchannels in IDE")


if __name__ == '__main__':
    unittest.main()
