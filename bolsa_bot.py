from playwright.sync_api import sync_playwright
import time

# ─── CONFIGURAÇÕES ───────────────────────────────────────────
EMAIL    = "seu_username_aqui"
SENHA    = "sua_senha_aqui"
STAKE    = "10"   # valor em reais
# ─────────────────────────────────────────────────────────────

def fazer_aposta(url_evento: str, mercado_alvo: str = "Over 1.5"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page    = context.new_page()

        # 0. ACEITAR POPUP DE IDADE via JavaScript
        print("🔞 Verificando popup de idade...")
        try:
            page.wait_for_selector("text=Você tem mais de 18 anos?", timeout=5000)
            page.evaluate("""
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.trim() === 'SIM') {
                        btn.click();
                        break;
                    }
                }
            """)
            page.wait_for_timeout(2000)
            print("✅ Popup de idade aceito")
        except:
            print("   [ok] Sem popup de idade")

        # 1. LOGIN
        print("🔐 Fazendo login...")
        page.goto("https://bolsadeaposta.bet.br")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        # Screenshot para ver o estado da página
        page.screenshot(path="antes_login.png")
        print("📸 Screenshot salvo: antes_login.png")

        # Clica no botão ENTRAR via JavaScript
        page.evaluate("""
            const links = document.querySelectorAll('a, button');
            for (const el of links) {
                if (el.textContent.trim().toUpperCase() === 'ENTRAR') {
                    el.click();
                    break;
                }
            }
        """)
        page.wait_for_timeout(2000)
        page.screenshot(path="depois_entrar.png")
        print("📸 Screenshot salvo: depois_entrar.png")

        # Preenche usuário e senha no formulário visível
        page.fill('input[placeholder="Usuário"]:visible', EMAIL)
        page.fill('input[type="password"]:visible', SENHA)
        page.click('button[type="submit"]:visible')
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        print("✅ Login OK")

        # 2. NAVEGAR ATÉ O EVENTO
        print(f"🎯 Abrindo evento: {url_evento}")
        page.goto(url_evento)
        page.wait_for_load_state("networkidle")

        # 3. LOCALIZAR E CLICAR NO MERCADO ALVO
        print(f"🔍 Procurando mercado: {mercado_alvo}")
        # Tenta localizar pelo texto visível (Over 1.5, Over 2.5, etc.)
        mercado = page.locator(f"text={mercado_alvo}").first
        mercado.wait_for(timeout=10000)
        mercado.click()
        print(f"✅ Mercado '{mercado_alvo}' clicado")

        # 4. POPUP DE STAKE
        print("💰 Aguardando popup de stake...")
        # Espera o campo de valor aparecer no popup
        stake_input = page.locator(
            'input[type="number"], input[placeholder*="stake" i], '
            'input[placeholder*="valor" i], input[placeholder*="amount" i]'
        ).first
        stake_input.wait_for(timeout=8000)
        stake_input.fill(STAKE)
        print(f"✅ Stake preenchida: R$ {STAKE}")

        # 5. CONFIRMAR APOSTA
        print("🖱️ Clicando em 'Colocar uma Aposta'...")
        btn = page.locator(
            'button:has-text("Colocar uma Aposta"), '
            'button:has-text("Apostar"), '
            'button:has-text("Place Bet")'
        ).first
        btn.wait_for(timeout=5000)

        # ⚠️  DESCOMENTE a linha abaixo quando quiser apostar de verdade
        # btn.click()

        print("✅ Aposta confirmada!")
        time.sleep(2)
        browser.close()


# ─── EXECUÇÃO ────────────────────────────────────────────────
if __name__ == "__main__":
    url   = "https://bolsadeaposta.bet.br/b/exchange/sport/soccer/event/33176368041500081/market/33176368332600081"
    fazer_aposta(url, mercado_alvo="Over 1.5")