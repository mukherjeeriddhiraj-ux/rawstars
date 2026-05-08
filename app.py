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
