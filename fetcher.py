import requests
from config import API_KEY, API_URL, LIGAS_BLOQUEADAS

HEADERS = {
    "x-apisports-key": API_KEY
}

def get_jogos_ao_vivo():
    """Busca TODOS os jogos ao vivo exceto ligas bloqueadas."""
    try:
        response = requests.get(
            f"{API_URL}/fixtures",
            headers=HEADERS,
            params={"live": "all"}
        )
        data = response.json()

        if not data.get("response"):
            return []

        jogos = []
        for jogo in data["response"]:
            liga_nome = jogo["league"]["name"]

            # Pula ligas bloqueadas
            if liga_nome in LIGAS_BLOQUEADAS:
                continue

            # Chutes totais
            chutes = 0
            escanteios = 0
            for time_stats in jogo.get("statistics", []):
                for stat in time_stats.get("statistics", []):
                    if stat["type"] == "Total Shots":
                        try:
                            chutes += int(stat["value"] or 0)
                        except:
                            pass
                    if stat["type"] == "Corner Kicks":
                        try:
                            escanteios += int(stat["value"] or 0)
                        except:
                            pass

            jogos.append({
                "id":           jogo["fixture"]["id"],
                "liga":         liga_nome,
                "liga_id":      jogo["league"]["id"],
                "home":         jogo["teams"]["home"]["name"],
                "away":         jogo["teams"]["away"]["name"],
                "placar_home":  jogo["goals"]["home"],
                "placar_away":  jogo["goals"]["away"],
                "minuto":       jogo["fixture"]["status"]["elapsed"] or 0,
                "chutes_totais": chutes,
                "escanteios":   escanteios,
            })

        return jogos

    except Exception as e:
        print(f"[ERRO fetcher] {e}")
        return []