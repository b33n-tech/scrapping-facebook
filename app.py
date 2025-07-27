import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Extraction Membres Facebook", layout="centered")
st.title("🔍 Extraction intelligente des membres Facebook")
st.markdown("Collez ici les informations copiées depuis l'affichage du groupe Facebook (profils, ancienneté, activités)")

raw_text = st.text_area("Texte copié", height=300, placeholder="Collez ici...")

def detect_line_type(line):
    # Ancienneté
    if "Membre depuis" in line:
        return "anciennete"
    # Activité / lieu (simple règle)
    elif "à " in line or "," in line:
        return "activite"
    # Nom (si ça ressemble à un prénom/nom)
    elif re.match(r"^[A-ZÉÈÊÎÏÀÂÄÔÖÙÛÜÇ][a-zéèêàçîïöôûü\-']+\s+[A-ZÉÈÊÎÏÀÂÄÔÖÙÛÜÇ][a-zéèêàçîïöôûü\-']+", line):
        return "nom"
    else:
        return "inconnu"

def parse_lines(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    parsed = []
    current = {"Nom": "", "Ancienneté": "", "Activité / Lieu": ""}
    
    for line in lines:
        line_type = detect_line_type(line)

        if line_type == "nom":
            # S'il y a déjà un nom en cours, on l'enregistre
            if current["Nom"]:
                parsed.append(current)
                current = {"Nom": "", "Ancienneté": "", "Activité / Lieu": ""}
            current["Nom"] = line

        elif line_type == "anciennete":
            current["Ancienneté"] = line

        elif line_type == "activite":
            current["Activité / Lieu"] = line

    if current["Nom"]:  # Dernier enregistrement
        parsed.append(current)

    return pd.DataFrame(parsed)

if raw_text:
    df = parse_lines(raw_text)

    if df.empty:
        st.warning("Aucune donnée détectée. Vérifie le format.")
    else:
        st.success("Extraction réussie ! Voici les données :")
        st.dataframe(df, use_container_width=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Membres")
        
        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=buffer.getvalue(),
            file_name="membres_facebook.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
