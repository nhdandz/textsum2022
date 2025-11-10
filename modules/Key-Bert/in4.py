from keybert import KeyBERT

doc = """
    The US Treasury Department on Tuesday sanctioned Russian President Vladimir Putin's reputed girlfriend as part of a series of measures targeting Russian elites in the Biden administration's latest attempt to punish the Kremlin for its ongoing war in Ukraine.

    Alina Maratovna Kabaeva, who has been romantically linked to the Russian leader, was sanctioned "for being or having been a leader, official, senior executive officer, or member of the board of directors of the Government of the Russian Federation," a Treasury Department statement said.
    That statement describes the 39-year-old Kabaeva as having "a close relationship to Putin." She is a former member of the State Duma "and is the current head of the National Media Group, a pro-Kremlin empire of television, radio, and print organizations."
    In April, the Wall Street Journal reported that sanctioning Kabaeva was under consideration by the US, but there was concern that such a move would inflame tensions given her close proximity to Putin.

    In addition to Kabaeva, the Treasury Department announced sanctions against a number of other oligarchs, a major steel production company and two of its subsidiaries as well as a financial institution accused of running a sanctions evasion operation and its general director.

    Separately, US Secretary of State Antony Blinken announced sanctions on three oligarchs, a Russian state-owned company overseen by the Ministry of Transportation, "four individuals and one entity illegitimately operating in Ukraine's territory in collaboration with Russia," and 24 Russian defense and technology-related entities.

    The US is also imposing visa restrictions on 893 Russian Federation officials and "31 foreign government officials who have acted to support Russia's purported annexation of the Crimea region of Ukraine and thereby threatened or violated Ukraine's sovereignty," Blinken said.

    Many of the designations announced by the US target oligarchs who were previously sanctioned by allies like the United Kingdom, Australia, Canada and the European Union. They come as the war in Ukraine has entered its sixth month.

    'Opulent lifestyles'
    "As innocent people suffer from Russia's illegal war of aggression, Putin's allies have enriched themselves and funded opulent lifestyles," Treasury Secretary Janet Yellen said in a statement. "The Treasury Department will use every tool at our disposal to make sure that Russian elites and the Kremlin's enablers are held accountable for their complicity in a war that has cost countless lives."
    The oligarchs sanctioned by the State Department Tuesday are Andrey Igorevich Melnichenko, Alexander Anatolevich Ponomarenko, and Dmitry Aleksandrovich Pumpyanskiy. The yacht AXIOMA was identified as blocked property in which Pumpyanskiy has an interest, the State Department said in a fact sheet.
    According to that fact sheet, Ponomarenko "is an oligarch with close ties to other oligarchs and the construction of Vladimir Putin's seaside palace" who has previously been sanctioned by the UK, EU, Canada, Australia and New Zealand.
    Among the oligarchs sanctioned by the Treasury Department Tuesday is Andrey Grigoryevich Guryev, the Russian billionaire founder of the chemical company "PhosAgro" and former government official described by the Treasury as "a known close associate" of Putin. He is also sanctioned by the UK, and according to the US Treasury, he "owns the Witanhurst estate, which is the second largest estate in London after Buckingham Palace."

    The Treasury Department on Tuesday identified the yacht Alfa Nero, reportedly owned by AG Guryev, as blocked property.
    AG Guryev's son, Andrey Andreevich Guryev, was also sanctioned by the US Tuesday, after previously being sanctioned by Australia, Canada, the European Union, Switzerland, and the UK, as was his investment firm Dzhi AI Invest OOO.
    Natalya Valeryevna Popova was sanctioned "for operating or having operated in the technology sector of the Russian Federation economy, and for being or having been a leader, official, senior executive officer, or member of the board of directors of LLC VEB Ventures," which is a sanctioned entity. She was also sanctioned for being the wife of Kirill Aleksandrovich Dmitriev, the CEO of the Russian Direct Investment Fund (RDIF). Both he and the RDIF were sanctioned in the days following the start of the war.
    The Joint Stock Company Promising Industrial and Infrastructure Technologies, "a financial institution owned by the Russian Federal Agency for State Property Management," and its General Director Anton Sergeevich Urusov were sanctioned Tuesday in relation to alleged sanctions evasion.
    According to the Treasury Department, "JSC PPIT attempted to facilitate the circumvention of sanctions imposed on the Russian Direct Investment Fund (RDIF)."
    The Treasury Department sanctioned Publichnoe Aktsionernoe Obschestvo Magnitogorskiy Metallurgicheskiy Kombinat (MMK), described as "one of the world's largest steel producers," the chairman of its board of directors Viktor Filippovich Rashnikov -- who has also been sanctioned by Australia, Canada, the EU, Switzerland, and the UK -- and two of MMK's subsidiaries.
    "MMK is one of Russia's largest taxpayers, providing a substantial source of revenue to the Government of the Russian Federation," the Treasury Department said. The agency has authorized a wind-down period for transactions with MMK and one of its subsidiaries.

      """
doc = doc.replace("\n", "")
print(doc)
kw_model = KeyBERT()
keywords = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1, 2), stop_words='english')
print(keywords)