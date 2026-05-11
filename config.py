import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "SUA_CHAVE_AQUI")
API_URL = "https://v3.football.api-sports.io"

# Filtros da estrategia
MIN_MINUTE = 45
MAX_MINUTE = 68
MIN_SHOTS = 8
MIN_CORNERS = 5
MIN_ODDS = 1.40
MIN_SCORE_EV = 70

# LISTA NEGRA — Over 1.5 abaixo de 65% (EV negativo comprovado)
# Fonte: progressivebetting.co.uk + footystats 2024/2025
LIGAS_BLOQUEADAS = {
    # Africa
    "Ghana Premier League",        # 1.77 gols
    "Algeria Ligue 1",             # 1.89 gols
    "Tunisia Ligue 1",
    "Morocco Botola Pro",
    "Egypt Premier League",
    "Tanzania Premier League",
    "Uganda Premier League",
    "Zambia Super League",
    "Zimbabwe Premier Soccer League",

    # America do Sul defensiva
    "Argentina Primera Nacional",  # 1.79 gols
    "Liga Profesional Argentina",  # 2.00 gols
    "Primera B Metropolitana",
    "Primera B Nacional",
    "Peru Liga 1",
    "Ecuador Liga Pro",
    "Venezuela Primera Division",
    "Paraguay Division Profesional",

    # Asia defensiva
    "Persian Gulf Pro League",     # Ira - 1.99 gols
    "Iraq Stars League",
    "Uzbekistan Super League",
    "Tajikistan League",
    "Turkmenistan League",
    "Afghanistan Premier League",

    # Europa defensiva
    "Belarus Premier League",
    "Azerbaijan Premier League",
    "Armenia Premier League",
    "Georgia Erovnuli Liga",
    "Kosovo Superleague",

    # Outros
    "Olympic Games Men",
    "Friendlies",
    "Club Friendly",
    "World Cup",                   # odds muito eficientes
    "UEFA Champions League",       # mercado hiperliquido
    "UEFA Europa League",          # mercado hiperliquido
}

# Tier S — bonus +20pts (Over 1.5 acima de 82%, odds lentas)
# Fonte: progressivebetting.co.uk ranking atual
LIGAS_TIER_S = {
    "Singapore Premier League",    # 92.3%
    "Norway 1. Division",          # 90.0%
    "Iceland Urvalsdeild",         # 88.6%
    "Bolivia LFPB",                # 88.1%
    "Germany Regionalliga North",  # 87.7%
    "Eredivisie",                  # 86.2%
    "Slovenia PrvaLiga",           # 85.0%
    "Swiss Super League",          # 84.9%
    "Poland I Liga",               # 84.8%
    "Qatar Stars League",          # 84.7%
    "Chile Primera B",             # 83.6%
    "Scotland League Two",         # 83.3%
    "Iceland 1. Deild",            # 83.3%
    "3. Liga",                     # 83.1% (Alemanha)
    "Bundesliga",                  # 83.0%
    "Allsvenskan",                 # 82.7%
    "England National League North", # 82.6%
    "Northern Ireland Premiership",# 82.4%
    "Honduras LNP",                # 82.4%
    "Danish Superliga",            # 82.4%
    "Eerste Divisie",              # 82.1%
    "Malaysia Super League",       # 81.1%
    "Estonia Meistriliiga",        # 81.1%
    "Moldova National Division",   # 81.1%
    "J1 League",                   # 80.8%
    "Hungary NB I",                # 80.7%
    "Saudi Professional League",   # 80.5%
    "Croatia HNL",                 # 80.3%
    "2. Bundesliga",               # 80.2%
    "England National League",     # 80.0%
}

# Tier A — bonus +10pts (Over 1.5 entre 76% e 82%)
LIGAS_TIER_A = {
    "Liga MX",                     # 79.3%
    "MLS",                         # 79.1%
    "La Liga",                     # 78.6%
    "Turkey 1. Lig",               # 78.5%
    "Premier League",              # 78.5%
    "Israeli Premier League",      # 78.4%
    "Scotland League One",         # 78.3%
    "Swiss Challenge League",      # 78.2%
    "A-League Men",                # 78.2%
    "Slovakia Super Liga",         # 76.1%
    "Scotland Premiership",        # 76.7%
    "Ekstraklasa",                 # 76.6%
    "Austrian Bundesliga",         # 76.5%
    "Süper Lig",                   # 76.4%
    "Latvia Virsliga",             # 76.4%
    "Thai League 1",               # 76.3%
    "Pro League",                  # 76.2% (Belgica)
    "Championship",                # 76.2%
    "Brazil Serie A",              # 77.3%
    "Sweden Superettan",           # 77.1%
    "China Super League",          # 76.9%
    "Eliteserien",                 # 81.4%
    "J2 League",
    "K League 1",
    "K League 2",
    "Brazil Serie B",
    "Liga BetPlay",
}