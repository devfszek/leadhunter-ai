from playwright.sync_api import sync_playwright
import pandas as pd
import time
import urllib.parse


def buscar_leads(busca):
    dados_empresas = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page()

        page.goto(
            "https://www.google.com/maps/search/" + busca.replace(" ", "+"),
            wait_until="domcontentloaded",
            timeout=60000
        )

        time.sleep(10)

        for _ in range(5):
            page.mouse.wheel(0, 5000)
            time.sleep(2)

        empresas = page.locator('div[role="article"]')
        total = empresas.count()

        for i in range(min(total, 20)):
            try:
                empresas.nth(i).click()
                time.sleep(5)

                nome = page.locator('h1.DUwDvf').inner_text(timeout=10000)

                telefone = "Não encontrado"
                tel = page.locator('button[data-item-id*="phone"]')
                if tel.count() > 0:
                    telefone = tel.first.inner_text()

                site = "Não possui site"
                site_btn = page.locator('a[data-item-id="authority"]')
                if site_btn.count() > 0:
                    site = site_btn.first.get_attribute("href")

                endereco = "Não encontrado"
                end = page.locator('button[data-item-id="address"]')
                if end.count() > 0:
                    endereco = end.first.inner_text()

                nota = "Sem nota"
                try:
                    nota = page.locator('div.F7nice span').first.inner_text(timeout=5000)
                except:
                    pass

                avaliacoes = "0 avaliações"
                try:
                    avaliacoes = page.locator('div.F7nice span').nth(1).inner_text(timeout=5000)
                except:
                    pass

                score = 0

                if site == "Não possui site":
                    score += 5

                try:
                    nota_num = float(nota.replace(",", "."))
                    if nota_num >= 4.5:
                        score += 3
                except:
                    pass

                try:
                    numero_avaliacoes = ''.join(filter(str.isdigit, avaliacoes))
                    if numero_avaliacoes and int(numero_avaliacoes) >= 100:
                        score += 2
                except:
                    pass

                nivel = "❌ Lead Fraco"

                if score >= 8:
                    nivel = "🔥 Lead Quente"
                elif score >= 5:
                    nivel = "🟡 Lead Médio"

                mensagem = f"""
Olá, {nome}! Tudo bem? 🙂

Encontrei a empresa de vocês no Google e percebi que ainda não possuem uma landing page profissional.

Hoje em dia, uma página com botão direto para WhatsApp, Instagram e catálogo ajuda bastante empresas locais a conseguirem mais clientes.

Eu trabalho criando landing pages modernas e rápidas para negócios da região.

Se quiser, posso te mostrar um exemplo gratuitamente.
"""

                telefone_limpo = ''.join(filter(str.isdigit, telefone))
                texto_formatado = urllib.parse.quote(mensagem)

                if telefone_limpo.startswith("55"):
                    link_whatsapp = f"https://wa.me/{telefone_limpo}?text={texto_formatado}"
                else:
                    link_whatsapp = f"https://wa.me/55{telefone_limpo}?text={texto_formatado}"

                if site == "Não possui site":
                    dados_empresas.append({
                        "Empresa": nome,
                        "Telefone": telefone,
                        "Endereco": endereco,
                        "Nota": nota,
                        "Avaliacoes": avaliacoes,
                        "Score": score,
                        "Nivel": nivel,
                        "Site": site,
                        "Mensagem": mensagem,
                        "WhatsApp": link_whatsapp
                    })

                page.go_back()
                time.sleep(5)

            except Exception as erro:
                print("Erro:", erro)

        browser.close()

    df = pd.DataFrame(dados_empresas)
    df.to_excel("leads.xlsx", index=False)

    return dados_empresas