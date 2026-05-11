import requests
import os
from dotenv import load_dotenv

load_dotenv()

BSD_KEY = os.getenv("BSD_API_KEY")
BSD_URL = "https://sports.bzzoiro.com/api"
HEADERS = {"Authorization": f"Token {BSD_KEY}"}

def get_jogos_ao_vivo_bsd():
    """Busca jogos ao vivo via BSD — sem limite de requisições."""
    try:
        response = requests.get(
            f"{BSD_URL}/live/",
            headers=HEADERS,
            timeout=10
        )
        data = response.json()
        resultados = data.get("results", [])

        if not resultados:
            return []

        jogos = []
        for jogo in resultados:
            try:
                live_stats = jogo.get("live_stats", {}) or {}
                home_stats = live_stats.get("home", {}) or {}
                away_stats = live_stats.get("away", {}) or {}

                chutes = (
                    int(home_stats.get("total_shots", 0) or 0) +
                    int(away_stats.get("total_shots", 0) or 0)
                )
                escanteios = (
                    int(home_stats.get("corner_kicks", 0) or 0) +
                    int(away_stats.get("corner_kicks", 0) or 0)
                )
                chutes_alvo = (
                    int(home_stats.get("shots_on_target", 0) or 0) +
                    int(away_stats.get("shots_on_target", 0) or 0)
                )
                big_chances = (
                    int(home_stats.get("big_chances", 0) or 0) +
                    int(away_stats.get("big_chances", 0) or 0)
                )
                xg = (
                    float(jogo.get("home_xg_live", 0) or 0) +
                    float(jogo.get("away_xg_live", 0) or 0)
                )

                minuto = int(jogo.get("current_minute", 0) or 0)

                jogos.append({
                    "id":            f"bsd_{jogo.get('id')}",
                    "liga":          jogo.get("league", {}).get("name", ""),
                    "liga_id":       jogo.get("league", {}).get("id", 0),
                    "home":          jogo.get("home_team", ""),
                    "away":          jogo.get("away_team", ""),
                    "placar_home":   int(jogo.get("home_score", 0) or 0),
                    "placar_away":   int(jogo.get("away_score", 0) or 0),
                    "minuto":        minuto,
                    "chutes_totais": chutes,
                    "chutes_alvo":   chutes_alvo,
                    "escanteios":    escanteios,
                    "big_chances":   big_chances,
                    "xg":            round(xg, 2),
                    "odd_over15":    0,
                    "odd_over25":    0,
                    "fonte":         "BSD",
                })
            except Exception as e:
                continue

        return jogos

    except Exception as e:
        print(f"[ERRO BSD] {e}")
        return []


if __name__ == "__main__":
    jogos = get_jogos_ao_vivo_bsd()
    print(f"BSD: {len(jogos)} jogos ao vivo\n")
    for j in jogos:
        print(f"  {j['home']} x {j['away']} | {j['liga']} | {j['minuto']}' | {j['placar_home']}x{j['placar_away']}")
        print(f"    chutes: {j['chutes_totais']} | alvo: {j['chutes_alvo']} | escanteios: {j['escanteios']} | xG: {j['xg']} | big chances: {j['big_chances']}")