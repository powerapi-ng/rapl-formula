# RAPL-formula

A [powerAPI](https://github.com/powerapi-ng/powerapi) formula using RAPL
counters to provides power consumption information of each socket of the
monitored machine.

Use RAPL data collected with the
[hwpc-sensor](https://github.com/powerapi-ng/hwpc-sensor) and convert it into
power consumption measures (in Watt). The power consumption measures are store
in a MongoDB database.

# Usage

## Get input data

You have to launch the [hwpc-sensor](https://github.com/powerapi-ng/hwpc-sensor) to 
monitor sockets. The sensor must store its data in a mongoDB database. This
database must be accessible by the rapl_formula.

## Launch formula

with python(>=3.7):

```bash
python3 -m rapl_formula --output mongodb --uri input_mongo_uri --db input_db
	--collection input_collection --input mongodb --uri output_mongo_uri --db output_db
	--collection output_collection
```

with docker:

```bash
docker run powerapi/rapl-formula --output mongodb --uri input_mongo_uri --db input_db
	--collection input_collection --input mongodb --uri output_mongo_uri --db output_db
	--collection output_collection
```

with the following configuration: 

- input_mongo_uri : uri to the mongoDB used by the hwpc-sensor to store its output data
- input_db : database used by the hwpc-sensor to store its output data
- input_collection : collection used by the hwpc-sensor to store its output data
- output_mongo_uri : uri to the mongoDB used to store the power consumption data
- output_db : database used to store the power consumption data
- output_collection : collection used to store the power consumption data
