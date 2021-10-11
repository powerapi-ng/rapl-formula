# RAPL-formula

A [powerAPI](https://github.com/powerapi-ng/powerapi) formula using RAPL
counters to provides power consumption information of each socket of the
monitored machine.

Use RAPL data collected with the
[hwpc-sensor](https://github.com/powerapi-ng/hwpc-sensor) and convert it into
power consumption measures (in Watt). The power consumption measures are store
in a MongoDB database.

# Quick start

We detail here how to quickly start rapl-formula and connect it to a hwpc-sensor
using a mongoDB instance.

For more detail see our documentation [here](http://powerapi.org)

## Get input data

You have to launch the [hwpc-sensor](https://github.com/powerapi-ng/hwpc-sensor) to
monitor sockets. The sensor must store its data in a mongoDB database. This
database must be accessible by the rapl_formula.

## Configuration

You can pass the configuration through a file or the CLI.
In both case the parameters to precises are the following :

- `verbose` (bool)
- `stream` (bool): If working with a sensor in real-time
- `input`
- `output`
- `enable-cpu-formula` (bool): Enable CPU formula', default=True
- `enable-dram-formula` (bool): Enable DRAM formula, default=True
- `'cpu-rapl-ref-event` (str): RAPL event used as reference for the CPU power models, default='RAPL_ENERGY_PKG'
- `'dram-rapl-ref-event` (str): RAPL event used as reference for the DRAM power models, default='RAPL_ENERGY_DRAM'
- `'sensor-report-sampling-interval` (int): (for stream mode) The frequency with which measurements are made
  (in milliseconds)
