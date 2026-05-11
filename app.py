import streamlit as st
from supabase import create_client

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def get_form_rating(recent_scores):
    try:
        scores = [int(x.strip()) for x in recent_scores.split(",")]
        average = sum(scores) / len(scores)
        if average >= 50:
            rating = "🔥 Hot Form"
        elif average >= 25:
            rating = "👍 Average Form"
        else:
            rating = "❄️ Poor Form"
        return rating, round(average, 1)
    except:
        return "N/A", 0.0

def load_players():
    response = supabase.table("players").select("*").execute()
    return response.data

def register_player(name, username, role, age, city, matches, average, strike_rate, recent_form):
    supabase.table("players").insert({
        "name": name,
        "username": username,
        "role": role,
        "age": age,
        "city": city,
        "matches": matches,
        "average": average,
        "strike_rate": strike_rate,
        "recent_form": recent_form
    }).execute()

st.set_page_config(page_title="RawStars", page_icon="🏏")
st.title("🏏 RawStars")
st.subheader("India's Cricket Talent Intelligence Platform")
st.divider()

page = st.sidebar.radio("Navigate", [
    "Scout Dashboard",
    "Player Profile",
    "Compare Players",
    "Register Player"
])

if page == "Scout Dashboard":
    st.header("🏆 Scout Dashboard")
    st.caption("Players ranked by current form")
    players = load_players()
    if players:
        cities = ["All Cities"] + sorted(list(set(p["city"] for p in players)))
        selected_city = st.selectbox("🏙️ Filter by City", cities)
        if selected_city != "All Cities":
            players = [p for p in players if p["city"] == selected_city]
        rankings = []
        for p in players:
            rating, avg = get_form_rating(p["recent_form"])
            rankings.append({
                "Player": p["name"],
                "City": p["city"],
                "Role": p["role"],
                "Form": rating,
                "Recent Avg": avg,
                "Career Avg": p["average"],
            })
        rankings.sort(key=lambda x: x["Recent Avg"], reverse=True)
        for i, p in enumerate(rankings):
            st.write(f"**#{i+1} {p['Player']}** — {p['City']} — {p['Role']} — {p['Form']} — Recent Avg: {p['Recent Avg']}")
    else:
        st.info("No players registered yet. Be the first to join RawStars!")

elif page == "Player Profile":
    st.header("👤 Player Profile")
    players = load_players()
    if players:
        search = st.text_input("🔍 Search player by name")
        names = [p["name"] for p in players if search.lower() in p["name"].lower()]
        if not names:
            st.warning("No players found!")
            st.stop()
        name = st.selectbox("Select Player", names)
        player = next(p for p in players if p["name"] == name)
        rating, avg = get_form_rating(player["recent_form"])
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Career Average", player["average"])
        col2.metric("Strike Rate", player["strike_rate"])
        col3.metric("Recent Average", avg)
        col4.metric("Matches", player["matches"])
        st.info(f"Current Form: {rating}")
        st.caption(f"City: {player['city']} | Age: {player['age']}")
        st.divider()
        share_text = f"Check out {player['name']} on RawStars! 🏏%0A Role: {player['role']} | City: {player['city']}%0A Current Form: {rating} | Recent Avg: {avg}%0A%0ADiscover cricket talent at: https://rawstars-qzayzvdcf7alqcojvzoa46.streamlit.app"
        whatsapp_url = f"https://wa.me/?text={share_text}"
        st.markdown(f"[📲 Share on WhatsApp]({whatsapp_url})", unsafe_allow_html=True)
        st.caption("Share this player's profile with your coach or franchise!")
    else:
        st.info("No players registered yet!")

elif page == "Compare Players":
    st.header("⚔️ Compare Players")
    players = load_players()
    if players and len(players) >= 2:
        names = [p["name"] for p in players]
        col1, col2 = st.columns(2)
        p1_name = col1.selectbox("Player 1", names)
        p2_name = col2.selectbox("Player 2", names)
        if st.button("Compare"):
            d1 = next(p for p in players if p["name"] == p1_name)
            d2 = next(p for p in players if p["name"] == p2_name)
            r1, avg1 = get_form_rating(d1["recent_form"])
            r2, avg2 = get_form_rating(d2["recent_form"])
            col1.metric("Career Avg", d1["average"])
            col1.metric("Recent Avg", avg1)
            col1.write(r1)
            col2.metric("Career Avg", d2["average"])
            col2.metric("Recent Avg", avg2)
            col2.write(r2)
            st.divider()
            if avg1 > avg2:
                st.success(f"🏆 Scout Verdict: {p1_name} is in better current form")
            elif avg2 > avg1:
                st.success(f"🏆 Scout Verdict: {p2_name} is in better current form")
            else:
                st.success("🏆 Scout Verdict: Both players in equal form")
    else:
        st.info("Need at least 2 players registered to compare!")

elif page == "Register Player":
    st.header("📝 Register Your Profile")
    st.caption("Grassroots players — get discovered by scouts")
    name = st.text_input("Full Name")
    username = st.text_input("Username", placeholder="e.g. rahul_sharma_mumbai")
    st.caption("Your unique RawStars ID — choose carefully, it can't be changed!")
    col1, col2 = st.columns(2)
    role = col1.selectbox("Role", ["Batsman", "Bowler", "All-Rounder"])
    age = col2.number_input("Age", min_value=10, max_value=50, value=18)
    city = st.text_input("City")
    matches = st.number_input("Total Matches Played", min_value=1, value=10)
    average = st.number_input("Career Batting Average", min_value=0.0, value=25.0)
    strike_rate = st.number_input("Strike Rate", min_value=0.0, value=110.0)
    recent_form = st.text_input(
        "Recent 5 Match Scores (comma separated)",
        placeholder="e.g. 45,23,67,12,89"
    )
    if st.button("Register & Join RawStars"):
        if name and username and city and recent_form:
            existing = load_players()
            existing_usernames = [p["username"] for p in existing if p["username"]]
            if username.lower() in [u.lower() for u in existing_usernames]:
                st.error(f"Username '{username}' is already taken! Please choose another.")
            else:
                register_player(name, username, role, age, city, matches, average, strike_rate, recent_form)
                rating, avg = get_form_rating(recent_form)
                st.success(f"Welcome to RawStars, {name}!")
                st.info(f"Your username: @{username} | Form: {rating} | Recent Avg: {avg}")
                st.balloons()
        else:
            st.error("Please fill in all fields including username!")
