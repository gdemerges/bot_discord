import streamlit as st
import sqlite3
import pandas as pd

st.title("📊 Dashboard des conversations")

# Connexion à la DB
conn = sqlite3.connect("bot_discord.db")
cursor = conn.cursor()

# Affichage des messages
cursor.execute("SELECT user_id, role, content, timestamp FROM messages ORDER BY timestamp DESC")
data = cursor.fetchall()
conn.close()

# Affichage des données sous forme de tableau
df = pd.DataFrame(data, columns=["User ID", "Role", "Message", "Timestamp"])
st.dataframe(df)

# Filtrer par utilisateur
user_id = st.text_input("🔍 Filtrer par ID utilisateur (optionnel)")
if user_id:
    df = df[df["User ID"] == int(user_id)]
    st.dataframe(df)