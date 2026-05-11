import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_mensagem(texto):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": texto,
            "parse_mode": "HTML"
        }
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except Exception as e:
        print(f"[ERRO Telegram] {e}")
        return False


def formatar_alerta(op):
    prob         = op.get("prob", 0)
    oj           = op.get("odd_justa", 0)
    odd_mercado  = op.get("odd_mercado", 0)
    gols_nec     = op.get("gols_necessarios", 1)
    placar       = f"{op['placar_home']} x {op['placar_away']}"

    # Linha de ação — o que fazer
    if odd_mercado > 0:
        ev_pct = round((odd_mercado * prob - 1) * 100, 1)
        acao = (
            f"✅ <b>ENTRAR</b> — odd {odd_mercado} "
            f"(justa {oj} | EV +{ev_pct}%)"
        )
    else:
        acao = f"🔍 <b>Verificar</b> — entre se odd ≥ <b>{oj}</b>"

    # Contexto rápido do jogo
    diff = op['placar_home'] - op['placar_away']
    if diff > 0:
        situacao = f"{op['away']} perdendo, pressionando"
    elif diff < 0:
        situacao = f"{op['home']} perdendo, pressionando"
    else:
        situacao = "Empate, ambos atacando"

    return (
        f"🚨 <b>APOSTA EV+</b> — Score {op['score']}/100\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚽ <b>{op['home']} x {op['away']}</b>\n"
        f"🏆 {op['liga']}  |  {op['minuto']}'  |  {placar}\n"
        f"📌 {situacao}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Mercado: <b>{op['mercado']}</b>\n"
        f"📊 Prob: <b>{round(prob*100,1)}%</b>  |  "
        f"Odd justa: <b>{oj}</b>\n"
        f"{acao}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<i>Chutes: {op.get('chutes_totais',0)} | "
        f"Escanteios: {op.get('escanteios',0)} | "
        f"xG: {op.get('xg',0)}</i>"
    )


def enviar_alerta(op):
    mensagem = formatar_alerta(op)
    sucesso = enviar_mensagem(mensagem)
    if sucesso:
        print(f"  [Telegram] ✅ Alerta enviado: {op['home']} x {op['away']}")
    else:
        print(f"  [Telegram] ❌ Falha ao enviar alerta.")


def enviar_teste():
    return enviar_mensagem(
        "🤖 <b>Bot EV+ Gols iniciado!</b>\n\n"
        "Monitorando jogos ao vivo — BSD + API-Football.\n"
        "Aviso quando detectar oportunidade EV+! ⚽"
    )