import streamlit as st
from graph import build_graph

st.set_page_config(page_title="AI Travel Planner", page_icon="🌍", layout="wide")

st.title("🌍 AI Travel Planner")
st.caption("Powered by LangGraph + Groq — Multi-agent itinerary builder")

# ── Sidebar: Input Form ──────────────────────────────────────────
with st.sidebar:
    st.header("✈️ Trip Details")

    destination = st.text_input("Destination", "Bangkok, Thailand")
    origin = st.text_input("Flying from", "Bengaluru, India")

    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start date")
    end_date = col2.date_input("End date")

    # Manual budget input in rupees
    budget_inr = st.number_input(
        "Total Budget (₹)",
        min_value=1000,
        max_value=10000000,
        value=80000,
        step=1000
    )
    budget_usd = round(budget_inr / 84, 2)
    st.caption(f"≈ ${budget_usd} USD")

    travelers = st.number_input("Travelers", min_value=1, max_value=20, value=1)

    # Transport mode
    st.markdown("**Mode of Transport**")
    transport_mode = st.radio(
        "",
        ["✈️ Flight", "🚆 Train", "🚗 Car"],
        horizontal=True
    )

    # Extended interests
    preferences = st.multiselect(
        "Interests",
        [
            "Food", "Culture", "Adventure", "Nature", "Nightlife",
            "Shopping", "History", "Art", "Music", "Sports",
            "Photography", "Wildlife", "Beach", "Trekking",
            "Temples & Spirituality", "Local Markets", "Road Trips",
            "Luxury", "Budget Travel", "Family Friendly"
        ],
        default=["Food", "Culture"]
    )

    plan_button = st.button("🚀 Plan My Trip", use_container_width=True)

# ── Main Area ────────────────────────────────────────────────────
if plan_button:
    if not preferences:
        st.warning("Please select at least one interest.")
    else:
        app = build_graph()

        # Pass transport mode into preferences so agents are aware
        transport_label = transport_mode.split(" ")[1]  # "Flight", "Train", "Car"
        enriched_preferences = [p.lower() for p in preferences]

        initial_state = {
            "destination": destination,
            "origin": origin,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "budget": budget_inr,
            "budget_inr": budget_inr,
            "preferences": enriched_preferences,
            "travelers": travelers,
            "transport_mode": transport_label,
            "suggested_places": [],
            "daily_itinerary": [],
            "weather_summary": "",
            "cost_breakdown": {},
            "total_estimated_cost": 0.0,
            "within_budget": True,
            "optimization_suggestions": [],
            "messages": [],
            "replanning_needed": False,
            "iteration_count": 0

        }

        # Inject transport mode into the trip planner prompt via system context
        st.session_state["transport_mode"] = transport_label
        st.session_state["budget_inr"] = budget_inr

        with st.spinner("🗺️ Trip Planner agent building your itinerary..."):
            result = app.invoke(initial_state)

        # ── Weather Banner ───────────────────────────────────────
        if result.get("weather_summary"):
            st.info(f"🌤️ {result['weather_summary']}")

        # ── Transport Badge ──────────────────────────────────────
        transport_colors = {
            "Flight": "🟦", "Train": "🟩", "Car": "🟧"
        }
        st.markdown(f"{transport_colors.get(transport_label, '🔵')} **Travelling by {transport_label}** from {origin} to {destination}")

        st.divider()

        # ── Two Column Layout ────────────────────────────────────
        left, right = st.columns([3, 2])

        with left:
            st.subheader("📅 Your Itinerary")
            itinerary = result.get("daily_itinerary", [])
            if itinerary:
                raw = itinerary[0].get("raw", "")
                st.markdown(raw)
            else:
                st.warning("No itinerary generated.")

        with right:
            st.subheader("💰 Budget Breakdown")

            total_inr = round(result.get("total_estimated_cost", 0))
            breakdown = result.get("cost_breakdown", {})
            within_budget = result.get("within_budget", True)

            if within_budget:
                st.success(f"✅ Within budget! Total: **₹{total_inr:,}** / ₹{budget_inr:,}")
            else:
                st.error(f"❌ Over budget! Total: **₹{total_inr:,}** / ₹{budget_inr:,}")

            if breakdown:
                for category, amount in breakdown.items():
                    amount = round(amount)
                    pct = min(int((amount / budget_inr) * 100), 100)
                    st.markdown(f"**{category.capitalize()}** — ₹{amount:,}")
                    st.progress(pct)
            # Suggestions
            suggestions = result.get("optimization_suggestions", [])
            if suggestions:
                st.subheader("💡 Money-Saving Tips")
                for tip in suggestions:
                    st.markdown(f"- {tip}")

else:
    st.markdown("""
    ### How it works
    1. Fill in your trip details in the sidebar
    2. Choose your **mode of transport** — Flight, Train or Car
    3. Set your **budget in ₹ Rupees**
    4. Pick as many **interests** as you like
    5. Click **Plan My Trip** — two AI agents collaborate:
       - 🗺️ **Trip Planner** — builds a day-by-day itinerary using real data
       - 💰 **Budget Optimizer** — analyzes costs and suggests savings
    6. Get a full itinerary in under 2 minutes
    """)