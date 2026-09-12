"""
Label and URL generation for stations and lines.
"""
from . import config
from .ids import numeric_part


def station_label(station_id, naming_exceptions):
    if station_id in naming_exceptions:
        return naming_exceptions[station_id]
    return config.STATION_LABEL_TEMPLATE.format(num=numeric_part(station_id))


def line_label(line_id, naming_exceptions=None):
    naming_exceptions = naming_exceptions or {}
    if line_id in naming_exceptions:
        return naming_exceptions[line_id]
    return config.LINE_LABEL_TEMPLATE.format(num=numeric_part(line_id))


def station_url(station_id):
    return config.STATION_URL_TEMPLATE.format(num=numeric_part(station_id))


def line_url(line_id):
    return config.LINE_URL_TEMPLATE.format(num=numeric_part(line_id))
