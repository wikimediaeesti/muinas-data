import csv, urllib
import pywikibot
from pywikibot import pagegenerators as pg


# Provided coordinates are in LAMBERT-EST projection, we need geodetic coordinates
def lest_coords_to_geo_coords(lest_coords):
    page = urllib.urlopen("https://www.maaamet.ee/rr/geo-lest/url/?xy=" + lest_coords)
    coords = page.read()
    geo_coords = coords.split(",")
    return geo_coords


site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()

# We take the list of coordinates provided by the Estonian Heritage Register
coordinate_dict = {}

with open('koordinaadid.csv', 'r') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        coordinate_dict[row['id']] = row['gpsx'] + "," + row['gpsy']

# We get all items that have a muinas.ee ID and no coordinates yet
query = "SELECT ?item WHERE { ?item wdt:P2948 [] . MINUS {?item wdt:P625 []} }"
generator = pg.WikidataSPARQLPageGenerator(query, site=site)

for item in generator:
    # We get the Wikidata item
    item.get()
    # There should only ever exist one ID per item, so we take the first
    muinasID = item.claims[u'P2948'][0].target

    # We look for the appropriate ID in our coordinate list and take the coordinates
    geo_coords = None
    if coordinate_dict.get(muinasID):
        lest_coords = coordinate_dict.get(muinasID)

        # We turn the LEST coordinates into geodetic
        if lest_coords != ",":
            geo_coords = lest_coords_to_geo_coords(lest_coords)
            print geo_coords

    # As long as the type we found matched one of our items, we send the info, including the date, to Wikidata
    if geo_coords is not None and not (u'P625' in item.claims):
        claim = pywikibot.Claim(repo, "P625")
        coordinates = pywikibot.Coordinate(lat=float(geo_coords[0]), lon=float(geo_coords[1]), globe="earth", precision=0.001)
        print coordinates
        claim.setTarget(coordinates)
        item.addClaim(claim,
                      summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
        statedin = pywikibot.Claim(repo, "P248")
        enrcm = pywikibot.ItemPage(repo, "Q3743725")
        statedin.setTarget(enrcm)
        claim.addSources([statedin],
                         summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
    else:
        print "No coordinates sent"
