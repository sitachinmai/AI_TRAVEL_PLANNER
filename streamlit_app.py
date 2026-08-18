import streamlit as st
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import init_db, SessionLocal
from app.database.seed import seed_data
from app.travel.service import get_all_countries, get_all_destinations, get_destination_detail
from app.ai.agent import process_ai_chat_message
from app.core.research import get_research_url
from app.core.images import clean_image_url

# 1. Initialize Database Schema & Seed Data
init_db()
db = SessionLocal()
try:
    seed_data(db)
finally:
    db.close()

# 2. Page Setup
st.set_page_config(
    page_title="AI Travel Planner - Global Destinations & AI Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        color: #475569;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .destination-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
    }
    .badge-pill {
        background-color: #e0e7ff;
        color: #4338ca;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .research-btn {
        display: inline-block;
        background: #4f46e5;
        color: #ffffff !important;
        padding: 6px 14px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.image("static/images/cute_globe_mascot.jpg", use_container_width=True)
st.sidebar.title("🌍 AI Travel Planner")
navigation = st.sidebar.radio(
    "Navigation Menu",
    ["✈️ Explore Destinations", "🤖 AI Travel Assistant", "📅 Multi-Day Itinerary Planner", "📖 Research Source Registry"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Pro-Tip**: Ask the AI Assistant for multi-day itineraries for any destination (e.g. *'Plan a 4 day trip to Argentina'* or *'Plan a 3 day trip to Brussels'*).")


# ==========================================
# PAGE 1: EXPLORE DESTINATIONS
# ==========================================
if navigation == "✈️ Explore Destinations":
    st.markdown('<div class="main-title">🌍 Explore Global Travel Destinations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Discover top countries, primary landmarks, culture, and authentic local food dishes.</div>', unsafe_allow_html=True)

    db = SessionLocal()
    countries = get_all_countries(db)
    
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("🔍 Search destination or country:", placeholder="e.g. Argentina, Paris, Sydney, Tokyo...")
    with col_filter:
        country_names = ["All Countries"] + [c["name"] for c in countries]
        selected_country = st.selectbox("Filter by Country:", country_names)

    country_id = None
    if selected_country != "All Countries":
        c_match = next((c for c in countries if c["name"] == selected_country), None)
        if c_match:
            country_id = c_match["id"]

    destinations = get_all_destinations(db, query=search_query, country_id=country_id)
    db.close()

    st.markdown(f"**Showing {len(destinations)} destination(s)**")

    cols = st.columns(3)
    for idx, dest in enumerate(destinations):
        with cols[idx % 3]:
            st.image(dest["image"], use_container_width=True)
            st.subheader(f"{dest['name']}, {dest['country']}")
            st.caption(f"📍 Region: {dest['region']} | ⏱️ Best Duration: {dest['recommended_days']} Days")
            st.write(dest['description'][:140] + ("..." if len(dest['description']) > 140 else ""))
            
            research_url = get_research_url(dest['name']) or get_research_url(dest['country'])
            st.markdown(f"[📖 Research Source 🔗]({research_url})")
            
            if st.button(f"View Full Details →", key=f"btn_dest_{dest['id']}"):
                st.session_state["selected_dest_id"] = dest['id']
                st.session_state["show_dest_modal"] = True

    # Destination Details Section
    if st.session_state.get("show_dest_modal") and st.session_state.get("selected_dest_id"):
        st.markdown("---")
        db = SessionLocal()
        d_detail = get_destination_detail(db, st.session_state["selected_dest_id"])
        db.close()

        if d_detail:
            st.markdown(f"## 🏛️ {d_detail['name']} Details ({d_detail['country']})")
            d_col1, d_col2 = st.columns([1, 2])
            with d_col1:
                st.image(d_detail['image'], use_container_width=True)
                st.markdown(f"**Best Season**: {d_detail['best_time']}")
                st.markdown(f"**Approx. Daily Budget**: ₹{d_detail['approximate_budget']:,.0f}")
                r_url = d_detail.get('research_url') or get_research_url(d_detail['name'])
                st.markdown(f"[📖 Open Official Research Page 🔗]({r_url})")
            with d_col2:
                st.markdown(f"### Overview & Culture")
                st.write(d_detail['description'])
                if d_detail.get('culture'):
                    st.info(f"🎭 **Culture**: {d_detail['culture']}")
                if d_detail.get('history'):
                    st.write(f"📜 **History**: {d_detail['history']}")

            st.markdown("---")
            tab_places, tab_food, tab_stays = st.tabs(["🏛️ Top Places to Visit", "🍱 Authentic Local Foods", "🏨 Stays & Hotels"])
            
            with tab_places:
                p_cols = st.columns(2)
                for p_idx, place in enumerate(d_detail['places']):
                    with p_cols[p_idx % 2]:
                        st.image(place['image'], use_container_width=True)
                        st.markdown(f"#### {place['name']}")
                        st.caption(f"Category: {place['category']} | Visit Time: {place['estimated_visit_time']}")
                        st.write(place['description'])
                        p_res = place.get('research_url') or get_research_url(place['name'])
                        st.markdown(f"[📖 Landmark Research 🔗]({p_res})")

            with tab_food:
                f_cols = st.columns(2)
                for f_idx, food in enumerate(d_detail['local_foods']):
                    with f_cols[f_idx % 2]:
                        st.image(food['image'], use_container_width=True)
                        st.markdown(f"#### {food['name']}")
                        st.caption(f"Category: {food['category']} | Must Try: {'Yes ⭐' if food['is_must_try'] else 'No'}")
                        st.write(food['description'])

            with tab_stays:
                s_cols = st.columns(2)
                for s_idx, stay in enumerate(d_detail['stays']):
                    with s_cols[s_idx % 2]:
                        st.image(stay['image'], use_container_width=True)
                        st.markdown(f"#### {stay['name']}")
                        st.caption(f"Area: {stay['area']} | Rating: ⭐ {stay['rating']}")
                        st.write(stay['description'])


# ==========================================
# PAGE 2: AI TRAVEL ASSISTANT CHATBOT
# ==========================================
elif navigation == "🤖 AI Travel Assistant":
    st.markdown('<div class="main-title">🤖 AI Travel Assistant Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ask for custom itineraries, food recommendations, and budget plans for any destination worldwide.</div>', unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Hello! I am your AI Travel Assistant. Where would you like to travel today? Ask me to plan a trip to Argentina, Belgium, Australia, Paris, Tokyo, or anywhere else!"}
        ]

    # Quick Prompt Buttons
    st.write("💡 **Quick Prompt Chips:**")
    chip_cols = st.columns(4)
    quick_prompts = [
        "Plan a 4 day trip to Argentina",
        "Plan a 3 day trip to Brussels",
        "Plan a 4 day trip to Australia",
        "What food should I try in France?"
    ]
    
    selected_quick = None
    for idx, prompt_text in enumerate(quick_prompts):
        with chip_cols[idx]:
            if st.button(prompt_text, key=f"chip_{idx}"):
                selected_quick = prompt_text

    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input Handling
    user_prompt = st.chat_input("Ask AI Travel Assistant...") or selected_quick

    if user_prompt:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Process message via AI Agent engine
        with st.chat_message("assistant"):
            with st.spinner("AI Travel Assistant is crafting your custom travel plan..."):
                db = SessionLocal()
                result = process_ai_chat_message(db, user=None, user_message=user_prompt)
                db.close()

                response_text = result["response"]
                st.markdown(response_text)
                
                # Check for structured itinerary data
                trip_data = result.get("trip_data")
                if trip_data and "itinerary" in trip_data:
                    st.success("🎉 Multi-day itinerary generated successfully with 0 attraction repeats!")

        st.session_state.messages.append({"role": "assistant", "content": response_text})


# ==========================================
# PAGE 3: MULTI-DAY ITINERARY PLANNER
# ==========================================
elif navigation == "📅 Multi-Day Itinerary Planner":
    st.markdown('<div class="main-title">📅 Multi-Day Itinerary Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Generate structured, day-by-day travel plans with budget breakdowns.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        target_dest = st.text_input("Destination Name:", value="Paris")
    with col2:
        duration_days = st.number_input("Number of Days:", min_value=1, max_value=30, value=4)
    with col3:
        num_travelers = st.number_input("Number of Travelers:", min_value=1, max_value=10, value=2)

    if st.button("🚀 Generate Detailed Itinerary"):
        with st.spinner("Generating plan..."):
            db = SessionLocal()
            prompt = f"Plan a {duration_days} day trip to {target_dest} for {num_travelers} travelers"
            result = process_ai_chat_message(db, user=None, user_message=prompt)
            db.close()

            st.markdown(result["response"])


# ==========================================
# PAGE 4: RESEARCH SOURCE REGISTRY
# ==========================================
elif navigation == "📖 Research Source Registry":
    st.markdown('<div class="main-title">📖 Research & Source Registry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Verified Wikipedia and official research pages for all 50+ supported countries and landmarks.</div>', unsafe_allow_html=True)

    db = SessionLocal()
    countries = get_all_countries(db)
    db.close()

    for c in countries:
        with st.expander(f"{c['flag']} {c['name']} ({c['continent']})"):
            r_url = get_research_url(c['name'])
            st.markdown(f"**Country Official Source**: [{r_url}]({r_url})")
            st.write(c['description'])

            db = SessionLocal()
            dests = get_all_destinations(db, country_id=c['id'])
            db.close()

            for d in dests:
                d_r = get_research_url(d['name']) or r_url
                st.markdown(f"- 🏛️ **{d['name']}**: [{d_r}]({d_r})")

st.markdown("---")
st.caption("AI Travel Planner Streamlit Web Application • Powered by FastAPI & Streamlit")
