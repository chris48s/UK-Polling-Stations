"""
Specialised base import classes for handling data exported from
popular Electoral Management Software packages
"""
import abc
from django.contrib.gis.geos import Point
from django.utils.text import slugify
from data_collection.base_importers import BaseCsvStationsCsvAddressesImporter
from data_finder.helpers import geocode_point_only, PostcodeError


"""
We see a lot of CSVs exported from Xpress
electoral service software: http://www.xssl.uk/
with the addresses and stations in a single CSV file

There are 2 formats we see:
* WebLookup export (hopefully we will start seeing less of these)
* DemocracyClub export (hopefully we will start seeing more of these)
This is the parent class for both of them.
"""
class BaseXpressCsvImporter(BaseCsvStationsCsvAddressesImporter,
                            metaclass=abc.ABCMeta):
    csv_delimiter = ','

    @property
    @abc.abstractmethod
    def station_postcode_field(self):
        pass

    @property
    @abc.abstractmethod
    def station_address_fields(self):
        pass

    @property
    @abc.abstractmethod
    def station_id_field(self):
        pass

    @property
    @abc.abstractmethod
    def easting_field(self):
        pass

    @property
    @abc.abstractmethod
    def northing_field(self):
        pass

    def get_station_hash(self, record):
        return "-".join([
            getattr(record, self.station_id_field),
        ])

    def get_station_address(self, record):
        address = "\n".join([
            getattr(record, field) for field in self.station_address_fields
        ])
        while "\n\n" in address:
            address = address.replace("\n\n", "\n").strip()
        return address

    def get_station_postcode(self, record):
        return getattr(record, self.station_postcode_field).strip()

    def get_station_point(self, record):
        location = None

        if (hasattr(record, self.easting_field) and\
            hasattr(record, self.northing_field) and\
            getattr(record, self.easting_field) != '0' and\
            getattr(record, self.easting_field) != '' and\
            getattr(record, self.northing_field) != '0' and\
            getattr(record, self.northing_field) != ''):

            # if we've got points, use them
            location = Point(
                float(getattr(record, self.easting_field)),
                float(getattr(record, self.northing_field)),
                srid=27700)
        else:
            # otherwise, geocode using postcode
            postcode = self.get_station_postcode(record)
            if not postcode:
                return None

            try:
                location_data = geocode_point_only(postcode)
                location = Point(
                    location_data['wgs84_lon'],
                    location_data['wgs84_lat'],
                    srid=4326)
            except PostcodeError:
                location = None

        return location

    def station_record_to_dict(self, record):
        address = self.get_station_address(record)
        location = self.get_station_point(record)
        return {
            'internal_council_id': getattr(record, self.station_id_field).strip(),
            'postcode'           : self.get_station_postcode(record),
            'address'            : address.strip(),
            'location'           : location
        }


"""
Specialised case of BaseCsvStationsCsvAddressesImporter
with some sensible presets for processing WebLookup
CSVs exported from Xpress
"""
class BaseXpressWebLookupCsvImporter(BaseXpressCsvImporter,
                                     metaclass=abc.ABCMeta):
    station_postcode_field = 'pollingplaceaddress7'
    station_address_fields = [
        'pollingplaceaddress1',
        'pollingplaceaddress2',
        'pollingplaceaddress3',
        'pollingplaceaddress4',
        'pollingplaceaddress5',
        'pollingplaceaddress6',
    ]
    station_id_field = 'pollingplaceid'
    easting_field = 'pollingplaceeasting'
    northing_field = 'pollingplacenorthing'

    def address_record_to_dict(self, record):
        if record.postcode.strip() == '':
            return None

        if record.propertynumber.strip() == '0' or record.propertynumber.strip() == '':
            address = record.streetname.strip()
        else:
            address = '%s %s' % (record.propertynumber.strip(), record.streetname.strip())

        return {
            'address'           : address.strip(),
            'postcode'          : record.postcode.strip(),
            'polling_station_id': getattr(record, self.station_id_field).strip()
        }


"""
Specialised case of BaseCsvStationsCsvAddressesImporter
with some sensible presets for processing DemocracyClub
CSVs exported from Xpress
"""
class BaseXpressDemocracyClubCsvImporter(BaseXpressCsvImporter,
                                         metaclass=abc.ABCMeta):
    station_postcode_field = 'polling_place_postcode'
    station_address_fields = [
        'polling_place_name',
        'polling_place_address_1',
        'polling_place_address_2',
        'polling_place_address_3',
        'polling_place_address_4',
    ]
    station_id_field = 'polling_place_id'
    easting_field = 'polling_place_easting'
    northing_field = 'polling_place_northing'

    def address_record_to_dict(self, record):
        if record.addressline6.strip() == '':
            return None

        address = ", ".join([
            record.addressline1,
            record.addressline2,
            record.addressline3,
            record.addressline4,
            record.addressline5,
        ])
        while ", , " in address:
            address = address.replace(", , ", ", ")
        if address[-2:] == ', ':
            address = address[:-2]

        return {
            'address'           : address.strip(),
            'postcode'          : record.addressline6.strip(),
            'polling_station_id': getattr(record, self.station_id_field).strip()
        }


"""
Sometimes the postcode doesn't appear in a consistent
column and we need to work around that
"""
class BaseXpressDCCsvInconsistentPostcodesImporter(
    BaseXpressDemocracyClubCsvImporter, metaclass=abc.ABCMeta):

    # concat all the address columns together into address
    # don't bother trying to split into address/postcode
    station_address_fields = [
        'polling_place_name',
        'polling_place_address_1',
        'polling_place_address_2',
        'polling_place_address_3',
        'polling_place_address_4',
        'polling_place_postcode',
    ]
    station_postcode_search_fields = [
        'polling_place_postcode',
        'polling_place_address_4',
        'polling_place_address_3',
    ]

    def station_record_to_dict(self, record):
        address = self.get_station_address(record)
        location = self.get_station_point(record)
        return {
            'internal_council_id': getattr(record, self.station_id_field).strip(),
            'postcode'           : '',  # don't rely on get_station_postcode()
            'address'            : address.strip(),
            'location'           : location
        }

    def get_station_postcode(self, record):
        # postcode does not appear in a consistent column
        # return the contents of the last populated address
        # field and we'll attempt to geocode with that
        for field in self.station_postcode_search_fields:
            if getattr(record, field):
                return getattr(record, field).strip()
        return None


"""
We see a lot of CSVs exported from Halarose
electoral service software: https://www.halarose.co.uk/
with the addresses and stations in a single CSV file

This is a specialised case of BaseCsvStationsCsvAddressesImporter
with some sensible presets for processing CSVs in this format
but we can override them if necessary
"""
class BaseHalaroseCsvImporter(BaseCsvStationsCsvAddressesImporter,
                              metaclass=abc.ABCMeta):
    csv_delimiter = ','
    station_postcode_field = 'pollingstationpostcode'
    station_address_fields = [
        'pollingstationname',
        'pollingstationaddress_1',
        'pollingstationaddress_2',
        'pollingstationaddress_3',
        'pollingstationaddress_4',
        'pollingstationaddress_5',
    ]

    def get_station_hash(self, record):
        return "-".join([
            record.pollingstationnumber.strip(),
            slugify(record.pollingstationname.strip())[:90]
        ])

    def get_station_address(self, record):
        address = "\n".join([
            getattr(record, field) for field in self.station_address_fields
        ])
        while "\n\n" in address:
            address = address.replace("\n\n", "\n").strip()
        return address

    def get_station_point(self, record):
        location = None

        # geocode using postcode
        postcode = getattr(record, self.station_postcode_field).strip()
        if postcode == '':
            return None

        try:
            location_data = geocode_point_only(postcode)
            location = Point(
                location_data['wgs84_lon'],
                location_data['wgs84_lat'],
                srid=4326)
        except PostcodeError:
            location = None

        return location

    def station_record_to_dict(self, record):

        if record.pollingstationnumber.strip() == 'n/a':
            return None

        address = self.get_station_address(record)
        location = self.get_station_point(record)
        return {
            'internal_council_id': self.get_station_hash(record),
            'postcode'           : getattr(record, self.station_postcode_field).strip(),
            'address'            : address.strip(),
            'location'           : location
        }

    def get_residential_address(self, record):

        def replace_na(text):
            if text.strip() == 'n/a':
                return ''
            return text.strip()

        address_line_1 = replace_na(record.housename) + ' ' + replace_na(record.housenumber)
        address_line_1 = address_line_1.strip()
        street_address = replace_na(record.streetnumber) + ' ' + replace_na(record.streetname)
        street_address = street_address.strip()
        address_line_1 = address_line_1 + ' ' + street_address

        address = "\n".join([
            address_line_1.strip(),
            replace_na(record.locality),
            replace_na(record.town),
            replace_na(record.adminarea),
        ])

        while "\n\n" in address:
            address = address.replace("\n\n", "\n").strip()

        return address

    def address_record_to_dict(self, record):
        if record.streetname.lower().strip() == 'other electors':
            return None
        if record.streetname.lower().strip() == 'other voters':
            return None
        if record.streetname.lower().strip() == 'other electors address':
            return None

        if record.housepostcode.strip() == '':
            return None

        address = self.get_residential_address(record)

        return {
            'address'           : address,
            'postcode'          : record.housepostcode.strip(),
            'polling_station_id': self.get_station_hash(record),
        }


"""
We see a lot of CSVs exported from Democracy Counts
electoral service software: http://www.democracycounts.co.uk/
with the addresses and stations in a single CSV file

This is a specialised case of BaseCsvStationsCsvAddressesImporter
with some sensible presets for processing CSVs in this format
but we can override them if necessary
"""
class BaseDemocracyCountsCsvImporter(BaseCsvStationsCsvAddressesImporter,
                                     metaclass=abc.ABCMeta):

    csv_delimiter = ','
    station_name_field = 'placename'
    address_fields = [
        'add1',
        'add2',
        'add3',
        'add4',
        'add5',
        'add6',
    ]
    postcode_field = 'postcode'
    station_id_field = 'stationcode'

    def address_record_to_dict(self, record):

        if not getattr(record, self.postcode_field).strip():
            return None

        address = ", ".join([
            getattr(record, field) for field in self.address_fields
        ])
        while ", , " in address:
            address = address.replace(", , ", ", ")
        if address[-2:] == ', ':
            address = address[:-2]

        if 'Dummy Record' in address:
            return None

        return {
            'address'           : address,
            'postcode'          : getattr(record, self.postcode_field).strip(),
            'polling_station_id': getattr(record, self.station_id_field).strip(),
        }

    def get_station_point(self, record):
        location = None

        badvalues = ['', '0', '0.00']
        if (record.xordinate not in badvalues and record.yordinate not in badvalues):
            # if we've got points, use them
            location = Point(float(record.xordinate), float(record.yordinate), srid=27700)
        else:
            # otherwise, geocode using postcode
            postcode = record.postcode.strip()
            if postcode == '':
                return None

            try:
                location_data = geocode_point_only(postcode)
                location = Point(
                    location_data['wgs84_lon'],
                    location_data['wgs84_lat'],
                    srid=4326)
            except PostcodeError:
                location = None

        return location

    def station_record_to_dict(self, record):

        address = "\n".join(
            [getattr(record, self.station_name_field)] +
            [getattr(record, field) for field in self.address_fields])
        while "\n\n" in address:
            address = address.replace("\n\n", "\n").strip()

        location = self.get_station_point(record)

        return {
            'internal_council_id': getattr(record, self.station_id_field).strip(),
            'postcode'           : getattr(record, self.postcode_field).strip(),
            'address'            : address,
            'location'           : location
        }
