import pytest

@pytest.fixture
def rapl_timeline():
    """
    Timeline of procfs report for the tests
    """

    return [{ "timestamp": "2021-10-05T09:14:58.226", "sensor": "toto", "target": "all", "groups": { "rapl": { "0": { "7": { "RAPL_ENERGY_PKG": 5558763520.0, "time_enabled": 1000770053.0, "time_running": 1000770053.0 } } } } },
            { "timestamp": "2021-10-05T09:14:59.226", "sensor": "toto", "target": "all", "groups": { "rapl": { "0": { "7": { "RAPL_ENERGY_PKG": 4777050112.0, "time_enabled": 2001065535.0, "time_running": 2001065535.0 } } } } },
            { "timestamp": "2021-10-05T09:15:00.227", "sensor": "toto", "target": "all", "groups": { "rapl": { "0": { "7": { "RAPL_ENERGY_PKG": 6847987712.0, "time_enabled": 3001449088.0, "time_running": 3001449088.0 } } } } },
            { "timestamp": "2021-10-05T09:15:01.227", "sensor": "toto", "target": "all", "groups": { "rapl": { "0": { "7": { "RAPL_ENERGY_PKG": 5054922752.0, "time_enabled": 4001882359.0, "time_running": 4001882359.0 } } } } },
            { "timestamp": "2021-10-05T09:15:02.228", "sensor": "toto", "target": "all", "groups": { "rapl": { "0": { "7": { "RAPL_ENERGY_PKG": 5434507264.0, "time_enabled": 5002352709.0, "time_running": 5002352709.0 } } } } }
            ]
