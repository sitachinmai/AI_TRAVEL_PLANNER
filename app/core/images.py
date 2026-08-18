import os
from urllib.parse import parse_qs, urlparse, unquote

# Centralized Image Engine & Safe Category Fallbacks
DEFAULT_PLACEHOLDER = "/static/images/placeholder.svg"
DEFAULT_PLACE_FALLBACK = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&auto=format&fit=crop&q=80"
DEFAULT_FOOD_FALLBACK = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&auto=format&fit=crop&q=80"


def clean_image_url(url: str) -> str:
    """
    Extracts direct image URL from Google imgres links if present.
    Guarantees clean, loadable direct image URLs.
    """
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    if "google.com/imgres" in url:
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if "imgurl" in params and params["imgurl"]:
                return unquote(params["imgurl"][0])
        except Exception:
            pass
    return url


DESTINATION_IMAGE_MAP = {
    # India
    "delhi": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&auto=format&fit=crop&q=80",
    "mumbai": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800&auto=format&fit=crop&q=80",
    "hyderabad": "https://images.unsplash.com/photo-1605379399642-870262d3d051?w=800&auto=format&fit=crop&q=80",
    "tirupati": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?w=800&auto=format&fit=crop&q=80",
    "agra": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800&auto=format&fit=crop&q=80",
    "jaipur": "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800&auto=format&fit=crop&q=80",
    "goa": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&auto=format&fit=crop&q=80",
    "munnar": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800&auto=format&fit=crop&q=80",
    "kakinada": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",

    # International
    "paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&auto=format&fit=crop&q=80",
    "bangkok": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&auto=format&fit=crop&q=80",
    "dubai": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&auto=format&fit=crop&q=80",
    "london": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&auto=format&fit=crop&q=80",
    "tokyo": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&auto=format&fit=crop&q=80",
    "rome": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800&auto=format&fit=crop&q=80",
    "kyoto": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&auto=format&fit=crop&q=80",
    "osaka": "https://images.unsplash.com/photo-1590559899731-a382839e5549?w=800&auto=format&fit=crop&q=80",
    "singapore": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&auto=format&fit=crop&q=80",
    "new york": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800&auto=format&fit=crop&q=80",

    # Australia
    "australia": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&auto=format&fit=crop&q=80",
    "australia:sydney": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&auto=format&fit=crop&q=80",
    "australia:adelaide": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&auto=format&fit=crop&q=80",
    "australia:brisbane": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&auto=format&fit=crop&q=80",
    "australia:cairns": "https://images.contentstack.io/v3/assets/blt06f605a34f1194ff/blt7f06c8ed0913ac7c/665307202dad65fdace53db7/iStock-480314300-MOBILE-HEADER.jpg?format=webp&quality=60&width=1440",
    "australia:gold coast": "https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=558973539734630",
    "sydney": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&auto=format&fit=crop&q=80",
    "adelaide": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&auto=format&fit=crop&q=80",
    "brisbane": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&auto=format&fit=crop&q=80",
    "cairns": "https://images.contentstack.io/v3/assets/blt06f605a34f1194ff/blt7f06c8ed0913ac7c/665307202dad65fdace53db7/iStock-480314300-MOBILE-HEADER.jpg?format=webp&quality=60&width=1440",
    "gold coast": "https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=558973539734630",

    # Argentina
    "argentina": "https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=800&auto=format&fit=crop&q=80",
    "argentina:buenos aires": "https://cdn.britannica.com/63/188963-050-2C94FEC2/Night-view-obelisk-Buenos-Aires.jpg",
    "argentina:bariloche": "https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=800&auto=format&fit=crop&q=80",
    "buenos aires": "https://cdn.britannica.com/63/188963-050-2C94FEC2/Night-view-obelisk-Buenos-Aires.jpg",
    "bariloche": "https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=800&auto=format&fit=crop&q=80"
}

FOOD_IMAGE_MAP = {
    # Delhi & North India Foods
    "butter chicken": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=800&auto=format&fit=crop&q=80",
    "chole bhature": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=800&auto=format&fit=crop&q=80",
    "aloo tikki": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&auto=format&fit=crop&q=80",
    "gol gappe": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?w=800&auto=format&fit=crop&q=80",
    "dahi bhalla": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=800&auto=format&fit=crop&q=80",
    "jalebi": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop&q=80",
    "jalebi & rabri": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop&q=80",
    "kulfi falooda": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=800&auto=format&fit=crop&q=80",

    # Mumbai Foods
    "vada pav": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&auto=format&fit=crop&q=80",
    "pav bhaji": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=800&auto=format&fit=crop&q=80",

    # Hyderabad Foods
    "hyderabadi biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80",
    "biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80",
    "hyderabadi haleem": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80",
    "haleem": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80",
    "mirchi ka salan": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop&q=80",
    "double ka meetha": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop&q=80",
    "qubani ka meetha": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop&q=80",

    # International Foods
    "butter croissant": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800&auto=format&fit=crop&q=80",
    "croissant": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800&auto=format&fit=crop&q=80",
    "boeuf bourguignon": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80",
    "pad thai": "https://images.unsplash.com/photo-1559847844-5315695dadae?w=800&auto=format&fit=crop&q=80",
    "shawarma": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=800&auto=format&fit=crop&q=80",
    "fish and chips": "https://images.unsplash.com/photo-1579217499578-8a4e444b563d?w=800&auto=format&fit=crop&q=80",

    # Australia Foods
    "australia:adelaide food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&auto=format&fit=crop&q=80",
    "australia:brisbane food": "https://wp.australiantraveller.com/wp-content/uploads/2022/11/Gonuts.jpg?quality=80&w=640",
    "australia:cairns food": "https://www.cairnsholidayspecialists.com.au/shared_resources/media/84ehWa4HSnkMt5_1280x856.jpg",
    "australia:gold coast food": "https://i.guim.co.uk/img/media/b3a1bb10e82666b4d1fcbfa73f7c6fa219e3027f/0_180_4909_2946/master/4909.jpg?width=445&dpr=1&s=none&crop=none",

    # Argentina Foods
    "empanadas porteñas": "https://www.seriouseats.com/thmb/nLV-v9ompV4DCkOnuhL0G3GwOTs=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/SEA-Global-Eats-Buenos-Aires-Kevin-Vaughn-96185af91f9348398a91eabb12a2fae8.jpg",
    "asado & chimichurri": "https://www.seriouseats.com/thmb/nLV-v9ompV4DCkOnuhL0G3GwOTs=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/SEA-Global-Eats-Buenos-Aires-Kevin-Vaughn-96185af91f9348398a91eabb12a2fae8.jpg"
}

ATTRACTION_IMAGE_MAP = {
    # Delhi
    "red fort": "https://media.istockphoto.com/id/520840182/photo/red-fort-lal-qila-with-indian-flag-delhi-india.jpg?s=612x612&w=0&k=20&c=pOIkOX7dnJh2zwJhF9HrknY7kwYZtDgOd1n98wkHCKQ=",
    "red fort (lal qila)": "https://media.istockphoto.com/id/520840182/photo/red-fort-lal-qila-with-indian-flag-delhi-india.jpg?s=612x612&w=0&k=20&c=pOIkOX7dnJh2zwJhF9HrknY7kwYZtDgOd1n98wkHCKQ=",
    "humayun's tomb": "https://images.unsplash.com/photo-1608659597669-b45511779f93?w=800&auto=format&fit=crop&q=80",
    "india gate": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&auto=format&fit=crop&q=80",
    "india gate & kartavya path": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&auto=format&fit=crop&q=80",
    "qutub minar": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&auto=format&fit=crop&q=80",
    "lotus temple": "https://images.unsplash.com/photo-1597040663342-45b1eb757ecc?w=800&auto=format&fit=crop&q=80",
    "jama masjid": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&auto=format&fit=crop&q=80",
    "chandni chowk": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&auto=format&fit=crop&q=80",
    "rashtrapati bhavan": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&auto=format&fit=crop&q=80",
    "national museum": "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=800&auto=format&fit=crop&q=80",

    # Paris
    "eiffel tower": "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?w=800&auto=format&fit=crop&q=80",
    "louvre museum": "https://images.unsplash.com/photo-1565099824688-e93eb20fe622?w=800&auto=format&fit=crop&q=80",
    "arc de triomphe": "https://images.unsplash.com/photo-1509439581779-6298f75bf6e5?w=800&auto=format&fit=crop&q=80",
    "notre-dame": "https://images.unsplash.com/photo-1478359844494-1092259d93e4?w=800&auto=format&fit=crop&q=80",
    "notre-dame cathedral": "https://images.unsplash.com/photo-1478359844494-1092259d93e4?w=800&auto=format&fit=crop&q=80",
    "musée d'orsay": "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=800&auto=format&fit=crop&q=80",
    "champs-élysées": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&auto=format&fit=crop&q=80",

    # Hyderabad
    "charminar": "https://images.unsplash.com/photo-1605379399642-870262d3d051?w=800&auto=format&fit=crop&q=80",
    "golconda fort": "https://images.unsplash.com/photo-1616423640778-28d1b53229bd?w=800&auto=format&fit=crop&q=80",
    "hussain sagar": "https://images.unsplash.com/photo-1626014903708-69b9b7754b2a?w=800&auto=format&fit=crop&q=80",
    "hussain sagar lake": "https://images.unsplash.com/photo-1626014903708-69b9b7754b2a?w=800&auto=format&fit=crop&q=80",
    "salar jung museum": "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=800&auto=format&fit=crop&q=80",
    "chowmahalla palace": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop&q=80",

    # Mumbai
    "gateway of india": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800&auto=format&fit=crop&q=80",
    "marine drive": "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=800&auto=format&fit=crop&q=80",
    "elephanta caves": "https://images.unsplash.com/photo-1596402184320-417e7178b2cd?w=800&auto=format&fit=crop&q=80",

    # London
    "big ben": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&auto=format&fit=crop&q=80",
    "tower bridge": "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?w=800&auto=format&fit=crop&q=80",
    "london eye": "https://images.unsplash.com/photo-1533929736458-ca588d08c8be?w=800&auto=format&fit=crop&q=80",

    # Dubai
    "burj khalifa": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&auto=format&fit=crop&q=80",
    "dubai frame": "https://images.unsplash.com/photo-1580674684081-7617fbf3d745?w=800&auto=format&fit=crop&q=80",

    # Bangkok
    "grand palace": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&auto=format&fit=crop&q=80",
    "wat arun": "https://images.unsplash.com/photo-1563492065599-3520f775eeed?w=800&auto=format&fit=crop&q=80"
}

HOTEL_IMAGE_MAP = {
    "bloomrooms": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
    "haveli dharampura": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&auto=format&fit=crop&q=80",
    "hosteller": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&auto=format&fit=crop&q=80",
    "imperial": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
    "zostel": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
    "generator": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&auto=format&fit=crop&q=80",
    "citizenm": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80",
    "plaza athénée": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&auto=format&fit=crop&q=80",
    "plaza athenee": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&auto=format&fit=crop&q=80",
    "relais": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&auto=format&fit=crop&q=80",
    "piaules": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&auto=format&fit=crop&q=80",
    "ritz": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&auto=format&fit=crop&q=80"
}


def resolve_hotel_image(hotel_name: str, destination_name: str = None) -> str:
    """
    Returns a hotel-specific image URL or safe hotel fallback.
    Never returns an attraction or landmark image.
    """
    if not hotel_name:
        return "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80"
    
    h_clean = hotel_name.lower().strip()
    for key, path in HOTEL_IMAGE_MAP.items():
        if key in h_clean or h_clean in key:
            return clean_image_url(path)

    return "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=80"


def resolve_destination_image(destination_name: str, country_name: str = None) -> str:
    """
    Returns a destination-specific image URL or safe PLACE fallback.
    Never returns food images or empty strings.
    """
    if not destination_name:
        return DEFAULT_PLACE_FALLBACK
    
    d_clean = destination_name.lower().strip()
    c_clean = country_name.lower().strip() if country_name else ""
    
    # Try hierarchical key country:destination
    if c_clean:
        h_key = f"{c_clean}:{d_clean}"
        if h_key in DESTINATION_IMAGE_MAP:
            return clean_image_url(DESTINATION_IMAGE_MAP[h_key])

    for key, path in DESTINATION_IMAGE_MAP.items():
        if key in d_clean or d_clean in key:
            return clean_image_url(path)
            
    return DEFAULT_PLACE_FALLBACK


def resolve_food_image(food_name: str, destination_name: str = None, country_name: str = None) -> str:
    """
    Returns a food-specific image URL or safe FOOD fallback.
    Never returns an attraction or city hero image.
    """
    if not food_name:
        return DEFAULT_FOOD_FALLBACK
        
    f_clean = food_name.lower().strip()
    d_clean = destination_name.lower().strip() if destination_name else ""
    c_clean = country_name.lower().strip() if country_name else ""

    if c_clean and d_clean:
        h_key = f"{c_clean}:{d_clean} food"
        if h_key in FOOD_IMAGE_MAP:
            return clean_image_url(FOOD_IMAGE_MAP[h_key])

    for key, path in FOOD_IMAGE_MAP.items():
        if key in f_clean or f_clean in key:
            return clean_image_url(path)
            
    return DEFAULT_FOOD_FALLBACK


def resolve_attraction_image(place_name: str, destination_name: str = None) -> str:
    """
    Returns an attraction-specific image URL or safe PLACE fallback.
    Never returns a food image.
    """
    if not place_name:
        return DEFAULT_PLACE_FALLBACK
    
    p_clean = place_name.lower().strip()
    for key, path in ATTRACTION_IMAGE_MAP.items():
        if key in p_clean or p_clean in key:
            return clean_image_url(path)

    return DEFAULT_PLACE_FALLBACK
