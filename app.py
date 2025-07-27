import streamlit as st
import pandas as pd
import io
import re

st.title("Extraction des membres d'un groupe Facebook")

st.markdown("Colle ici les informations copiées depuis l'affichage du groupe Facebook :")

raw_text = st.text_area("Texte copié", height=300)

def parse_facebook_members(text):
    lines = [line.strip() for line in text.split('\n') if line.strip() != '']
    members = []
    i = 0
    while i < len(lines):
        if i + 1 < len(lines) and "Membre depuis" in lines[i+1]:
            name = lines[i]
            seniority = lines[i+1]
            activity = ""
            if i + 2 < len(lines) and "Membre depuis" not in lines[i+2]:
                activity = lines[i+2]
                i += 3
            else:
                i += 2
            members.append({
                "Nom": name,
                "Ancienneté": seniority,
                "Activité / Lieu": activity
            })
        else:
            i += 1
    return pd.DataFrame(members)

if raw_text:
    df = parse_facebook_members(raw_text)
    st.success("Extraction terminée ! Voici l'aperçu :")
    st.dataframe(df)

    # Préparer le fichier Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Membres")
        writer.save()
        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=buffer.getvalue(),
            file_name="membres_facebook.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
