import math
from config import (MIN_MINUTE, MAX_MINUTE, MIN_SHOTS,
                    MIN_CORNERS, MIN_ODDS, MIN_SCORE_EV,
                    LIGAS_TIER_S, LIGAS_TIER_A)


# ─── CONSTANTES CALIBRADAS ────────────────────────────────────────────────────
# Baseado em Dixon-Robinson (1998) e dados de 25.464 jogos históricos

# Multiplicadores de intensidade por estado do jogo (placar diferencial)
# Fonte: Dixon-Robinson state-dependent Poisson
INTENSIDADE_PERDENDO = {
    0: 1.00,   # empatado
    1: 1.35,   # perdendo por 1
    2: 1.60,   # perdendo por 2
    3: 1.80,   # perdendo por 3+
}
INTENSIDADE_GANHANDO = {
    0: 1.00,   # empatado
    1: 0.75,   # ganhando por 1 (segura)
    2: 0.60,   # ganhando por 2 (muito fechado)
    3: 0.50,   # ganhando por 3+ (só administra)
}

# Taxa de gols por minuto no 2T (normalizada para 1.0 no 1T)
# Gols aumentam no final — dados históricos
FATOR_TEMPO_2T = {
    (45, 55): 1.10,
    (55, 65): 1.20,
    (65, 75): 1.30,
    (75, 85): 1.40,
    (85, 95): 1.50,
}

# xG médio por big chance não convertida (baseado em Opta/StatsBomb)
XG_POR_BIG_CHANCE = 0.35


# ─── MODELO DE POISSON SEPARADO POR TIME ─────────────────────────────────────

def get_fator_tempo(minuto):
    for (inicio, fim), fator in FATOR_TEMPO_2T.items():
        if inicio <= minuto < fim:
            return fator
    return 1.50  # acréscimos


def estimar_lambda(xg_time, big_chances_time, minuto, diff_gols):
    """
    Estima o λ (taxa de gols) restante para um time específico.

    xg_time: xG acumulado do time no jogo
    big_chances_time: big chances do time
    minuto: minuto atual
    diff_gols: diferença de gols do ponto de vista deste time
               positivo = ganhando, negativo = perdendo
    """
    minutos_jogados   = max(minuto, 1)
    minutos_restantes = max(90 - minuto, 1)

    # Taxa base de xG por minuto
    taxa_base = xg_time / minutos_jogados

    # xG projetado para os minutos restantes (taxa × tempo)
    xg_restante = taxa_base * minutos_restantes

    # Fator temporal (mais gols no final)
    xg_restante *= get_fator_tempo(minuto)

    # Fator de estado — must win ou se fecha
    if diff_gols < 0:
        # Time perdendo — pressiona mais
        mult = INTENSIDADE_PERDENDO.get(abs(diff_gols), 1.80)
        xg_restante *= mult
    elif diff_gols > 0:
        # Time ganhando — se fecha
        mult = INTENSIDADE_GANHANDO.get(diff_gols, 0.50)
        xg_restante *= mult
    # diff_gols == 0: empatado, sem ajuste

    # Big chances não convertidas = pressão latente
    xg_restante += big_chances_time * XG_POR_BIG_CHANCE * (minutos_restantes / 90)

    # Fallback se não temos xG (API sem dado)
    if xg_time == 0:
        chutes_time = big_chances_time * 2  # estimativa grosseira
        xg_restante = chutes_time * 0.09 * (minutos_restantes / 90)

    return max(0.001, round(xg_restante, 4))


def poisson_prob(k, lam):
    """P(X = k) para distribuição de Poisson com taxa λ."""
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)


def prob_gols_adicionais(lam_home, lam_away, gols_necessarios):
    """
    Calcula P(gols adicionais >= N) usando Poisson separado por time.
    Combina as distribuições independentes de home e away.

    gols_necessarios: quantos gols ADICIONAIS precisam sair
    """
    if gols_necessarios == 1:
        # P(≥1 gol adicional) = 1 - P(0 gols home) × P(0 gols away)
        p_zero_home  = math.exp(-lam_home)
        p_zero_away  = math.exp(-lam_away)
        p_zero_total = p_zero_home * p_zero_away
        return round(1 - p_zero_total, 4)

    elif gols_necessarios == 2:
        # P(≥2 gols adicionais) — soma combinações
        prob = 0
        for h in range(6):
            for a in range(6):
                if h + a >= 2:
                    prob += poisson_prob(h, lam_home) * poisson_prob(a, lam_away)
        return round(min(prob, 0.999), 4)

    elif gols_necessarios == 3:
        prob = 0
        for h in range(7):
            for a in range(7):
                if h + a >= 3:
                    prob += poisson_prob(h, lam_home) * poisson_prob(a, lam_away)
        return round(min(prob, 0.999), 4)

    return 0.5


def odd_justa(prob):
    """Odd justa sem margem da casa."""
    if prob <= 0:
        return 99.0
    return round(1 / prob, 2)


# ─── MERCADO CORRETO POR SITUAÇÃO ─────────────────────────────────────────────

def definir_mercado_e_gols_necessarios(gols_totais, minuto):
    """
    Define o mercado correto E quantos gols adicionais são necessários.
    Isso corrige o bug onde mostrávamos prob errada para o mercado.
    """
    if gols_totais == 0:
        if minuto <= 60:
            return "Over 1.5 gols (jogo)", 2   # precisa de 2 gols adicionais
        else:
            return "Over 0.5 gols no 2T", 1    # precisa de 1 gol adicional

    elif gols_totais == 1:
        if minuto <= 65:
            return "Over 2.5 gols (jogo)", 2   # precisa de 2 gols adicionais
        else:
            return "Over 1.5 gols no 2T", 1    # precisa de 1 gol adicional

    elif gols_totais == 2:
        return "Over 2.5 gols (jogo)", 1       # precisa de 1 gol adicional

    return "Avaliar manualmente", 1


# ─── SCORE EV + FILTROS ───────────────────────────────────────────────────────

def calcular_score_ev(jogo):
    score   = 0
    motivos = []

    minuto      = jogo["minuto"]
    placar_home = jogo.get("placar_home") or 0
    placar_away = jogo.get("placar_away") or 0
    gols_totais = placar_home + placar_away
    chutes      = jogo.get("chutes_totais", 0)
    escanteios  = jogo.get("escanteios", 0)
    chutes_alvo = jogo.get("chutes_alvo", 0)

    # xG e big chances separados por time (BSD fornece isso)
    xg_home = jogo.get("xg_home", jogo.get("xg", 0.0) / 2)
    xg_away = jogo.get("xg_away", jogo.get("xg", 0.0) / 2)
    bc_home = jogo.get("big_chances_home", jogo.get("big_chances", 0) // 2)
    bc_away = jogo.get("big_chances_away", jogo.get("big_chances", 0) - bc_home)

    # ── Filtro de minuto ──────────────────────────────────────────────────────
    if minuto < MIN_MINUTE or minuto > MAX_MINUTE:
        return None
    score += 30
    motivos.append(f"minuto ideal ({minuto}')")

    # ── Filtro de placar ──────────────────────────────────────────────────────
    if gols_totais == 0:
        score += 25
        motivos.append("0x0 — ambos vão atacar no 2T")
    elif gols_totais == 1:
        score += 18
        motivos.append(f"placar {placar_home}x{placar_away} — must win ativo")
    elif gols_totais == 2:
        score += 8
        motivos.append(f"placar {placar_home}x{placar_away} — Over 2.5 em aberto")
    else:
        return None

    # ── Filtro de finalizações ────────────────────────────────────────────────
    if chutes >= 14:
        score += 20
        motivos.append(f"{chutes} finalizações — jogo muito aberto")
    elif chutes >= 10:
        score += 14
        motivos.append(f"{chutes} finalizações — pressão ofensiva")
    elif chutes >= MIN_SHOTS:
        score += 8
        motivos.append(f"{chutes} finalizações — mínimo atingido")
    else:
        return None

    # ── Chutes no alvo ────────────────────────────────────────────────────────
    if chutes_alvo >= 5:
        score += 10
        motivos.append(f"{chutes_alvo} chutes no alvo — perigo real")
    elif chutes_alvo >= 3:
        score += 5
        motivos.append(f"{chutes_alvo} chutes no alvo")

    # ── Filtro de escanteios ──────────────────────────────────────────────────
    if escanteios >= 7:
        score += 12
        motivos.append(f"{escanteios} escanteios — alta pressão")
    elif escanteios >= MIN_CORNERS:
        score += 6
        motivos.append(f"{escanteios} escanteios — pressão moderada")
    else:
        return None

    # ── Bonus por liga ────────────────────────────────────────────────────────
    liga = jogo["liga"]
    if liga in LIGAS_TIER_S:
        score += 15
        motivos.append(f"Tier S ({liga}) — odds lentas")
    elif liga in LIGAS_TIER_A:
        score += 8
        motivos.append(f"Tier A ({liga}) — bom histórico EV+")
    else:
        score += 3

    # ── MODELO DIXON-ROBINSON ─────────────────────────────────────────────────
    mercado, gols_necessarios = definir_mercado_e_gols_necessarios(gols_totais, minuto)

    # Diferença de gols do ponto de vista de cada time
    diff_home = placar_home - placar_away  # positivo = home ganhando
    diff_away = placar_away - placar_home  # positivo = away ganhando

    # Lambda restante para cada time
    lam_home = estimar_lambda(xg_home, bc_home, minuto, diff_home)
    lam_away = estimar_lambda(xg_away, bc_away, minuto, diff_away)

    # Probabilidade correta para o mercado
    prob = prob_gols_adicionais(lam_home, lam_away, gols_necessarios)
    oj   = odd_justa(prob)

    # Elimina se probabilidade muito baixa
    if prob < 0.45:
        return None

    # Motivo com contexto claro
    motivos.append(
        f"λ home {lam_home} + λ away {lam_away} → "
        f"P({gols_necessarios}+ gols adicionais) = {round(prob*100,1)}% → odd justa {oj}"
    )

    # Must-win explícito no motivo
    if diff_home < 0:
        motivos.append(f"must win: {jogo['home']} perdendo, intensidade +{int((INTENSIDADE_PERDENDO.get(abs(diff_home), 1.8)-1)*100)}%")
    elif diff_away < 0:
        motivos.append(f"must win: {jogo['away']} perdendo, intensidade +{int((INTENSIDADE_PERDENDO.get(abs(diff_away), 1.8)-1)*100)}%")

    # Verifica odd do mercado
    odd_over15  = jogo.get("odd_over15", 0)
    odd_over25  = jogo.get("odd_over25", 0)
    odd_mercado = odd_over15 if gols_necessarios <= 1 else odd_over25

    if odd_mercado > 0:
        if odd_mercado < oj:
            return None
        ev_pct = round((odd_mercado * prob - 1) * 100, 1)
        motivos.append(f"odd mercado {odd_mercado} > odd justa {oj} → EV +{ev_pct}%")
    else:
        motivos.append(f"entre se odd ≥ {oj} na casa")

    return {
        "score":           min(score, 100),
        "motivos":         motivos,
        "mercado":         mercado,
        "gols_necessarios": gols_necessarios,
        "prob":            prob,
        "odd_justa":       oj,
        "odd_mercado":     odd_mercado,
        "lam_home":        lam_home,
        "lam_away":        lam_away,
    }


# ─── FILTRO FINAL ─────────────────────────────────────────────────────────────

def filtrar_oportunidades(jogos):
    oportunidades = []
    for jogo in jogos:
        resultado = calcular_score_ev(jogo)
        if resultado and resultado["score"] >= MIN_SCORE_EV:
            oportunidades.append({**jogo, **resultado})
    return sorted(oportunidades, key=lambda x: x["score"], reverse=True)