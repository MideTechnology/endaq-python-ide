import os.path
import unittest

from idelib.dataset import Dataset
from endaq.ide import files


IDE_FILENAME = os.path.join(os.path.dirname(__file__), "test.ide")
IDE_LOCAL_URL = "file://" + IDE_FILENAME.replace('\\', '/')


class GetDocTests(unittest.TestCase):

    def test_get_doc_basics(self):
        doc = files.get_doc(IDE_FILENAME)
        self.assertIsInstance(doc, Dataset, "get_doc() did not return a Dataset")
        self.assertRaises(TypeError, files.get_doc, (), {})
        self.assertRaises(TypeError, files.get_doc, (IDE_FILENAME), {'url': IDE_LOCAL_URL})
        self.assertRaises(TypeError, files.get_doc, (), {'filename': IDE_FILENAME, 'url': IDE_LOCAL_URL})


    def test_get_doc_files(self):
        """ Test basic opening of a file from a filename. """
        # The baseline file
        doc1 = files.get_doc(IDE_FILENAME)

        # Verify `name` and `filename` parameters equivalent
        doc2 = files.get_doc(filename=IDE_FILENAME)
        self.assertEqual(doc1.filename, doc2.filename)

        # Verify a "file:" URL (with forward slashes) translates
        doc3 = files.get_doc(IDE_LOCAL_URL)
        self.assertEqual(doc1.filename, doc3.filename)

        # Verify a "file:" URL (with Windows delimiter) translates
        if "\\" in IDE_FILENAME:
            doc4 = files.get_doc( "file://" + IDE_FILENAME)
            self.assertEqual(doc1.filename, doc4.filename)

        # Verify validation
        self.assertRaises(ValueError, files.get_doc, (__file__), {})


    def test_get_doc_url(self):
        """ Test getting an IDE from a URL (HTTP/HTTPS). """
        print("test_get_doc_url() Not implemented!")


    def test_get_doc_gdrive(self):
        """ Test getting an IDE from a Google Drive URL. """
        print("test_get_doc_gdrive() Not implemented!")


if __name__ == '__main__':
    unittest.main()
