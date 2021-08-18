"""
files.py: File access functions.

TODO: Progress callback for `get_doc()` (separate from the `callback` argument
 of `idelib.importer.openFile()` and `idelib.importer.readData()`?)
TODO: Exception subclasses for `get_doc()` failures, to separate the function's
 own errors from `ValueError` exceptions raised by things the function calls?
"""
import os
import tempfile
from urllib.parse import urlparse

from idelib.importer import openFile, readData
import requests

from .gdrive import gdrive_download
from .util import validate

__all__ = ['get_doc']

# ============================================================================
#
# ============================================================================


def _get_url(url, localfile=None, params=None, cookies=None):
    """
    Retrieve an IDE from a (HTTP/HTTPS) URL, including Google Drive shared
    links.

    :param url: The file's URL.
    :param localfile: The local filename (if saving the file).
    :param params: Additional (optional) request parameters.
    :param cookies: Optional browser cookies for the session.
    :return: An open file stream containing the IDE data and the number of
        bytes downloaded.
    """
    parsed_url = urlparse(url)
    session = requests.Session()

    netloc = parsed_url.netloc.lower()
    if netloc.endswith('.google.com') or netloc == "google.com":
        response, filename = gdrive_download(url, localfile, params=params, cookies=cookies)
    else:
        response = session.get(parsed_url.geturl(), params=params, cookies=cookies)
        filename = None

    if not response.ok:
        raise ValueError(f"Could not retrieve data from URL {url} "
                         f"({response.status_code}: {response.reason})")

    if localfile is None:
        stream = tempfile.SpooledTemporaryFile(suffix=".ide")
    else:
        localfile = os.path.abspath(os.path.expanduser(localfile))
        if os.path.isdir(localfile):
            if not filename:
                filename = os.path.basename(parsed_url.path)
            localfile = os.path.join(localfile, filename)
        if not localfile.lower().endswith('.ide'):
            localfile += ".ide"
        stream = open(localfile, 'w+b')

    total = 0
    for chunk in response.iter_content(2**15):
        # future: Confirm that this is an IDE from 1st chunk, avoiding download if not
        if chunk:
            stream.write(chunk)
            total += len(chunk)

    response.close()
    stream.seek(0)

    return stream, total


# ============================================================================
#
# ============================================================================

def get_doc(name=None, filename=None, url=None, parsed=True,
            localfile=None, params=None, cookies=None, **kwargs):
    """
    Retrieve an IDE file from either a file or URL.

    Note: `name`, `filename`, and `url` are mutually exclusive arguments.
    One and only one must be specified. Attempting to supply more than one
    will generate an error.

    Example usage:
    ```
    get_doc("my_recording.ide")
    get_doc("https://example.com/remote_recording.ide")
    get_doc(filename="my_recording.ide")
    get_doc(url="https://example.com/remote_recording.ide")
    ```

    :param name: The name or URL of the IDE. The method of fetching it will
        be automatically chosen based on how it is formatted.
    :param filename: The name of an IDE file. Supplying a name this way will
        force it to be read from a file, avoiding the possibility of
        accidentally trying to retrieve it via URL.
    :param url: The URL of an IDE file. Supplying a name this way will force
        it to be read from a URL, avoiding the possibility of accidentally
        trying to retrieve it from a local file.
    :param parsed: If `True` (default), the IDE will be fully parsed after it
        is fetched. If `False`, only the file metadata will be initially
        loaded, and a call to `idelib.importer.readData()`. This can save
        time.
    :param localfile: The name of the file to which to write data recieved
        from a URL. If none is supplied, a temporary file will be used. Only
        applicable when opening a URL.
    :param params: Additional URL request parameters. Only applicable when
        opening a URL.
    :param cookies: Additional browser cookies for use in the URL request.
        Only applicable when opening a URL.
    :return: The fetched IDE data.

    Additionally, `get_doc()` will accept the keyword arguments for
    `idelib.importer.importFile()` or `idelib.importer.openFile()`
    """
    if len([x for x in (name, filename, url) if x]) != 1:
        raise TypeError("Only one source can be specified: name, filename, or url")

    original = name or filename or url  # For error reporting
    stream = None
    parsed_url = None

    if name:
        if os.path.isfile(name):
            filename = name
        else:
            parsed_url = urlparse(name.replace('\\', '/'))
            if not parsed_url.scheme or parsed_url.scheme == "file":
                filename = parsed_url.path
            else:
                url = name

    if filename:
        filename = os.path.abspath(os.path.expanduser(filename))
        stream = open(filename, 'rb')

    elif url:
        kwargs.setdefault('name', url)
        parsed_url = parsed_url or urlparse(url)
        if parsed_url.scheme.startswith('http'):
            stream, _total = _get_url(url, localfile=localfile, params=params, cookies=cookies)
        else:
            # future: more fetching schemes before this `else` (ftp, etc.)?
            raise ValueError(f"Unsupported transfer scheme: {parsed_url.scheme}")

    if stream:
        if not validate(stream):
            stream.close()
            raise ValueError(f"Could not read a Dataset from '{original}'"
                             f"(not an IDE file?)")

        doc = openFile(stream, **kwargs)

        if parsed:
            readData(doc, **kwargs)

        return doc

    raise ValueError(f"Could not read data from '{original}'")

