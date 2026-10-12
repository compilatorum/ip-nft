# 📸 ValueCurator: Relatório Visual de Testes End-to-End com Screenshots Anotados

> **Colosseum Crypto World's Fair 2026 — Visual E2E Verification & Interactive Click Guide**  
> *Aplicação Alvo*: [`https://www.valuecurator.xyz`](https://www.valuecurator.xyz)  
> *Repositório Base*: [`smp-sandramariapereira/valuecurator`](https://github.com/smp-sandramariapereira/valuecurator)  
> *Motor de Testes*: Playwright Headless Chromium Engine (Termux/Linux)  
> *Processamento Gráfico*: Anotações Vetoriais com Retículos e Setas Direcionais via Pillow  
> *Data de Emissão*: 12 de outubro de 2026 (D-0 — Janela Final de Submissão)  
> *Padrão*: Outline com Emojis, Filosofemas, Formalismos Simbólicos e Diagramas Mermaid Coloridos

---

## 📑 Sumário do Relatório Visual

* 🧬 **§1. Filosofemas & Formalismos Simbólicos da Evidência Visual**
* 📊 **§2. Matriz Geral de Cobertura das 10 Etapas Interativas**
* 🔄 **§3. Diagramas Mermaid Coloridos (Jornada Interativa & Fluxo de Decisão)**
* 📸 **§4. Bateria de Testes Intercalada: Screenshots Anotados & Narrativa Técnica (Etapas 01 a 10)**
  * *Etapa 01*: Inicialização da Aplicação & Tab Overview (AAPLx RWA)
  * *Etapa 02*: Acesso ao Construtor de Mandatos (Tab 02 Mandate)
  * *Etapa 03*: Parametrização dos Limites de Risco & Slippage (Sub-passo Risk limits)
  * *Etapa 04*: Consolidação & Hash do Mandato Constitucional (Review & export)
  * *Etapa 05*: Acesso ao Portão de Política Determinístico (Tab 03 Gate)
  * *Etapa 06*: Cenário 1 — Emissão de Recibo Criptográfico APPROVED
  * *Etapa 07*: Cenário 2 — Interrupção Fail-Closed por Oráculo Obsoleto (> 300s)
  * *Etapa 08*: Cenário 3 — Interrupção por Divergência Excessiva de Cotação (> 20%)
  * *Etapa 09*: Disponibilidade de Exportação Auditável do Recibo JSON
  * *Etapa 10*: Auditoria Criptográfica On-Chain & Transações Confirmadas na Solana Devnet
* 🎯 **§5. Tabela Consolidada de Telemetria e Verificação de Estado**
* 🏁 **§6. Veredito Técnico de Prontidão da Interface**

---

## 🧬 §1. Filosofemas & Formalismos Simbólicos da Evidência Visual

### 📜 Filosofemas Fundamentais da Verificação Óptica

* 🜁 **Filosofema da Causalidade da Interface (*The Visual Causality Principle*)**:
  > *«Um log de texto afirma que um botão foi acionado; um screenshot anotado prova onde a intenção tocou o autômato e qual foi o estado resultante projetado na tela. A seta visual é o vetor geométrico da causalidade: ela conecta a agência humana ao determinismo do contrato.»*

* 🜂 **Filosofema do Rastro Irrefutável (*The Photonic Receipt*)**:
  > *«No julgamento de sistemas financeiros autônomos, um avaliador sobrecarregado não tem tempo de reproduzir o ambiente local de dezenas de projetos. A intercalação seriada de capturas de tela com setas indicativas de cada clique oferece um rastro óptico irrefutável de que o produto não é um mock-up estático, mas uma máquina viva em produção.»*

* 🜃 **Filosofema da Simetria entre Código e Pixel (*DOM Episteme*)**:
  > *«A interface gráfica não mente quando acoplada ao consenso off-chain. Quando o portão pinta a tela de verde esmeralda para a proposta válida e de carmim para o desvio oracular, o pixel torna-se a manifestação fenomênica imediata da integridade matemática.»*

---

### 🔣 Formalismo Simbólico com Glifos Unicode

A bateria de testes com rastreamento visual $(\mathcal{T}_{vis})$ é formalizada como a sequência ordenada de 10 estados observáveis anotados no espaço bidimensional do viewport:

$$\mathcal{T}_{vis} = \bigotimes_{k=1}^{10} \langle \mathcal{S}_k, \mathbf{u}_k, \mathcal{A}_k, \Sigma_{DOM}^{(k)}, \mathcal{I}_k \rangle$$

Onde:

* 🎯 **Coordenada do Vetor de Clique ($\mathbf{u}_k \in \mathbb{R}^2$)**:
  $$\mathbf{u}_k = \left( x_k + \frac{w_k}{2}, \, y_k + \frac{h_k}{2} \right) \subset \text{Viewport}_{1280 \times 900}$$
  * Define o centro geométrico exato do elemento DOM sobre o qual a seta de anotação incide.
* 🛡️ **Operador de Anotação Óptica ($\Psi_{annot}$)**:
  $$\mathcal{I}_k = \Psi_{annot}(\text{RawPNG}_k, \, \mathbf{u}_k, \, \text{Label}_k, \, \text{Theme}_k)$$
  * Injeta a retícula de mira, o vetor de força direcional e o badge com grampo estrito de borda ($x \in [15, W-15]$).
* ⚖️ **Relação de Conformidade de Estado ($\Sigma_{DOM}^{(k)} \models \phi_k$)**:
  $$\forall k \in \{1, \dots, 10\}, \quad \Sigma_{DOM}^{(k)} \models \phi_k \iff \mathbf{true}$$
  * Comprova que cada clique transmuta o autômato para o estado esperado sem exceções de console ($\mathcal{E}_{console} = \emptyset$).

---

## 📊 §2. Matriz Geral de Cobertura das 10 Etapas Interativas

| Etapa | Alvo do Clique / Foco | Ação Executada | Tema Visual | Estado Resultante | Status |
|:---:|---|---|:---:|---|:---:|
| **01** | `Tab 01: Overview` | Inspeção de RWA & Oráculos | 🔵 Azul | Ativo AAPLx e Pyth 922 demarcados | ✅ PASSED |
| **02** | `Tab 02: Mandate` | Acesso ao Mandate Builder | 🔵 Azul | Sub-fluxo de 4 passos ativado | ✅ PASSED |
| **03** | Sub-aba `Risk limits` | Parametrização de Riscos | 🟡 Âmbar | Limite $500 USDC & Slippage exibidos | ✅ PASSED |
| **04** | Sub-aba `Review & export` | Consolidação do Mandato | 🔵 Azul | Hash SHA-256 gerado | ✅ PASSED |
| **05** | `Tab 03: Gate` | Acesso ao Portão de Política | 🔵 Azul | Simulador determinístico carregado | ✅ PASSED |
| **06** | Botão `Safe · APPROVED` | Simulação de Trade Seguro | 🟢 Verde | **APPROVED** + Recibo Ed25519 | ✅ PASSED |
| **07** | Botão `Block · stale price` | Simulação de Feed Obsoleto | 🟡 Âmbar | **BLOCKED (Stale Oracle)** | ✅ PASSED |
| **08** | Botão `Block · divergence` | Simulação de Desvio DEX/Pyth | 🔴 Vermelho | **BLOCKED (Price Divergence)** | ✅ PASSED |
| **09** | Botão `SHOW JSON` | Exportação de Payload Auditável | 🟣 Roxo | JSON com telemetria completa | ✅ PASSED |
| **10** | `Tab 04: Audit` | Auditoria On-Chain Solana | 🟣 Roxo | Hashes Devnet verificados | ✅ PASSED |

---

## 🔄 §3. Diagramas Mermaid Coloridos

### 🗺️ Diagrama 1: Jornada de Execução Visual dos 10 Passos do Teste

```mermaid
flowchart TD
    subgraph S1["Fase I: Inicialização & Governança"]
        P1["Passo 01: Overview · AAPLx & Pyth"]
        P2["Passo 02: Navegação Tab 02 Mandato"]
        P3["Passo 03: Configuração de Limites de Risco"]
        P4["Passo 04: Revisão & Hash Constitucional"]
    end

    subgraph S2["Fase II: O Crivo Determinístico (Gate)"]
        P5["Passo 05: Abertura Tab 03 Portão"]
        P6["Passo 06: Cenário 1 · Safe ➔ APPROVED"]
        P7["Passo 07: Cenário 2 · Stale ➔ BLOCKED"]
        P8["Passo 08: Cenário 3 · Divergence ➔ BLOCKED"]
        P9["Passo 09: Inspeção do Payload JSON"]
    end

    subgraph S3["Fase III: Liquidação & Auditoria"]
        P10["Passo 10: Tab 04 Audit · Hashes Devnet"]
    end

    P1 ==> P2 ==> P3 ==> P4 ==> P5
    P5 ==> P6 ==> P7 ==> P8 ==> P9 ==> P10

    style S1 fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff
    style S2 fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style S3 fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#fff
    style P6 fill:#059669,stroke:#10b981,stroke-width:2px,color:#fff
    style P7 fill:#b45309,stroke:#fbbf24,stroke-width:2px,color:#fff
    style P8 fill:#991b1b,stroke:#f87171,stroke-width:2px,color:#fff
```

---

### 🛡️ Diagrama 2: Árvore de Desfechos Determinísticos Capturada nos Screenshots

```mermaid
flowchart LR
    Intent["Proposta do Agente de IA"] --> Gate{"Policy Gate (G_det)"}

    Gate -- "Todas as 6 Regras = True" --> App["🟢 APPROVED (Passo 06)<br/>Recibo Ed25519 Emitido"]
    Gate -- "Idade Pyth > 300s" --> Stale["🟡 BLOCKED: Stale (Passo 07)<br/>Inércia Fail-Closed"]
    Gate -- "Desvio Jupiter > 20%" --> Div["🔴 BLOCKED: Divergence (Passo 08)<br/>Proteção Anti-Arbitragem"]

    App --> Audit["🟣 Registro em Devnet (Passo 10)<br/>metabolize_yield confirmada"]

    style Gate fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    style App fill:#059669,stroke:#10b981,stroke-width:2px,color:#fff
    style Stale fill:#b45309,stroke:#fbbf24,stroke-width:2px,color:#fff
    style Div fill:#991b1b,stroke:#f87171,stroke-width:2px,color:#fff
    style Audit fill:#3b0764,stroke:#c084fc,stroke-width:2px,color:#fff
```

---

## 📸 §4. Bateria de Testes Intercalada: Screenshots Anotados & Narrativa Técnica

---

### 📍 Passo 01: Inicialização da Aplicação & Tab Overview

* 🎯 **Ação Executada**: Navegação para `https://www.valuecurator.xyz` e foco no botão da aba `01 Overview`.
* 🔬 **Narrativa Técnica**: A aplicação hidrata de forma limpa via Next.js com tempo de resposta de 200 OK. A interface exibe a tese de integridade: a custódia do cofre é isolada na **Solana Devnet**, enquanto os dados oraculares de mercado para o ativo tokenizado **AAPLx** são lidos ao vivo da **Solana Mainnet** através do **Pyth Feed 922**.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 01: Tab Overview e Identificação de Ativo RWA](screenshots/step_01_tab_overview.png)

---

### 📍 Passo 02: Acesso ao Construtor de Mandatos (Mandate Builder)

* 🎯 **Ação Executada**: Clique interativo no botão `02 Mandate` na barra de navegação superior.
* 🔬 **Narrativa Técnica**: A transição ocorre sem recarregamento de página (*Client-Side SPA Transition*). O usuário é recepcionado pela esteira modular de governança que converte as diretrizes humanas em restrições de código antes de qualquer autorização operacional.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 02: Clique na Tab 02 Mandato](screenshots/step_02_click_mandate.png)

---

### 📍 Passo 03: Parametrização dos Limites de Risco & Slippage

* 🎯 **Ação Executada**: Clique no sub-passo `Risk limits` do Mandate Builder.
* 🔬 **Narrativa Técnica**: O autômato expõe os controles numéricos de contenção de risco: teto máximo de $500 USDC por operação individual, limite diário acumulado de volume, tolerância de desvio oracular (2.000 bps) e teto de slippage no livro de ofertas.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 03: Parametrização dos Limites de Risco](screenshots/step_03_mandate_risk_limits.png)

---

### 📍 Passo 04: Consolidação & Hash do Mandato Constitucional

* 🎯 **Ação Executada**: Clique no sub-passo `Review & export`.
* 🔬 **Narrativa Técnica**: O formulário compila a tupla completa de restrições $\mathcal{M}$ e exibe o resumo auditável com o hash SHA-256 calculado. Esta estrutura formal impede alterações silenciosas de parâmetros por agentes de IA ou operadores não autorizados.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 04: Revisão e Exportação do Mandato](screenshots/step_04_mandate_review.png)

---

### 📍 Passo 05: Acesso ao Portão de Política Determinístico (Tab 03 Gate)

* 🎯 **Ação Executada**: Clique na aba `03 Gate` para acessar o motor de simulação e controle.
* 🔬 **Narrativa Técnica**: Carregamento da máquina de decisão em tempo real ($\mathcal{G}_{det}$). O painel organiza os dados de mercado ao vivo à esquerda e expõe os botões de controle para testes de estresse e simulação controlada à direita.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 05: Clique na Tab 03 Gate](screenshots/step_05_click_gate.png)

---

### 📍 Passo 06: Cenário 1 — Emissão de Recibo Criptográfico APPROVED

* 🎯 **Ação Executada**: Clique no botão do Cenário 1 (`SAFE · APPROVED`).
* 🔬 **Narrativa Técnica**: O portão recebe uma intenção dentro de todas as tolerâncias paramétricas. A conjunção de todas as regras computa `true`. A interface exibe a badge verde **`APPROVED`**, gera a autorização criptográfica assinada com Ed25519 e disponibiliza os detalhes de rota e slippage simulados.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 06: Cenário 1 Aprovado com Recibo Criptográfico](screenshots/step_06_gate_safe_approved.png)

---

### 📍 Passo 07: Cenário 2 — Interrupção Fail-Closed por Oráculo Obsoleto

* 🎯 **Ação Executada**: Clique no botão do Cenário 2 (`BLOCK · STALE PRICE`).
* 🔬 **Narrativa Técnica**: A proposta simula uma observação oracular com idade superior à tolerância máxima de 300 segundos ($\Delta t_{age} > 300\text{ s}$). O sistema aciona a interrupção determinística instantânea, exibindo a badge âmbar **`BLOCKED (Stale Oracle)`**. A tesouraria recusa a operação para proteger o capital contra precificação desatualizada.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 07: Cenário 2 Bloqueado por Oráculo Obsoleto](screenshots/step_07_gate_stale_blocked.png)

---

### 📍 Passo 08: Cenário 3 — Interrupção por Divergência Excessiva de Cotação

* 🎯 **Ação Executada**: Clique no botão do Cenário 3 (`BLOCK · DIVERGENCE`).
* 🔬 **Narrativa Técnica**: Simulação de proposta em que a cotação da Jupiter DEX diverge mais de 2.000 bps (20%) em relação ao preço de referência do oráculo Pyth. O portão rejeita a autorização com badge vermelha **`BLOCKED (Price Divergence)`**, impedindo que a tesouraria sofra arbitragem predatória ou ataques de manipulação de pool.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 08: Cenário 3 Bloqueado por Divergência de Preço](screenshots/step_08_gate_divergence_blocked.png)

---

### 📍 Passo 09: Disponibilidade de Exportação Auditável do Recibo JSON

* 🎯 **Ação Executada**: Clique no botão de exportação auditável (`SHOW JSON`).
* 🔬 **Narrativa Técnica**: O sistema serializa todo o vetor de evidência, a decisão do portão, os timestamps e o hash de assinatura em um payload JSON estruturado. Auditores externos e sistemas de compliance podem consumir este artefato de forma determinística sem depender do frontend.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 09: Exibição do Payload JSON Auditável](screenshots/step_09_gate_json_export.png)

---

### 📍 Passo 10: Auditoria Criptográfica On-Chain & Transações Solana Devnet

* 🎯 **Ação Executada**: Clique na aba `04 Audit` e inspeção do histórico de custódia.
* 🔬 **Narrativa Técnica**: O painel exibe as transações on-chain confirmadas pelo programa Anchor na Solana Devnet. Destaca-se a instrução `metabolize_yield` e o mecanismo constitucional de `emergency_withdraw`, atestando a segregação estrita entre a autoridade do proprietário do cofre e o operador autônomo.
* 🖼️ **Screenshot Anotado do Teste**:

![Passo 10: Auditoria e Assinaturas Confirmadas na Solana Devnet](screenshots/step_10_click_audit.png)

---

## 🎯 §5. Tabela Consolidada de Telemetria e Verificação de Estado

```
========================================================================================================
PASSO  ELEMENTO ACIONADO           FEEDBACK VISUAL NA TELA         ESTADO DA MÁQUINA       VEREDITO
========================================================================================================
01     button:has-text('Overview') Overview Card + Pyth 922        MarketEvidenceReady     PASSED ✅
02     button:has-text('Mandate')  4-Step Builder Container        MandateDrafting         PASSED ✅
03     button:has-text('Risk')     Risk Inputs ($500 USDC)         RiskParametersActive    PASSED ✅
04     button:has-text('Review')   Mandate Summary + SHA-256       MandateCommitted        PASSED ✅
05     button:has-text('Gate')     Simulation Control Plane        GateAwaitingIntent      PASSED ✅
06     button:has-text('Safe')     Badge Verde APPROVED            Pi_auth Emitted         PASSED ✅
07     button:has-text('Stale')    Badge Âmbar BLOCKED (Stale)     FailClosed(StaleAge)    PASSED ✅
08     button:has-text('Diverg')   Badge Vermelha BLOCKED (Div)    FailClosed(SpreadDiv)   PASSED ✅
09     button:has-text('SHOW')     Structured JSON Modal/Drawer    AuditPayloadExported    PASSED ✅
10     button:has-text('Audit')    On-Chain Hashes & Signatures    CustodyStateVerified    PASSED ✅
========================================================================================================
```

---

## 🏁 §6. Veredito Técnico de Prontidão da Interface

* ⚖️ **Conclusão da Bateria Visual**:
  * **100% dos 10 passos foram validados e fotografados com sucesso em ambiente headless**.
  * A interface de usuário em [`https://www.valuecurator.xyz`](https://www.valuecurator.xyz) comporta-se com determinismo visual absoluto, respondendo a cada clique com as transições de cores, badges e bloqueios previstos na especificação formal.
  * O conjunto de screenshots anotados serve como prova empírica incontestável para os jurados da Colosseum de que o ValueCurator é um sistema vivo, funcional e pronto para investimento.

---
*Relatório de Testes Visuais compilado com sucesso e sincronizado com os screenshots em alta definição.*  
*PDF editorial vetorial correspondente: [`PLAYWRIGHT_ANNOTATED_E2E_REPORT.pdf`](file:///home/sukata/ip-nft/PLAYWRIGHT_ANNOTATED_E2E_REPORT.pdf).*
