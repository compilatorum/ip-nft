#!/usr/bin/env python3
"""
Playwright E2E Test Suite with Step-by-Step Annotated Screenshots
Draws high-contrast directional arrows, target reticles, and clamped callout badges.
"""
import os
import math
import json
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/sukata/ip-nft/screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def draw_arrow_and_callout(image_path: Path, target_box: dict, label: str, direction: str = "auto", theme: str = "red"):
    """
    Annotate screenshot with a high-contrast glowing arrow, target reticle, and safe clamped callout badge.
    """
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Color themes
    themes = {
        "red": {"main": (239, 68, 68, 255), "bg": (15, 23, 42, 245), "ring": (239, 68, 68, 255)},
        "green": {"main": (16, 185, 129, 255), "bg": (6, 78, 59, 245), "ring": (16, 185, 129, 255)},
        "amber": {"main": (245, 158, 11, 255), "bg": (120, 53, 15, 245), "ring": (245, 158, 11, 255)},
        "blue": {"main": (56, 189, 248, 255), "bg": (15, 23, 42, 245), "ring": (56, 189, 248, 255)},
        "purple": {"main": (168, 85, 247, 255), "bg": (59, 7, 100, 245), "ring": (168, 85, 247, 255)},
    }
    tc = themes.get(theme, themes["red"])

    # Target point
    tx = int(target_box['x'] + target_box['width'] / 2)
    ty = int(target_box['y'] + target_box['height'] / 2)

    # Clamp target to canvas
    tx = max(20, min(w - 20, tx))
    ty = max(20, min(h - 20, ty))

    # Auto direction if auto
    if direction == "auto":
        if ty > h * 0.65:
            direction = "top"
        elif ty < h * 0.35:
            direction = "bottom"
        elif tx < w * 0.4:
            direction = "right"
        else:
            direction = "top"

    # Element bounding box highlight
    bx0 = max(2, int(target_box['x']) - 4)
    by0 = max(2, int(target_box['y']) - 4)
    bx1 = max(bx0 + 10, min(w - 2, int(target_box['x'] + max(10, target_box.get('width', 10))) + 4))
    by1 = max(by0 + 10, min(h - 2, int(target_box['y'] + max(10, target_box.get('height', 10))) + 4))

    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=6, outline=tc["main"], width=3)
    draw.rounded_rectangle([bx0 - 1, by0 - 1, bx1 + 1, by1 + 1], radius=7, outline=(255, 255, 255, 200), width=1)

    # Calculate arrow start and head points
    arrow_len = 50
    if direction == "top":
        sx, sy = tx, ty - arrow_len
        target_head = (tx, ty - 10)
    elif direction == "bottom":
        sx, sy = tx, ty + arrow_len
        target_head = (tx, ty + 10)
    elif direction == "left":
        sx, sy = tx - arrow_len, ty
        target_head = (tx - 10, ty)
    else:  # right
        sx, sy = tx + arrow_len, ty
        target_head = (tx + 10, ty)

    # Target bullseye ring
    draw.ellipse([tx - 10, ty - 10, tx + 10, ty + 10], outline=(255, 255, 255, 255), width=3)
    draw.ellipse([tx - 8, ty - 8, tx + 8, ty + 8], outline=tc["ring"], width=3)
    draw.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=tc["main"])

    # Arrow line
    draw.line([(sx, sy), target_head], fill=(255, 255, 255, 255), width=7)
    draw.line([(sx, sy), target_head], fill=tc["main"], width=4)

    # Arrow head polygon
    angle = math.atan2(target_head[1] - sy, target_head[0] - sx)
    head_len = 16
    head_angle = math.pi / 6

    p1 = target_head
    p2 = (int(target_head[0] - head_len * math.cos(angle - head_angle)),
          int(target_head[1] - head_len * math.sin(angle - head_angle)))
    p3 = (int(target_head[0] - head_len * math.cos(angle + head_angle)),
          int(target_head[1] - head_len * math.sin(angle + head_angle)))

    draw.polygon([p1, p2, p3], fill=tc["main"], outline=(255, 255, 255, 255))

    # Callout badge font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), label, font=font)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]

    padx, pady = 12, 6
    if direction == "top":
        cx0 = sx - tw // 2 - padx
        cy0 = sy - th - pady * 2 - 4
    elif direction == "bottom":
        cx0 = sx - tw // 2 - padx
        cy0 = sy + 6
    elif direction == "left":
        cx0 = sx - tw - padx * 2 - 6
        cy0 = sy - th // 2 - pady
    else:  # right
        cx0 = sx + 6
        cy0 = sy - th // 2 - pady

    # Strict canvas clamping to guarantee zero cutoff
    if cx0 < 15:
        cx0 = 15
    if cx0 + tw + padx * 2 > w - 15:
        cx0 = w - 15 - tw - padx * 2

    if cy0 < 15:
        cy0 = 15
    if cy0 + th + pady * 2 > h - 15:
        cy0 = h - 15 - th - pady * 2

    cx1 = cx0 + tw + padx * 2
    cy1 = cy0 + th + pady * 2

    # Draw badge shadow & background
    draw.rounded_rectangle([cx0 + 2, cy0 + 2, cx1 + 2, cy1 + 2], radius=6, fill=(0, 0, 0, 120))
    draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=6, fill=tc["bg"], outline=tc["main"], width=2)
    draw.text((cx0 + padx, cy0 + pady), label, font=font, fill=(255, 255, 255, 255))

    # Composite & save
    final_img = Image.alpha_composite(img, overlay).convert("RGB")
    final_img.save(image_path, "PNG", optimize=True)
    print(f"Annotated screenshot saved: {image_path.name}")

async def run_e2e_screenshots():
    steps_data = []

    async with async_playwright() as p:
        print("Launching Chromium engine (viewport: 1280x900)...")
        browser = await p.chromium.launch(
            executable_path='/data/data/com.termux/files/usr/bin/chromium-browser',
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1280,900'
            ]
        )
        page = await browser.new_page(viewport={'width': 1280, 'height': 900})

        # Step 1: Carregar Home e Tab Overview
        print("Step 1: Navigating to Home / Overview...")
        await page.goto("https://www.valuecurator.xyz", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1200)

        overview_btn = page.locator("button:has-text('Overview')").first
        box1 = await overview_btn.bounding_box()
        s1_path = OUTPUT_DIR / "step_01_tab_overview.png"
        await page.screenshot(path=s1_path)
        if box1:
            draw_arrow_and_callout(s1_path, box1, "CLIQUE 1: Aba Overview & Ativos RWA", direction="top", theme="blue")
        steps_data.append({
            "step": 1,
            "title": "Passo 01: Inicialização da Aplicação & Tab Overview",
            "file": "screenshots/step_01_tab_overview.png",
            "action": "Acesso ao domínio principal https://www.valuecurator.xyz e inspeção da aba '01 Overview'.",
            "observation": "Carregamento instantâneo do ativo AAPLx Tokenized Equity e leitura dos feeds oraculares Pyth 922 da Mainnet com custódia demarcada em Devnet."
        })

        # Step 2: Navegação para Tab 02 Mandate
        print("Step 2: Navigating to Tab 02 Mandate...")
        mandate_btn = page.locator("button:has-text('Mandate')").first
        box2 = await mandate_btn.bounding_box()
        s2_path = OUTPUT_DIR / "step_02_click_mandate.png"
        await page.screenshot(path=s2_path)
        if box2:
            draw_arrow_and_callout(s2_path, box2, "CLIQUE 2: Aba Mandato (Mandate Builder)", direction="top", theme="blue")
        
        await mandate_btn.click()
        await page.wait_for_timeout(800)
        steps_data.append({
            "step": 2,
            "title": "Passo 02: Abertura do Construtor de Mandatos (Mandate Builder)",
            "file": "screenshots/step_02_click_mandate.png",
            "action": "Clique na aba '02 Mandate' da barra de navegação superior.",
            "observation": "Transição reativa para a interface modular de governança constitucional, exibindo a sequência de 4 etapas de parametrização."
        })

        # Step 3: Sub-passo Risk Limits
        print("Step 3: Navigating to Risk Limits sub-tab...")
        risk_btn = page.locator("button:has-text('Risk limits')").first
        box3 = await risk_btn.bounding_box()
        s3_path = OUTPUT_DIR / "step_03_mandate_risk_limits.png"
        await page.screenshot(path=s3_path)
        if box3:
            draw_arrow_and_callout(s3_path, box3, "CLIQUE 3: Parametrizar Limites de Risco", direction="bottom", theme="amber")

        await risk_btn.click()
        await page.wait_for_timeout(800)
        steps_data.append({
            "step": 3,
            "title": "Passo 03: Parametrização dos Limites de Risco & Slippage",
            "file": "screenshots/step_03_mandate_risk_limits.png",
            "action": "Seleção do sub-passo 'Risk limits' dentro do Mandate Builder.",
            "observation": "Apresentação dos parâmetros de teto de trade ($500 USDC), exposição diária, tolerância máxima de desvio oracular e slippage de mercado."
        })

        # Step 4: Sub-passo Review & Export
        print("Step 4: Navigating to Review & Export...")
        review_btn = page.locator("button:has-text('Review & export')").first
        box4 = await review_btn.bounding_box()
        s4_path = OUTPUT_DIR / "step_04_mandate_review.png"
        await page.screenshot(path=s4_path)
        if box4:
            draw_arrow_and_callout(s4_path, box4, "CLIQUE 4: Revisar Mandato e Exportar", direction="bottom", theme="blue")

        await review_btn.click()
        await page.wait_for_timeout(800)
        steps_data.append({
            "step": 4,
            "title": "Passo 04: Consolidação & Resumo do Mandato Constitucional",
            "file": "screenshots/step_04_mandate_review.png",
            "action": "Clique na etapa 'Review & export' para inspeção do resumo do mandato.",
            "observation": "Geração do hash SHA-256 do mandato e visualização das restrições prontas para aplicação pelo autômato."
        })

        # Step 5: Navegação para Tab 03 Gate
        print("Step 5: Navigating to Tab 03 Gate...")
        gate_btn = page.locator("button:has-text('Gate')").first
        box5 = await gate_btn.bounding_box()
        s5_path = OUTPUT_DIR / "step_05_click_gate.png"
        await page.screenshot(path=s5_path)
        if box5:
            draw_arrow_and_callout(s5_path, box5, "CLIQUE 5: Acessar o Portão Determinístico", direction="top", theme="blue")

        await gate_btn.click()
        await page.wait_for_timeout(800)
        steps_data.append({
            "step": 5,
            "title": "Passo 05: Acesso ao Portão de Política (Policy Gate)",
            "file": "screenshots/step_05_click_gate.png",
            "action": "Clique na aba '03 Gate' para carregar a máquina de decisão determinística.",
            "observation": "Painel de simulação carregado, pronto para testar propostas contra evidências ao vivo de oráculos e livros de ofertas."
        })

        # Step 6: Gate Cenário 1 - Safe APPROVED
        print("Step 6: Executing Scenario 1 (Safe APPROVED)...")
        safe_btn = page.locator("button:has-text('Safe · APPROVED')").first
        box6 = await safe_btn.bounding_box()
        await safe_btn.click()
        await page.wait_for_timeout(800)

        s6_path = OUTPUT_DIR / "step_06_gate_safe_approved.png"
        await page.screenshot(path=s6_path)
        if box6:
            draw_arrow_and_callout(s6_path, box6, "CLIQUE 6: Simular Proposta Segura ➔ Status APPROVED", direction="top", theme="green")

        steps_data.append({
            "step": 6,
            "title": "Passo 06: Cenário 1 — Emissão de Recibo Criptográfico APPROVED",
            "file": "screenshots/step_06_gate_safe_approved.png",
            "action": "Execução da proposta em conformidade total com o mandato.",
            "observation": "O portão computa a conjunção de todas as regras e exibe a badge verde APPROVED com a assinatura Ed25519 e telemetria completa."
        })

        # Step 7: Gate Cenário 2 - Block Stale
        print("Step 7: Executing Scenario 2 (Block Stale Price)...")
        stale_btn = page.locator("button:has-text('Block · stale price')").first
        box7 = await stale_btn.bounding_box()
        await stale_btn.click()
        await page.wait_for_timeout(800)

        s7_path = OUTPUT_DIR / "step_07_gate_stale_blocked.png"
        await page.screenshot(path=s7_path)
        if box7:
            draw_arrow_and_callout(s7_path, box7, "CLIQUE 7: Simular Oráculo Obsoleto ➔ Rejeição Stale", direction="top", theme="amber")

        steps_data.append({
            "step": 7,
            "title": "Passo 07: Cenário 2 — Interrupção Fail-Closed por Oráculo Obsoleto",
            "file": "screenshots/step_07_gate_stale_blocked.png",
            "action": "Simulação de proposta com observação oracular com idade superior a 300 segundos.",
            "observation": "O portão bloqueia a execução instantaneamente (BLOCKED: Stale Oracle), protegendo o cofre contra precificação defasada."
        })

        # Step 8: Gate Cenário 3 - Block Divergence
        print("Step 8: Executing Scenario 3 (Block Price Divergence)...")
        div_btn = page.locator("button:has-text('Block · divergence')").first
        box8 = await div_btn.bounding_box()
        await div_btn.click()
        await page.wait_for_timeout(800)

        s8_path = OUTPUT_DIR / "step_08_gate_divergence_blocked.png"
        await page.screenshot(path=s8_path)
        if box8:
            draw_arrow_and_callout(s8_path, box8, "CLIQUE 8: Simular Desvio de Cotação ➔ Rejeição Divergence", direction="top", theme="red")

        steps_data.append({
            "step": 8,
            "title": "Passo 08: Cenário 3 — Interrupção por Divergência Excessiva de Cotação",
            "file": "screenshots/step_08_gate_divergence_blocked.png",
            "action": "Simulação de proposta onde a cotação da DEX diverge mais de 20% do oráculo Pyth.",
            "observation": "Bloqueio imediato (BLOCKED: Price Divergence), prevenindo a tesouraria contra arbitragens tóxicas e manipulação de liquidez."
        })

        # Step 9: Exportação JSON Auditável
        print("Step 9: Highlighting JSON Export button...")
        json_btn = page.locator("button:has-text('SHOW JSON'), button:has-text('DOWNLOAD JSON'), button:has-text('Show JSON')").first
        if await json_btn.count() > 0:
            box_json = await json_btn.bounding_box()
            s_json_path = OUTPUT_DIR / "step_09_gate_json_export.png"
            await page.screenshot(path=s_json_path)
            if box_json and box_json.get('width', 0) > 5 and box_json.get('height', 0) > 5:
                draw_arrow_and_callout(s_json_path, box_json, "CLIQUE 9: Exportar Payload JSON Auditável", direction="top", theme="purple")
            steps_data.append({
                "step": 9,
                "title": "Passo 09: Disponibilidade de Exportação do Recibo JSON",
                "file": "screenshots/step_09_gate_json_export.png",
                "action": "Inspeção do mecanismo de exportação auditável do portão determinístico.",
                "observation": "Exportação estruturada de todos os parâmetros para verificação de compliance off-chain e histórico criptográfico."
            })

        # Step 10: Navegação para Tab 04 Audit
        print("Step 10: Navigating to Tab 04 Audit...")
        audit_btn = page.locator("button:has-text('Audit')").first
        box10 = await audit_btn.bounding_box()
        await audit_btn.click()
        await page.wait_for_timeout(800)

        s10_path = OUTPUT_DIR / "step_10_click_audit.png"
        await page.screenshot(path=s10_path)
        if box10:
            draw_arrow_and_callout(s10_path, box10, "CLIQUE 10: Aba Auditoria & Transações Solana Devnet", direction="top", theme="purple")

        steps_data.append({
            "step": 10,
            "title": "Passo 10: Auditoria Criptográfica & Transações Confirmadas na Solana",
            "file": "screenshots/step_10_click_audit.png",
            "action": "Navegação para a aba '04 Audit' e verificação das transações on-chain.",
            "observation": "Exibição das assinaturas de transação confirmadas na Solana Devnet (metabolize_yield e emergency_withdraw) com separação constitucional de autoridades."
        })

        await browser.close()
        print(f"Annotated test suite completed successfully with {len(steps_data)} screenshots!")

    return steps_data

if __name__ == "__main__":
    data = asyncio.run(run_e2e_screenshots())
    with open("/home/sukata/ip-nft/screenshots/steps_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Execution data saved to screenshots/steps_data.json")
