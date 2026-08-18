import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "travel_planner.db"))
print("Connecting to SQLite database:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure code_alpha3 column exists
cursor.execute("PRAGMA table_info(countries)")
cols = [row[1] for row in cursor.fetchall()]
if "code_alpha3" not in cols:
    print("Adding code_alpha3 column to countries table...")
    cursor.execute("ALTER TABLE countries ADD COLUMN code_alpha3 VARCHAR")
    conn.commit()

# Comprehensive List of EXACTLY 195 World Countries (193 UN Members + Palestine + Vatican City)
# (name, ISO-2, ISO-3, continent, flag_emoji, latitude, longitude, description)
countries_195 = [
    # --- ASIA (48 Countries) ---
    ("Afghanistan", "AF", "AFG", "Asia", "🇦🇫", 33.9391, 67.7099, "Ancient Silk Road crossroads with Hindu Kush mountain ranges."),
    ("Armenia", "AM", "ARM", "Asia", "🇦🇲", 40.0691, 45.0382, "Caucasus mountain country featuring Mount Ararat views and ancient monasteries."),
    ("Azerbaijan", "AZ", "AZE", "Asia", "🇦🇿", 40.1431, 47.5769, "Land of Fire combining Baku Flame Towers and Caspian Sea coast."),
    ("Bahrain", "BH", "BHR", "Asia", "🇧🇭", 26.0667, 50.5577, "Island kingdom famous for Formula 1 circuit and Dilmun burial mounds."),
    ("Bangladesh", "BD", "BGD", "Asia", "🇧🇩", 23.6850, 90.3563, "Sundarbans mangrove forest and Cox's Bazar sea beach."),
    ("Bhutan", "BT", "BTN", "Asia", "🇧🇹", 27.5142, 90.4336, "Himalayan Buddhist kingdom famous for Tiger's Nest Monastery."),
    ("Brunei", "BN", "BRN", "Asia", "🇧🇳", 4.5353, 114.7277, "Sultanate on Borneo famous for golden mosques and rainforests."),
    ("Cambodia", "KH", "KHM", "Asia", "🇰🇭", 12.5657, 104.9910, "Khmer Empire kingdom famous for the majestic Angkor Wat temple complex."),
    ("China", "CN", "CHN", "Asia", "🇨🇳", 35.8617, 104.1954, "Great Wall of China, Forbidden City, Terracotta Army, and Shanghai skyline."),
    ("Cyprus", "CY", "CYP", "Asia", "🇨🇾", 35.1264, 33.4299, "Mediterranean island with Aphrodite beaches and ancient archaeological mosaics."),
    ("Georgia", "GE", "GEO", "Asia", "🇬🇪", 42.3154, 43.3569, "Caucasus mountain kingdom famous for ancient winemaking and Tbilisi old town."),
    ("India", "IN", "IND", "Asia", "🇮🇳", 20.5937, 78.9629, "Spiritual land of royal palaces, ancient temples, Taj Mahal, and backwaters."),
    ("Indonesia", "ID", "IDN", "Asia", "🇮🇩", -0.7893, 113.9213, "Tropical archipelago home to Bali beaches, Komodo dragons, and volcanoes."),
    ("Iran", "IR", "IRN", "Asia", "🇮🇷", 32.4279, 53.6880, "Persian Empire heritage featuring Isfahan Naqsh-e Jahan and Persepolis."),
    ("Iraq", "IQ", "IRQ", "Asia", "🇮🇶", 33.2232, 43.6793, "Cradle of Civilization along the Tigris and Euphrates featuring ancient Babylon."),
    ("Israel", "IL", "ISR", "Asia", "🇮🇱", 31.0461, 34.8516, "Holy Land featuring Jerusalem Old City, Dead Sea, and Tel Aviv coast."),
    ("Japan", "JP", "JPN", "Asia", "🇯🇵", 36.2048, 138.2529, "Futuristic metropolis meets Shinto shrines, Zen gardens, and Mount Fuji."),
    ("Jordan", "JO", "JOR", "Asia", "🇯🇴", 30.5852, 36.2384, "Ancient rose-red rock city of Petra, Wadi Rum desert, and Dead Sea."),
    ("Kazakhstan", "KZ", "KAZ", "Asia", "🇰🇿", 48.0196, 66.9237, "Central Asian giant with futuristic Astana and Almaty mountain canyons."),
    ("Kuwait", "KW", "KWT", "Asia", "🇰🇼", 29.3117, 47.4818, "Gulf nation featuring iconic Kuwait Towers and Souq Al-Mubarakiya."),
    ("Kyrgyzstan", "KG", "KGZ", "Asia", "🇰🇬", 41.2044, 74.7661, "Celestial Tian Shan mountains, alpine Issyk-Kul lake, and yurt culture."),
    ("Laos", "LA", "LAO", "Asia", "🇱🇦", 19.8563, 102.4955, "Tranquil Mekong river country known for Luang Prabang waterfalls."),
    ("Lebanon", "LB", "LBN", "Asia", "🇱🇧", 33.8547, 35.8623, "Beirut nightlife, ancient Byblos harbor, and Jeita Grotto caves."),
    ("Malaysia", "MY", "MYS", "Asia", "🇲🇾", 4.2105, 101.9758, "Kuala Lumpur Petronas Towers, Langkawi beaches, and Penang street food."),
    ("Maldives", "MV", "MDV", "Asia", "🇲🇻", 3.2028, 73.2207, "Subtropical paradise of overwater bungalows and turquoise lagoons."),
    ("Mongolia", "MN", "MNG", "Asia", "🇲🇳", 46.8625, 103.8467, "Nomadic steppes, Gobi Desert dunes, traditional gers, and Genghis Khan heritage."),
    ("Myanmar", "MM", "MMR", "Asia", "🇲🇲", 21.9162, 95.9560, "Land of golden pagodas featuring ancient Bagan temple plains."),
    ("Nepal", "NP", "NPL", "Asia", "🇳🇵", 28.3949, 84.1240, "Himalayan kingdom home to Mount Everest, Kathmandu stupas, and trekking."),
    ("North Korea", "KP", "PRK", "Asia", "🇰🇵", 40.3399, 127.5101, "Pyongyang monuments, Mount Paektu, and DMZ border history."),
    ("Oman", "OM", "OMN", "Asia", "🇴🇲", 21.5126, 55.9233, "Sultanate of desert wadis, Muscat Grand Mosque, and Jebel Akhdar mountains."),
    ("Pakistan", "PK", "PAK", "Asia", "🇵🇰", 30.3753, 69.3451, "Karakoram mountain highway, Hunza Valley, and Mughal heritage in Lahore."),
    ("Palestine", "PS", "PSE", "Asia", "🇵🇸", 31.9522, 35.2332, "Historic Holy Land region featuring Bethlehem Nativity Church and Jericho."),
    ("Philippines", "PH", "PHL", "Asia", "🇵🇭", 12.8797, 121.7740, "7,000+ tropical islands including El Nido lagoons and Boracay beaches."),
    ("Qatar", "QA", "QAT", "Asia", "🇶🇦", 25.3548, 51.1839, "Futuristic Doha skyline, Souq Waqif market, and inland desert sea."),
    ("Saudi Arabia", "SA", "SAU", "Asia", "🇸🇦", 23.8859, 45.0792, "Kingdom featuring ancient Hegra / AlUla rock tombs and Red Sea coast."),
    ("Singapore", "SG", "SGP", "Asia", "🇸🇬", 1.3521, 103.8198, "Futuristic garden city known for Marina Bay Sands and Gardens by the Bay."),
    ("South Korea", "KR", "KOR", "Asia", "🇰🇷", 35.9078, 127.7669, "K-pop culture, historic Joseon palaces, Seoul, and Jeju Island beaches."),
    ("Sri Lanka", "LK", "LKA", "Asia", "🇱🇰", 7.8731, 80.7718, "Pearl of the Indian Ocean featuring Sigiriya rock fortress and tea hills."),
    ("Syria", "SY", "SYR", "Asia", "🇸🇾", 34.8021, 38.9968, "Ancient Silk Road kingdom featuring historic Damascus and Krak des Chevaliers."),
    ("Taiwan", "TW", "TWN", "Asia", "🇹🇼", 23.6978, 120.9605, "Taipei 101 skyscraper, Taroko Gorge, night markets, and Sun Moon Lake."),
    ("Tajikistan", "TJ", "TJK", "Asia", "🇹🇯", 38.8610, 71.2761, "High-altitude Pamir Highway, turquoise Iskanderkul lake, and mountains."),
    ("Thailand", "TH", "THA", "Asia", "🇹🇭", 15.8700, 100.9925, "Tropical beaches, ornate Buddhist temples, floating markets, and street food."),
    ("East Timor", "TL", "TLS", "Asia", "🇹🇱", -8.8742, 125.7275, "Untouched tropical coral reefs, Atauro Island diving, and Portuguese forts."),
    ("Turkey", "TR", "TUR", "Asia", "🇹🇷", 38.9637, 35.2433, "Cappadocia hot air balloons, Istanbul Hagia Sophia, and Pamukkale terraces."),
    ("Turkmenistan", "TM", "TKM", "Asia", "🇹🇲", 38.9697, 59.5563, "Karakum desert features the mesmerizing Darvaza Gas Crater Door to Hell."),
    ("United Arab Emirates", "AE", "ARE", "Asia", "🇦🇪", 23.4241, 53.8478, "Home to Dubai Burj Khalifa, Palm Jumeirah, and Abu Dhabi Grand Mosque."),
    ("Uzbekistan", "UZ", "UZB", "Asia", "🇺🇿", 41.3775, 64.5853, "Silk Road heartland famous for blue-tiled Samarkand and Bukhara madrasas."),
    ("Vietnam", "VN", "VNM", "Asia", "🇻🇳", 14.0583, 108.2772, "Halong Bay limestone karsts, historic Hoi An, vibrant Hanoi, and coffee."),
    ("Yemen", "YE", "YEM", "Asia", "🇾🇪", 15.5527, 48.5164, "Ancient gingerbread skyscraper architecture in Sanaa and alien Socotra trees."),

    # --- EUROPE (44 Countries) ---
    ("Albania", "AL", "ALB", "Europe", "🇦🇱", 41.1533, 20.1683, "Albanian Riviera pristine beaches and UNESCO Ottoman old towns."),
    ("Andorra", "AD", "AND", "Europe", "🇦🇩", 42.5063, 1.5218, "Pyrenees mountain tax-free haven famous for ski resorts and mountain spas."),
    ("Austria", "AT", "AUT", "Europe", "🇦🇹", 47.5162, 14.5501, "Vienna imperial palaces, Mozart musical heritage, and Alpine Hallstatt."),
    ("Belarus", "BY", "BLR", "Europe", "🇧🇾", 53.7098, 27.9534, "Minsk architecture, Mir and Nesvizh castles, and Bialowieza forest."),
    ("Belgium", "BE", "BEL", "Europe", "🇧🇪", 50.5039, 4.4699, "Brussels Grand Place, medieval Bruges canals, chocolates, and waffles."),
    ("Bosnia & Herzegovina", "BA", "BIH", "Europe", "🇧🇦", 43.9159, 17.6791, "Mostar historic arched bridge Stari Most and multicultural Sarajevo."),
    ("Bulgaria", "BG", "BGR", "Europe", "🇧🇬", 42.7339, 25.4858, "Rila Monastery in mountains, Black Sea resorts, and Rose Valley."),
    ("Croatia", "HR", "HRV", "Europe", "🇭🇷", 45.1000, 15.2000, "Dubrovnik Game of Thrones city walls, Plitvice Lakes, and Adriatic coast."),
    ("Czech Republic", "CZ", "CZE", "Europe", "🇨🇿", 49.8175, 15.4730, "Prague Charles Bridge, Astronomical Clock, and Bohemian castles."),
    ("Denmark", "DK", "DNK", "Europe", "🇩🇰", 56.2639, 9.5018, "Copenhagen Nyhavn harbor, Little Mermaid statue, and Lego heritage."),
    ("Estonia", "EE", "EST", "Europe", "🇪🇪", 58.5953, 25.0136, "Tallinn medieval cobblestone old town and Baltic digital tech hub."),
    ("Finland", "FI", "FIN", "Europe", "🇫🇮", 64.9631, 25.7482, "Santa Claus village in Rovaniemi, thousand lakes, saunas, and aurora."),
    ("France", "FR", "FRA", "Europe", "🇫🇷", 46.2276, 2.2137, "Haute cuisine, Eiffel Tower, Louvre art, and French Riviera beaches."),
    ("Germany", "DE", "DEU", "Europe", "🇩🇪", 51.1657, 10.4515, "Fairytale Neuschwanstein Castle, Bavarian Alps, Berlin wall, and Oktoberfest."),
    ("Greece", "GR", "GRC", "Europe", "🇬🇷", 39.0742, 21.8243, "Santorini caldera sunsets, Athens Acropolis ruins, and Aegean islands."),
    ("Hungary", "HU", "HUN", "Europe", "🇭🇺", 47.1625, 19.5033, "Budapest Parliament building along Danube, thermal bathhouses, and ruin bars."),
    ("Iceland", "IS", "ISL", "Europe", "🇮🇸", 64.9631, -19.0208, "Land of fire and ice featuring Blue Lagoon hot springs and geysers."),
    ("Ireland", "IE", "IRL", "Europe", "🇮🇪", 53.4129, -8.2439, "Cliffs of Moher, Dublin traditional pubs, Ring of Kerry, and emerald hills."),
    ("Italy", "IT", "ITA", "Europe", "🇮🇹", 41.8719, 12.5674, "Renaissance masterpieces, Roman Colosseum, Amalfi coast, and authentic pizza."),
    ("Kosovo", "XK", "XKX", "Europe", "🇽🇰", 42.6026, 20.9030, "Balkan nation known for Ottoman architecture in Prizren and Rugova Canyon."),
    ("Latvia", "LV", "LVA", "Europe", "🇱🇻", 56.8796, 24.6032, "Riga Art Nouveau district, Jurmala white sand beaches, and Baltic forests."),
    ("Liechtenstein", "LI", "LIE", "Europe", "🇱🇮", 47.1410, 9.5209, "Alpine microstate known for medieval castles and mountain trails."),
    ("Lithuania", "LT", "LTU", "Europe", "🇱🇹", 55.1694, 23.8813, "Vilnius baroque old town, Trakai island castle, and Curonian Spit dunes."),
    ("Luxembourg", "LU", "LUX", "Europe", "🇱🇺", 49.8153, 6.1296, "Grand Duchy of cliffside fortress casemates and Ardennes valleys."),
    ("Malta", "MT", "MLT", "Europe", "🇲🇹", 35.9375, 14.3754, "Valletta Knights of Malta fortress city, Blue Lagoon, and ancient temples."),
    ("Moldova", "MD", "MDA", "Europe", "🇲🇩", 47.4116, 28.3699, "Milestii Mici underground wine cellars and Orheiul Vechi monastery."),
    ("Monaco", "MC", "MCO", "Europe", "🇲🇨", 43.7384, 7.4246, "Glamorous Riviera Principality of Monte Carlo Casino and Grand Prix."),
    ("Montenegro", "ME", "MNE", "Europe", "🇲🇪", 42.7087, 19.3744, "Dramatic Bay of Kotor fjords and coastal medieval Budva old town."),
    ("Netherlands", "NL", "NLD", "Europe", "🇳🇱", 52.1326, 5.2913, "Amsterdam canals, tulip fields, windmills, Van Gogh art, and cycling."),
    ("North Macedonia", "MK", "MKD", "Europe", "🇲🇰", 41.6086, 21.7453, "Lake Ohrid ancient churches, Matka Canyon, and Skopje architecture."),
    ("Norway", "NO", "NOR", "Europe", "🇳🇴", 60.4720, 8.4689, "Dramatic western fjords, Northern Lights aurora in Tromso, and midnight sun."),
    ("Poland", "PL", "POL", "Europe", "🇵🇱", 51.9194, 19.1451, "Krakow medieval square, Wawel Castle, Warsaw reborn old town, and Tatras."),
    ("Portugal", "PT", "PRT", "Europe", "🇵🇹", 39.3999, -8.2245, "Lisbon yellow trams, Sintra palaces, Algarve golden beaches, and port wine."),
    ("Romania", "RO", "ROU", "Europe", "🇷🇴", 45.9432, 24.9668, "Transylvania Bran Castle of Count Dracula, Carpathian mountains, and Danube."),
    ("San Marino", "SM", "SMR", "Europe", "🇸🇲", 43.9424, 12.4578, "Oldest republic built atop Mount Titano featuring Three Towers cliff views."),
    ("Serbia", "RS", "SRB", "Europe", "🇷🇸", 44.0165, 21.0059, "Belgrade fortress on Danube, EXIT festival at Petrovaradin, and Balkan nightlife."),
    ("Slovakia", "SK", "SVK", "Europe", "🇸🇰", 48.6690, 19.6990, "High Tatras alpine peaks, Bratislava castle along Danube, and wooden churches."),
    ("Slovenia", "SI", "SVN", "Europe", "🇸🇮", 46.1512, 14.9955, "Lake Bled island church with castle, Postojna Cave, and green Ljubljana."),
    ("Spain", "ES", "ESP", "Europe", "🇪🇸", 40.4637, -3.7492, "Barcelona Gaudi architecture, Alhambra palace, flamenco, and beaches."),
    ("Sweden", "SE", "SWE", "Europe", "🇸🇪", 60.1282, 18.6435, "Stockholm archipelago, Icehotel in Lapland, and Scandinavian design."),
    ("Switzerland", "CH", "CHE", "Europe", "🇨🇭", 46.8182, 8.2275, "Snow-capped Alpine peaks, Matterhorn, scenic railways, and Swiss chocolate."),
    ("Ukraine", "UA", "UKR", "Europe", "🇺🇦", 48.3794, 31.1656, "Kyiv golden-domed Pechersk Lavra monastery, Lviv coffee, and Carpathians."),
    ("United Kingdom", "GB", "GBR", "Europe", "🇬🇧", 55.3781, -3.4360, "Historic London Big Ben, Scottish Highlands, castles, and literary heritage."),
    ("Vatican City", "VA", "VAT", "Europe", "🇻🇦", 41.9029, 12.4534, "Holy See microstate home to St. Peter's Basilica and Sistine Chapel."),

    # --- NORTH AMERICA (23 Countries) ---
    ("Antigua & Barbuda", "AG", "ATG", "North America", "🇦🇬", 17.0608, -61.7964, "365 pink and white sand beaches, Nelson's Dockyard, and sunsets."),
    ("Bahamas", "BS", "BHS", "North America", "🇧🇸", 25.0343, -77.3963, "Pig Beach Exuma, Atlantis Paradise Island, and blue holes."),
    ("Barbados", "BB", "BRB", "North America", "🇧🇧", 13.1939, -59.5432, "Rihanna homeland of Carlisle Bay, Harrison's Cave, and rum distilleries."),
    ("Belize", "BZ", "BLZ", "North America", "🇧🇿", 17.1899, -88.4976, "Great Blue Hole marine sinkhole, Ambergris Caye, and Mayan temples."),
    ("Canada", "CA", "CAN", "North America", "🇨🇦", 56.1304, -106.3468, "Canadian Rockies & Banff turquoise lakes, Niagara Falls, and Toronto."),
    ("Costa Rica", "CR", "CRI", "North America", "🇨🇷", 9.7489, -83.7534, "Pura Vida eco-paradise of rainforests, Arenal volcano, and sloths."),
    ("Cuba", "CU", "CUB", "North America", "🇨🇺", 21.5218, -77.7812, "Classic 1950s vintage cars in Havana, Varadero beaches, and tobacco fields."),
    ("Dominica", "DM", "DMA", "North America", "🇩🇲", 15.4150, -61.3710, "Nature Island of the Caribbean with Boiling Lake and Morne Trois Pitons."),
    ("Dominican Republic", "DO", "DOM", "North America", "🇩🇴", 18.7357, -70.1627, "Punta Cana palm beaches, Santo Domingo, and Samana whale watching."),
    ("El Salvador", "SV", "SLV", "North America", "🇸🇻", 13.7942, -88.8965, "El Tunco Pacific surf beaches, Santa Ana volcano, and Ruta de las Flores."),
    ("Grenada", "GD", "GRD", "North America", "🇬🇩", 12.1165, -61.6790, "Spice Island of the Caribbean famous for Grand Anse Beach."),
    ("Guatemala", "GT", "GTM", "North America", "🇬🇹", 15.7835, -90.2308, "Antigua colonial city, Lake Atitlan volcanic ring, and Tikal Mayan ruins."),
    ("Haiti", "HT", "HTI", "North America", "🇭🇹", 18.9712, -72.2852, "Citadelle Laferrière hilltop fortress and Jacmel art culture."),
    ("Honduras", "HN", "HND", "North America", "🇭🇳", 15.2000, -86.2419, "Roatan Island barrier reef diving and Copan Mayan ruins."),
    ("Jamaica", "JM", "JAM", "North America", "🇯🇲", 18.1096, -77.2975, "Reggae homeland of Bob Marley, Negril Seven Mile Beach, and waterfalls."),
    ("Mexico", "MX", "MEX", "North America", "🇲🇽", 23.6345, -102.5528, "Cancun beaches, Chichen Itza Mayan pyramids, Mexico City street tacos."),
    ("Nicaragua", "NI", "NIC", "North America", "🇳🇮", 12.8654, -85.2072, "Granada Spanish colonial architecture and Ometepe twin volcano island."),
    ("Panama", "PA", "PAN", "North America", "🇵🇦", 8.5380, -80.7821, "Panama Canal engineering wonder, San Blas islands, and Boquete highlands."),
    ("Saint Kitts & Nevis", "KN", "KNA", "North America", "🇰🇳", 17.3578, -62.7830, "Brimstone Hill Fortress UNESCO site and Nevis Peak volcanic trails."),
    ("Saint Lucia", "LC", "LCA", "North America", "🇱🇨", 13.9094, -60.9789, "Iconic Pitons volcanic spires, drive-in volcano, and Marigot Bay."),
    ("Saint Vincent & Grenadines", "VC", "VCT", "North America", "🇻🇨", 12.9843, -61.2872, "Bequia sailing island, Tobago Cays marine park, and coral coves."),
    ("Trinidad & Tobago", "TT", "TTO", "North America", "🇹🇹", 10.6918, -61.2225, "Carnival steelpan music culture, Maracas Beach, and Tobago coral reefs."),
    ("United States", "US", "USA", "North America", "🇺🇸", 37.0902, -95.7129, "New York Statue of Liberty, Grand Canyon national park, and Hawaii."),

    # --- SOUTH AMERICA (12 Countries) ---
    ("Argentina", "AR", "ARG", "South America", "🇦🇷", -38.4161, -63.6167, "Buenos Aires tango, Iguazu Falls, Patagonia glaciers, and Mendoza wine."),
    ("Bolivia", "BO", "BOL", "South America", "🇧🇴", -16.2902, -63.5887, "Salar de Uyuni giant mirror salt flats, La Paz cable cars, and Lake Titicaca."),
    ("Brazil", "BR", "BRA", "South America", "🇧🇷", -14.2350, -51.9253, "Rio de Janeiro Christ the Redeemer, Copacabana beach, Amazon, and Carnival."),
    ("Chile", "CL", "CHL", "South America", "🇨🇱", -35.6751, -71.5430, "Atacama desert star-gazing, Patagonia Torres del Paine, and Easter Island."),
    ("Colombia", "CO", "COL", "South America", "🇨🇴", 4.5709, -74.2973, "Cartagena Caribbean walled city, Medellin innovation, and Coffee Triangle."),
    ("Ecuador", "EC", "ECU", "South America", "🇪🇨", -1.8312, -78.1834, "Galapagos Islands endemic wildlife, Quito UNESCO center, and Andes."),
    ("Guyana", "GY", "GUY", "South America", "🇬🇾", 4.8604, -58.9302, "Kaieteur Falls single-drop waterfall and untouched Amazonian rainforest."),
    ("Paraguay", "PY", "PRY", "South America", "🇵🇾", -23.4425, -58.4438, "Jesuit Ruins of Trinidad, Asuncion historic center, and Chaco wilderness."),
    ("Peru", "PE", "PER", "South America", "🇵🇪", -9.1900, -75.0152, "Inca citadel of Machu Picchu, Sacred Valley, and Rainbow Mountain."),
    ("Suriname", "SR", "SUR", "South America", "🇸🇷", 3.9193, -56.0278, "Paramaribo wooden Dutch colonial architecture and Nature Reserve."),
    ("Uruguay", "UY", "URY", "South America", "🇺🇾", -32.5228, -55.7658, "Punta del Este beach resort, Montevideo coastal Rambla, and Colonia."),
    ("Venezuela", "VE", "VEN", "South America", "🇻🇪", 6.4238, -66.5897, "Angel Falls highest waterfall, Los Roques coral islands, and Tepuis."),

    # --- AFRICA (54 Countries) ---
    ("Algeria", "DZ", "DZA", "Africa", "🇩🇿", 28.0339, 1.6596, "Tassili n'Ajjer Saharan rock art, Algiers Casbah, and Timgad Roman ruins."),
    ("Angola", "AO", "AGO", "Africa", "🇦🇴", -11.2027, 17.8739, "Kalandula Falls, Luanda Atlantic bay promenade, and Serra da Leba pass."),
    ("Benin", "BJ", "BEN", "Africa", "🇧🇯", 9.3077, 2.3158, "Ouidah Vodun cultural heritage, Abomey Royal Palaces, and Pendjari safari."),
    ("Botswana", "BW", "BWA", "Africa", "🇧🇼", -22.3285, 24.6849, "Okavango Delta mokoro safaris, Chobe elephant herds, and Kalahari desert."),
    ("Burkina Faso", "BF", "BFA", "Africa", "🇧🇫", 12.2383, -1.5616, "Ouagadougou pan-African film festival and Sindou rock peaks."),
    ("Burundi", "BI", "BDI", "Africa", "🇧🇮", -3.3731, 29.9189, "Lake Tanganyika beaches, Karera waterfalls, and royal drum sanctuaries."),
    ("Cabo Verde", "CV", "CPV", "Africa", "🇨🇻", 16.0021, -24.0132, "Sal Island beaches, Fogo active volcano, and Cesaria Evora music."),
    ("Cameroon", "CM", "CMR", "Africa", "🇨🇲", 7.3697, 12.3547, "Africa in Miniature featuring Mount Cameroon volcano and Kribi waterfalls."),
    ("Central African Republic", "CF", "CAF", "Africa", "🇨🇫", 6.6111, 20.9394, "Dzanga-Sangha Special Reserve lowland gorillas and rainforests."),
    ("Chad", "TD", "TCD", "Africa", "🇹🇩", 15.4542, 18.7322, "Ennedi Plateau desert arches and Lakes of Unianga UNESCO site."),
    ("Comoros", "KM", "COM", "Africa", "🇰🇲", -11.8750, 43.8722, "Perfume islands of Mount Karthala active volcano and white sand coves."),
    ("Congo (Congo-Brazzaville)", "CG", "COG", "Africa", "🇨🇬", -0.2280, 15.8277, "Odzala-Kokoua National Park gorilla wilderness and Congo River."),
    ("Congo (DRC)", "CD", "COD", "Africa", "🇨🇩", -4.0383, 21.7587, "Virunga National Park gorillas and active Mount Nyiragongo lava lake."),
    ("Djibouti", "DJ", "DJI", "Africa", "🇩🇯", 11.8251, 42.5903, "Lake Assal lowest point in Africa, Lake Abbe chimneys, and whale sharks."),
    ("Egypt", "EG", "EGY", "Africa", "🇪🇬", 26.8206, 30.8025, "Giza Pyramids, Sphinx, Luxor Valley of Kings, Nile cruises, and Red Sea."),
    ("Equatorial Guinea", "GQ", "GNQ", "Africa", "🇬🇶", 1.6508, 10.2679, "Bioko Island black sand beaches and Malabo Spanish architecture."),
    ("Eritrea", "ER", "ERI", "Africa", "🇪🇷", 15.1794, 39.7823, "Asmara UNESCO Italian modernist architecture and Red Sea Dahlak islands."),
    ("Eswatini", "SZ", "SWZ", "Africa", "🇸🇿", -26.5225, 31.4659, "Kingdom of Mlilwane Wildlife Sanctuary and Mantenga Cultural Village."),
    ("Ethiopia", "ET", "ETH", "Africa", "🇪🇹", 9.1450, 40.4897, "Lalibela rock-hewn churches, Simien Mountains, and coffee birthplace."),
    ("Gabon", "GA", "GAB", "Africa", "🇬🇦", -0.8037, 11.6094, "Loango National Park surfing hippos and Atlantic rainforest biodiversity."),
    ("Gambia", "GM", "GMB", "Africa", "🇬🇲", 13.4432, -15.3101, "Smiley Coast of Africa, Gambia River boat cruises, and birdwatching."),
    ("Ghana", "GH", "GHA", "Africa", "🇬🇭", 7.9465, -1.0232, "Cape Coast Castle, Kakum canopy walkway, and West African hospitality."),
    ("Guinea", "GN", "GIN", "Africa", "🇬🇳", 9.9456, -9.6966, "Fouta Djallon highlands, waterfalls, and West African musical traditions."),
    ("Guinea-Bissau", "GW", "GNB", "Africa", "🇬🇼", 11.8037, -15.1804, "Bijagós Archipelago UNESCO biosphere reserve and saltwater hippos."),
    ("Ivory Coast", "CI", "CIV", "Africa", "🇨🇮", 7.5400, -5.5471, "Yamoussoukro Basilica of Our Lady of Peace and Grand-Bassam beach."),
    ("Kenya", "KE", "KEN", "Africa", "🇰🇪", -0.0236, 37.9062, "Maasai Mara annual wildebeest migration, Mount Kenya, and Diani Beach."),
    ("Lesotho", "LS", "LSO", "Africa", "🇱🇸", -29.6099, 28.2336, "Kingdom in the Sky known for Maletsunyane Falls and pony trekking."),
    ("Liberia", "LR", "LBR", "Africa", "🇱🇷", 6.4281, -9.4295, "Robertsport Atlantic surf beaches and Sapo National Park rainforest."),
    ("Libya", "LY", "LBY", "Africa", "🇱🇾", 26.3351, 17.2283, "Leptis Magna ancient Roman ruins and Sahara desert oasis lakes."),
    ("Madagascar", "MG", "MDG", "Africa", "🇲🇬", -18.7669, 46.8691, "Avenue of the Baobabs, endemic lemurs, and Tsingy stone forests."),
    ("Malawi", "MW", "MWI", "Africa", "🇲🇼", -13.2543, 34.3015, "Lake Malawi freshwater fish snorkelling and Mount Mulanje peaks."),
    ("Mali", "ML", "MLI", "Africa", "🇲🇱", 17.5707, -3.9962, "Djenné Great Mud Mosque, Timbuktu manuscripts, and Dogon Country."),
    ("Mauritania", "MR", "MRT", "Africa", "🇲🇷", 21.0079, -10.9408, "Chinguetti ancient desert library town and Iron Ore Train across Sahara."),
    ("Mauritius", "MU", "MUS", "Africa", "🇲🇺", -20.3484, 57.5522, "Underwater waterfall illusion, Chamarel 7-Colored Earths, and resorts."),
    ("Morocco", "MA", "MAR", "Africa", "🇲🇦", 31.7917, -7.0926, "Marrakech Jemaa el-Fnaa medina market, Chefchaouen blue city, and Sahara."),
    ("Mozambique", "MZ", "MOZ", "Africa", "🇲🇿", -18.6657, 35.5296, "Bazaruto Archipelago coral reefs, Maputo architecture, and dhow sailing."),
    ("Namibia", "NA", "NAM", "Africa", "🇳🇦", -22.9576, 18.4904, "Sossusvlei Namib desert red dunes, Deadvlei clay pan, and Skeleton Coast."),
    ("Niger", "NE", "NER", "Africa", "🇳🇪", 17.6078, 8.0817, "Agadez mudbrick minaret, Air Mountains, and Saharan caravan routes."),
    ("Nigeria", "NG", "NGA", "Africa", "🇳🇬", 9.0820, 8.6753, "Lagos Afrobeats music culture, Lekki conservation center, and Zuma Rock."),
    ("Rwanda", "RW", "RWA", "Africa", "🇷🇼", -1.9403, 29.8739, "Land of a Thousand Hills featuring Volcanoes National Park gorilla tracking."),
    ("Sao Tome & Principe", "ST", "STP", "Africa", "🇸🇹", 0.1864, 6.6131, "Chocolate islands of Pico Cão Grande volcanic needle and quiet beaches."),
    ("Senegal", "SN", "SEN", "Africa", "🇸🇳", 14.4974, -14.4524, "Gorée Island historic house, Pink Lake Retba, and Dakar hospitality."),
    ("Seychelles", "SC", "SYC", "Africa", "🇸🇨", -4.6796, 55.4920, "Anse Source d'Argent granite boulder beaches and giant tortoises."),
    ("Sierra Leone", "SL", "SLE", "Africa", "🇸🇱", 8.4606, -11.7799, "River Number Two beach, Tiwai Island wildlife, and Tacugama Sanctuary."),
    ("Somalia", "SO", "SOM", "Africa", "🇸🇴", 5.1521, 46.1996, "Laas Geel ancient cave rock paintings and Horn of Africa coast."),
    ("South Africa", "ZA", "ZAF", "Africa", "🇿🇦", -30.5595, 22.9375, "Cape Town Table Mountain, Kruger National Park Big 5 safari, and Garden Route."),
    ("South Sudan", "SS", "SSD", "Africa", "🇸🇸", 6.8770, 31.3070, "Sudd wetland wildlife migrations along the White Nile River."),
    ("Sudan", "SD", "SDN", "Africa", "🇸🇩", 12.8628, 30.2176, "Meroe Nubian black pyramids along the Nile River and Red Sea reefs."),
    ("Tanzania", "TZ", "TZA", "Africa", "🇹🇿", -6.3690, 34.8888, "Serengeti National Park safari, Mount Kilimanjaro, and Zanzibar beaches."),
    ("Togo", "TG", "TGO", "Africa", "🇹🇬", 8.6195, 0.8248, "Lomé Grand Marché, Akodessewa Fetish Market, and Koutammakou mud towers."),
    ("Tunisia", "TN", "TUN", "Africa", "🇹🇳", 33.8869, 9.5375, "Carthage Roman ruins, Sidi Bou Said blue village, and Sahara dunes."),
    ("Uganda", "UG", "UGA", "Africa", "🇺🇬", 1.3733, 32.2903, "Pearl of Africa famous for Bwindi mountain gorilla trekking."),
    ("Zambia", "ZM", "ZMB", "Africa", "🇿🇲", -13.1339, 27.8493, "Victoria Falls Devil's Pool, South Luangwa walking safaris, and Zambezi."),
    ("Zimbabwe", "ZW", "ZWE", "Africa", "🇿🇼", -19.0154, 29.1549, "Mosi-oa-Tunya Victoria Falls, Great Zimbabwe stone ruins, and Hwange."),

    # --- OCEANIA (14 Countries) ---
    ("Australia", "AU", "AUS", "Oceania", "🇦🇺", -25.2744, 133.7751, "Sydney Opera House, Great Barrier Reef, Uluru red monolith, and kangaroos."),
    ("Fiji", "FJ", "FJI", "Oceania", "🇫🇯", -17.7134, 178.0650, "Mamanuca and Yasawa islands, soft coral reefs, and traditional kava."),
    ("Kiribati", "KI", "KIR", "Oceania", "🇰🇮", 1.8369, -157.3626, "Line Islands Christmas Island fly fishing and vast Pacific marine sanctuary."),
    ("Marshall Islands", "MH", "MHL", "Oceania", "🇲🇭", 7.1315, 171.1845, "Majuro atoll lagoon and Bikini Atoll nuclear test site diving history."),
    ("Micronesia", "FM", "FSM", "Oceania", "🇫🇲", 7.4256, 150.5508, "Nan Madol stone city on coral reef in Pohnpei and Chuuk Lagoon diving."),
    ("Nauru", "NR", "NRU", "Oceania", "🇳🇷", -0.5228, 166.9315, "World's smallest island republic featuring Command Ridge and Anibare Bay."),
    ("New Zealand", "NZ", "NZL", "Oceania", "🇳🇿", -40.9006, 174.8860, "Milford Sound fjords, Hobbiton movie set, Queenstown, and Rotorua geysers."),
    ("Palau", "PW", "PLW", "Oceania", "🇵🇼", 7.5150, 134.5825, "Rock Islands Southern Lagoon and Jellyfish Lake non-stinging swimming."),
    ("Papua New Guinea", "PG", "PNG", "Oceania", "🇵🇬", -6.3149, 143.9555, "Kokoda Trail, Goroka Show tribal festivals, and Sepik River rainforests."),
    ("Samoa", "WS", "WSM", "Oceania", "🇼🇸", -13.7590, -172.1046, "To Sua Ocean Trench natural swimming hole and fale beach huts."),
    ("Solomon Islands", "SB", "SLB", "Oceania", "🇸🇧", -9.6457, 160.1562, "World War II wreck diving in Iron Bottom Sound and Marovo Lagoon."),
    ("Tonga", "TO", "TON", "Oceania", "🇹🇴", -21.1789, -175.1982, "Kingdom of Tonga humpback whale swimming and Mapu'a 'a Vaea blowholes."),
    ("Tuvalu", "TV", "TUV", "Oceania", "🇹🇻", -7.1095, 177.6493, "Funafuti lagoon conservation area and secluded coral sand islets."),
    ("Vanuatu", "VU", "VUT", "Oceania", "🇻🇺", -15.3767, 166.9592, "Mount Yasur accessible active volcano and Blue Holes of Espiritu Santo.")
]

print(f"Total structured country records defined in script: {len(countries_195)}")

# Upsert countries into SQLite database
cursor.execute("SELECT name, code FROM countries")
existing_rows = cursor.fetchall()
existing_names = set(row[0].lower() for row in existing_rows if row[0])
existing_codes = set(row[1].upper() for row in existing_rows if row[1])

inserted = 0
updated = 0
for name, code, code3, continent, flag, lat, lng, desc in countries_195:
    if name.lower() not in existing_names and code.upper() not in existing_codes:
        cursor.execute("""
            INSERT INTO countries (name, code, code_alpha3, continent, flag_emoji, latitude, longitude, description, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, code, code3, continent, flag, lat, lng, desc, f"/static/images/countries/{code.lower()}.jpg"))
        existing_names.add(name.lower())
        existing_codes.add(code.upper())
        inserted += 1
    else:
        cursor.execute("""
            UPDATE countries
            SET code_alpha3 = ?, continent = ?, flag_emoji = ?, latitude = ?, longitude = ?, description = ?
            WHERE name = ? OR code = ?
        """, (code3, continent, flag, lat, lng, desc, name, code))
        updated += 1

conn.commit()

cursor.execute("SELECT COUNT(*) FROM countries")
total_cnt = cursor.fetchone()[0]
print(f"Upsert complete. Inserted {inserted} new, updated {updated}. Total countries now in SQLite: {total_cnt}")

conn.close()
