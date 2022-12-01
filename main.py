from service import Service
import config

from Influx import Influx, Point
import __locale

if __name__ == "__main__":


    service = Service(config.config())
    service.start()

