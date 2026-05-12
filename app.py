from playwright.sync_api import sync_playwright
import pandas as pd
import time
import urllib.parse

BUSCA = input("Digite o nicho e cidade: ")

dados_empresas = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page()

    page.goto("https://www.google.com/maps/search/" + BUSCA.replace(" ", "+"))

    time.sleep(10)

    for _ in range(5):
        page.mouse.wheel(0, 5000)
        time.sleep(2)

    empresas = page.locator('div[role="article"]')
    total = empresas.count()

    print(f"\nEmpresas encontradas: {total}\n")

    for i in range(min(total, 20)):
        try:
            empresas.nth(i).click()
            time.sleep(5)

            nome = page.locator('h1.DUwDvf').inner_text()

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
                nota = page.locator('div.F7nice span').first.inner_text()
            except:
                pass

            avaliacoes = "0 avaliações"

            try:
                avaliacoes = page.locator('div.F7nice span').nth(1).inner_text()
            except:
                pass

            mensagem = f"""
Olá, {nome}! Tudo bem? 🙂

Encontrei a empresa de vocês no Google e percebi que ainda não possuem uma landing page profissional.

Hoje em dia, uma página com botão direto para WhatsApp, Instagram e catálogo ajuda bastante empresas locais a conseguirem mais clientes.

Eu trabalho criando landing pages modernas e rápidas para negócios da região.

Se quiser, posso te mostrar um exemplo gratuitamente.
"""

            telefone_limpo = ''.join(filter(str.isdigit, telefone))

            texto_formatado = urllib.parse.quote(mensagem)

            link_whatsapp = f"https://wa.me/55{telefone_limpo}?text={texto_formatado}"

            print(f"\nEmpresa: {nome}")
            print("Telefone:", telefone)
            print("Endereço:", endereco)
            print("Nota:", nota)
            print("Avaliações:", avaliacoes)
            print("Site:", site)
            print("WhatsApp:", link_whatsapp)

            if site == "Não possui site":
                dados_empresas.append({
                    "Empresa": nome,
                    "Telefone": telefone,
                    "Endereco": endereco,
                    "Nota": nota,
                    "Avaliacoes": avaliacoes,
                    "Site": site,
                    "Mensagem": mensagem,
                    "WhatsApp": link_whatsapp
                })

                print("Lead salvo!")

            else:
                print("Ignorado: já possui site.")

            print("-" * 50)

            page.go_back()
            time.sleep(5)

        except Exception as erro:
            print("Erro:", erro)

    browser.close()

df = pd.DataFrame(dados_empresas)

df.to_excel("leads.xlsx", index=False)

print("\nExcel criado com sucesso com links automáticos do WhatsApp!")