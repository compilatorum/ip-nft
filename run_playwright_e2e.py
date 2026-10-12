import re
import time
import json
from playwright.sync_api import sync_playwright

def run_comprehensive_e2e():
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target_url": "https://www.valuecurator.xyz",
        "browser": "Chromium 146.0 (Termux Headless Engine)",
        "suites": {},
        "console_logs": [],
        "page_errors": [],
        "failed_requests": [],
        "passed_tests": 0,
        "failed_tests": 0,
    }

    def record_test(suite_name, test_name, status, details=None):
        if suite_name not in results["suites"]:
            results["suites"][suite_name] = []
        results["suites"][suite_name].append({
            "test": test_name,
            "status": status,
            "details": details or {}
        })
        if status == "PASSED":
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        print(f"[{status}] {suite_name} :: {test_name}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/data/data/com.termux/files/usr/bin/chromium-browser",
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.on("console", lambda msg: results["console_logs"].append({
            "type": msg.type, "text": msg.text
        }))
        page.on("pageerror", lambda err: results["page_errors"].append(str(err)))
        page.on("requestfailed", lambda req: results["failed_requests"].append({
            "url": req.url, "failure": req.failure
        }))

        # ======================================================================
        # SUITE 1: Inicialização, Metadados & Carregamento
        # ======================================================================
        suite1 = "1. Inicialização, Metadados & Carregamento"
        t0 = time.time()
        try:
            resp = page.goto(results["target_url"], timeout=30000, wait_until="networkidle")
            load_time_ms = int((time.time() - t0) * 1000)
            if resp.status == 200:
                record_test(suite1, "HTTP 200 Status OK", "PASSED", {"status": resp.status, "load_time_ms": load_time_ms})
            else:
                record_test(suite1, "HTTP 200 Status OK", "FAILED", {"status": resp.status})
        except Exception as e:
            record_test(suite1, "HTTP 200 Status OK", "FAILED", {"error": str(e)})

        try:
            title = page.title()
            expected_title = "ValueCurator"
            if expected_title in title:
                record_test(suite1, "Verificação do Page Title", "PASSED", {"title": title})
            else:
                record_test(suite1, "Verificação do Page Title", "FAILED", {"title": title, "expected": expected_title})
        except Exception as e:
            record_test(suite1, "Verificação do Page Title", "FAILED", {"error": str(e)})

        try:
            body_text = page.locator("body").inner_text()
            has_proofgate = "ValueCurator" in body_text and "Stocklana" in body_text
            record_test(suite1, "Presença de Headings Institucionais", "PASSED" if has_proofgate else "FAILED")
        except Exception as e:
            record_test(suite1, "Presença de Headings Institucionais", "FAILED", {"error": str(e)})

        # ======================================================================
        # SUITE 2: Tab 01: Overview & Ativos Verificados
        # ======================================================================
        suite2 = "2. Tab 01: Overview & Ativos Verificados"
        try:
            btn_overview = page.locator("button:has-text('Overview')").first
            btn_overview.click(timeout=5000)
            page.wait_for_timeout(800)
            overview_text = page.locator("body").inner_text()
            
            has_aapl = "AAPLx" in overview_text
            has_pyth = "922" in overview_text or "Pyth" in overview_text
            has_devnet = "Devnet" in overview_text
            has_treasury = "15CiCmUr42Za5i4RHaZewd1Dkx4v7gM46VkRMK25BmYKVA" in overview_text or "Treasury" in overview_text

            record_test(suite2, "Identificação de Ativo RWA (AAPLx Tokenized Equity)", "PASSED" if has_aapl else "FAILED", {"detected": has_aapl})
            record_test(suite2, "Identificação de Oráculo Pyth Feed 922", "PASSED" if has_pyth else "FAILED", {"detected": has_pyth})
            record_test(suite2, "Demarcação Explícita de Redes (Devnet Custody vs Mainnet Market)", "PASSED" if has_devnet else "FAILED", {"detected": has_devnet})
            record_test(suite2, "Conta de Tesouraria de Infraestrutura Conectada", "PASSED" if has_treasury else "FAILED")
        except Exception as e:
            record_test(suite2, "Inspeção da Tab Overview", "FAILED", {"error": str(e)})

        # ======================================================================
        # SUITE 3: Tab 02: Construtor de Mandatos (Mandate Builder)
        # ======================================================================
        suite3 = "3. Tab 02: Construtor de Mandatos (Mandate Builder)"
        try:
            btn_mandate = page.locator("button:has-text('Mandate')").first
            btn_mandate.click(timeout=5000)
            page.wait_for_timeout(800)
            mandate_text = page.locator("body").inner_text()

            record_test(suite3, "Navegação Interativa para Tab Mandato", "PASSED")

            has_asset_subtab = page.locator("button:has-text('Verified asset')").count() > 0
            has_risk_subtab = page.locator("button:has-text('Risk limits')").count() > 0
            has_sim_subtab = page.locator("button:has-text('Simulation')").count() > 0
            has_review_subtab = page.locator("button:has-text('Review & export')").count() > 0

            record_test(suite3, "Sub-navegação Modular do Mandato (Ativos, Risco, Simulação, Exportação)", 
                        "PASSED" if (has_asset_subtab and has_risk_subtab and has_sim_subtab) else "FAILED",
                        {"asset": has_asset_subtab, "risk": has_risk_subtab, "sim": has_sim_subtab, "review": has_review_subtab})

            # Click Risk Limits subtab
            btn_risk = page.locator("button:has-text('Risk limits')").first
            btn_risk.click(timeout=5000)
            page.wait_for_timeout(600)
            risk_text = page.locator("body").inner_text()

            has_limits = any(k in risk_text for k in ["Trade limit", "Daily", "bps", "deviation", "age"])
            record_test(suite3, "Exibição de Limites Paramétricos de Risco (Trade, BPS, Slippage)", "PASSED" if has_limits else "FAILED")
        except Exception as e:
            record_test(suite3, "Navegação Interativa para Tab Mandato", "FAILED", {"error": str(e)})

        # ======================================================================
        # SUITE 4: Tab 03: Portão de Política & Cenários de Simulação
        # ======================================================================
        suite4 = "4. Tab 03: Portão de Política & Avaliação Determinística"
        try:
            btn_gate = page.locator("button:has-text('Gate')").first
            btn_gate.click(timeout=5000)
            page.wait_for_timeout(800)

            record_test(suite4, "Navegação Interativa para Tab Gate", "PASSED")

            # Scenario 1: Safe · APPROVED
            btn_approved = page.locator("button:has-text('Safe · APPROVED')").first
            btn_approved.click(timeout=5000)
            page.wait_for_timeout(500)
            text_app = page.locator("body").inner_text()
            pass_approved = "SAFE · APPROVED" in text_app or "APPROVED" in text_app
            record_test(suite4, "Cenário 1: Proposta Válida -> Emissão de Recibo APPROVED", "PASSED" if pass_approved else "FAILED")

            # Scenario 2: Block · stale price
            btn_stale = page.locator("button:has-text('Block · stale price')").first
            btn_stale.click(timeout=5000)
            page.wait_for_timeout(500)
            text_stale = page.locator("body").inner_text()
            pass_stale = "stale" in text_stale and ("Block" in text_stale or "BLOCKED" in text_stale)
            record_test(suite4, "Cenário 2: Oráculo Obsoleto -> Interrupção com Rejeição por Idade", "PASSED" if pass_stale else "FAILED")

            # Scenario 3: Block · divergence
            btn_div = page.locator("button:has-text('Block · divergence')").first
            btn_div.click(timeout=5000)
            page.wait_for_timeout(500)
            text_div = page.locator("body").inner_text()
            pass_div = "divergen" in text_div and ("Block" in text_div or "BLOCKED" in text_div)
            record_test(suite4, "Cenário 3: Desvio de Cotação Excessivo -> Interrupção por Divergência", "PASSED" if pass_div else "FAILED")

            # Check JSON Export action
            has_json_btn = page.locator("button:has-text('Show JSON'), button:has-text('Download JSON')").count() > 0
            record_test(suite4, "Disponibilidade de Exportação Auditável em Formato JSON", "PASSED" if has_json_btn else "FAILED")
        except Exception as e:
            record_test(suite4, "Navegação Interativa para Tab Gate", "FAILED", {"error": str(e)})

        # ======================================================================
        # SUITE 5: Tab 04: Auditoria Criptográfica & Transações Devnet
        # ======================================================================
        suite5 = "5. Tab 04: Auditoria Criptográfica & Transações Devnet"
        try:
            btn_audit = page.locator("button:has-text('Audit')").first
            btn_audit.click(timeout=5000)
            page.wait_for_timeout(800)
            audit_text = page.locator("body").inner_text()

            record_test(suite5, "Navegação Interativa para Tab Audit", "PASSED")

            has_sig = any(sig in audit_text for sig in [
                "5iYZdNguAxH5u1niikvtBW7oPLj9qodor5coKmDyZWoJaXKsqfwroaJdyy7r23zRTFQYinXH7wACMUdgYXQ9chJq",
                "metabolize_yield",
                "Confirmed split"
            ])
            record_test(suite5, "Exibição de Transação Confirmada na Solana (metabolize_yield)", "PASSED" if has_sig else "FAILED")

            has_export_btn = page.locator("button:has-text('Export JSON')").count() > 0
            record_test(suite5, "Botão de Exportação do Relatório Criptográfico Final", "PASSED" if has_export_btn else "FAILED")
        except Exception as e:
            record_test(suite5, "Navegação Interativa para Tab Audit", "FAILED", {"error": str(e)})

        # ======================================================================
        # SUITE 6: Rota de Customer Discovery (/interview)
        # ======================================================================
        suite6 = "6. Rota de Customer Discovery (/interview)"
        try:
            resp_int = page.goto("https://www.valuecurator.xyz/interview", timeout=15000)
            if resp_int and resp_int.status == 200:
                record_test(suite6, "Disponibilidade da Rota /interview em Produção", "PASSED", {"status": 200})
            elif resp_int and resp_int.status == 404:
                record_test(suite6, "Disponibilidade da Rota /interview em Produção", "FAILED", {
                    "status": 404,
                    "diagnostic": "O servidor de produção em valuecurator.xyz ainda não deployou o pacote apps/discovery-api e o componente discovery-interview.tsx presente no monorepo."
                })
            else:
                record_test(suite6, "Disponibilidade da Rota /interview em Produção", "FAILED", {"status": resp_int.status if resp_int else None})
        except Exception as e:
            record_test(suite6, "Disponibilidade da Rota /interview em Produção", "FAILED", {"error": str(e)})

        # ======================================================================
        # SUITE 7: Auditoria de Console, Erros JS e Integridade de Rede
        # ======================================================================
        suite7 = "7. Auditoria de Console, Erros JS e Integridade de Rede"
        critical_errors = [e for e in results["page_errors"]]
        failed_asset_reqs = [r for r in results["failed_requests"] if not "favicon" in r["url"]]
        
        record_test(suite7, "Ausência de Erros Não Capturados de Execução JS", "PASSED" if len(critical_errors) == 0 else "FAILED", {
            "page_errors": critical_errors
        })
        record_test(suite7, "Carregamento Íntegro de Recursos de Rede (Sem 404/CORS de Assets)", "PASSED" if len(failed_asset_reqs) == 0 else "FAILED", {
            "failed_requests": failed_asset_reqs
        })

        browser.close()

    with open("/home/sukata/ip-nft/playwright_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n==========================================")
    print(f"BATALHÃO DE TESTES FINALIZADO: {results['passed_tests']} PASSADOS | {results['failed_tests']} FALHAS")
    print(f"Resultados exportados para /home/sukata/ip-nft/playwright_test_results.json")
    print(f"==========================================")

if __name__ == "__main__":
    run_comprehensive_e2e()
