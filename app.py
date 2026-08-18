import streamlit as st
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import init_db, SessionLocal
from app.database.seed import seed_data
from app.travel.service import get_all_countries, get_all_destinations, get_destination_detail, get_destination_by_id
from app.ai.agent import process_ai_chat_message
from app.core.research import get_research_url
from app.core.images import clean_image_url

# Initialize Database Schema & Seed Data
init_db()
db = SessionLocal()
try:
    seed_data(db)
finally:
    db.close()

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Travel Planner — Global Destinations & AI Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Premium Aesthetic
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }
    .sub-title {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .hero-banner-container {
        position: relative;
        height: 240px;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    .hero-banner-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .hero-banner-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1.5rem;
        background: linear-gradient(to top, rgba(15, 23, 42, 0.85) 0%, rgba(15, 23, 42, 0) 100%);
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(241, 245, 249, 0.8);
        padding: 8px 12px;
        border-radius: 9999px;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9999px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
if os.path.exists("static/images/cute_globe_mascot.jpg"):
    st.sidebar.image("static/images/cute_globe_mascot.jpg", use_container_width=True)

st.sidebar.title("🌍 AI Travel Planner")
navigation = st.sidebar.radio(
    "Navigation Menu",
    ["✈️ Explore Destinations", "🤖 AI Travel Assistant", "📅 Multi-Day Itinerary Planner", "📖 Research Source Registry"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Pro-Tip**: Ask the AI Assistant for multi-day itineraries for any destination (e.g. *'Plan a 4 day trip to Argentina'* or *'Plan a 3 day trip to Brussels'*).")

# API Key Secrets integration for Streamlit Cloud
if "GEMINI_API_KEY" in st.secrets and not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]


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
        search_query = st.text_input("🔍 Search destination or country:", placeholder="e.g. Delhi, Paris, Mumbai, Hyderabad, Bangkok, London...")
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
            st.caption(f"📍 Region: {dest['region']} | ⏱️ Recommended: {dest['recommended_days']} Days")
            st.write(dest['description'][:130] + ("..." if len(dest['description']) > 130 else ""))
            
            research_url = get_research_url(dest['name']) or get_research_url(dest['country'])
            st.markdown(f"[📖 Research Source 🔗]({research_url})")
            
            if st.button(f"View Details for {dest['name']} →", key=f"btn_dest_{dest['id']}"):
                st.session_state["selected_dest_id"] = dest['id']
                st.session_state["show_dest_details"] = True

    # Detailed Destination View (Single Content Container below Horizontal Tabs)
    if st.session_state.get("show_dest_details") and st.session_state.get("selected_dest_id"):
        st.markdown("---")
        db = SessionLocal()
        d_detail = get_destination_by_id(db, st.session_state["selected_dest_id"])
        db.close()

        if d_detail:
            # Compact Destination Hero
            st.markdown(f"""
            <div class="hero-banner-container">
                <img src="{d_detail['image']}" class="hero-banner-img">
                <div class="hero-banner-overlay">
                    <span style="background: rgba(255,255,255,0.25); padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.85rem;">
                        📍 {d_detail.get('region') or d_detail.get('country')}
                    </span>
                    <h2 style="font-size: 2.2rem; font-weight: 800; margin: 6px 0 2px 0; color: #ffffff;">{d_detail['name']}</h2>
                    <p style="margin: 0; opacity: 0.95; font-size: 1rem;">{d_detail['description']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Horizontal Tab Navigation Row
            tab_overview, tab_history, tab_places, tab_stays, tab_food, tab_transport, tab_safety = st.tabs([
                "📜 Overview",
                "📜 History & Culture",
                f"📍 Places ({len(d_detail['places'])})",
                f"🏨 Stays ({len(d_detail['stays'])})",
                f"🍜 Food ({len(d_detail['local_foods'])})",
                "🚕 Transportation",
                "🚨 Emergency Info"
            ])

            # 1. Overview Tab
            with tab_overview:
                st.markdown("### 📜 Overview & Key Details")
                st.write(d_detail['description'])
                ov_col1, ov_col2, ov_col3 = st.columns(3)
                with ov_col1:
                    st.info(f"🌤️ **Best Time**: {d_detail['best_time']}")
                with ov_col2:
                    st.info(f"📅 **Recommended**: {d_detail['recommended_days']} Days")
                with ov_col3:
                    st.info(f"💰 **Approx Budget**: ₹{d_detail['approximate_budget']:,.0f} / day")
                
                r_url = d_detail.get('research_url') or get_research_url(d_detail['name'])
                st.markdown(f"[📖 Open Official Research Page 🔗]({r_url})")

            # 2. History & Culture Tab
            with tab_history:
                st.markdown(f"### 📖 History & Heritage of {d_detail['name']}")
                st.write(d_detail['history'])
                st.markdown(f"### ✨ Cultural Identity & Local Customs")
                st.write(d_detail['culture'])

            # 3. Places to Visit Tab
            with tab_places:
                st.markdown(f"### 📍 Top Places to Visit in {d_detail['name']}")
                p_cols = st.columns(3)
                for p_idx, place in enumerate(d_detail['places']):
                    with p_cols[p_idx % 3]:
                        st.image(place['image'], use_container_width=True)
                        st.markdown(f"#### {place['name']}")
                        st.caption(f"Category: {place['category']} | Visit Time: {place.get('estimated_visit_time', '2 Hours')}")
                        st.write(place['description'])
                        p_res = place.get('research_url') or get_research_url(place['name'])
                        st.markdown(f"[📖 Landmark Research 🔗]({p_res})")

            # 4. Stays Tab
            with tab_stays:
                st.markdown(f"### 🏨 Accommodation & Stays in {d_detail['name']}")
                s_cols = st.columns(3)
                for s_idx, stay in enumerate(d_detail['stays']):
                    with s_cols[s_idx % 3]:
                        st.image(stay['image'], use_container_width=True)
                        st.markdown(f"#### {stay['name']}")
                        price_str = stay.get('price_display') or f"₹{stay.get('approximate_price', 2500):,.0f} / night"
                        st.caption(f"Category: {stay['category']} | Rate: **{price_str}**")
                        st.caption(f"Rating: ⭐ {stay.get('rating', '4.5')}")
                        st.write(stay['description'])

            # 5. Food & Specialties Tab
            with tab_food:
                st.markdown(f"### 🍜 Must-Try Food & Local Specialties in {d_detail['name']}")
                f_cols = st.columns(3)
                for f_idx, food in enumerate(d_detail['local_foods']):
                    with f_cols[f_idx % 3]:
                        st.image(food['image'], use_container_width=True)
                        st.markdown(f"#### {food['name']}")
                        st.caption(f"Category: {food['category']} | Must-Try: {'🔥 Yes' if food.get('is_must_try') else 'Regular'}")
                        st.write(food['description'])

            # 6. Transportation Tab
            with tab_transport:
                st.markdown(f"### 🚕 Transportation & Getting Around {d_detail['name']}")
                for t in d_detail['transports']:
                    cost_str = t.get('cost_display') or f"₹{t.get('approximate_cost', 200):,.0f}"
                    st.markdown(f"- 🚆 **{t.get('transport_mode') or t.get('mode')}**: {t.get('origin')} → {t.get('destination')} | **{cost_str}**")
                    if t.get('description'):
                        st.caption(t['description'])

            # 7. Emergency Info Tab
            with tab_safety:
                st.markdown("### 🚨 Emergency Contacts & Tourist Safety Info")
                e_col1, e_col2, e_col3, e_col4 = st.columns(4)
                with e_col1:
                    st.error("👮 **Police**: 112 / 100")
                with e_col2:
                    st.error("🚑 **Ambulance**: 102 / 108")
                with e_col3:
                    st.error("📞 **Helpline**: 1363")
                with e_col4:
                    st.error("🏥 **Hospital**: City Hospital")


# ==========================================
# PAGE 2: AI TRAVEL ASSISTANT CHATBOT
# ==========================================
elif navigation == "🤖 AI Travel Assistant":
    st.markdown('<div class="main-title">🤖 AI Travel Assistant Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ask for custom itineraries, food recommendations, and budget plans for any destination worldwide.</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Hello! I am your AI Travel Assistant. Where would you like to travel today? Ask me to plan a trip to Argentina, Belgium, Australia, Paris, Tokyo, or anywhere else!"}
        ]

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

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask AI Travel Assistant...") or selected_quick

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI Travel Assistant is crafting your custom response..."):
                db = SessionLocal()
                result = process_ai_chat_message(db, user=None, user_message=user_prompt)
                db.close()

                response_text = result["response"]
                st.markdown(response_text)

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
    st.markdown('<div class="sub-title">Verified Wikipedia and official research pages for all supported countries and landmarks.</div>', unsafe_allow_html=True)

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
