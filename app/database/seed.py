import os
from sqlalchemy.orm import Session
from app.database.models import Country, Destination, Place, Stay, FoodSpot, LocalFood, Transport


def seed_data(db: Session):
    """
    Seeds a massive international travel dataset across Asia, Europe, Americas,
    Africa, Oceania, and Middle East.
    Uses safe INSERT operations without wiping or recreating data/travel_planner.db.
    """
    countries_data = [
        # --- ASIA ---
        {
            "name": "India", "code": "IN", "continent": "Asia", "flag_emoji": "🇮🇳",
            "latitude": 20.5937, "longitude": 78.9629,
            "description": "Spiritual land of royal palaces, ancient temples, backwaters, and rich culinary traditions.",
            "destinations": [
                {"name": "Delhi", "state": "Delhi", "region": "North", "country": "India", "description": "India's historic capital blending Mughal monuments, colonial architecture, and street markets.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 6000.0},
                {"name": "Agra", "state": "Uttar Pradesh", "region": "North", "country": "India", "description": "Home to the Taj Mahal and grand Mughal architecture along the Yamuna River.", "best_time": "November to March", "recommended_days": 2, "approximate_budget": 4500.0},
                {"name": "Jaipur", "state": "Rajasthan", "region": "North", "country": "India", "description": "The Pink City of Rajasthan, famous for Amber Fort, royal palaces, and Rajput heritage.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 5000.0},
                {"name": "Mumbai", "state": "Maharashtra", "region": "West", "country": "India", "description": "Financial capital and Bollywood metropolis on the Arabian Sea.", "best_time": "November to February", "recommended_days": 3, "approximate_budget": 6500.0},
                {"name": "Bengaluru", "state": "Karnataka", "region": "South", "country": "India", "description": "Garden city tech hub famous for pleasant climate, microbreweries, and botanical parks.", "best_time": "October to February", "recommended_days": 3, "approximate_budget": 5500.0},
                {"name": "Hyderabad", "state": "Telangana", "region": "South", "country": "India", "description": "City of Pearls famous for Charminar, Golconda Fort, and world-renowned biryani.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 5500.0},
                {"name": "Chennai", "state": "Tamil Nadu", "region": "South", "country": "India", "description": "Gateway to South India known for Marina Beach, Dravidian temples, and Carnatic music.", "best_time": "November to February", "recommended_days": 3, "approximate_budget": 5000.0},
                {"name": "Kolkata", "state": "West Bengal", "region": "East", "country": "India", "description": "Cultural capital famous for Howrah Bridge, colonial architecture, and sweet delicacies.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 4800.0},
                {"name": "Goa", "state": "Goa", "region": "South", "country": "India", "description": "Sun-drenched beaches, Portuguese churches, and vibrant coastal night markets.", "best_time": "November to February", "recommended_days": 4, "approximate_budget": 7000.0},
                {"name": "Varanasi", "state": "Uttar Pradesh", "region": "North", "country": "India", "description": "Ancient spiritual city on the sacred Ganges River famous for Ganga Aarti.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 4000.0},
                {"name": "Udaipur", "state": "Rajasthan", "region": "North", "country": "India", "description": "City of Lakes featuring Lake Pichola, royal Lake Palace, and romantic sunsets.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 6000.0},
                {"name": "Jodhpur", "state": "Rajasthan", "region": "North", "country": "India", "description": "The Blue City dominated by the massive hilltop Mehrangarh Fort.", "best_time": "October to March", "recommended_days": 2, "approximate_budget": 4500.0},
                {"name": "Amritsar", "state": "Punjab", "region": "North", "country": "India", "description": "Spiritual home of the Golden Temple and rich Punjabi culinary heritage.", "best_time": "October to March", "recommended_days": 2, "approximate_budget": 4000.0},
                {"name": "Rishikesh", "state": "Uttarakhand", "region": "North", "country": "India", "description": "Yoga capital of the world situated in the Himalayan foothills along the Ganges.", "best_time": "September to May", "recommended_days": 3, "approximate_budget": 4500.0},
                {"name": "Manali", "state": "Himachal Pradesh", "region": "North", "country": "India", "description": "High-altitude Himalayan resort town famous for Solang Valley adventure sports.", "best_time": "October to June", "recommended_days": 4, "approximate_budget": 6500.0},
                {"name": "Shimla", "state": "Himachal Pradesh", "region": "North", "country": "India", "description": "Former British summer capital featuring colonial Mall Road and Toy Train.", "best_time": "March to June / Dec to Jan", "recommended_days": 3, "approximate_budget": 5500.0},
                {"name": "Srinagar", "state": "Jammu & Kashmir", "region": "North", "country": "India", "description": "Paradise on Earth featuring Dal Lake houseboats and Shikara rides.", "best_time": "April to October", "recommended_days": 4, "approximate_budget": 8000.0},
                {"name": "Kochi", "state": "Kerala", "region": "South", "country": "India", "description": "Port city blending Chinese fishing nets, Portuguese synagogues, and Spice markets.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 5500.0},
                {"name": "Munnar", "state": "Kerala", "region": "South", "country": "India", "description": "Lush Western Ghats hill station famous for rolling tea plantations and mist.", "best_time": "September to May", "recommended_days": 3, "approximate_budget": 5000.0},
                {"name": "Ooty", "state": "Tamil Nadu", "region": "South", "country": "India", "description": "Queen of Nilgiri Hill Stations famous for Botanical Gardens and mountain railway.", "best_time": "October to June", "recommended_days": 3, "approximate_budget": 4800.0},
                {"name": "Mysuru", "state": "Karnataka", "region": "South", "country": "India", "description": "Heritage city famous for illuminated Mysore Palace and Dasara festivals.", "best_time": "October to March", "recommended_days": 2, "approximate_budget": 4500.0},
                {"name": "Pune", "state": "Maharashtra", "region": "West", "country": "India", "description": "Cultural capital of Maharashtra, Maratha forts, and thriving student culture.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 5000.0},
                {"name": "Ahmedabad", "state": "Gujarat", "region": "West", "country": "India", "description": "UNESCO World Heritage city famous for Sabarmati Ashram and textile heritage.", "best_time": "October to March", "recommended_days": 2, "approximate_budget": 4200.0},
                {"name": "Surat", "state": "Gujarat", "region": "West", "country": "India", "description": "Diamond and textile hub famous for street food and coastal forts.", "best_time": "October to March", "recommended_days": 2, "approximate_budget": 4000.0},
                {"name": "Bhubaneswar", "state": "Odisha", "region": "East", "country": "India", "description": "Temple City of India renowned for Lingaraj Temple and ancient Kalinga art.", "best_time": "October to March", "recommended_days": 2, "approximate_budget": 4000.0},
                {"name": "Visakhapatnam", "state": "Andhra Pradesh", "region": "South", "country": "India", "description": "Coastal port city known for RK Beach, Submarine Museum, and Kailasagiri.", "best_time": "October to March", "recommended_days": 3, "approximate_budget": 4500.0},
                {"name": "Amalapuram", "state": "Andhra Pradesh", "region": "South", "country": "India", "description": "Picturesque Konaseema coconut groves, lush delta backwaters, and river ghats.", "best_time": "November to February", "recommended_days": 2, "approximate_budget": 3500.0},
                {"name": "Tirupati", "state": "Andhra Pradesh", "region": "South", "country": "India", "description": "World-renowned pilgrimage center home to Sri Venkateswara Swamy Temple.", "best_time": "September to March", "recommended_days": 2, "approximate_budget": 3500.0},
                {"name": "Vijayawada", "state": "Andhra Pradesh", "region": "South", "country": "India", "description": "Commercial city along Krishna River featuring Kanaka Durga Temple and Undavalli Caves.", "best_time": "October to March", "recommended_days": 2, "approximate_budget": 4000.0},
                {"name": "Araku Valley", "state": "Andhra Pradesh", "region": "South", "country": "India", "description": "Scenic hill station in Eastern Ghats famous for coffee plantations and Borra Caves.", "best_time": "September to February", "recommended_days": 2, "approximate_budget": 3800.0}
            ]
        },
        {
            "name": "Japan", "code": "JP", "continent": "Asia", "flag_emoji": "🇯🇵",
            "latitude": 36.2048, "longitude": 138.2529,
            "description": "Futuristic metropolis meets Shinto shrines, Zen gardens, and Mount Fuji views.",
            "destinations": [
                {"name": "Tokyo", "state": "Kanto", "region": "East Asia", "country": "Japan", "description": "Ultra-modern capital featuring Shibuya Crossing, Senso-ji temple, and anime culture.", "best_time": "March to May / Oct to Nov", "recommended_days": 4, "approximate_budget": 18000.0},
                {"name": "Kyoto", "state": "Kansai", "region": "East Asia", "country": "Japan", "description": "Cultural heart of Japan known for thousand torii gates, wooden temples, and geishas.", "best_time": "March to May", "recommended_days": 3, "approximate_budget": 15000.0},
                {"name": "Osaka", "state": "Kansai", "region": "East Asia", "country": "Japan", "description": "Japan's street food capital featuring Dotonbori neon lights and Osaka Castle.", "best_time": "March to May", "recommended_days": 3, "approximate_budget": 14000.0},
                {"name": "Hiroshima", "state": "Chugoku", "region": "East Asia", "country": "Japan", "description": "Peace Memorial Park and iconic floating torii gate at Miyajima Island.", "best_time": "April to May", "recommended_days": 2, "approximate_budget": 12000.0},
                {"name": "Nara", "state": "Kansai", "region": "East Asia", "country": "Japan", "description": "Ancient capital famous for free-roaming deer and Todai-ji Great Buddha temple.", "best_time": "March to May", "recommended_days": 2, "approximate_budget": 10000.0},
                {"name": "Sapporo", "state": "Hokkaido", "region": "East Asia", "country": "Japan", "description": "Northern island capital known for winter Snow Festival and ramen street.", "best_time": "December to February", "recommended_days": 3, "approximate_budget": 16000.0},
                {"name": "Fukuoka", "state": "Kyushu", "region": "East Asia", "country": "Japan", "description": "Southern coastal culinary city famous for open-air Yatai ramen food stalls.", "best_time": "October to April", "recommended_days": 3, "approximate_budget": 13000.0},
                {"name": "Okinawa", "state": "Okinawa", "region": "East Asia", "country": "Japan", "description": "Subtropical tropical island chain featuring coral reefs and Ryukyu culture.", "best_time": "May to October", "recommended_days": 4, "approximate_budget": 17000.0}
            ]
        },
        {
            "name": "France", "code": "FR", "continent": "Europe", "flag_emoji": "🇫🇷",
            "latitude": 46.2276, "longitude": 2.2137,
            "description": "Haute cuisine, world-class art museums, romantic castles, and French Riviera beaches.",
            "destinations": [
                {"name": "Paris", "state": "Île-de-France", "region": "Western Europe", "country": "France", "description": "City of Light featuring Eiffel Tower, Louvre, Notre-Dame, and Seine cruises.", "best_time": "June to August", "recommended_days": 4, "approximate_budget": 22000.0},
                {"name": "Nice", "state": "Provence-Alpes-Côte d'Azur", "region": "Western Europe", "country": "France", "description": "Capital of the French Riviera with Promenade des Anglais and turquoise Mediterranean waters.", "best_time": "May to September", "recommended_days": 3, "approximate_budget": 20000.0},
                {"name": "Lyon", "state": "Auvergne-Rhône-Alpes", "region": "Western Europe", "country": "France", "description": "Gastronomic capital of France famous for traditional Traboules secret passageways.", "best_time": "April to October", "recommended_days": 3, "approximate_budget": 18000.0},
                {"name": "Marseille", "state": "Provence-Alpes-Côte d'Azur", "region": "Western Europe", "country": "France", "description": "Historic port city featuring Vieux-Port and dramatic limestone Calanques cliffs.", "best_time": "May to October", "recommended_days": 3, "approximate_budget": 17000.0},
                {"name": "Bordeaux", "state": "Nouvelle-Aquitaine", "region": "Western Europe", "country": "France", "description": "World wine capital surrounded by grand 18th-century mansions and vineyards.", "best_time": "May to October", "recommended_days": 3, "approximate_budget": 19000.0},
                {"name": "Strasbourg", "state": "Grand Est", "region": "Western Europe", "country": "France", "description": "Alsatian fairytale town with timbered houses and famous Christmas markets.", "best_time": "November to December", "recommended_days": 2, "approximate_budget": 16000.0},
                {"name": "Cannes", "state": "Provence-Alpes-Côte d'Azur", "region": "Western Europe", "country": "France", "description": "Glamorous resort town famous for its annual International Film Festival and beach resorts.", "best_time": "May to September", "recommended_days": 2, "approximate_budget": 25000.0}
            ]
        },
        {
            "name": "Italy", "code": "IT", "continent": "Europe", "flag_emoji": "🇮🇹",
            "latitude": 41.8719, "longitude": 12.5674,
            "description": "Renaissance masterpieces, Roman ruins, Mediterranean coastlines, and authentic pizza.",
            "destinations": [
                {"name": "Rome", "state": "Lazio", "region": "Southern Europe", "country": "Italy", "description": "Eternal City featuring the Colosseum, Pantheon, Trevi Fountain, and Vatican City.", "best_time": "April to May / Sept to Oct", "recommended_days": 4, "approximate_budget": 20000.0},
                {"name": "Venice", "state": "Veneto", "region": "Southern Europe", "country": "Italy", "description": "Floating city of canals, gondolas, St. Mark's Basilica, and Rialto Bridge.", "best_time": "April to June", "recommended_days": 3, "approximate_budget": 22000.0},
                {"name": "Milan", "state": "Lombardy", "region": "Southern Europe", "country": "Italy", "description": "Global fashion capital featuring gothic Duomo di Milano and Da Vinci's Last Supper.", "best_time": "April to May", "recommended_days": 3, "approximate_budget": 21000.0},
                {"name": "Florence", "state": "Tuscany", "region": "Southern Europe", "country": "Italy", "description": "Cradle of the Renaissance home to Michelangelo's David and Uffizi Gallery.", "best_time": "May to September", "recommended_days": 3, "approximate_budget": 19000.0},
                {"name": "Naples", "state": "Campania", "region": "Southern Europe", "country": "Italy", "description": "Birthplace of Neapolitan pizza near historic Mount Vesuvius and Pompeii.", "best_time": "April to October", "recommended_days": 3, "approximate_budget": 15000.0},
                {"name": "Amalfi", "state": "Campania", "region": "Southern Europe", "country": "Italy", "description": "Dramatic cliffside coastal village overlooking pastel houses and Tyrrhenian Sea.", "best_time": "May to September", "recommended_days": 3, "approximate_budget": 28000.0},
                {"name": "Pisa", "state": "Tuscany", "region": "Southern Europe", "country": "Italy", "description": "Famous for the iconic Leaning Tower of Pisa and Piazza dei Miracoli.", "best_time": "April to October", "recommended_days": 1, "approximate_budget": 12000.0}
            ]
        },
        {
            "name": "Switzerland", "code": "CH", "continent": "Europe", "flag_emoji": "🇨🇭",
            "latitude": 46.8182, "longitude": 8.2275,
            "description": "Snow-capped Alpine peaks, crystal clear lakes, scenic mountain railways, and Swiss chocolate.",
            "destinations": [
                {"name": "Zurich", "state": "Zurich", "region": "Central Europe", "country": "Switzerland", "description": "Lakeside banking capital combining medieval Old Town with Alpine mountain backdrops.", "best_time": "June to August", "recommended_days": 3, "approximate_budget": 28000.0},
                {"name": "Geneva", "state": "Geneva", "region": "Central Europe", "country": "Switzerland", "description": "Diplomatic center home to UN headquarters, Jet d'Eau fountain, and Lake Geneva.", "best_time": "May to September", "recommended_days": 3, "approximate_budget": 27000.0},
                {"name": "Lucerne", "state": "Lucerne", "region": "Central Europe", "country": "Switzerland", "description": "Picturesque town featuring Chapel Bridge and Mount Pilatus cable car rides.", "best_time": "June to September", "recommended_days": 2, "approximate_budget": 25000.0},
                {"name": "Interlaken", "state": "Bern", "region": "Central Europe", "country": "Switzerland", "description": "Adventure sports capital sandwiched between Lake Thun and Lake Brienz near Jungfraujoch.", "best_time": "June to September", "recommended_days": 3, "approximate_budget": 29000.0},
                {"name": "Bern", "state": "Bern", "region": "Central Europe", "country": "Switzerland", "description": "Swiss capital with UNESCO preserved medieval sandstone arcades and bear park.", "best_time": "May to October", "recommended_days": 2, "approximate_budget": 24000.0},
                {"name": "Zermatt", "state": "Valais", "region": "Central Europe", "country": "Switzerland", "description": "Car-free Alpine village situated directly under the iconic pyramid-shaped Matterhorn.", "best_time": "December to April / July to Aug", "recommended_days": 3, "approximate_budget": 32000.0}
            ]
        },
        {
            "name": "United Kingdom", "code": "GB", "continent": "Europe", "flag_emoji": "🇬🇧",
            "latitude": 55.3781, "longitude": -3.4360,
            "description": "Royal palaces, Big Ben, red buses, historic universities, and picturesque countryside.",
            "destinations": [
                {"name": "London", "state": "England", "region": "Western Europe", "country": "United Kingdom", "description": "Historic British capital featuring Big Ben, Tower Bridge, and West End theatre.", "best_time": "May to September", "recommended_days": 4, "approximate_budget": 25000.0},
                {"name": "Edinburgh", "state": "Scotland", "region": "Western Europe", "country": "United Kingdom", "description": "Scottish capital featuring hilltop Edinburgh Castle and historic Royal Mile.", "best_time": "May to August", "recommended_days": 3, "approximate_budget": 22000.0},
                {"name": "Manchester", "state": "England", "region": "Western Europe", "country": "United Kingdom", "description": "Industrial heritage powerhouse famous for football, music, and Northern Quarter cafes.", "best_time": "May to September", "recommended_days": 2, "approximate_budget": 18000.0},
                {"name": "Liverpool", "state": "England", "region": "Western Europe", "country": "United Kingdom", "description": "Maritime city world-famous as the birthplace of The Beatles.", "best_time": "May to September", "recommended_days": 2, "approximate_budget": 17000.0},
                {"name": "Bath", "state": "England", "region": "Western Europe", "country": "United Kingdom", "description": "Famous for ancient Roman Baths and elegant Georgian honey-colored stone architecture.", "best_time": "April to October", "recommended_days": 2, "approximate_budget": 19000.0},
                {"name": "Oxford", "state": "England", "region": "Western Europe", "country": "United Kingdom", "description": "City of Dreaming Spires home to the oldest university in the English-speaking world.", "best_time": "May to September", "recommended_days": 2, "approximate_budget": 18000.0},
                {"name": "Cambridge", "state": "England", "region": "Western Europe", "country": "United Kingdom", "description": "University town famous for punting on the River Cam and King's College Chapel.", "best_time": "May to September", "recommended_days": 2, "approximate_budget": 18000.0}
            ]
        },
        {
            "name": "USA", "code": "US", "continent": "Americas", "flag_emoji": "🇺🇸",
            "latitude": 37.0902, "longitude": -95.7129,
            "description": "Iconic skylines, Grand Canyon national parks, Hollywood entertainment, and coastal beaches.",
            "destinations": [
                {"name": "New York City", "state": "New York", "region": "North America", "country": "USA", "description": "The Big Apple featuring Times Square, Central Park, Statue of Liberty, and Broadway.", "best_time": "September to November", "recommended_days": 4, "approximate_budget": 30000.0},
                {"name": "Los Angeles", "state": "California", "region": "North America", "country": "USA", "description": "Entertainment capital featuring Hollywood Walk of Fame, Santa Monica Pier, and Beverly Hills.", "best_time": "March to May / Sept to Nov", "recommended_days": 4, "approximate_budget": 28000.0},
                {"name": "San Francisco", "state": "California", "region": "North America", "country": "USA", "description": "Golden Gate Bridge, historic cable cars, Fisherman's Wharf, and Alcatraz Island.", "best_time": "September to November", "recommended_days": 3, "approximate_budget": 29000.0},
                {"name": "Las Vegas", "state": "Nevada", "region": "North America", "country": "USA", "description": "Entertainment capital of the world famous for the Strip, resorts, and nightlife.", "best_time": "March to May / Sept to Nov", "recommended_days": 3, "approximate_budget": 25000.0},
                {"name": "Chicago", "state": "Illinois", "region": "North America", "country": "USA", "description": "Windy City famous for Willis Tower, Millennium Park Bean, deep-dish pizza, and jazz.", "best_time": "June to August", "recommended_days": 3, "approximate_budget": 24000.0},
                {"name": "Miami", "state": "Florida", "region": "North America", "country": "USA", "description": "Vibrant coastal city famous for South Beach, Art Deco architecture, and nightlife.", "best_time": "December to April", "recommended_days": 3, "approximate_budget": 26000.0},
                {"name": "Orlando", "state": "Florida", "region": "North America", "country": "USA", "description": "Theme park capital of the world featuring Walt Disney World and Universal Studios.", "best_time": "January to April", "recommended_days": 4, "approximate_budget": 27000.0},
                {"name": "Seattle", "state": "Washington", "region": "North America", "country": "USA", "description": "Pacific Northwest emerald city home to Space Needle and Pike Place Market.", "best_time": "June to September", "recommended_days": 3, "approximate_budget": 25000.0},
                {"name": "Boston", "state": "Massachusetts", "region": "North America", "country": "USA", "description": "Historic New England city featuring Freedom Trail, Harvard University, and seafood.", "best_time": "June to October", "recommended_days": 3, "approximate_budget": 24000.0},
                {"name": "Washington DC", "state": "District of Columbia", "region": "North America", "country": "USA", "description": "US capital featuring US Capitol, White House, and free Smithsonian Museums.", "best_time": "March to May / Sept to Nov", "recommended_days": 3, "approximate_budget": 23000.0},
                {"name": "Honolulu", "state": "Hawaii", "region": "North America", "country": "USA", "description": "Capital of Hawaii featuring Waikiki Beach, Pearl Harbor, and Diamond Head volcano.", "best_time": "April to October", "recommended_days": 5, "approximate_budget": 35000.0}
            ]
        },
        {
            "name": "UAE", "code": "AE", "continent": "Asia", "flag_emoji": "🇦🇪",
            "latitude": 23.4241, "longitude": 53.8478,
            "description": "Futuristic desert oasis known for Burj Khalifa, luxury shopping malls, and desert safaris.",
            "destinations": [
                {"name": "Dubai", "state": "Dubai", "region": "Middle East", "country": "UAE", "description": "Ultramodern city famous for Burj Khalifa, Palm Jumeirah, and luxury living.", "best_time": "November to March", "recommended_days": 4, "approximate_budget": 24000.0},
                {"name": "Abu Dhabi", "state": "Abu Dhabi", "region": "Middle East", "country": "UAE", "description": "UAE capital home to Sheikh Zayed Grand Mosque and Louvre Abu Dhabi.", "best_time": "November to March", "recommended_days": 3, "approximate_budget": 23000.0},
                {"name": "Sharjah", "state": "Sharjah", "region": "Middle East", "country": "UAE", "description": "Cultural capital of the Arab world featuring heritage museums and Islamic art.", "best_time": "November to March", "recommended_days": 2, "approximate_budget": 15000.0},
                {"name": "Ras Al Khaimah", "state": "Ras Al Khaimah", "region": "Middle East", "country": "UAE", "description": "Northern emirate featuring Jebel Jais mountain zipline and desert dunes.", "best_time": "November to March", "recommended_days": 2, "approximate_budget": 18000.0}
            ]
        },
        {
            "name": "Thailand", "code": "TH", "continent": "Asia", "flag_emoji": "🇹🇭",
            "latitude": 15.8700, "longitude": 100.9925,
            "description": "Tropical paradise of golden Buddhist temples, limestone island beaches, and spicy street food.",
            "destinations": [
                {"name": "Bangkok", "state": "Bangkok", "region": "Southeast Asia", "country": "Thailand", "description": "Bustling capital known for Grand Palace, floating night markets, and street food.", "best_time": "November to February", "recommended_days": 3, "approximate_budget": 8000.0},
                {"name": "Phuket", "state": "Phuket", "region": "Southeast Asia", "country": "Thailand", "description": "Thailand's largest island famous for Patong Beach and Phi Phi island boat tours.", "best_time": "November to April", "recommended_days": 4, "approximate_budget": 10000.0},
                {"name": "Chiang Mai", "state": "Chiang Mai", "region": "Southeast Asia", "country": "Thailand", "description": "Northern mountainous cultural hub surrounded by ancient temples and elephant sanctuaries.", "best_time": "November to February", "recommended_days": 3, "approximate_budget": 7000.0},
                {"name": "Pattaya", "state": "Chonburi", "region": "Southeast Asia", "country": "Thailand", "description": "Resort city featuring Sanctuary of Truth, Coral Island, and vibrant night markets.", "best_time": "November to April", "recommended_days": 3, "approximate_budget": 7500.0},
                {"name": "Krabi", "state": "Krabi", "region": "Southeast Asia", "country": "Thailand", "description": "Stunning limestone karst sea cliffs, Railay Beach, and Emerald Pool.", "best_time": "November to April", "recommended_days": 3, "approximate_budget": 9000.0},
                {"name": "Koh Samui", "state": "Surat Thani", "region": "Southeast Asia", "country": "Thailand", "description": "Gulf island famous for palm-fringed beaches and luxury spa resorts.", "best_time": "December to April", "recommended_days": 4, "approximate_budget": 12000.0}
            ]
        },
        {
            "name": "Singapore", "code": "SG", "continent": "Asia", "flag_emoji": "🇸🇬",
            "latitude": 1.3521, "longitude": 103.8198,
            "description": "Garden city state famous for Marina Bay Sands, Supertree Grove, and hawker food centers.",
            "destinations": [
                {"name": "Singapore City", "state": "Singapore", "region": "Southeast Asia", "country": "Singapore", "description": "Clean, futuristic island city with botanical domes and multicultural heritage.", "best_time": "All Year Round", "recommended_days": 3, "approximate_budget": 16000.0}
            ]
        },
        {
            "name": "Australia", "code": "AU", "continent": "Oceania", "flag_emoji": "🇦🇺",
            "latitude": -25.2744, "longitude": 133.7751,
            "description": "Land of Sydney Opera House, Great Barrier Reef, kangaroos, and sun-drenched beaches.",
            "destinations": [
                {"name": "Sydney", "state": "New South Wales", "region": "Oceania", "country": "Australia", "description": "Harbor city featuring Sydney Opera House, Harbour Bridge, and Bondi Beach.", "best_time": "September to November / Feb to April", "recommended_days": 4, "approximate_budget": 28000.0},
                {"name": "Melbourne", "state": "Victoria", "region": "Oceania", "country": "Australia", "description": "Cultural coffee capital famous for laneways, street art, and Great Ocean Road.", "best_time": "March to May", "recommended_days": 3, "approximate_budget": 26000.0},
                {"name": "Brisbane", "state": "Queensland", "region": "Oceania", "country": "Australia", "description": "Subtropical river city featuring South Bank artificial beach and koala sanctuaries.", "best_time": "May to October", "recommended_days": 3, "approximate_budget": 24000.0},
                {"name": "Perth", "state": "Western Australia", "region": "Oceania", "country": "Australia", "description": "Sunniest Australian state capital situated on Swan River near Rottnest Island quokkas.", "best_time": "September to November", "recommended_days": 3, "approximate_budget": 25000.0},
                {"name": "Adelaide", "state": "South Australia", "region": "Oceania", "country": "Australia", "description": "Festival city surrounded by Barossa Valley wineries and Kangaroo Island.", "best_time": "March to May", "recommended_days": 3, "approximate_budget": 23000.0},
                {"name": "Gold Coast", "state": "Queensland", "region": "Oceania", "country": "Australia", "description": "Surfers Paradise beach hub famous for theme parks and coastal high-rises.", "best_time": "May to October", "recommended_days": 3, "approximate_budget": 24000.0},
                {"name": "Cairns", "state": "Queensland", "region": "Oceania", "country": "Australia", "description": "Gateway to the world-famous Great Barrier Reef and Daintree Rainforest.", "best_time": "May to October", "recommended_days": 4, "approximate_budget": 27000.0}
            ]
        },
        {
            "name": "Egypt", "code": "EG", "continent": "Africa", "flag_emoji": "🇪🇬",
            "latitude": 26.8206, "longitude": 30.8025,
            "description": "Ancient civilization of the Great Pyramids of Giza, Sphinx, Nile River cruises, and Red Sea coral reefs.",
            "destinations": [
                {"name": "Cairo", "state": "Cairo", "region": "North Africa", "country": "Egypt", "description": "Bustling Nile metropolis home to Pyramids of Giza and Egyptian Museum.", "best_time": "October to April", "recommended_days": 3, "approximate_budget": 12000.0},
                {"name": "Luxor", "state": "Luxor", "region": "North Africa", "country": "Egypt", "description": "World's greatest open-air museum home to Valley of the Kings and Karnak Temple.", "best_time": "October to April", "recommended_days": 3, "approximate_budget": 11000.0},
                {"name": "Alexandria", "state": "Alexandria", "region": "North Africa", "country": "Egypt", "description": "Mediterranean port city home to Citadel of Qaitbay and modern Bibliotheca Alexandrina.", "best_time": "October to April", "recommended_days": 2, "approximate_budget": 10000.0},
                {"name": "Sharm El Sheikh", "state": "South Sinai", "region": "North Africa", "country": "Egypt", "description": "Red Sea resort town famous for Ras Muhammad world-class scuba diving.", "best_time": "October to April", "recommended_days": 4, "approximate_budget": 15000.0}
            ]
        },
        {
            "name": "South Africa", "code": "ZA", "continent": "Africa", "flag_emoji": "🇿🇦",
            "latitude": -30.5595, "longitude": 22.9375,
            "description": "Rainbow Nation of Table Mountain, Big Five wildlife safaris, and Cape Winelands.",
            "destinations": [
                {"name": "Cape Town", "state": "Western Cape", "region": "Southern Africa", "country": "South Africa", "description": "Coastal city overlooked by Table Mountain, Cape of Good Hope, and Robben Island.", "best_time": "November to March", "recommended_days": 4, "approximate_budget": 22000.0},
                {"name": "Johannesburg", "state": "Gauteng", "region": "Southern Africa", "country": "South Africa", "description": "City of Gold featuring Soweto Mandela House and Apartheid Museum.", "best_time": "March to May / Sept to Nov", "recommended_days": 3, "approximate_budget": 18000.0},
                {"name": "Durban", "state": "KwaZulu-Natal", "region": "Southern Africa", "country": "South Africa", "description": "Golden Mile beach city known for Indian ocean surfing and Bunny Chow cuisine.", "best_time": "May to September", "recommended_days": 3, "approximate_budget": 16000.0},
                {"name": "Pretoria", "state": "Gauteng", "region": "Southern Africa", "country": "South Africa", "description": "Jacaranda City featuring Union Buildings and Voortrekker Monument.", "best_time": "October to November", "recommended_days": 2, "approximate_budget": 15000.0},
                {"name": "Kruger National Park", "state": "Mpumalanga", "region": "Southern Africa", "country": "South Africa", "description": "One of Africa's largest game reserves for Big Five wildlife safaris.", "best_time": "May to September", "recommended_days": 4, "approximate_budget": 30000.0}
            ]
        },
        {
            "name": "Brazil", "code": "BR", "continent": "Americas", "flag_emoji": "🇧🇷",
            "latitude": -14.2350, "longitude": -51.9253,
            "description": "Land of Christ the Redeemer, Copacabana beach, Amazon rainforest, and Samba Carnival.",
            "destinations": [
                {"name": "Rio de Janeiro", "state": "Rio de Janeiro", "region": "South America", "country": "Brazil", "description": "Marvelous City home to Christ the Redeemer, Sugarloaf Mountain, and Copacabana.", "best_time": "December to March", "recommended_days": 4, "approximate_budget": 24000.0},
                {"name": "Sao Paulo", "state": "Sao Paulo", "region": "South America", "country": "Brazil", "description": "Financial metropolis famous for MASP art museum, Paulistano gastronomy, and nightlife.", "best_time": "March to May", "recommended_days": 3, "approximate_budget": 22000.0},
                {"name": "Salvador", "state": "Bahia", "region": "South America", "country": "Brazil", "description": "Afro-Brazilian cultural heart famous for Pelourinho colonial cobblestone streets.", "best_time": "September to March", "recommended_days": 3, "approximate_budget": 18000.0},
                {"name": "Brasilia", "state": "Federal District", "region": "South America", "country": "Brazil", "description": "Futuristic airplane-shaped capital city designed by architect Oscar Niemeyer.", "best_time": "May to September", "recommended_days": 2, "approximate_budget": 19000.0}
            ]
        }
    ]

    inserted_countries = 0
    inserted_destinations = 0

    for c_data in countries_data:
        dests = c_data.pop("destinations", [])
        
        # Check existing country
        existing_c = db.query(Country).filter(Country.code == c_data["code"]).first()
        if not existing_c:
            existing_c = Country(**c_data)
            db.add(existing_c)
            db.flush()
            inserted_countries += 1

        for d_data in dests:
            existing_d = db.query(Destination).filter(Destination.name == d_data["name"]).first()
            if not existing_d:
                destination = Destination(country_id=existing_c.id, **d_data)
                db.add(destination)
                db.flush()
                inserted_destinations += 1

                # Seed sample place & stay for completeness
                db.add(Place(
                    destination_id=destination.id,
                    name=f"{destination.name} Red Fort",
                    category="Attraction",
                    description=f"Iconic attraction and historic landmark in {destination.name}.",
                    estimated_cost=50.0,
                    recommended_time="Morning / Daytime"
                ))
                db.add(Place(
                    destination_id=destination.id,
                    name=f"{destination.name} Heritage Monument",
                    category="Heritage Site",
                    description=f"Historic heritage site and architectural wonder in {destination.name}.",
                    estimated_cost=40.0,
                    recommended_time="Afternoon / Evening"
                ))
                db.add(Stay(
                    destination_id=destination.id,
                    name=f"Grand {destination.name} Hotel",
                    category="Comfort",
                    approximate_price=3500.0,
                    rating=4.7,
                    description=f"Comfortable luxury stay in central {destination.name}."
                ))
                db.add(FoodSpot(
                    destination_id=destination.id,
                    name=f"{destination.name} Central Bistro",
                    cuisine="Local & International",
                    specialty=f"{destination.name} Chef Specialty",
                    approximate_price=400.0
                ))
                db.add(LocalFood(
                    destination_id=destination.id,
                    name=f"Famous {destination.name} Delicacy",
                    category="Local Food",
                    is_must_try=True
                ))
                db.add(Transport(
                    destination_id=destination.id,
                    origin="Central Station / Airport",
                    destination=f"{destination.name} Downtown",
                    transport_mode="Taxi / Bus",
                    approximate_cost=150.0,
                    approximate_duration="30 mins"
                ))

    db.commit()
    print(f"[SAFE SEED COMPLETE] Inserted {inserted_countries} new countries and {inserted_destinations} new destinations safely.")
