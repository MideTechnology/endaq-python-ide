from datetime import timedelta
import os.path
import unittest

from idelib.importer import importFile
from endaq.ide import info, measurement


IDE_FILENAME = os.path.join(os.path.dirname(__file__), "test.ide")


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
        # XXX: Implement additional get_channel_table() tests
        ct = info.get_channel_table(self.dataset)

        self.assertEqual(len(ct.data), len(self.dataset.getPlots()),
                         "Length of table's data did not match number of subchannels in IDE")


if __name__ == '__main__':
    unittest.main()
