"""Constants for apschool."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

BASE_URL = "https://api.plateforme.apschool.be"
NAME = "APSchool"
DOMAIN = "apschool"
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 10
VERSION = "0.0.1"
ATTRIBUTION = "Data provided by https://plateforme.apschool.be/"
