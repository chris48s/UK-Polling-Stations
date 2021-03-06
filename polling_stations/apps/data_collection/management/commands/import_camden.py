"""
Imports Camden
"""
import json
import tempfile
import urllib.request
from lxml import etree
from django.contrib.gis.geos import GEOSGeometry, Point
from data_collection.base_importers import BaseGenericApiImporter
from data_collection.geo_utils import convert_linestring_to_multiploygon

class Command(BaseGenericApiImporter):
    """
    Imports the Polling Station data from Camden Council
    """
    stations_filetype = None
    districts_filetype = None
    srid             = 4326
    districts_srid   = 4326
    council_id       = 'E09000007'
    # This isn't GeoJSON - it is JSON with serialised WKT strings embedded in it
    districts_url    = 'https://opendata.camden.gov.uk/api/views/ta65-2szc/rows.json?accessType=DOWNLOAD'
    # This is just a bespoke XML format
    stations_url     = 'https://opendata.camden.gov.uk/api/views/5rhh-fxna/rows.xml?accessType=DOWNLOAD'
    elections        = ['parl.2017-06-08']

    def get_districts(self):
        with tempfile.NamedTemporaryFile() as tmp:
            req = urllib.request.urlretrieve(self.districts_url, tmp.name)
            data = json.load(open(tmp.name))
            return data['data']

    def district_record_to_dict(self, record):
        poly = GEOSGeometry(record[8], srid=self.get_srid('districts'))
        # poly is a LineString, but we need to convert it to a MultiPolygon so it will import
        poly = convert_linestring_to_multiploygon(poly)

        return {
            'internal_council_id': record[-1],
            'extra_id': record[-2],
            'name': 'Camden - %s' % (record[-1]),
            'area': poly,
            'polling_station_id': record[-1]
        }

    def get_stations(self):
        with tempfile.NamedTemporaryFile() as tmp:
            req = urllib.request.urlretrieve(self.stations_url, tmp.name)
            xml = etree.parse(tmp.name)
            return xml.getroot()[0]

    def station_record_to_dict(self, record):
        info = {}
        for tag in record:
            info[tag.tag] = tag.text

        address = "\n".join([info['organisation'], info['street']])

        if info['polling_district_name'] == "JA" and info['organisation'] == 'Rainbow Nursery':
            info['postcode'] = "NW5 2HY"
            address = "Rainbow Nursery, St. Benet's Church Hall, Lupton Street London"
            info['longitude'] = "-0.1381025"
            info['latitude'] = "51.554399"

        location = Point(
            float(info['longitude']),
            float(info['latitude']),
            srid=self.get_srid())

        return {
            'internal_council_id': info['polling_district_name'],
            'postcode': info['postcode'],
            'address': address,
            'location': location
        }
