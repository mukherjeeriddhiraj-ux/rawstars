import streamlit as st

player_data = {
    "Virat Kohli": {"role": "Batsman", "matches": 111, "average": 53.5, "strike_rate": 137.9, "recent_form": "85,12,67,44,91"},
    "Rohit Sharma": {"role": "Batsman", "matches": 105, "average": 52.5, "strike_rate": 136.5, "recent_form": "82,33,44,45,20"},
    "Hardik Pandya": {"role": "All-Rounder", "matches": 107, "average": 49.5, "strike_rate": 120.6, "recent_form": "33,24,55,0,44"},
    "Ravindra Jadeja": {"role": "All-Rounder", "matches": 106, "average": 43.2, "strike_rate": 112.0, "recent_form": "30,20,35,45,28"},
    "Jasprit Bumrah": {"role": "Bowler", "matches": 145, "average": 24.1, "strike_rate": 118.3, "recent_form": "22,8,15,30,12"},
}

def get_form_rating(recent_scores):
    scores = [int(x.strip()) for x in recent_scores.split(",")]
    average = sum(scores) / len(scores)
    if average >= 50:
        rating = "🔥 Hot Form"
    elif average >= 25:
        rating = "👍 Average Form"
    else:
        rating = "❄️ Poor Form"
    return rating, round(average, 1)

st.set_page_config(page_title="RawStars", page_icon="🏏")
st.title("🏏 RawStars")
st.subheader("India's Cricket Talent Intelligence Platform")
st.divider()

page = st.sidebar.radio("Navigate", ["Scout Dashboard", "Player Profile", "Compare Players"])

if page == "Scout Dashboard":
    st.header("Scout Dashboard")
    rankings = []
    for name in player_data:
        p = player_data[name]
        rating, avg = get_form_rating(p["recent_form"])
        rankings.append({"Player": name, "Role": p["role"], "Form": rating, "Recent Avg": avg, "Career Avg": p["average"], "Strike Rate": p["strike_rate"]})
    rankings.sort(key=lambda x: x["Recent Avg"], reverse=True)
    for i, p in enumerate(rankings):
        st.write(f"**#{i+1} {p['Player']}** — {p['Role']} — {p['Form']} — Recent Avg: {p['Recent Avg']}")

elif page == "Player Profile":
    st.header("Player Profile")
    name = st.selectbox("Select Player", list(player_data.keys()))
    p = player_data[name]
    rating, avg = get_form_rating(p["recent_form"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Career Average", p["average"])
    col2.metric("Strike Rate", p["strike_rate"])
    col3.metric("Recent Average", avg)
    st.info(f"Current Form: {rating}")

elif page == "Compare Players":
    st.header("Compare Players")
    col1, col2 = st.columns(2)
    p1 = col1.selectbox("Player 1", list(player_data.keys()))
    p2 = col2.selectbox("Player 2", list(player_data.keys()))
    if st.button("Compare"):
        d1, d2 = player_data[p1], player_data[p2]
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
            st.success(f"Scout Verdict: {p1} is in better current form")
        elif avg2 > avg1:
            st.success(f"Scout Verdict: {p2} is in better current form")
        else:
            st.success("Scout Verdict: Both players in equal form")
            elif page == "Register Player":
    st.header("📝 Register Your Profile")
    st.caption("Grassroots players — get discovered by scouts")
    
    name = st.text_input("Full Name")
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
        if name and city and recent_form:
            st.session_state.player_data[name] = {
                "role": role,
                "age": age,
                "city": city,
                "matches": matches,
                "average": average,
                "strike_rate": strike_rate,
                "recent_form": recent_form
            }
            rating, avg = get_form_rating(recent_form)
            st.success(f"Welcome to RawStars, {name}!")
            st.info(f"Your current form rating: {rating} — Recent Average: {avg}")
            st.balloons()
        else:
            st.error("Please fill in all fields!")
