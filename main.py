import time
from datetime import datetime
from fetcher import get_jogos_ao_vivo
from fetcher_bsd import get_jogos_ao_vivo_bsd
from analyzer import filtrar_oportunidades
from telegram_bot import enviar_alerta, enviar_teste

INTERVALO = 60


def exibir_alerta(op):
    print("\n" + "="*55)
    print(f"🚨 OPORTUNIDADE EV+ | Score: {op['score']}/100")
    print(f"   {op['home']} x {op['away']}")
    print(f"   {op['liga']} | {op['minuto']}' | {op['placar_home']}x{op['placar_away']}")
    print(f"   Mercado: {op['mercado']}")
    print(f"   xG: {op.get('xg', 0)} | Chutes: {op['chutes_totais']} | Escanteios: {op.get('escanteios', 0)}")
    print(f"   Big chances: {op.get('big_chances', 0)} | Fonte: {op.get('fonte', '?')}")
    print(f"   Motivos:")
    for m in op["motivos"]:
        print(f"     ✅ {m}")
    print("="*55)


def merge_jogos(jogos_bsd, jogos_api):
    """
    Combina jogos das duas fontes sem duplicar.
    
    FIX: Usa home+away+minuto (range) para deduplicação mais robusta
    """
    ids_bsd = set()
    for j in jogos_bsd:
        # Usa minuto com range para reduzir falsos positivos
        chave = (j["home"], j["away"], j["minuto"] // 3)
        ids_bsd.add(chave)
    
    extras = []
    for j in jogos_api:
        chave = (j["home"], j["away"], j["minuto"] // 3)
        if chave not in ids_bsd:
            extras.append(j)
    
    return jogos_bsd + extras


def gerar_chave_alerta(op):
    """
    Gera chave única para deduplica oportunidade.
    
    FIX: Menos sensível a variações de minuto
    """
    return f"{op['home']}_{op['away']}_{op['minuto'] // 10}_{op['mercado']}"


def main():
    print("\n🤖 Bot EV+ Gols iniciado!")
    print(f"   Janela de entrada: 45' a 68'")
    print(f"   Score mínimo EV+: 70/100")
    print(f"   Verificando a cada {INTERVALO}s...")
    print(f"   Horario: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    enviar_teste()
    alertas_enviados = set()
    ultimas_oportunidades = {}  # histórico de últimas 5 min

    while True:
        agora = datetime.now().strftime("%H:%M:%S")
        print(f"[{agora}] Buscando jogos ao vivo...")

        try:
            jogos_bsd = get_jogos_ao_vivo_bsd()
            jogos_api = get_jogos_ao_vivo()
            jogos = merge_jogos(jogos_bsd, jogos_api)

            if not jogos:
                print(f"[{agora}] Nenhum jogo ao vivo agora.")
            else:
                print(f"[{agora}] {len(jogos)} jogo(s) | BSD: {len(jogos_bsd)} | API: {len(jogos_api)}")
                oportunidades = filtrar_oportunidades(jogos)

                if not oportunidades:
                    print(f"[{agora}] Nenhuma oportunidade EV+ no momento.")
                else:
                    print(f"[{agora}] {len(oportunidades)} oportunidade(s) encontrada(s)!")
                    for op in oportunidades:
                        chave = gerar_chave_alerta(op)
                        
                        if chave not in alertas_enviados:
                            exibir_alerta(op)
                            try:
                                enviar_alerta(op)
                                alertas_enviados.add(chave)
                                ultimas_oportunidades[chave] = datetime.now()
                            except Exception as e:
                                print(f"   [ERRO] Falha ao enviar alerta: {e}")
                        else:
                            # Log mais sucinto para já alertados
                            tempo_desde = (datetime.now() - ultimas_oportunidades.get(chave, datetime.now())).total_seconds()
                            print(f"   [skip] {op['home']} x {op['away']} — alertado há {int(tempo_desde)}s")

        except Exception as e:
            print(f"[{agora}] ERRO na busca: {e}")

        print(f"\n   Proxima verificacao em {INTERVALO}s...\n")
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()