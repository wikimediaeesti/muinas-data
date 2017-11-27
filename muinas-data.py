from lxml import html
import requests
import pywikibot
from pywikibot import pagegenerators as pg


# Turns a scraped muinas.ee monument type into its equivalent Wikidata item
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

# We get all items that have a muinas.ee ID
query = "SELECT ?item WHERE { ?item wdt:P2948 [] } LIMIT 10"
generator = pg.WikidataSPARQLPageGenerator(query, site=site)

for item in generator:
    # We get the Wikidata item
    item.get()
    # There should only ever exist one ID per item, so we take the first
    muinasID = item.claims[u'P2948'][0].target

    # We scrape the muinas.ee page to get the type of monument and the date of registration
    page = requests.get("http://register.muinas.ee/public.php?menuID=monument&action=view&id=" + muinasID)
    tree = html.fromstring(page.content)
    muinasType = tree.xpath("//th[contains(.,'Liigitus')]/following-sibling::td/text()")
    muinasDate = tree.xpath("(//th[contains(.,'Registreeritud')])[2]/following-sibling::td/strong/text()")

    # We turn the scraped monument type into its equivalent Wikidata item
    muinasTypeItem = muinastype_to_item(muinasType[0])

    # We turn the scraped date into something Wikidata can recognize
    tempDate = muinasDate[0].split('.')
    muinasYear = int(tempDate[0])
    muinasMonth = int(tempDate[1])
    muinasDay = int(tempDate[2])
    muinasWbDate = pywikibot.WbTime(year=muinasYear, month=muinasMonth, day=muinasDay, precision='day')

    # As long as the type we found matched one of our items, we send the info, including the date, to Wikidata
    if muinasTypeItem != "nothing" and not (u'P1435' in item.claims):
        claim = pywikibot.Claim(repo, "P1435")
        target = pywikibot.ItemPage(repo, muinasTypeItem)
        claim.setTarget(target)
        item.addClaim(claim,
                      summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
        # Dates currently broken, WIP
        # qualifier = pywikibot.Claim(repo, "P580")
        # qualifier.setTarget(muinasWbDate)
        # claim.addQualifier(qualifier, summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
        statedin = pywikibot.Claim(repo, "P248")
        enrcm = pywikibot.ItemPage(repo, "Q3743725")
        statedin.setTarget(enrcm)
        claim.addSources([statedin],
                         summary=u'Importing heritage information from the Estonian National Registry of Cultural Monuments')
