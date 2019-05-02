from django.core.management.base import BaseCommand

from django.contrib.gis.geos import Point
from pollingstations.models import PollingStation, PollingDistrict, ResidentialAddress
from councils.models import Council
from addressbase.models import Address, Blacklist


def update_station_point(council_id, station_id, point):
    stations = PollingStation.objects.filter(
        council_id=council_id, internal_council_id=station_id
    )
    if len(stations) == 1:
        station = stations[0]
        station.location = point
        station.save()
        print("..updated")
    else:
        print("..NOT updated")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        print("updating Watford address...")
        watford = Council.objects.get(pk="E07000103")
        watford.address = "Electoral Services Office\nRoom 22\nTown Hall\nWatford"
        watford.postcode = "WD17 3EX"
        watford.save()
        print("..updated")

        print("updating Harrogate address...")
        harrogate = Council.objects.get(pk="E07000165")
        harrogate.address = "Civic Centre\nSt Lukes Avenue\nHarrogate"
        harrogate.postcode = "HG1 2AE"
        harrogate.save()
        print("..updated")

        print("updating Oadby & Wigston name...")
        oadby = Council.objects.get(pk="E07000135")
        oadby.name = "Oadby & Wigston Borough Council"
        oadby.save()
        print("..updated")

        print("updating Swansea name...")
        swansea = Council.objects.get(pk="W06000011")
        swansea.name = "City & County of Swansea"
        swansea.save()
        print("..updated")

        print("removing bad points from AddressBase")
        bad_uprns = [
            "10023906550",
            "2630153843",
            "14059977",
            "10007921239",
            "10007920387",
            "10007920390",
            "10024288188",
            "10024288190",
            "10024288189",
            "10023117526",
            "10009922833",
        ]
        addresses = Address.objects.filter(pk__in=bad_uprns)
        for address in addresses:
            print(address.uprn)
            address.delete()
        print("..deleted")

        print("removing dodgy blacklist entries (result of bad point in AddressBase)..")
        blacklist = Blacklist.objects.filter(postcode="RH122LP")
        if len(blacklist) == 2:
            for b in blacklist:
                b.delete()
                print("..deleted")
        else:
            print("..NOT deleted")

        print(
            "removing dodgy blacklist entries (result of bad points in AddressBase).."
        )
        blacklist = Blacklist.objects.filter(postcode="S24AX")
        if len(blacklist) == 2:
            for b in blacklist:
                b.delete()
                print("..deleted")
        else:
            print("..NOT deleted")

        print("updating: Meppershall Village Hall...")
        stations = PollingStation.objects.filter(
            council_id="E06000056", internal_council_id="10361"
        )
        if len(stations) == 1:
            station = stations[0]
            station.location = Point(-0.340481, 52.018151, srid=4326)
            station.address = (
                "Meppershall Village Hall\nWalnut Tree Way\nMeppershall\nSG17 5AB"
            )
            station.save()
            print("..updated")
        else:
            print("..NOT updated")

        # user issue report #49
        print("updating: WI Hall, Faversham Road...")
        update_station_point("E07000105", "5707", Point(0.885308, 51.169796, srid=4326))

        # user issue report #50
        print("updating: Sandhurst School Sports Hall...")
        update_station_point(
            "E06000036", "4019", Point(-0.782442, 51.350179, srid=4326)
        )

        # user issue report #51
        print("updating: Weobley Village Hall...")
        update_station_point(
            "E06000019",
            "99-weobley-village-hall",
            Point(-2.869103, 52.159915, srid=4326),
        )

        # user issue report #47 (again)
        print("updating: Southill Community Centre...")
        stations = PollingStation.objects.filter(
            council_id="E06000059", internal_council_id="30560"
        )
        if len(stations) == 1:
            station = stations[0]
            station.postcode = "DT4 9SS"
            station.save()
            print("..updated")
        else:
            print("..NOT updated")

        # user issue report #52
        print("updating: Rhodes Arts Complex...")
        update_station_point("E07000242", "1919", Point(0.163535, 51.863442, srid=4326))

        # user issue report #53
        print("updating: Moose Lodge...")
        update_station_point(
            "E06000059", "30570", Point(-2.466883, 50.606307, srid=4326)
        )

        print("updating: SW&T station 6753...")
        # All those electors who were going to Staplegrove Church School
        # are actually going to
        # Staplegrove Village Hall, 214 Staplegrove Road, Taunton TA2 6AL
        stations = PollingStation.objects.filter(
            council_id="E07000246", internal_council_id="6753"
        )
        if len(stations) == 1:
            station = stations[0]
            station.location = Point(-3.122027, 51.028508, srid=4326)
            station.address = "Staplegrove Village Hall\n214 Staplegrove Road\nTaunton"
            station.postcode = "TA2 6AL"
            station.save()
            print("..updated")
        else:
            print("..NOT updated")

        # user issue report #54
        print("updating: West Moors Memorial Hall...")
        update_station_point(
            "E06000059", "30798", Point(-1.889868, 50.828982, srid=4326)
        )
        update_station_point(
            "E06000059", "30801", Point(-1.889868, 50.828982, srid=4326)
        )

        # user issue report #55
        print("updating: Dorset Fire & Rescue, Peverell Avenue West...")
        update_station_point(
            "E06000059", "30244", Point(-2.471750, 50.713013, srid=4326)
        )

        # user issue report #56
        print("updating: Higher Failsworth Primary School...")
        update_station_point(
            "E08000004", "5063", Point(-2.148726, 53.514296, srid=4326)
        )

        # user issue report #65
        print("updating: Penistone Cricket Club...")
        update_station_point("E08000016", "110", Point(-1.618343, 53.525626, srid=4326))

        # user issue report #66
        print("updating: St Mary's Catholic Primary School...")
        update_station_point(
            "E06000040",
            "23-st-marys-catholic-primary-school",
            Point(-0.724786, 51.535229, srid=4326),
        )
        update_station_point(
            "E06000040",
            "24-st-marys-catholic-primary-school",
            Point(-0.724786, 51.535229, srid=4326),
        )

        deleteme = [
            # nothing yet
        ]
        for council_id in deleteme:
            print("Deleting data for council %s..." % (council_id))
            # check this council exists
            c = Council.objects.get(pk=council_id)
            print(c.name)

            PollingStation.objects.filter(council=council_id).delete()
            PollingDistrict.objects.filter(council=council_id).delete()
            ResidentialAddress.objects.filter(council=council_id).delete()
            print("..deleted")

        print("..done")
