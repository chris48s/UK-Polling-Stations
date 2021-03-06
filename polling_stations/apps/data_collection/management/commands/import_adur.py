from data_collection.management.commands import BaseXpressDemocracyClubCsvImporter

class Command(BaseXpressDemocracyClubCsvImporter):
    council_id = 'E07000223'
    addresses_name = 'parl.2017-06-08/Version 1/ADUR Democracy_Club__08June2017.TSV'
    stations_name = 'parl.2017-06-08/Version 1/ADUR Democracy_Club__08June2017.TSV'
    elections = ['parl.2017-06-08']
    csv_delimiter = '\t'
