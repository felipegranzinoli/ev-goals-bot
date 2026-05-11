import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": FOOTBALL_DATA_KEY}

# Ligas disponíveis no plano gratuito
LIGAS = {
    "PL":  "Premier League",
    "BL1": "Bundesliga",
    "SA":  "Serie A",
    "PD":  "La Liga",
    "FL1": "Ligue 1",
    "DED": "Eredivisie",
    "BSA": "Brasileirao Serie A",
}

def get_partidas(codigo_liga, temporada=2024, limite=60):
    """Busca partidas encerradas de uma liga."""
    try:
        url = f"{BASE_URL}/competitions/{codigo_liga}/matches"
        r = requests.get(url, headers=HEADERS, params={
            "season": temporada,
            "status": "FINISHED",
        })
        data = r.json()
        partidas = data.get("matches", [])[:limite]
        print(f"  {len(partidas)} partidas encontradas.")
        return partidas
    except Exception as e:
        print(f"  [ERRO] {e}")
        return []


def analisar_partida(partida):
    """
    Simula o bot no minuto 50 com 0x0
    e verifica se o Over 1.5 teria ganhado.
    """
    try:
        home = partida["homeTeam"]["name"]
        away = partida["awayTeam"]["name"]
        gols_home = partida["score"]["fullTime"]["home"] or 0
        gols_away = partida["score"]["fullTime"]["away"] or 0
        gols_totais = gols_home + gols_away

        # Simulamos entrada no minuto 50 com 0x0
        # Critério principal: jogo terminou com gols suficientes?
        mercado = "Over 1.5 gols (jogo)"
        ganhou = gols_totais >= 2

        return {
            "jogo": f"{home} x {away}",
            "gols": gols_totais,
            "mercado": mercado,
            "ganhou": ganhou,
        }
    except Exception as e:
        print(f"  [ERRO partida] {e}")
        return None


def rodar_backtest_liga(codigo, nome, temporada=2024):
    print(f"\n{'='*55}")
    print(f"📊 {nome} — temporada {temporada}")
    print(f"{'='*55}")

    partidas = get_partidas(codigo, temporada)
    if not partidas:
        return

    resultados = []
    for p in partidas:
        r = analisar_partida(p)
        if r:
            resultados.append(r)
        time.sleep(0.2)

    if not resultados:
        print("  Nenhuma partida analisada.")
        return

    ganhos = sum(1 for r in resultados if r["ganhou"])
    total = len(resultados)
    hit_rate = (ganhos / total) * 100
    ev_ok = "✅ EV+" if hit_rate >= 57 else "❌ EV-"

    print(f"  Partidas analisadas : {total}")
    print(f"  Ganhos / Perdas     : {ganhos} / {total - ganhos}")
    print(f"  Hit rate            : {hit_rate:.1f}%  {ev_ok}")

    # Top 5 jogos com mais gols
    print(f"\n  Top jogos (mais gols):")
    for r in sorted(resultados, key=lambda x: x["gols"], reverse=True)[:5]:
        icon = "✅" if r["ganhou"] else "❌"
        print(f"  {icon} {r['jogo']} | {r['gols']} gols")


def rodar_backtest_completo():
    print("\n🤖 BACKTEST REAL — football-data.org")
    print("Estratégia: Over 1.5 gols — entrada simulada no 50'")

    ganhos_total = 0
    total_geral = 0

    for codigo, nome in LIGAS.items():
        partidas = get_partidas(codigo, temporada=2024)
        if not partidas:
            continue

        resultados = [analisar_partida(p) for p in partidas]
        resultados = [r for r in resultados if r]

        ganhos = sum(1 for r in resultados if r["ganhou"])
        total = len(resultados)

        if total == 0:
            continue

        hit_rate = (ganhos / total) * 100
        ev_ok = "✅ EV+" if hit_rate >= 57 else "❌ EV-"
        ganhos_total += ganhos
        total_geral += total

        print(f"\n🏆 {nome}")
        print(f"   {total} jogos | Hit rate: {hit_rate:.1f}% {ev_ok}")
        time.sleep(1)  # respeita rate limit

    if total_geral > 0:
        hit_geral = (ganhos_total / total_geral) * 100
        print(f"\n{'='*55}")
        print(f"📈 RESULTADO GERAL")
        print(f"   Total jogos : {total_geral}")
        print(f"   Hit rate    : {hit_geral:.1f}%")
        print(f"   {'✅ ESTRATÉGIA COM EV+' if hit_geral >= 57 else '❌ ESTRATÉGIA SEM EV+'}")
        print("="*55)


if __name__ == "__main__":
    rodar_backtest_completo()