import os.path

import pytest
from idelib.importer import importFile
from endaq.ide import measurement


@pytest.fixture
def dataset():
    with importFile(os.path.join("tests", "test.ide")) as ds:
        yield ds


@pytest.fixture
def types():
    return [m for m in measurement.__dict__.values() if isinstance(m, measurement.MeasurementType)]


class TestMeasurementTypes:
    """ Basic tests of the MeasurementType class and constant instances.
    """

    def test_uniqueness(self):
        # Trying to instantiate a duplicate MeasurementType should return the original instance
        FOO = measurement.MeasurementType("Foo", "foo")
        BAR = measurement.MeasurementType("Foo", "foo")
        assert FOO == BAR
        assert FOO is BAR

        # Again, this time testing against one predefined in the module
        ACCEL = measurement.MeasurementType("Acceleration", "acc")
        assert ACCEL == measurement.ACCELERATION
        assert ACCEL is measurement.ACCELERATION


    def test_comp(self, types):
        # Test that all predefined MeasurementTypes are equal to their string equivalents
        for mt in types:
            assert mt == str(mt), f"{mt!r} not equal to string '{mt}'"


    def test_strings(self):
        # Adding MeasurementTypes concatenates their strings
        assert (measurement.ACCELERATION + measurement.PRESSURE
                == f"{measurement.ACCELERATION} {measurement.PRESSURE}")

        # Negating creates a string prefixed by ``"-"``
        assert -measurement.ACCELERATION == f"-{measurement.ACCELERATION}"

        assert (measurement.ACCELERATION - measurement.PRESSURE
                == f"{measurement.ACCELERATION} -{measurement.PRESSURE}")



class TestGetByType:
    """ Test the functions that retrieve `Channel` and/or `SubChannel` objects by
        measurement type from an IDE file (`idelib.dataset.Dataset`).
    """

    def test_get_measurement_type(self, dataset):
        assert (measurement.get_measurement_type(dataset.channels[32][0])
                == measurement.ACCELERATION)
        assert (measurement.get_measurement_type(dataset.channels[80])
                == [measurement.ACCELERATION]*3)


    def test_split_types(self):
        inc, exc = measurement.split_types("*")
        assert len(measurement.MeasurementType.types) == len(inc)
        assert len(exc) == 0

        inc, exc = measurement.split_types(measurement.ACCELERATION + measurement.PRESSURE - measurement.LIGHT)
        assert measurement.ACCELERATION in inc
        assert measurement.PRESSURE in inc
        assert measurement.LIGHT in exc
        assert measurement.LIGHT not in inc
        assert measurement.PRESSURE not in exc


    def test_filter_channels(self, dataset):
        """ Test filter_channels() filtering of Channels (filter applies
            if any SubChannel matches).
        """
        channels = dataset.channels
        everything = measurement.filter_channels(channels)
        assert everything == measurement.filter_channels(list(channels.values())), \
            "filter_channels(list) did not match filter_channels(dict)"

        accels = measurement.filter_channels(channels, measurement.ACCELERATION)
        assert len(accels) == 2

        noaccel = measurement.filter_channels(channels, -measurement.ACCELERATION)
        assert len(noaccel) == len(everything) - len(accels)


    def test_filter_channels_subchannels(self, dataset):
        """ Test filter_channels() filtering of SubChannels.
        """
        subchannels = dataset.getPlots()
        everything = measurement.filter_channels(subchannels)

        accels = measurement.filter_channels(subchannels, measurement.ACCELERATION)
        assert len(accels) == 6

        noaccel = measurement.filter_channels(subchannels, -measurement.ACCELERATION)
        assert len(noaccel) == len(everything) - len(accels)


    def test_get_channels(self, dataset):
        everything = measurement.get_channels(dataset)

        accels = measurement.get_channels(dataset, measurement.ACCELERATION)
        assert len(accels) == 6

        noaccel = measurement.get_channels(dataset, -measurement.ACCELERATION)
        assert len(noaccel) == len(everything) - len(accels)

        everything = measurement.get_channels(dataset, subchannels=False)

        accels = measurement.get_channels(dataset, measurement.ACCELERATION, subchannels=False)
        assert len(accels) == 2

        noaccel = measurement.get_channels(dataset, -measurement.ACCELERATION, subchannels=False)
        assert len(noaccel) == len(everything) - len(accels)
