import requests, json
import pywikibot
from pywikibot import pagegenerators as pg


# Turns a muinas.ee monument type into its equivalent Wikidata item
def muinastype_to_item(argument):
    switcher = {
        u'ehitism\xe4lestis': "Q12361770",
        u'tehnikam\xe4lestis': "Q25503888",
        u'muinsuskaitseala': "Q25504552",
        u'kunstim\xe4lestis': "Q25503887",
        u'ajaloom\xe4lestis': "Q12358501",
        u'arheoloogiam\xe4lestis': "Q43874039",
    }
    return switcher.get(argument, "nothing")


site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()

# We get all items that have a muinas.ee ID and no monument type yet
query = "SELECT ?item WHERE { ?item wdt:P2948 [] . MINUS {?item wdt:P1435 []} }"
generator = pg.WikidataSPARQLPageGenerator(query, site=site)

for item in generator:
    # We get the Wikidata item
    item.get()
    # There should only ever exist one ID per item, so we take the first
    muinasID = item.claims[u'P2948'][0].target


    # We look at the muinas.ee API to get the type of monument and the date of registration
    response = requests.get("https://register.muinas.ee/rest/v1/monuments/" + muinasID)
    data = response.json()
    muinasTypes = data['classifications']
    muinasDate = data['registered']

    # We turn the monument type into its equivalent Wikidata item
    muinasTypeItems = []
    for type in muinasTypes:
        muinasTypeItems.append(muinastype_to_item(type))

    # We turn the date into something Wikidata can recognize
    tempDate = muinasDate.split('-')
    muinasYear = int(tempDate[0])
    muinasMonth = int(tempDate[1])
    muinasDay = int(tempDate[2])
    muinasWbDate = pywikibot.WbTime(year=muinasYear, month=muinasMonth, day=muinasDay)

    # As long as the type we found matched one of our items, we send the info, including the date, to Wikidata
    if muinasTypeItems and not (u'P1435' in item.claims):
        for type in muinasTypeItems:
            claim = pywikibot.Claim(repo, "P1435")
            target = pywikibot.ItemPage(repo, type)
            claim.setTarget(target)
            item.addClaim(claim,
                          summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
            qualifier = pywikibot.Claim(repo, "P580")
            qualifier.setTarget(muinasWbDate)
            claim.addQualifier(qualifier, summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
            statedin = pywikibot.Claim(repo, "P248")
            enrcm = pywikibot.ItemPage(repo, "Q3743725")
            statedin.setTarget(enrcm)
            claim.addSources([statedin],
                             summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
            print "Adding type: " + type
    else:
        print "No muinastype detected"

    if not (u'P17' in item.claims):
        claim = pywikibot.Claim(repo, "P17")
        target = pywikibot.ItemPage(repo, "Q191")
        claim.setTarget(target)
        item.addClaim(claim,
                      summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
        print "Adding country: Estonia"