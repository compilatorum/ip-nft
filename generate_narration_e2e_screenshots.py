#!/usr/bin/env python3
"""
Generate 14 Annotated E2E Screenshots for ElevenLabs Voiceover Narration
Aligns every narration item from 0:00 to 2:50 with annotated screenshots and callout badges.
"""
import os
import math
import json
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/sukata/ip-nft/screenshots_narration")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def draw_arrow_and_callout(image_path: Path, target_box: dict, label: str, direction: str = "auto", theme: str = "red"):
    """
    Annotate screenshot with a high-contrast glowing arrow, target reticle, and safe clamped callout badge.
    """
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    themes = {
        "red": {"main": (239, 68, 68, 255), "bg": (20, 10, 15, 245), "ring": (239, 68, 68, 255)},
        "green": {"main": (16, 185, 129, 255), "bg": (5, 30, 20, 245), "ring": (16, 185, 129, 255)},
        "amber": {"main": (245, 158, 11, 255), "bg": (35, 20, 5, 245), "ring": (245, 158, 11, 255)},
        "blue": {"main": (56, 189, 248, 255), "bg": (10, 20, 40, 245), "ring": (56, 189, 248, 255)},
        "purple": {"main": (168, 85, 247, 255), "bg": (25, 10, 45, 245), "ring": (168, 85, 247, 255)},
    }
    tc = themes.get(theme, themes["red"])

    # Center target point
    tx = int(target_box['x'] + target_box['width'] / 2)
    ty = int(target_box['y'] + target_box['height'] / 2)
    tx = max(25, min(w - 25, tx))
    ty = max(25, min(h - 25, ty))

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

    arrow_len = 55
    if direction == "top":
        sx, sy = tx, ty - arrow_len
        target_head = (tx, ty - 12)
    elif direction == "bottom":
        sx, sy = tx, ty + arrow_len
        target_head = (tx, ty + 12)
    elif direction == "left":
        sx, sy = tx - arrow_len, ty
        target_head = (tx - 12, ty)
    else:  # right
        sx, sy = tx + arrow_len, ty
        target_head = (tx + 12, ty)

    # Bullseye
    draw.ellipse([tx - 12, ty - 12, tx + 12, ty + 12], outline=(255, 255, 255, 255), width=3)
    draw.ellipse([tx - 9, ty - 9, tx + 9, ty + 9], outline=tc["ring"], width=3)
    draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=tc["main"])

    # Arrow shaft
    draw.line([(sx, sy), target_head], fill=(255, 255, 255, 255), width=7)
    draw.line([(sx, sy), target_head], fill=tc["main"], width=4)

    # Arrow tip
    angle = math.atan2(target_head[1] - sy, target_head[0] - sx)
    head_len = 18
    head_angle = math.pi / 6
    p1 = target_head
    p2 = (int(target_head[0] - head_len * math.cos(angle - head_angle)),
          int(target_head[1] - head_len * math.sin(angle - head_angle)))
    p3 = (int(target_head[0] - head_len * math.cos(angle + head_angle)),
          int(target_head[1] - head_len * math.sin(angle + head_angle)))
    draw.polygon([p1, p2, p3], fill=tc["main"], outline=(255, 255, 255, 255))

    # Badge font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except Exception:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), label, font=font)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]

    padx, pady = 14, 8
    if direction == "top":
        cx0 = sx - tw // 2 - padx
        cy0 = sy - th - pady * 2 - 6
    elif direction == "bottom":
        cx0 = sx - tw // 2 - padx
        cy0 = sy + 8
    elif direction == "left":
        cx0 = sx - tw - padx * 2 - 8
        cy0 = sy - th // 2 - pady
    else:  # right
        cx0 = sx + 8
        cy0 = sy - th // 2 - pady

    # Clamp
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

    draw.rounded_rectangle([cx0 + 2, cy0 + 2, cx1 + 2, cy1 + 2], radius=6, fill=(0, 0, 0, 140))
    draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=6, fill=tc["bg"], outline=tc["main"], width=2)
    draw.text((cx0 + padx, cy0 + pady), label, font=font, fill=(255, 255, 255, 255))

    final_img = Image.alpha_composite(img, overlay).convert("RGB")
    final_img.save(image_path, "PNG", optimize=True)
    print(f"Annotated screenshot saved: {image_path.name}")

async def run_narration_e2e():
    steps = []

    async with async_playwright() as p:
        print("Launching Chromium engine (viewport: 1280x880)...")
        browser = await p.chromium.launch(
            executable_path='/data/data/com.termux/files/usr/bin/chromium-browser',
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1280,880'
            ]
        )
        page = await browser.new_page(viewport={'width': 1280, 'height': 880})

        # =========================================================================
        # ITEM 1: 0:00 - 0:15
        # Welcome Colosseum judges... who controls the capital?
        # =========================================================================
        print("Capturing Item 1 (0:00 - 0:15)...")
        await page.goto("https://www.valuecurator.xyz", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1000)

        h1 = page.locator("h1:has-text('ValueCurator')").first
        box1 = await h1.bounding_box()
        s1 = OUTPUT_DIR / "narration_step_01.png"
        await page.screenshot(path=s1)
        if box1:
            draw_arrow_and_callout(s1, box1, "ITEM 1 [0:00-0:15] · Tese Soberana: Quem Controla o Capital?", direction="bottom", theme="blue")
        steps.append({
            "item": 1,
            "timestamp": "0:00 - 0:15",
            "title": "Abertura Filosófica & Soberania de Capital",
            "voiceover_en": "Welcome, Colosseum judges. Autonomous AI agents are beginning to trade on-chain markets. But greater intelligence doesn't answer the core question: who controls the capital?",
            "voiceover_pt": "Bem-vindos, jurados da Colosseum. Agentes autônomos de IA estão começando a negociar em mercados on-chain. Mas maior inteligência não responde à pergunta central: quem controla o capital?",
            "file": "screenshots_narration/narration_step_01.png",
            "ui_action": "Carregamento da página inicial e foco no manifesto central do protocolo.",
            "target_element": "Cabeçalho Soberano: ValueCurator Control Plane"
        })

        # =========================================================================
        # ITEM 2: 0:15 - 0:25
        # Private keys to agents flaw... autonomy != sovereignty
        # =========================================================================
        print("Capturing Item 2 (0:15 - 0:25)...")
        prot_card = page.locator("text=The protection").first
        box2 = await prot_card.bounding_box()
        s2 = OUTPUT_DIR / "narration_step_02.png"
        await page.screenshot(path=s2)
        if box2:
            draw_arrow_and_callout(s2, box2, "ITEM 2 [0:15-0:25] · Princípio: Autonomia Operacional ≠ Soberania", direction="top", theme="green")
        steps.append({
            "item": 2,
            "timestamp": "0:15 - 0:25",
            "title": "Princípio da Separação Constitucional",
            "voiceover_en": "Giving raw private keys to an autonomous agent creates an existential security flaw. We built ValueCurator around a fundamental principle: operational autonomy must not mean sovereignty over capital.",
            "voiceover_pt": "Entregar chaves privadas a um agente autônomo cria uma falha de segurança existencial. Construímos o ValueCurator em torno de um princípio fundamental: autonomia operacional não deve significar soberania sobre o capital.",
            "file": "screenshots_narration/narration_step_02.png",
            "ui_action": "Destaque no pilar 'The protection' evidenciando a separação entre chave do dono e chave do operador.",
            "target_element": "Card: The Protection · Limites Invioláveis de Custódia"
        })

        # =========================================================================
        # ITEM 3: 0:25 - 0:35
        # Overview tab, AAPLx tokenized equity, Pyth Feed 922 Mainnet
        # =========================================================================
        print("Capturing Item 3 (0:25 - 0:35)...")
        # Scroll slightly to show AAPLx card
        await page.evaluate("window.scrollBy(0, 220)")
        await page.wait_for_timeout(500)
        aaplx_card = page.locator("text=AAPLx").first
        box3 = await aaplx_card.bounding_box()
        s3 = OUTPUT_DIR / "narration_step_03.png"
        await page.screenshot(path=s3)
        if box3:
            draw_arrow_and_callout(s3, box3, "ITEM 3 [0:25-0:35] · RWA AAPLx & Oráculo Pyth Feed 922", direction="top", theme="amber")
        steps.append({
            "item": 3,
            "timestamp": "0:25 - 0:35",
            "title": "Ativos RWA & Telemetria Pyth Mainnet",
            "voiceover_en": "Here on our Overview tab, we monitor real-world tokenized equity like AAPLx. Our system reads live Pyth Feed 922 market evidence directly from Solana Mainnet, while all custody vaults remain strictly segregated on Solana Devnet.",
            "voiceover_pt": "Aqui na aba Overview, monitoramos ações tokenizadas do mundo real como AAPLx. Nosso sistema lê evidências ao vivo do Pyth Feed 922 da Mainnet, enquanto os cofres permanecem segregados na Devnet.",
            "file": "screenshots_narration/narration_step_03.png",
            "ui_action": "Inspeção do card do ativo sintético AAPLx e telemetria do oráculo Pyth.",
            "target_element": "Painel de RWA: AAPLx com Leitura do Oráculo Pyth 922"
        })

        # =========================================================================
        # ITEM 4: 0:35 - 0:50
        # Step into Mandate Builder... immutable mathematical invariants
        # =========================================================================
        print("Capturing Item 4 (0:35 - 0:50)...")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(400)
        mandate_tab = page.locator("button:has-text('02Mandate')").first
        box4 = await mandate_tab.bounding_box()
        s4 = OUTPUT_DIR / "narration_step_04.png"
        await page.screenshot(path=s4)
        if box4:
            draw_arrow_and_callout(s4, box4, "ITEM 4 [0:35-0:50] · CLIQUE: Construtor de Mandatos Constitucionais", direction="bottom", theme="blue")

        await mandate_tab.click()
        await page.wait_for_timeout(800)
        steps.append({
            "item": 4,
            "timestamp": "0:35 - 0:50",
            "title": "Abertura do Construtor de Mandatos (Mandate Builder)",
            "voiceover_en": "Now, let's step into the Mandate Builder. Instead of soft natural-language prompts that agents can hallucinate or bypass, we convert investor policies into immutable mathematical invariants.",
            "voiceover_pt": "Agora, entramos no Construtor de Mandatos. Em vez de prompts frágeis em linguagem natural que agentes podem burlar ou alucinar, convertemos políticas de investimento em invariantes matemáticos imutáveis.",
            "file": "screenshots_narration/narration_step_04.png",
            "ui_action": "Transição interativa para a aba '02 Mandate'.",
            "target_element": "Navegação: Aba 02 Mandate Builder"
        })

        # =========================================================================
        # ITEM 5: 0:50 - 1:05
        # Under Risk Limits, 500 USDC trade cap, volume ceilings, staleness
        # =========================================================================
        print("Capturing Item 5 (0:50 - 1:05)...")
        risk_btn = page.locator("button:has-text('Risk limits')").first
        await risk_btn.click()
        await page.wait_for_timeout(800)
        box5 = await risk_btn.bounding_box()
        s5 = OUTPUT_DIR / "narration_step_05.png"
        await page.screenshot(path=s5)
        if box5:
            draw_arrow_and_callout(s5, box5, "ITEM 5 [0:50-1:05] · Limites de Risco: Teto de $500 USDC & Slippage", direction="bottom", theme="amber")
        steps.append({
            "item": 5,
            "timestamp": "0:50 - 1:05",
            "title": "Parametrização dos Limites de Risco e Slippage",
            "voiceover_en": "Under Risk Limits, the treasury owner configures strict boundaries: a 500 USDC trade cap, cumulative daily volume ceilings, and exact thresholds for price staleness and slippage.",
            "voiceover_pt": "Em Risk Limits, o dono da tesouraria define fronteiras estritas: teto de $500 USDC por trade, limites cumulativos diários e parâmetros exatos para desvio e idade do oráculo.",
            "file": "screenshots_narration/narration_step_05.png",
            "ui_action": "Seleção da sub-etapa 'Risk limits' e ajuste dos tetos financeiros de execução.",
            "target_element": "Sub-aba: Risk Limits ($500 USDC Trade Cap)"
        })

        # =========================================================================
        # ITEM 6: 1:05 - 1:15
        # Reviewing mandate commits deterministic SHA-256 hash. Boundary locked.
        # =========================================================================
        print("Capturing Item 6 (1:05 - 1:15)...")
        review_btn = page.locator("button:has-text('Review & export')").first
        await review_btn.click()
        await page.wait_for_timeout(800)
        box6 = await review_btn.bounding_box()
        s6 = OUTPUT_DIR / "narration_step_06.png"
        await page.screenshot(path=s6)
        if box6:
            draw_arrow_and_callout(s6, box6, "ITEM 6 [1:05-1:15] · Mandato Travado: Hash SHA-256 Imutável", direction="bottom", theme="purple")
        steps.append({
            "item": 6,
            "timestamp": "1:05 - 1:15",
            "title": "Consolidação & Hash Criptográfico SHA-256",
            "voiceover_en": "Reviewing the mandate commits a deterministic SHA-256 hash. The boundary is locked.",
            "voiceover_pt": "Revisar o mandato comita um hash SHA-256 determinístico. A fronteira de risco está travada.",
            "file": "screenshots_narration/narration_step_06.png",
            "ui_action": "Clique na sub-etapa 'Review & export' e geração do hash imutável do mandato.",
            "target_element": "Sub-aba: Review & Export (SHA-256 Commitment)"
        })

        # =========================================================================
        # ITEM 7: 1:15 - 1:25
        # The heart of protocol: Deterministic Policy Gate
        # =========================================================================
        print("Capturing Item 7 (1:15 - 1:25)...")
        gate_tab = page.locator("button:has-text('03Gate')").first
        box7 = await gate_tab.bounding_box()
        s7 = OUTPUT_DIR / "narration_step_07.png"
        await page.screenshot(path=s7)
        if box7:
            draw_arrow_and_callout(s7, box7, "ITEM 7 [1:15-1:25] · CLIQUE: Portão Determinístico de Políticas", direction="bottom", theme="blue")

        await gate_tab.click()
        await page.wait_for_timeout(800)
        steps.append({
            "item": 7,
            "timestamp": "1:15 - 1:25",
            "title": "O Crivo do Portão Determinístico (Policy Gate)",
            "voiceover_en": "Now, the heart of our protocol: the Deterministic Policy Gate. Before any transaction can touch the blockchain, the gate evaluates the proposed action against real-time market data.",
            "voiceover_pt": "Agora, o coração do nosso protocolo: o Portão Determinístico de Políticas. Antes de qualquer transação tocar a blockchain, o portão avalia a ação proposta contra dados em tempo real de mercado.",
            "file": "screenshots_narration/narration_step_07.png",
            "ui_action": "Transição para a aba '03 Gate' onde as propostas são submetidas ao crivo matemático.",
            "target_element": "Navegação: Aba 03 Gate (Policy Verification Engine)"
        })

        # =========================================================================
        # ITEM 8: 1:25 - 1:40
        # Watch Scenario 1: safe proposal, APPROVED, Ed25519 receipt
        # =========================================================================
        print("Capturing Item 8 (1:25 - 1:40)...")
        safe_btn = page.locator("button:has-text('Safe · APPROVED')").first
        box8 = await safe_btn.bounding_box()
        await safe_btn.click()
        await page.wait_for_timeout(800)
        s8 = OUTPUT_DIR / "narration_step_08.png"
        await page.screenshot(path=s8)
        if box8:
            draw_arrow_and_callout(s8, box8, "ITEM 8 [1:25-1:40] · Cenário 1: Conforme ➔ APPROVED (Recibo Ed25519)", direction="top", theme="green")
        steps.append({
            "item": 8,
            "timestamp": "1:25 - 1:40",
            "title": "Cenário 1 — Emissão do Recibo Criptográfico APPROVED",
            "voiceover_en": "Watch Scenario 1: a safe proposal within all mandate limits. All rules pass. The gate displays APPROVED, emitting an Ed25519 cryptographic authorization receipt. The agent receives the permit, but never touches the private key.",
            "voiceover_pt": "Observe o Cenário 1: uma proposta segura dentro de todos os limites. Todas as regras passam. O portão exibe APPROVED, emitindo um recibo Ed25519. O agente recebe a autorização, mas jamais toca na chave privada.",
            "file": "screenshots_narration/narration_step_08.png",
            "ui_action": "Clique no botão 'Safe · APPROVED' e verificação do recibo de autorização criptográfica.",
            "target_element": "Botão de Simulação: Safe · APPROVED & Recibo Ed25519"
        })

        # =========================================================================
        # ITEM 9: 1:40 - 1:52
        # Scenario 2: stale oracle > 300s, BLOCKED Stale Oracle, Fail-Closed
        # =========================================================================
        print("Capturing Item 9 (1:40 - 1:52)...")
        stale_btn = page.locator("button:has-text('Block · stale price')").first
        box9 = await stale_btn.bounding_box()
        await stale_btn.click()
        await page.wait_for_timeout(800)
        s9 = OUTPUT_DIR / "narration_step_09.png"
        await page.screenshot(path=s9)
        if box9:
            draw_arrow_and_callout(s9, box9, "ITEM 9 [1:40-1:52] · Cenário 2: Oráculo > 300s ➔ BLOCKED (Fail-Closed)", direction="top", theme="amber")
        steps.append({
            "item": 9,
            "timestamp": "1:40 - 1:52",
            "title": "Cenário 2 — Bloqueio Fail-Closed por Oráculo Obsoleto",
            "voiceover_en": "Now, watch Scenario 2: we simulate a stale oracle observation older than 300 seconds. The system triggers an instant block: BLOCKED, Stale Oracle. Our engine is strictly Fail-Closed. When market data is uncertain, the vault refuses to trade.",
            "voiceover_pt": "Agora, veja o Cenário 2: simulamos uma cotação oracular com mais de 300 segundos. O sistema bloqueia instantaneamente: BLOCKED, Stale Oracle. Nosso motor é estritamente Fail-Closed. Quando o dado é incerto, o cofre recusa a execução.",
            "file": "screenshots_narration/narration_step_09.png",
            "ui_action": "Clique em 'Block · stale price' com rejeição determinística.",
            "target_element": "Botão de Simulação: Block · Stale Price & Veredito Fail-Closed"
        })

        # =========================================================================
        # ITEM 10: 1:52 - 2:00
        # Scenario 3: divergence 20%, Blocked Price Divergence, toxic arbitrage
        # =========================================================================
        print("Capturing Item 10 (1:52 - 2:00)...")
        div_btn = page.locator("button:has-text('Block · divergence')").first
        box10 = await div_btn.bounding_box()
        await div_btn.click()
        await page.wait_for_timeout(800)
        s10 = OUTPUT_DIR / "narration_step_10.png"
        await page.screenshot(path=s10)
        if box10:
            draw_arrow_and_callout(s10, box10, "ITEM 10 [1:52-2:00] · Cenário 3: Desvio > 20% ➔ BLOCKED (Anti-Arbitrage)", direction="top", theme="red")
        steps.append({
            "item": 10,
            "timestamp": "1:52 - 2:00",
            "title": "Cenário 3 — Proteção Contra Divergência Tóxica de Cotação",
            "voiceover_en": "Next, Scenario 3: an execution route diverging 20% from Pyth benchmark pricing. Blocked immediately! Price Divergence. Capital is shielded from toxic arbitrage.",
            "voiceover_pt": "Em seguida, Cenário 3: uma rota divergindo 20% do benchmark Pyth. Bloqueio imediato! Divergência de Preço. O capital é protegido contra arbitragem tóxica.",
            "file": "screenshots_narration/narration_step_10.png",
            "ui_action": "Clique em 'Block · divergence' demonstrando a proteção de liquidez.",
            "target_element": "Botão de Simulação: Block · Divergence & Proteção Tóxica"
        })

        # =========================================================================
        # ITEM 11: 2:00 - 2:08
        # Export auditable JSON payload for institutional compliance
        # =========================================================================
        print("Capturing Item 11 (2:00 - 2:08)...")
        json_btn = page.locator("button:has-text('Show JSON')").first
        box11 = await json_btn.bounding_box()
        await json_btn.click()
        await page.wait_for_timeout(800)
        s11 = OUTPUT_DIR / "narration_step_11.png"
        await page.screenshot(path=s11)
        if box11:
            draw_arrow_and_callout(s11, box11, "ITEM 11 [2:00-2:08] · Recibo Auditável: Exportação JSON Institucional", direction="top", theme="purple")
        steps.append({
            "item": 11,
            "timestamp": "2:00 - 2:08",
            "title": "Exportação & Auditoria Institucional em JSON",
            "voiceover_en": "Every decision can be exported as an auditable JSON payload for off-chain institutional compliance.",
            "voiceover_pt": "Toda decisão pode ser exportada como um payload JSON auditável para compliance institucional off-chain.",
            "file": "screenshots_narration/narration_step_11.png",
            "ui_action": "Clique no botão 'Show JSON' revelando os metadados de auditoria.",
            "target_element": "Botão: Show JSON (Payload Estruturado Criptográfico)"
        })

        # =========================================================================
        # ITEM 12: 2:08 - 2:20
        # Audit tab, confirmed Solana Devnet transactions, metabolize_yield
        # =========================================================================
        print("Capturing Item 12 (2:08 - 2:20)...")
        audit_tab = page.locator("button:has-text('04Audit')").first
        box12 = await audit_tab.bounding_box()
        await audit_tab.click()
        await page.wait_for_timeout(800)
        s12 = OUTPUT_DIR / "narration_step_12.png"
        await page.screenshot(path=s12)
        if box12:
            draw_arrow_and_callout(s12, box12, "ITEM 12 [2:08-2:20] · Transação On-Chain: metabolize_yield (Devnet)", direction="top", theme="blue")
        steps.append({
            "item": 12,
            "timestamp": "2:08 - 2:20",
            "title": "Auditoria On-Chain & Transações Confirmadas na Solana",
            "voiceover_en": "Finally, on the Audit tab, we verify confirmed Solana Devnet transactions. Our Anchor program enforces Program Derived Address custody. We see real executions of metabolize_yield.",
            "voiceover_pt": "Finalmente, na aba Audit, verificamos transações confirmadas na Solana Devnet. Nosso programa Anchor isola custódia em PDAs. Vemos execuções reais de metabolize_yield.",
            "file": "screenshots_narration/narration_step_12.png",
            "ui_action": "Transição para a aba '04 Audit' e inspeção de transações on-chain com hash real.",
            "target_element": "Transação On-Chain Confirmada: metabolize_yield"
        })

        # =========================================================================
        # ITEM 13: 2:20 - 2:32
        # Human owner constitutional right: emergency_withdraw, revoke operators
        # =========================================================================
        print("Capturing Item 13 (2:20 - 2:32)...")
        # Scroll up or focus on Owner key / Custody rules on Audit tab
        owner_section = page.locator("text=OWNER KEY").first
        box13 = await owner_section.bounding_box()
        s13 = OUTPUT_DIR / "narration_step_13.png"
        await page.screenshot(path=s13)
        if box13:
            draw_arrow_and_callout(s13, box13, "ITEM 13 [2:20-2:32] · Soberania Humana: emergency_withdraw & Chave do Owner", direction="bottom", theme="red")
        steps.append({
            "item": 13,
            "timestamp": "2:20 - 2:32",
            "title": "Soberania Humana & Salvaguarda emergency_withdraw",
            "voiceover_en": "And if an agent ever misbehaves, the human owner holds the constitutional right to trigger emergency_withdraw, revoking operators and reclaiming capital.",
            "voiceover_pt": "E se um agente falhar ou agir maliciosamente, o dono humano detém o direito constitucional de acionar emergency_withdraw, revogando operadores e recuperando o capital.",
            "file": "screenshots_narration/narration_step_13.png",
            "ui_action": "Destaque na soberania da 'Owner Key' sobre as chaves do operador no programa Anchor.",
            "target_element": "Pilar de Governança: Owner Key vs. Operator Key & Emergency Controls"
        })

        # =========================================================================
        # ITEM 14: 2:32 - 2:50
        # Live verifiable control plane on Solana, AI advises, owner governs, Colosseum
        # =========================================================================
        print("Capturing Item 14 (2:32 - 2:50)...")
        # Return to Overview for hero conclusion
        overview_tab = page.locator("button:has-text('01Overview')").first
        await overview_tab.click()
        await page.wait_for_timeout(800)
        sub_card = page.locator("text=Public query · read only, text=STOCKLANA").first
        if await sub_card.count() == 0:
            sub_card = page.locator("text=ValueCurator").first
        box14 = await sub_card.bounding_box()
        s14 = OUTPUT_DIR / "narration_step_14.png"
        await page.screenshot(path=s14)
        if box14:
            draw_arrow_and_callout(s14, box14, "ITEM 14 [2:32-2:50] · Conclusão: Plano de Controle On-Chain · Colosseum 2026", direction="bottom", theme="green")
        steps.append({
            "item": 14,
            "timestamp": "2:32 - 2:50",
            "title": "Epílogo: Plano de Controle Verificável na Solana & Colosseum",
            "voiceover_en": "ValueCurator is not an abstract AI concept. It is a live, verifiable control plane on Solana. AI advises. Evidence proves. Policy authorizes. The owner governs. Thank you, and we look forward to the Colosseum Accelerator.",
            "voiceover_pt": "O ValueCurator não é um conceito abstrato de IA. É um plano de controle vivo e verificável na Solana. IA aconselha. Evidência comprova. Política autoriza. O dono governa. Obrigado, e nos vemos no Colosseum Accelerator.",
            "file": "screenshots_narration/narration_step_14.png",
            "ui_action": "Encerramento triunfante da apresentação com os axiomas soberanos e chamada para a banca avaliadora.",
            "target_element": "Painel de Conclusão: Arquitetura Verificável na Solana"
        })

        await browser.close()
        print("All 14 narration screenshots captured and annotated successfully!")

    return steps

if __name__ == "__main__":
    data = asyncio.run(run_narration_e2e())
    with open("/home/sukata/ip-nft/screenshots_narration/narration_steps.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Saved metadata to /home/sukata/ip-nft/screenshots_narration/narration_steps.json")
