import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_mensagem(texto):
    """Envia mensagem para o Telegram."""
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
    """Formata a mensagem de alerta para o Telegram."""
    motivos = "\n".join([f"  ✅ {m}" for m in op["motivos"]])
    prob            = op.get("prob", 0)
    oj              = op.get("odd_justa", 0)
    odd_mercado     = op.get("odd_mercado", 0)
    gols_necessarios = op.get("gols_necessarios", 1)

    if odd_mercado > 0:
        odd_linha = (
            f"📐 Precisa de <b>{gols_necessarios} gol(s) adicional(is)</b>\n"
            f"📊 Probabilidade: <b>{round(prob*100,1)}%</b>\n"
            f"⚖️ Odd justa: <b>{oj}</b>\n"
            f"💰 Odd mercado: <b>{odd_mercado}</b> ✅ ENTRAR\n"
        )
    else:
        odd_linha = (
            f"📐 Precisa de <b>{gols_necessarios} gol(s) adicional(is)</b>\n"
            f"📊 Probabilidade: <b>{round(prob*100,1)}%</b>\n"
            f"⚖️ Odd justa: <b>{oj}</b>\n"
            f"💰 Entre se odd ≥ <b>{oj}</b> na casa\n"
        )

    return (
        f"🚨 <b>OPORTUNIDADE EV+ DETECTADA</b>\n\n"
        f"⚽ <b>{op['home']} x {op['away']}</b>\n"
        f"🏆 {op['liga']}\n"
        f"⏱ Minuto: {op['minuto']}'\n"
        f"📊 Placar: {op['placar_home']} x {op['placar_away']}\n"
        f"🎯 Mercado: <b>{op['mercado']}</b>\n"
        f"{odd_linha}"
        f"📈 Score EV: <b>{op['score']}/100</b>\n\n"
        f"<b>Motivos:</b>\n{motivos}"
    )


def enviar_alerta(op):
    """Envia alerta formatado de uma oportunidade."""
    mensagem = formatar_alerta(op)
    sucesso = enviar_mensagem(mensagem)
    if sucesso:
        print(f"  [Telegram] ✅ Alerta enviado: {op['home']} x {op['away']}")
    else:
        print(f"  [Telegram] ❌ Falha ao enviar alerta.")


def enviar_teste():
    """Envia mensagem de teste para confirmar conexão."""
    return enviar_mensagem(
        "🤖 <b>Bot EV+ Gols iniciado!</b>\n\n"
        "Monitorando jogos ao vivo com dados BSD + API-Football.\n"
        "Quando detectar uma oportunidade EV+, aviso aqui! ⚽"
    )