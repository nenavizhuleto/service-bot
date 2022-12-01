import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS



class Influx():
    def __init__(self, token, url, org) -> None:
        self.db = InfluxDBClient(url=url, token=token, org=org)

    def write(self, bucket, points):
        write_api = self.db.write_api(write_options=SYNCHRONOUS)

        for point in points:
            write_api.write(bucket=bucket, org=self.db.org, record=point)
            time.sleep(1)

    def read(self, query):
        query_api = self.db.query_api()

        tables = query_api.query(query=query, org=self.db.org)
        

        return tables