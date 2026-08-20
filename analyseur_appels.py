import streamlit as st
import google.generativeai as genai
import os

# Configuration de la page
st.set_page_config(page_title="AGHassur - Auditeur Vocal IA", layout="wide")

# 🔒 LE PROMPT D'ORIGINE COMPLET ISOLÉ EN HAUT
PROMPT_BASE = """Tu es un expert en audit de vente d'assurances santé (Spécialiste Mutuelle Senior en France) agissant pour le cabinet AGHassur.
Rédige TOUTE ton analyse en français de manière extrêmement professionnelle, structurée, scannable et TRÈS APPROFONDIE.
Analyse cet appel UNIQUE dans sa totalité pour donner un rapport cohérent du début à la fin.

RÈGLES DE DÉCODAGE DES PERSONNAGES & GESTION DU TRANSFERT :
1. Le PREMIER interlocuteur qui parle dans le script est TOUJOURS l'Expert / Le Conseiller Commercial.
2. CONTEXTE DE TRANSFERT DE LIGNE CRUCIAL : Le DEUXIÈME interlocuteur (Interlocuteur 2) est TOUJOURS le Prospect/Client Senior final.
⚠️ ATTENTION : À cause du transfert de ligne sur Ringover, le nom affiché à côté des répliques de l'interlocuteur 2 peut être erroné. Ignore cette erreur.

CONSIGNE ULTRA-CRUCIALE : IMPLANTATION DES VERBATIMS (PROPOS EXACTS) :
Tu devez impérativement extraire et CITER LE TEXTE EXACT (Verbatim entre guillemets) dit par l'expert ou le client pour appuyer tes conclusions dans chaque section, en particulier dans les erreurs, les objections et les commentaires du responsable.

CONSIGNE ABSOLUE SUR LE TEMPS (TIMESTAMPS) :
Tu dois lister le temps exact (Timestamp comme [01:23] ou [04:12]) extrait du texte pour TOUTES LES SECTIONS du rapport. Il est interdit de rédiger une observation sans son horodatage précis.

Génère un rapport contenant obligatoirement les sections suivantes :

### 1. Analyse Critique et Profonde des Erreurs de l'Expert (Horodatage Chronologique)
Dudique chaque ligne et chaque mot prononcé par l'Expert (Interlocuteur 1). Repère la moindre faille sur le plan commercial, technique et métier (Flou Reste à Charge, mauvaise explication Noémie/Tiers Payant, manquement au devoir de conseil, non-respect de la grille tarifaire).
Format strict attendu :
- [Horodatage] - Erreur détectée. Propos exacts de l'expert : "[Citer sa phrase exacte ici]". Analyse de l'impact : [Expliquer pourquoi c'est une erreur].
⚠️ NOTE D'ÉQUITÉ QUANT AUX CLIENTS DIFFICILES : Si après analyse ultra-poussée du texte, tu constates que l'expert n'a commis aucune erreur métier ou technique, qu'il a été irréprochable et que le blocage vient uniquement d'un client hermétique, mentionne explicitement : 'Aucune erreur technique ou commerciale détectée. L'expert a parfaitement respecté le cahier des charges.'

### 2. Causes de Refus, Objections et Profil du Client Final (Interlocuteur 2) (Avec Horodatage)
Base-toi uniquement sur les propos du deuxième interlocuteur (le client senior réel) pour lister ses blocages.
Format strict attendu :
- [Horodatage] - Objection / Cause de refus. Propos exacts du client : "[Citer sa phrase exacte ici]". Analyse psychologique/commerciale : [Client de mauvaise foi, agressif, pas coopératif, indécis, ou bloqué].

### 3. Solutions de Traitement & Plan d'Action Correctif (Mise en correspondance temporelle)
Donne pour chaque minute d'erreur de l'expert ou d'objection du client final, le script exact ou la posture idéale attendue.
Si l'expert a tout bien fait face à un client bloqué, propose des techniques de contournement psychologique ou des offres alternatives adaptées aux profils seniors complexes.

### 4. Tableau de Comparaison des Garanties
Génère un tableau comparatif au format Markdown strict basé uniquement sur les données réelles de cet appel :

| Poste de Santé | Attentes & Besoins du Client Senior (Interlocuteur 2) | Offre & Proposition de l'Expert (Interlocuteur 1) |

### 5. Avis Indépendant et Évaluation du R.G.P.D AGHassur (Module Final Isolé)
Prends de la hauteur en tant que R.G.P.D AGHassur pour donner une conclusion claire, juridique, technique et stratégique sur le dossier. Tu devez obligatoirement fournir :
- **Orientation de la Responsabilité Principale de l'échec :** [Détermine avec précision si l'échec de la vente est imputable à un manque de compétence/clarté de l'Expert, ou s'il s'agit d'un 'Échec commercial inhérent au profil du Client' (Client hermétique / refus de coopérer malgré la bonne posture de l'expert)].
- **Statut Conformité R.G.P.D. (Données de Santé) :** [Analyse si l'expert a respecté la protection des données sensibles : Vérification d'identité, recueil du consentement, absence de fuite d'informations sur les pathologies. Statut : Conforme / Non Conforme avec justification].
- **Risque de Chute de Contrat (Résiliation / Non-signature) :** [Évalue l'impact au regard des réglementations françaises : Risque Faible, Moyen ou Critique de perte du client lié aux lois Hamon ou Châtel].
- **Raison Métier du Blocage :** [Sélectionne la cause majeure détectée : Flou sur le Reste à Charge / Problème Noémie ou Tiers Payant / Devis non conforme ou pièces manquantes / Client difficile ou réfractaire].
- **Commentaire Détaillé de Synthèse (R.G.P.D AGHassur) :** [Rédige ici un long paragraphe de synthèse approfondi reprenant les points clés de l'échange. Tu devez impérativement inclure et commenter les phrases clés d'illustrations].
- **ALERTES SUR LES RISQUES (Impact sur la Vente & Litige Mutuelle) :** [Alerte le cabinet AGHassur sur l'impact direct des erreurs détectées. Précise si l'erreur commise par l'expert 'altère / plombe définitivement la vente' ou si elle 'génère un litige grave avec la Mutuelle partenaire'].
- **Décision et Recommandation Finale du R.G.P.D AGHassur :** [Action concrète à mener : Si l'expert a échoué -> Plan de formation ciblé. Si l'expert a bien travaillé -> Validation qualité du conseiller + Transmission immédiate du dossier à un superviseur pour rappel de rétention/sauvetage].

Voici la transcription de l'appel complète à analyser :
"""

# 🔒 Base de données des utilisateurs certifiés AGHassur
USERS_DB = {
    "admin": {"password": "aghassur2026", "credits": "Illimité"},
    "cabinet_tunis": {"password": "tp1234", "credits": 5},
    "client_france": {"password": "agh7500", "credits": 5}
}

# Initialisation sécurisée
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_logged" not in st.session_state:
    st.session_state.user_logged = ""
if "analyse_text" not in st.session_state:
    st.session_state.analyse_text = None
if "user_credits" not in st.session_state:
    st.session_state.user_credits = 0

# Style CSS
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:700; color:#1E3A8A; margin-bottom:5px; text-align: center; }
    .subtitle { font-size:16px; color:#4B5563; margin-bottom:25px; text-align: center; }
    .stButton>button { background-color: #1E3A8A; color: white; font-weight:600; padding: 10px 24px; border-radius: 6px; border: none; width: 100%; }
    .stButton>button:hover { background-color: #172554; color: white; }
    </style>
""", unsafe_allow_html=True)

# 1️⃣ ÉCRAN DE CONNEXION PRIVÉ
if not st.session_state.authenticated:
    st.markdown('<div class="main-title">🔐 Connexion — AGHassur Audit IA</div>', unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit_login = st.form_submit_button("Se connecter")
        if submit_login:
            if username in USERS_DB and USERS_DB[username]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user_logged = username
                st.session_state.user_credits = USERS_DB[username]["credits"]
                st.rerun()
            else:
                st.error("Identifiants incorrects. Veuillez réessayer.")

# 2️⃣ INTERFACE PRINCIPALE
else:
    user = st.session_state.user_logged
    st.markdown('<div class="main-title">🎙️ AGHassur — Auditeur Vocal IA</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Connecté en tant que : <b>{user}</b></div>', unsafe_allow_html=True)
    
    st.sidebar.metric(label="Crédits d'analyse restants", value=str(st.session_state.user_credits))
    
    if st.sidebar.button("Se déconnecter"):
        st.session_state.authenticated = False
        st.session_state.user_logged = ""
        st.session_state.analyse_text = None
        st.rerun()

    st.markdown("### 📝 Collez la transcription de l'appel ci-dessous :")
    transcription = st.text_area("Insérez le texte complet de l'échange ici...", height=300, placeholder="[00:01] Expert: Bonjour...", key="input_transcription")
    
    # معالجة الضغط الفلاتر والتحليل
    if st.button("🚀 Lancer l'Audit et l'Analyse de l'appel"):
        if not transcription.strip():
            st.warning("⚠️ Veuillez coller une transcription avant de lancer l'analyse.")
        elif user != "admin" and st.session_state.user_credits <= 0:
            st.error("❌ Vous n'avez plus de crédits suffisants pour effectuer cette analyse.")
        else:
            with st.spinner("🧠 L'IA AGHassur analyse l'échange en profondeur... Veuillez patienter..."):
                try:
                    # 🔴 ضع مفتاح الـ API الحقيقي الخاص بك هنا مكان الكلمة المكتوبة بالفرنسية
                    api_key = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
                    genai.configure(api_key=api_key)
                    
                    model = genai.GenerativeModel("gemini-1.5-pro")
                    prompt_final = f"{PROMPT_BASE}\n{transcription}"
                    
                    response = model.generate_content(prompt_final)
                    st.session_state.analyse_text = response.text
                    
                    if user != "admin":
                        st.session_state.user_credits -= 1
                        
                    st.success("✅ Analyse terminée avec succès !")
                except Exception as e:












