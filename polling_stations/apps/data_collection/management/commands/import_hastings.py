from data_collection.management.commands import BaseHalaroseCsvImporter

class Command(BaseHalaroseCsvImporter):
    council_id      = 'E07000062'
    addresses_name  = 'parl.2017-06-08/Version 1/Hastings polling_station_export-2017-05-17.csv'
    stations_name   = 'parl.2017-06-08/Version 1/Hastings polling_station_export-2017-05-17.csv'
    elections       = ['parl.2017-06-08']
    csv_encoding    = 'windows-1252'
