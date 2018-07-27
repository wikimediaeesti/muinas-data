# muinas-data
This tool imports data from the [Estonian National Registry of Cultural Monuments](http://register.muinas.ee/public.php) into Wikidata.

You will need a working [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation) installation to use the tool.

Right now, the bot imports the specific type(s) of monument and the date of registration.

Additionally, it allows importing coordinates, if a separate CSV file with the info is provided (this data is only available via the Estonian X-Road otherwise)