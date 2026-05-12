import streamlit as st
from supabase import create_client
import pandas as pd

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def get_form_rating(recent_form, role="Batsman"):
    try:
        if role == "Bowler":
            entries = [x.strip() for x in recent_form.split(",")]
            wickets = [int(e.split("/")[0]) for e in entries]
            avg_wickets = sum(wickets) / len(wickets)
            if avg_wickets >= 3:
                rating = "🔥 Hot Form"
            elif avg_wickets >= 1.5:
                rating = "👍 Average Form"
            else:
                rating = "❄️ Poor Form"
            return rating, round(avg_wickets, 1)
        else:
            scores = [int(x.strip()) for x in recent_form.split(",")]
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

st.set_page_config(page_title="RawStars", page_icon="🏏")
st.title("🏏 RawStars")
st.subheader("India's Cricket Talent Intelligence Platform")

players_all = load_players()
if players_all:
    total_players = len(players_all)
    total_cities = len(set(p["city"] for p in players_all))
    total_roles = len(set(p["role"] for p in players_all))
    col1, col2, col3 = st.columns(3)
    col1.metric("🏏 Players", total_players)
    col2.metric("🏙️ Cities", total_cities)
    col3.metric("⚡ Roles", total_roles)

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
        col1, col2, col3 = st.columns(3)
        cities = ["All Cities"] + sorted(list(set(p["city"] for p in players)))
        selected_city = col1.selectbox("🏙️ City", cities)
        roles = ["All Roles", "Batsman", "Bowler", "Wicketkeeper", "All-Rounder"]
        selected_role = col2.selectbox("🏏 Role", roles)
        styles = ["All Styles"] + sorted(list(set(p["bowling_style"] for p in players if p.get("bowling_style"))))
        selected_style = col3.selectbox("🌀 Bowling Style", styles)
        col4, col5 = st.columns(2)
        hands = ["All", "Right Hand", "Left Hand"]
        selected_hand = col4.selectbox("🤚 Batting Hand", hands)
        if selected_hand != "All":
            players = [p for p in players if p.get("batting_hand") == selected_hand]
        if selected_city != "All Cities":
            players = [p for p in players if p["city"] == selected_city]
        if selected_role != "All Roles":
            players = [p for p in players if p["role"] == selected_role]
        if selected_style != "All Styles":
            players = [p for p in players if p.get("bowling_style") == selected_style]
        rankings = []
        for p in players:
            rating, avg = get_form_rating(p["recent_form"], p["role"])
            rankings.append({
                "Player": p["name"],
                "City": p["city"],
                "Role": p["role"],
                "Form": rating,
                "Recent Avg": avg,
                "Career Avg": p["average"],
                "Username": p.get("username", "N/A"),
            })
        rankings.sort(key=lambda x: x["Recent Avg"], reverse=True)
        for i, p in enumerate(rankings):
            st.write(f"**#{i+1} {p['Player']}** (@{p.get('Username', 'N/A')}) — {p['City']} — {p['Role']} — {p['Form']} — Recent Avg: {p['Recent Avg']}")
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
        rating, avg = get_form_rating(player["recent_form"], player["role"])
        col1, col2, col3, col4 = st.columns(4)
        col1, col2, col3, col4 = st.columns(4)
        if player["role"] == "Bowler":
            col1.metric("Bowling Avg", player["average"])
            col2.metric("Economy Rate", player["strike_rate"])
            col3.metric("Recent Wickets Avg", avg)
            col4.metric("Total Wickets", player.get("wickets", 0))
        elif player["role"] == "Wicketkeeper":
            col1.metric("Batting Average", player["average"])
            col2.metric("Strike Rate", player["strike_rate"])
            col3.metric("Recent Average", avg)
            col4.metric("Dismissals", player.get("dismissals", 0))
        else:
            col1.metric("Career Average", player["average"])
            col2.metric("Strike Rate", player["strike_rate"])
            col3.metric("Recent Average", avg)
            col4.metric("Matches", player["matches"])
        st.info(f"Current Form: {rating}")
        details = f"City: {player['city']} | Age: {player['age']}"
        if player.get('batting_hand'):
            details += f" | Batting: {player['batting_hand']}"
        if player.get('bowling_style'):
            details += f" | Bowling: {player['bowling_style']}"
        if player.get('wicketkeeper'):
            details += " | 🧤 Wicketkeeper"
        st.caption(details)
        st.divider()
        st.subheader("📈 Form Chart")
        try:
            if player["role"] == "Bowler":
                entries = [x.strip() for x in player["recent_form"].split(",")]
                scores = [int(e.split("/")[0]) for e in entries]
            else:
                scores = [int(x.strip()) for x in player["recent_form"].split(",")]
            matches = list(range(1, len(scores) + 1))
            df = pd.DataFrame({"Match": matches, "Score": scores})
            st.line_chart(df.set_index("Match"))
        except:
            st.caption("No chart data available")
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
            r1, avg1 = get_form_rating(d1["recent_form"], d1["role"])
            r2, avg2 = get_form_rating(d2["recent_form"], d2["role"])
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
    role = col1.selectbox("Role", ["Batsman", "Bowler", "Wicketkeeper", "All-Rounder"])
    age = col2.number_input("Age", min_value=10, max_value=50, value=18)
    city = st.text_input("City")

    batting_hand = None
    bowling_style = None
    wicketkeeper = False

    if role == "Batsman":
        batting_hand = st.selectbox("Batting Hand", ["Right Hand", "Left Hand"])
    elif role == "Bowler":
        bowling_style = st.selectbox("Bowling Style", [
            "Right Arm Fast", "Right Arm Medium Fast",
            "Left Arm Fast", "Left Arm Medium Fast",
            "Off Spin", "Leg Spin", "Wrist Spin", "Mystery Spin"
        ])
    elif role == "Wicketkeeper":
        batting_hand = st.selectbox("Batting Hand", ["Right Hand", "Left Hand"])
        wicketkeeper = True
    elif role == "All-Rounder":
        col1, col2 = st.columns(2)
        batting_hand = col1.selectbox("Batting Hand", ["Right Hand", "Left Hand"])
        bowling_style = col2.selectbox("Bowling Style", [
            "Right Arm Fast", "Right Arm Medium Fast",
            "Left Arm Fast", "Left Arm Medium Fast",
            "Off Spin", "Leg Spin", "Wrist Spin", "Mystery Spin"
        ])

    matches = st.number_input("Total Matches Played", min_value=1, value=10)

    if role == "Bowler":
        average = st.number_input("Bowling Average (runs per wicket)", min_value=0.0, value=25.0)
        strike_rate = st.number_input("Economy Rate", min_value=0.0, value=7.5)
        wickets = st.number_input("Total Wickets", min_value=0, value=20)
        dismissals = 0
        recent_form = st.text_input(
            "Recent 5 Match Figures (wickets/runs)",
            placeholder="e.g. 3/22,2/18,1/30,4/25,2/20"
        )
    elif role == "Wicketkeeper":
        average = st.number_input("Career Batting Average", min_value=0.0, value=25.0)
        strike_rate = st.number_input("Strike Rate", min_value=0.0, value=110.0)
        dismissals = st.number_input("Total Dismissals", min_value=0, value=10)
        wickets = 0
        recent_form = st.text_input(
            "Recent 5 Match Scores (comma separated)",
            placeholder="e.g. 45,23,67,12,89"
        )
    else:
        average = st.number_input("Career Batting Average", min_value=0.0, value=25.0)
        strike_rate = st.number_input("Strike Rate", min_value=0.0, value=110.0)
        wickets = 0
        dismissals = 0
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
                supabase.table("players").insert({
                    "name": name,
                    "username": username,
                    "role": role,
                    "age": age,
                    "city": city,
                    "matches": matches,
                    "average": average,
                    "strike_rate": strike_rate,
                    "recent_form": recent_form,
                    "batting_hand": batting_hand,
                    "bowling_style": bowling_style,
                    "wicketkeeper": wicketkeeper,
                    "wickets": int(wickets),
                    "dismissals": int(dismissals)
                }).execute()
                rating, avg = get_form_rating(recent_form, role)
                st.success(f"Welcome to RawStars, {name}!")
                st.info(f"Your username: @{username} | Form: {rating} | Recent Avg: {avg}")
                st.balloons()
        else:
            st.error("Please fill in all fields including username!")
