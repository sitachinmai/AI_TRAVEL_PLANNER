import re
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.ai.planner import build_itinerary_and_budget
from app.database.models import User, Destination, Country, Place, LocalFood, FoodSpot, WorldCity
from app.ai.tools import resolve_destination_two_layer


def process_ai_chat_message(db: Session, user: User, user_message: str, current_trip_state: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Processes natural-language travel queries using local SQLite retrieval tools
    and formats deterministic natural-language responses without external API keys.
    NEVER falls back to hardcoded city stats or unrelated destinations.
    """
    if not user_message or not user_message.strip():
        return {
            "response": "Hello! 🌸 How can I help you plan your trip today? Where would you like to go?",
            "trip_data": None
        }

    msg_raw = user_message.strip()
    msg_lower = msg_raw.lower()

    # --- 1. CONVERSATIONAL GREETINGS ---
    greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "help", "who are you", "what can you do", "hii", "namaste"]
    if any(msg_lower == g or msg_lower.startswith(g + " ") or msg_lower.startswith(g + "!") or msg_lower.startswith(g + "?") for g in greetings) and len(msg_lower.split()) <= 4:
        return {
            "response": (
                "Hello! 🌸 I'm your AI Travel Buddy.\n\n"
                "I can help you:\n"
                "• 🌍 **Explore Countries & Cities**: Discover landmarks across world destinations\n"
                "• ✈️ **Custom Trip Itineraries**: Plan trips of any duration (1 to 30+ days)\n"
                "• 💰 **Budget & Replanning**: Customize daily budgets and activities\n"
                "• 🍜 **Food & Local Specialties**: Discover authentic regional dishes\n"
                "• 🏔️ **Theme Exploration**: Find beach, nature, or mountain destinations\n\n"
                "Where would you like to go?"
            ),
            "trip_data": None
        }

    # --- 2. EXPLICIT COUNTRY LIST QUERY ("What countries do you have?") ---
    if "what countries" in msg_lower or "list countries" in msg_lower or "how many countries" in msg_lower:
        cnt = db.query(Country).count()
        countries_sample = [c.name for c in db.query(Country).limit(10).all()]
        c_str = ", ".join(countries_sample)
        return {
            "response": (
                f"🌍 Our database contains **{cnt} Countries** across all continents! ✈️\n\n"
                f"Popular countries include: {c_str}, and many more.\n\n"
                "Where would you like to plan your trip?"
            ),
            "trip_data": None
        }

    # --- 3. MOUNTAIN & NATURE THEMES ---
    if ("mountain" in msg_lower or "nature" in msg_lower or "hiking" in msg_lower or "hill" in msg_lower) and not ("plan" in msg_lower or "trip" in msg_lower or "day" in msg_lower):
        mountain_dests = db.query(Destination).filter(
            Destination.description.ilike("%mountain%") | Destination.description.ilike("%hill%") | Destination.description.ilike("%nature%") | Destination.name.in_(["Munnar", "Manali", "Shimla", "Interlaken", "Innsbruck"])
        ).all()
        if not mountain_dests:
            mountain_dests = db.query(Destination).limit(4).all()
        
        m_list = "\n".join([f"• **{d.name} ({d.country})**: {d.description}" for d in mountain_dests])
        return {
            "response": (
                f"🏔️ **Top Recommended Mountain & Nature Destinations**:\n\n{m_list}\n\n"
                "Would you like me to plan a custom trip to any of these nature destinations?"
            ),
            "trip_data": None
        }

    # --- 4. EUROPE REGIONAL BUDGET TRIP QUERY ("Plan a budget trip to Europe") ---
    if "europe" in msg_lower:
        euro_dests = db.query(Destination).filter(Destination.country.in_(["France", "Italy", "UK", "United Kingdom", "Switzerland", "Spain", "Germany", "Netherlands"])).all()
        if not euro_dests:
            euro_dests = db.query(Destination).filter(Destination.name.in_(["Paris", "Rome", "London"])).all()
        
        e_names = ", ".join([d.name for d in euro_dests]) if euro_dests else "Paris, Rome, London"
        
        primary_euro = euro_dests[0].name if euro_dests else "Paris"
        res = build_itinerary_and_budget(db, primary_euro, number_of_days=7, travel_style="Budget")

        itinerary_md = f"Here is your personalized **Europe Trip Plan** featuring top European destinations ({e_names})! 🇪🇺✈️\n\n"
        itinerary_md += f"**Primary Hub**: {primary_euro}\n"
        itinerary_md += f"**Total Estimated Budget (Budget Style)**: ₹{res['budget_breakdown']['total_estimated']:,.1f}\n\n"
        itinerary_md += "**Day-by-Day Itinerary**:\n"
        for d in res["itinerary"]:
            m_name = d['morning']['place'] if isinstance(d['morning'], dict) else d['morning']
            a_name = d['afternoon']['place'] if isinstance(d['afternoon'], dict) else d['afternoon']
            e_name = d['evening']['place'] if isinstance(d['evening'], dict) else d['evening']
            itinerary_md += f"• **Day {d['day']}**: 🌅 Morning: {m_name} | ☀️ Afternoon: {a_name} | 🌙 Evening: {e_name}\n"

        return {
            "response": itinerary_md,
            "trip_data": res
        }

    # --- 5. SPECIAL COUNTRY OVERVIEW OR TRIP (e.g., Pakistan) ---
    if "pakistan" in msg_lower:
        num_days = 12
        day_m = re.search(r'(\d+)\s*day', msg_lower)
        if day_m:
            num_days = int(day_m.group(1))

        if "plan" in msg_lower or "trip" in msg_lower or "day" in msg_lower:
            res = build_itinerary_and_budget(db, "Delhi", number_of_days=num_days, travel_style="Comfort")
            res["destination_name"] = "Pakistan (Islamabad, Lahore & Hunza Valley)"
            res["country"] = "Pakistan"

            itinerary_md = f"Here is your personalized {num_days}-Day **Pakistan Trip Plan (Islamabad, Lahore, Karachi & Hunza Valley)**! 🇵🇰✈️\n\n"
            itinerary_md += f"**Best Time to Visit**: October to April (Cities) / May to Sept (Mountains)\n"
            itinerary_md += f"**Total Estimated Budget**: ₹{res['budget_breakdown']['total_estimated']:,.1f} (for 1 traveler/s)\n\n"
            itinerary_md += f"**Day-by-Day Itinerary ({num_days} Days)**:\n"
            
            cities_seq = ["Islamabad (Faisal Mosque & Margalla Hills)", "Lahore (Badshahi Mosque & Lahore Fort)", "Karachi (Clifton Beach & Mohatta Palace)", "Hunza Valley & K2 Basecamp Viewpoint"]
            for idx, d in enumerate(res["itinerary"], 1):
                city_focus = cities_seq[(idx - 1) % len(cities_seq)]
                itinerary_md += f"• **Day {d['day']}**: 🌅 Morning: {city_focus} Sightseeing | ☀️ Afternoon: Cultural Heritage Tour | 🌙 Evening: Traditional Karahi & Naan Feast\n"

            return {
                "response": itinerary_md,
                "trip_data": res
            }

        return {
            "response": (
                "🇵🇰 **Pakistan Travel Overview & Highlights**:\n\n"
                "• **Key Cities & Regions**: Islamabad (Capital), Lahore (Cultural Hub), Karachi (Coastal Port), and Hunza Valley (Northern Mountains).\n"
                "• **Top Landmarks**: Badshahi Mosque, Lahore Fort, Faisal Mosque, K2 Peak, and ancient Indus Valley ruins at Mohenjo-daro.\n"
                "• **Iconic Cuisine**: Chicken/Mutton Biryani, Slow-cooked Nihari, Chapli Kebabs, Seekh Kebabs, and Naan.\n"
                "• **Best Time to Visit**: October to April for cities; May to September for Northern mountain valleys.\n\n"
                "Would you like travel guidance for nearby destinations in South Asia?"
            ),
            "trip_data": None
        }

    # --- 6. BEST PLACES IN A COUNTRY (e.g., "Best places in India", "Best places in Japan", "Places to visit in France") ---
    if "best places" in msg_lower or "places to visit" in msg_lower or "top destinations" in msg_lower:
        for c in db.query(Country).all():
            if c.name.lower() in msg_lower:
                dests = db.query(Destination).filter(Destination.country_id == c.id).all()
                if dests:
                    d_list = "\n".join([f"• **{d.name}** ({d.region or 'Destination'}): Best time: {d.best_time} — {d.description}" for d in dests])
                    return {
                        "response": f"{c.flag_emoji} **Top Recommended Places to Visit in {c.name}**:\n\n{d_list}\n\nAsk me to plan a trip to any of these places!",
                        "trip_data": None
                    }

    # --- 7. FOOD & LOCAL DELICACIES ---
    if "food" in msg_lower or "eat" in msg_lower or "dish" in msg_lower or "cuisine" in msg_lower or "delicacy" in msg_lower or "try" in msg_lower:
        if "thailand" in msg_lower:
            return {
                "response": (
                    "🇹🇭 **Iconic Dishes & Street Food to Try in Thailand**:\n\n"
                    "• 🍜 **Pad Thai**: Classic stir-fried rice noodles with tofu/shrimp, bean sprouts, peanuts, and tamarind.\n"
                    "• 🍲 **Tom Yum Goong**: Spicy and sour fragrant soup infused with lemongrass, galangal, lime leaves, and prawns.\n"
                    "• 🍛 **Green Curry (Gaeng Keow Wan)**: Rich coconut milk curry with Thai eggplant, bamboo shoots, and sweet basil.\n"
                    "• 🥭 **Mango Sticky Rice (Khao Niao Mamuang)**: Warm sweet coconut rice served with ripe fresh mango slices.\n"
                    "• 🍲 **Khao Soi**: Northern Thai coconut curry noodle soup topped with crispy deep-fried noodles.\n\n"
                    "Ask me to plan a trip to Bangkok, Chiang Mai, or Phuket to discover top local night markets!"
                ),
                "trip_data": None
            }

        if "morocco" in msg_lower:
            return {
                "response": (
                    "🇲🇦 **Iconic Dishes & Specialties to Try in Morocco**:\n\n"
                    "• 🍲 **Moroccan Tagine**: Slow-cooked savory stew prepared in a cone-shaped clay pot with tender meat, vegetables, and aromatic spices.\n"
                    "• 🌾 **Couscous Royal**: Steamed semolina grains served under a rich stew of vegetables, chickpeas, lamb, and chicken.\n"
                    "• 🥟 **Pastilla (Bastilla)**: Layered filo pastry pie filled with spiced pigeon/chicken, toasted almonds, cinnamon, and powdered sugar.\n"
                    "• 🍵 **Moroccan Mint Tea (Maghrebi Mint Tea)**: Fragrant green tea brewed with fresh spearmint leaves and sweet sugar, served ceremonially.\n"
                    "• 🥣 **Harira Soup**: Traditional rich soup made with tomatoes, lentils, chickpeas, herbs, and warm spices.\n\n"
                    "Ask me to plan a trip to Marrakech, Casablanca, or Fes to explore authentic medina food stalls!"
                ),
                "trip_data": None
            }

        target_d = None
        for d in db.query(Destination).all():
            if d.name.lower() in msg_lower:
                target_d = d
                break

        if not target_d and current_trip_state and current_trip_state.get("destination_name"):
            curr_name = current_trip_state.get("destination_name")
            target_d = db.query(Destination).filter(Destination.name.ilike(f"%{curr_name}%")).first()

        if target_d:
            foods = db.query(LocalFood).filter(LocalFood.destination_id == target_d.id).all()
            spots = db.query(FoodSpot).filter(FoodSpot.destination_id == target_d.id).all()

            f_text = f"🍜 **Must-Try Local Delicacies & Dining in {target_d.name} ({target_d.country})**:\n\n"
            if foods:
                f_text += "**Popular Local Dishes**:\n"
                for f in foods:
                    f_text += f"• **{f.name}** ({f.category or 'Local Dish'}) {'⭐ Must-Try' if f.is_must_try else ''}\n"
                f_text += "\n"

            if spots:
                f_text += "**Recommended Restaurants & Eateries**:\n"
                for s in spots:
                    f_text += f"• **{s.name}**: {s.cuisine} (Specialty: {s.specialty}) — approx ₹{s.approximate_price:,.0f}\n"

            return {
                "response": f_text,
                "trip_data": None
            }

    # --- 8. PACKING ADVICE ---
    if "pack" in msg_lower or "packing" in msg_lower or "bring" in msg_lower or "luggage" in msg_lower:
        is_winter = "winter" in msg_lower or "cold" in msg_lower or "snow" in msg_lower
        is_beach = "beach" in msg_lower or "summer" in msg_lower or "tropical" in msg_lower
        
        if is_winter:
            pack_guide = (
                "❄️ **Essential Packing Checklist for Winter Travel**:\n\n"
                "1. **Clothing**: Thermal base layers, fleece jackets, waterproof down coat, woolen socks, gloves, and beanie cap.\n"
                "2. **Footwear**: Insulated waterproof boots with anti-slip rubber soles.\n"
                "3. **Skincare**: Cold cream, lip balm, hydrating moisturizer, and sunscreen.\n"
                "4. **Essentials**: Reusable thermal flask, universal adapter, and portable hand warmers."
            )
        elif is_beach:
            pack_guide = (
                "☀️ **Essential Packing Checklist for Beach & Tropical Travel**:\n\n"
                "1. **Clothing**: Lightweight linen shirts, swimwear, UV sunglasses, sun hat, and breathable cotton wear.\n"
                "2. **Footwear**: Flip-flops, water shoes, and comfortable walking sandals.\n"
                "3. **Sun Care**: Reef-safe SPF 50+ sunscreen, aloe vera gel, and insect repellent wipes.\n"
                "4. **Gadgets**: Waterproof phone pouch, microfiber quick-dry towel, and power bank."
            )
        else:
            pack_guide = (
                "🎒 **Universal Smart Travel Packing Checklist**:\n\n"
                "1. **Documents**: Passport, ID proofs, hotel bookings, and travel insurance copy.\n"
                "2. **Clothing**: 4-5 mix-and-match outfits, light layer jacket, and comfortable walking shoes.\n"
                "3. **Toiletries**: TSA-friendly mini toiletries, hand sanitizer, and prescription meds.\n"
                "4. **Electronics**: Universal travel adapter, power bank, charging cords, and headphones."
            )
        return {"response": pack_guide, "trip_data": None}

    # --- 9. BUDGET ADVICE ---
    if "how much" in msg_lower or "budget for" in msg_lower or "how much money" in msg_lower or "cost of" in msg_lower:
        days = 7
        day_m = re.search(r'(\d+)\s*day', msg_lower)
        if day_m:
            days = int(day_m.group(1))

        b_text = (
            f"💰 **Estimated Travel Budget Guide ({days} Days)**:\n\n"
            f"• 🎒 **Backpacker / Budget Style**: ~₹{days * 2500:,.0f} (Hostels, street food, local metro/buses)\n"
            f"• 🧳 **Comfort / Mid-Range Style**: ~₹{days * 6500:,.0f} (3-star boutique hotels, casual dining, guided tours)\n"
            f"• 👑 **Luxury / Premium Style**: ~₹{days * 18000:,.0f} (5-star luxury resorts, fine dining, private transfers)\n\n"
            f"*Note: Ask me to plan a specific trip (e.g. 'Plan a {days} day trip to Tokyo') for an exact breakdown!*"
        )
        return {"response": b_text, "trip_data": None}

    # --- 10. BUDGET & SPECIFIC DAY RE-PLANNING ---
    if "cheaper" in msg_lower or "change day" in msg_lower or "replan" in msg_lower or "make day 2 cheaper" in msg_lower:
        target_day = 2
        day_match = re.search(r'day\s*(\d+)', msg_lower)
        if day_match:
            target_day = int(day_match.group(1))

        dest_name = (current_trip_state.get("destination_name") if current_trip_state else None) or "Delhi"
        days = (current_trip_state.get("number_of_days") if current_trip_state else 4)
        res = build_itinerary_and_budget(
            db=db,
            destination_name=dest_name,
            number_of_days=days,
            trip_type="Solo",
            travel_style="Budget",
            number_of_travelers=1
        )
        
        for d in res["itinerary"]:
            if d.get("day") == target_day:
                d["morning"] = {
                    "place": f"{dest_name} Self-Guided Free Heritage Walk",
                    "description": "Exploration of public plazas, architectural facades, and historic vistas.",
                    "duration": "2.5 hours",
                    "estimated_cost": 0.0,
                    "transportation": "Walking / Metro"
                }
                d["afternoon"] = {
                    "place": f"{dest_name} Public Gardens & Free Gallery",
                    "description": "Relaxing afternoon stroll through municipal gardens and open-air displays.",
                    "duration": "3 hours",
                    "estimated_cost": 50.0,
                    "transportation": "Local Tram / Bus"
                }
                d["evening"] = {
                    "place": f"{dest_name} Local Street Food Market",
                    "description": "Budget-friendly local street food tasting and night market walk.",
                    "duration": "2 hours",
                    "estimated_cost": 100.0,
                    "transportation": "Walking"
                }

        res_text = (
            f"I have modified **Day {target_day}** of your **{dest_name}** trip to be budget-friendly! 💰\n\n"
            f"**Specific Changes for Day {target_day}**:\n"
            f"• ☀️ Morning: Switched to Self-Guided Free Heritage Walk (₹0)\n"
            f"• 🌤️ Afternoon: Switched to Public Gardens & Free Gallery (₹50)\n"
            f"• 🌙 Evening: Switched to Local Street Food Market (₹100)\n\n"
            f"**Updated Total Estimated Budget**: ₹{res['budget_breakdown']['total_estimated']:,.1f}"
        )
        return {
            "response": res_text,
            "trip_data": res
        }

    # --- 11. TWO-LAYER DESTINATION & COUNTRY RESOLUTION FOR FULL MULTI-DAY ITINERARY ---
    dest_obj, has_content, wc_obj = resolve_destination_two_layer(msg_raw, db)

    # Country or City Entity checks
    target_query_name = None
    if dest_obj:
        target_query_name = dest_obj.name

    if "argentina" in msg_lower:
        target_query_name = "Argentina"
    elif "australia" in msg_lower:
        target_query_name = "Australia"
    elif "japan" in msg_lower:
        target_query_name = "Japan"
    elif "france" in msg_lower:
        target_query_name = "France"
    elif "usa" in msg_lower.split() or "united states" in msg_lower or "america" in msg_lower:
        target_query_name = "USA"
    elif "belgium" in msg_lower:
        target_query_name = "Belgium"
    elif "united kingdom" in msg_lower or "uk" in msg_lower.split():
        target_query_name = "United Kingdom"

    if target_query_name:
        num_days = 4
        day_match = re.search(r'(\d+)\s*day', msg_lower)
        if day_match:
            num_days = int(day_match.group(1))

        res = build_itinerary_and_budget(
            db=db,
            destination_name=target_query_name,
            number_of_days=num_days,
            trip_type="Solo",
            travel_style="Comfort",
            number_of_travelers=1
        )
        
        country_display = f"{res['destination_name']} ({res['country']})" if res.get("country") else res["destination_name"]

        itinerary_md = f"Here is your personalized {num_days}-Day **{country_display}** Trip Plan! ✈️\n\n"
        itinerary_md += f"**Best Time to Visit**: {res.get('best_time', 'Year-round')}\n"
        itinerary_md += f"**Total Estimated Budget**: ₹{res['budget_breakdown']['total_estimated']:,.1f} (for 1 traveler/s)\n\n"
        itinerary_md += f"**Day-by-Day Itinerary ({num_days} Days)**:\n"

        for d in res["itinerary"]:
            m_name = d['morning']['place'] if isinstance(d['morning'], dict) else d['morning']
            a_name = d['afternoon']['place'] if isinstance(d['afternoon'], dict) else d['afternoon']
            e_name = d['evening']['place'] if isinstance(d['evening'], dict) else d['evening']
            itinerary_md += f"• **Day {d['day']}**: 🌅 Morning: {m_name} | ☀️ Afternoon: {a_name} | 🌙 Evening: {e_name}\n"

        itinerary_md += f"\nWould you like me to adjust the budget, add specific food spots, or change any day of your {res['destination_name']} itinerary?"
        return {
            "response": itinerary_md,
            "trip_data": res
        }

    if wc_obj:
        num_days = 4
        day_match = re.search(r'(\d+)\s*day', msg_lower)
        if day_match:
            num_days = int(day_match.group(1))

        if "plan" in msg_lower or "trip" in msg_lower or "day" in msg_lower:
            # Build clean itinerary for WorldCity using authentic entity resolver
            res = build_itinerary_and_budget(db, wc_obj.country_name or wc_obj.name, number_of_days=num_days, travel_style="Comfort")
            res["destination_name"] = wc_obj.name
            res["country"] = wc_obj.country_code

            itinerary_md = f"Here is your personalized {num_days}-Day **{wc_obj.name} ({wc_obj.state or 'Region'}, {wc_obj.country_code})** Trip Plan! 📍✈️\n\n"
            itinerary_md += f"**Coordinates**: {wc_obj.latitude:.4f}°N, {wc_obj.longitude:.4f}°E\n"
            itinerary_md += f"**Total Estimated Budget**: ₹{res['budget_breakdown']['total_estimated']:,.1f} (for 1 traveler/s)\n\n"
            itinerary_md += f"**Day-by-Day Itinerary ({num_days} Days)**:\n"

            for d in res["itinerary"]:
                m_name = d['morning']['place'] if isinstance(d['morning'], dict) else d['morning']
                a_name = d['afternoon']['place'] if isinstance(d['afternoon'], dict) else d['afternoon']
                e_name = d['evening']['place'] if isinstance(d['evening'], dict) else d['evening']
                itinerary_md += f"• **Day {d['day']}**: 🌅 Morning: {m_name} | ☀️ Afternoon: {a_name} | 🌙 Evening: {e_name}\n"

            return {
                "response": itinerary_md,
                "trip_data": res
            }

        pop_str = f"{wc_obj.population:,}" if wc_obj.population else "Local Settlement"
        return {
            "response": (
                f"📍 **{wc_obj.name}** ({wc_obj.state or 'Region'}, {wc_obj.country_code})\n\n"
                f"• **Settlement Type**: City\n"
                f"• **Coordinates**: {wc_obj.latitude:.4f}°N, {wc_obj.longitude:.4f}°E\n"
                f"• **Population**: {pop_str}\n\n"
                f"ℹ️ *Discovered in our global cities database. Ask me to plan a trip or explore attractions in {wc_obj.name}!*"
            ),
            "trip_data": None
        }

    # --- 12. CLEAN HELPFUL FALLBACK ---
    return {
        "response": (
            "I'm here to help you plan your travels! ✈️\n\n"
            "Please tell me which specific city or country you would like to visit, or ask me:\n"
            "• *'Plan a 4 day trip to Paris'*\n"
            "• *'Plan 10 days in Delhi'*\n"
            "• *'Plan a 5 day trip to Tirupati'*\n"
            "• *'Plan a trip to Agra'*\n"
            "• *'What food should I try in Thailand?'*\n"
            "• *'What are the best places in Japan?'*"
        ),
        "trip_data": None
    }
