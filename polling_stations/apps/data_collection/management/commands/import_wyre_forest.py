from data_collection.management.commands import BaseXpressWebLookupCsvImporter

class Command(BaseXpressWebLookupCsvImporter):
    council_id      = 'E07000239'
    addresses_name  = 'WyreForestPropertyPostCodePollingStationWebLookup-2017-02-09.csv'
    stations_name   = 'WyreForestPropertyPostCodePollingStationWebLookup-2017-02-09.csv'
    elections       = [
        'local.worcestershire.2017-05-04',
        'parl.2017-06-08'
    ]
