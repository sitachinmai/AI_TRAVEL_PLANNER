"""
Centralized Research & Source URL Registry
Maps countries, destinations, and landmarks to verified Wikipedia / official travel research source pages.
"""

RESEARCH_URL_MAP = {
    # 🇦🇷 Argentina
    "argentina": "https://www.weforum.org/stories/economic-growth/argentina-radical-reform-unlock-economic-recovery/",
    "buenos aires": "https://en.wikipedia.org/wiki/Buenos_Aires",
    "bariloche": "https://solsalute.com/blog/things-to-do-in-bariloche-argentina/",
    "teatro colón": "https://en.wikipedia.org/wiki/Teatro_Col%C3%B3n",
    "plaza de mayo": "https://en.wikipedia.org/wiki/Plaza_de_Mayo",

    # 🇦🇺 Australia
    "australia": "https://en.wikipedia.org/wiki/Sydney_Opera_House",
    "sydney opera house": "https://en.wikipedia.org/wiki/Sydney_Opera_House",
    "sydney": "https://en.wikipedia.org/wiki/Sydney_Opera_House",
    "melbourne": "https://en.wikipedia.org/wiki/Melbourne",
    "brisbane": "https://www.travelandleisure.com/best-times-to-visit-brisbane-australia-8744626",
    "perth": "https://en.wikipedia.org/wiki/Perth",
    "adelaide": "https://en.wikivoyage.org/wiki/Adelaide",
    "cairns": "https://en.wikipedia.org/wiki/Cairns",
    "gold coast": "https://en.wikipedia.org/wiki/Gold_Coast,_Queensland",

    # 🇦🇹 Austria
    "austria": "https://en.wikipedia.org/wiki/Sch%C3%B6nbrunn_Palace",
    "vienna": "https://en.wikipedia.org/wiki/Sch%C3%B6nbrunn_Palace",
    "schönbrunn palace": "https://en.wikipedia.org/wiki/Sch%C3%B6nbrunn_Palace",

    # 🇧🇪 Belgium
    "belgium": "https://globalgrasshopper.com/destinations/europe/10-of-the-most-beautiful-places-to-visit-in-belgium/",
    "brussels": "https://en.wikipedia.org/wiki/Grand_Place",
    "grand place": "https://en.wikipedia.org/wiki/Grand_Place",

    # 🇧🇹 Bhutan
    "bhutan": "https://en.wikipedia.org/wiki/Paro_Taktsang",
    "paro": "https://en.wikipedia.org/wiki/Paro_Taktsang",
    "tiger's nest": "https://en.wikipedia.org/wiki/Paro_Taktsang",
    "paro taktsang": "https://en.wikipedia.org/wiki/Paro_Taktsang",

    # 🇧🇷 Brazil
    "brazil": "https://en.wikipedia.org/wiki/Christ_the_Redeemer_(statue)",
    "rio de janeiro": "https://en.wikipedia.org/wiki/Christ_the_Redeemer_(statue)",
    "christ the redeemer": "https://en.wikipedia.org/wiki/Christ_the_Redeemer_(statue)",

    # 🇨🇦 Canada
    "canada": "https://en.wikipedia.org/wiki/CN_Tower",
    "toronto": "https://en.wikipedia.org/wiki/CN_Tower",
    "cn tower": "https://en.wikipedia.org/wiki/CN_Tower",

    # 🇨🇱 Chile
    "chile": "https://en.wikipedia.org/wiki/Santiago",
    "santiago": "https://en.wikipedia.org/wiki/Santiago",
    "plaza de armas": "https://en.wikipedia.org/wiki/Santiago",

    # 🇨🇳 China
    "china": "https://en.wikipedia.org/wiki/Great_Wall_of_China",
    "beijing": "https://en.wikipedia.org/wiki/Great_Wall_of_China",
    "great wall of china": "https://en.wikipedia.org/wiki/Great_Wall_of_China",

    # 🇨🇴 Colombia
    "colombia": "https://en.wikipedia.org/wiki/Cartagena,_Colombia",
    "cartagena": "https://en.wikipedia.org/wiki/Cartagena,_Colombia",

    # 🇭🇷 Croatia
    "croatia": "https://en.wikipedia.org/wiki/Dubrovnik",
    "dubrovnik": "https://en.wikipedia.org/wiki/Dubrovnik",

    # 🇨🇿 Czech Republic
    "czech republic": "https://en.wikipedia.org/wiki/Charles_Bridge",
    "prague": "https://en.wikipedia.org/wiki/Charles_Bridge",
    "charles bridge": "https://en.wikipedia.org/wiki/Charles_Bridge",

    # 🇩🇰 Denmark
    "denmark": "https://en.wikipedia.org/wiki/Nyhavn",
    "copenhagen": "https://en.wikipedia.org/wiki/Nyhavn",
    "nyhavn": "https://en.wikipedia.org/wiki/Nyhavn",

    # 🇪🇬 Egypt
    "egypt": "https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza",
    "cairo": "https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza",
    "giza": "https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza",
    "pyramids of giza": "https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza",

    # 🇫🇯 Fiji
    "fiji": "https://en.wikipedia.org/wiki/Nadi",
    "nadi": "https://en.wikipedia.org/wiki/Nadi",

    # 🇫🇮 Finland
    "finland": "https://en.wikipedia.org/wiki/Helsinki_Cathedral",
    "helsinki": "https://en.wikipedia.org/wiki/Helsinki_Cathedral",
    "helsinki cathedral": "https://en.wikipedia.org/wiki/Helsinki_Cathedral",

    # 🇫🇷 France
    "france": "https://en.wikipedia.org/wiki/Eiffel_Tower",
    "paris": "https://en.wikipedia.org/wiki/Eiffel_Tower",
    "eiffel tower": "https://en.wikipedia.org/wiki/Eiffel_Tower",

    # 🇩🇪 Germany
    "germany": "https://en.wikipedia.org/wiki/Brandenburg_Gate",
    "berlin": "https://en.wikipedia.org/wiki/Brandenburg_Gate",
    "brandenburg gate": "https://en.wikipedia.org/wiki/Brandenburg_Gate",

    # 🇬🇷 Greece
    "greece": "https://en.wikipedia.org/wiki/Acropolis_of_Athens",
    "athens": "https://en.wikipedia.org/wiki/Acropolis_of_Athens",
    "acropolis": "https://en.wikipedia.org/wiki/Acropolis_of_Athens",

    # 🇭🇺 Hungary
    "hungary": "https://en.wikipedia.org/wiki/Hungarian_Parliament_Building",
    "budapest": "https://en.wikipedia.org/wiki/Hungarian_Parliament_Building",

    # 🇮🇸 Iceland
    "iceland": "https://en.wikipedia.org/wiki/Hallgr%C3%ADmskirkja",
    "reykjavik": "https://en.wikipedia.org/wiki/Hallgr%C3%ADmskirkja",
    "hallgrímskirkja": "https://en.wikipedia.org/wiki/Hallgr%C3%ADmskirkja",

    # 🇮🇳 India
    "india": "https://en.wikipedia.org/wiki/Taj_Mahal",
    "agra": "https://en.wikipedia.org/wiki/Taj_Mahal",
    "taj mahal": "https://en.wikipedia.org/wiki/Taj_Mahal",
    "delhi": "https://en.wikipedia.org/wiki/Delhi",

    # 🇮🇩 Indonesia
    "indonesia": "https://en.wikipedia.org/wiki/Uluwatu_Temple",
    "bali": "https://en.wikipedia.org/wiki/Uluwatu_Temple",
    "uluwatu temple": "https://en.wikipedia.org/wiki/Uluwatu_Temple",

    # 🇮🇪 Ireland
    "ireland": "https://en.wikipedia.org/wiki/Trinity_College_Dublin",
    "dublin": "https://en.wikipedia.org/wiki/Trinity_College_Dublin",

    # 🇮🇹 Italy
    "italy": "https://en.wikipedia.org/wiki/Colosseum",
    "rome": "https://en.wikipedia.org/wiki/Colosseum",
    "colosseum": "https://en.wikipedia.org/wiki/Colosseum",

    # 🇯🇵 Japan
    "japan": "https://en.wikipedia.org/wiki/Tokyo",
    "tokyo": "https://en.wikipedia.org/wiki/Tokyo",

    # 🇰🇪 Kenya
    "kenya": "https://en.wikipedia.org/wiki/Maasai_Mara",
    "nairobi": "https://en.wikipedia.org/wiki/Maasai_Mara",
    "maasai mara": "https://en.wikipedia.org/wiki/Maasai_Mara",

    # 🇲🇾 Malaysia
    "malaysia": "https://en.wikipedia.org/wiki/Petronas_Towers",
    "kuala lumpur": "https://en.wikipedia.org/wiki/Petronas_Towers",

    # 🇲🇻 Maldives
    "maldives": "https://en.wikipedia.org/wiki/Mal%C3%A9",
    "male": "https://en.wikipedia.org/wiki/Mal%C3%A9",

    # 🇲🇺 Mauritius
    "mauritius": "https://en.wikipedia.org/wiki/Port_Louis",
    "port louis": "https://en.wikipedia.org/wiki/Port_Louis",

    # 🇲🇽 Mexico
    "mexico": "https://en.wikipedia.org/wiki/Mexico_City",
    "mexico city": "https://en.wikipedia.org/wiki/Mexico_City",

    # 🇲🇦 Morocco
    "morocco": "https://en.wikipedia.org/wiki/Jardin_Majorelle",
    "marrakech": "https://en.wikipedia.org/wiki/Jardin_Majorelle",

    # 🇳🇵 Nepal
    "nepal": "https://en.wikipedia.org/wiki/Boudhanath",
    "kathmandu": "https://en.wikipedia.org/wiki/Boudhanath",

    # 🇳🇱 Netherlands
    "netherlands": "https://en.wikipedia.org/wiki/Amsterdam",
    "amsterdam": "https://en.wikipedia.org/wiki/Amsterdam",

    # 🇳🇿 New Zealand
    "new zealand": "https://en.wikipedia.org/wiki/Queenstown,_New_Zealand",
    "queenstown": "https://en.wikipedia.org/wiki/Queenstown,_New_Zealand",

    # 🇳🇴 Norway
    "norway": "https://en.wikipedia.org/wiki/Bergen",
    "bergen": "https://en.wikipedia.org/wiki/Bergen",

    # 🇴🇲 Oman
    "oman": "https://en.wikipedia.org/wiki/Sultan_Qaboos_Grand_Mosque",
    "muscat": "https://en.wikipedia.org/wiki/Sultan_Qaboos_Grand_Mosque",

    # 🇵🇪 Peru
    "peru": "https://en.wikipedia.org/wiki/Machu_Picchu",
    "cusco": "https://en.wikipedia.org/wiki/Machu_Picchu",
    "machu picchu": "https://en.wikipedia.org/wiki/Machu_Picchu",

    # 🇵🇭 Philippines
    "philippines": "https://en.wikipedia.org/wiki/Boracay",
    "boracay": "https://en.wikipedia.org/wiki/Boracay",

    # 🇵🇱 Poland
    "poland": "https://en.wikipedia.org/wiki/Wawel_Castle",
    "krakow": "https://en.wikipedia.org/wiki/Wawel_Castle",

    # 🇵🇹 Portugal
    "portugal": "https://en.wikipedia.org/wiki/Bel%C3%A9m_Tower",
    "lisbon": "https://en.wikipedia.org/wiki/Bel%C3%A9m_Tower",

    # 🇶🇦 Qatar
    "qatar": "https://en.wikipedia.org/wiki/Museum_of_Islamic_Art,_Doha",
    "doha": "https://en.wikipedia.org/wiki/Museum_of_Islamic_Art,_Doha",

    # 🇸🇦 Saudi Arabia
    "saudi arabia": "https://en.wikipedia.org/wiki/AlUla",
    "alula": "https://en.wikipedia.org/wiki/AlUla",

    # 🇸🇨 Seychelles
    "seychelles": "https://en.wikipedia.org/wiki/Mah%C3%A9,_Seychelles",
    "mahe": "https://en.wikipedia.org/wiki/Mah%C3%A9,_Seychelles",

    # 🇸🇬 Singapore
    "singapore": "https://en.wikipedia.org/wiki/Marina_Bay_Sands",

    # 🇿🇦 South Africa
    "south africa": "https://en.wikipedia.org/wiki/Table_Mountain",
    "cape town": "https://en.wikipedia.org/wiki/Table_Mountain",

    # 🇰🇷 South Korea
    "south korea": "https://en.wikipedia.org/wiki/Gyeongbokgung",
    "seoul": "https://en.wikipedia.org/wiki/Gyeongbokgung",

    # 🇪🇸 Spain
    "spain": "https://en.wikipedia.org/wiki/Sagrada_Fam%C3%ADlia",
    "barcelona": "https://en.wikipedia.org/wiki/Sagrada_Fam%C3%ADlia",

    # 🇱🇰 Sri Lanka
    "sri lanka": "https://en.wikipedia.org/wiki/Temple_of_the_Sacred_Tooth_Relic",
    "kandy": "https://en.wikipedia.org/wiki/Temple_of_the_Sacred_Tooth_Relic",

    # 🇸🇪 Sweden
    "sweden": "https://en.wikipedia.org/wiki/Gamla_stan",
    "stockholm": "https://en.wikipedia.org/wiki/Gamla_stan",

    # 🇨🇭 Switzerland
    "switzerland": "https://en.wikipedia.org/wiki/Matterhorn",
    "zermatt": "https://en.wikipedia.org/wiki/Matterhorn",

    # 🇹🇿 Tanzania
    "tanzania": "https://en.wikipedia.org/wiki/Stone_Town",
    "zanzibar": "https://en.wikipedia.org/wiki/Stone_Town",

    # 🇹🇭 Thailand
    "thailand": "https://en.wikipedia.org/wiki/Grand_Palace",
    "bangkok": "https://en.wikipedia.org/wiki/Grand_Palace",

    # 🇹🇷 Turkey
    "turkey": "https://en.wikipedia.org/wiki/Hagia_Sophia",
    "istanbul": "https://en.wikipedia.org/wiki/Hagia_Sophia",

    # 🇦🇪 UAE
    "uae": "https://en.wikipedia.org/wiki/Burj_Khalifa",
    "dubai": "https://en.wikipedia.org/wiki/Burj_Khalifa",

    # 🇺🇸 USA
    "usa": "https://en.wikipedia.org/wiki/Statue_of_Liberty",
    "new york": "https://en.wikipedia.org/wiki/Statue_of_Liberty",

    # 🇬🇧 United Kingdom
    "united kingdom": "https://en.wikipedia.org/wiki/Big_Ben",
    "london": "https://en.wikipedia.org/wiki/Big_Ben",

    # 🇻🇳 Vietnam
    "vietnam": "https://en.wikipedia.org/wiki/Ha_Long_Bay",
    "ha long bay": "https://en.wikipedia.org/wiki/Ha_Long_Bay"
}


def get_research_url(entity_name: str) -> str:
    """
    Returns verified Wikipedia / official research source URL for a country, destination, or landmark.
    """
    if not entity_name:
        return "https://en.wikipedia.org/wiki/Main_Page"
    
    clean_key = str(entity_name).lower().strip()
    
    for key, url in RESEARCH_URL_MAP.items():
        if key in clean_key or clean_key in key:
            return url

    return f"https://en.wikipedia.org/wiki/{entity_name.replace(' ', '_')}"
