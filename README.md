# muinas-data
This tool imports data from the [Estonian National Registry of Cultural Monuments](http://register.muinas.ee/public.php) into Wikidata.

Sadly, the registry seems to not provide an API, so this just scrapes the actual registry pages to find the data.

You will need a working [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation) installation to use the tool.

Right now, the bot imports the specific type of monument and the date of registration.