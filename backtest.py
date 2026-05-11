from sample_data import JOGOS_HISTORICOS
from analyzer import calcular_score_ev

def simular_entrada(jogo):
    """
    Simula o bot no minuto 50 com placar 0x0
    e verifica se o mercado sugerido teria ganhado.
    """
    jogo_simulado = {
        "id":          jogo["id"],
        "liga":        jogo["liga"],
        "liga_id":     jogo["liga_id"],
        "home":        jogo["home"],
        "away":        jogo["away"],
        "placar_home": 0,
        "placar_away": 0,
        "minuto":      50,
        "chutes_totais": jogo["chutes_totais"],
    }

    resultado = calcular_score_ev(jogo_simulado)
    if not resultado:
        return None

    gols_reais = jogo["gols_totais"]
    mercado    = resultado["mercado"]
    score      = resultado["score"]

    ganhou = False
    if "Over 1.5" in mercado and gols_reais >= 2:
        ganhou = True
    elif "Over 2.5" in mercado and gols_reais >= 3:
        ganhou = True
    elif "Over 0.5" in mercado and gols_reais >= 1:
        ganhou = True

    return {
        "jogo":    f"{jogo['home']} x {jogo['away']}",
        "liga":    jogo["liga"],
        "score":   score,
        "mercado": mercado,
        "gols":    gols_reais,
        "ganhou":  ganhou,
    }


def rodar_backtest():
    print("\n" + "="*55)
    print("📊 BACKTEST — Estratégia EV+ Gols ao Vivo")
    print("="*55)

    ligas = {}
    todos = []

    for jogo in JOGOS_HISTORICOS:
        r = simular_entrada(jogo)
        if not r or r["score"] < 60:
            continue
        todos.append(r)
        ligas.setdefault(r["liga"], []).append(r)

    # Resultado por liga
    for liga, resultados in ligas.items():
        ganhos   = sum(1 for r in resultados if r["ganhou"])
        total    = len(resultados)
        hit_rate = (ganhos / total) * 100
        ev_ok    = "✅ EV+" if hit_rate >= 57 else "❌ EV-"
        print(f"\n🏆 {liga}")
        print(f"   Jogos filtrados : {total}")
        print(f"   Ganhos / Perdas : {ganhos} / {total - ganhos}")
        print(f"   Hit rate        : {hit_rate:.1f}%  {ev_ok}")
        for r in sorted(resultados, key=lambda x: x["score"], reverse=True)[:3]:
            icon = "✅" if r["ganhou"] else "❌"
            print(f"   {icon} {r['jogo']} | {r['gols']} gols | score {r['score']} | {r['mercado']}")

    # Resultado geral
    if todos:
        ganhos_total = sum(1 for r in todos if r["ganhou"])
        hit_geral    = (ganhos_total / len(todos)) * 100
        print(f"\n{'='*55}")
        print(f"📈 RESULTADO GERAL")
        print(f"   Total de jogos filtrados : {len(todos)}")
        print(f"   Ganhos : {ganhos_total} | Perdas : {len(todos) - ganhos_total}")
        print(f"   Hit rate geral : {hit_geral:.1f}%")
        print(f"   {'✅ ESTRATÉGIA COM EV+' if hit_geral >= 57 else '❌ ESTRATÉGIA SEM EV+'}")
        print("="*55)
    else:
        print("\n⚠️  Nenhum jogo passou nos filtros.")


if __name__ == "__main__":
    rodar_backtest()