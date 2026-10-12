#!/usr/bin/env python3
"""
Convert Markdown with LaTeX and Mermaid diagrams to beautiful PDF using Playwright Chromium.
"""
import os
import re
import html
import asyncio
from pathlib import Path
from markdown_it import MarkdownIt
from playwright.async_api import async_playwright

def preprocess_markdown(text: str):
    """
    Safely isolate LaTeX math formulas and Mermaid blocks before markdown parsing.
    """
    math_blocks = []
    math_inlines = []
    mermaid_blocks = []

    # 1. Extract and protect display math: $$...$$
    def save_display_math(match):
        idx = len(math_blocks)
        content = match.group(1)
        math_blocks.append(content)
        return f"\n\n<!--DISPLAY_MATH_{idx}-->\n\n"

    text = re.sub(r'\$\$(.*?)\$\$', save_display_math, text, flags=re.DOTALL)

    # 2. Extract and protect inline math: $...$ (ignoring escaped \$)
    def save_inline_math(match):
        idx = len(math_inlines)
        content = match.group(1)
        math_inlines.append(content)
        return f"<!--INLINE_MATH_{idx}-->"

    # Match $...$ where $ is not preceded/followed by another $ and content is non-empty
    text = re.sub(r'(?<!\$)\$(?!\$)([^\n\$]+?)(?<!\$)\$(?!\$)', save_inline_math, text)

    # 3. Extract and protect mermaid code blocks: ```mermaid ... ```
    def save_mermaid(match):
        idx = len(mermaid_blocks)
        content = match.group(1).strip()
        mermaid_blocks.append(content)
        return f"\n\n<!--MERMAID_BLOCK_{idx}-->\n\n"

    text = re.sub(r'```mermaid\s*\n(.*?)\n```', save_mermaid, text, flags=re.DOTALL)

    return text, math_blocks, math_inlines, mermaid_blocks

def postprocess_html(html_text: str, math_blocks, math_inlines, mermaid_blocks):
    """
    Restore LaTeX and Mermaid blocks into suitable DOM containers.
    """
    # Restore Display Math
    for idx, content in enumerate(math_blocks):
        clean_content = content.strip()
        replacement = f'<div class="math-display">$$\n{clean_content}\n$$</div>'
        html_text = html_text.replace(f'<!--DISPLAY_MATH_{idx}-->', replacement)
        # Also handle potential paragraph wrapped comments
        html_text = html_text.replace(f'<p>&lt;!--DISPLAY_MATH_{idx}--&gt;</p>', replacement)
        html_text = html_text.replace(f'&lt;!--DISPLAY_MATH_{idx}--&gt;', replacement)

    # Restore Inline Math
    for idx, content in enumerate(math_inlines):
        clean_content = content.strip()
        replacement = f'<span class="math-inline">${clean_content}$</span>'
        html_text = html_text.replace(f'<!--INLINE_MATH_{idx}-->', replacement)
        html_text = html_text.replace(f'&lt;!--INLINE_MATH_{idx}--&gt;', replacement)

    # Restore Mermaid Blocks
    for idx, content in enumerate(mermaid_blocks):
        # We need raw unescaped text for Mermaid to parse arrows like ->> and -->
        replacement = f'<div class="mermaid-container"><div class="mermaid">\n{content}\n</div></div>'
        html_text = html_text.replace(f'<!--MERMAID_BLOCK_{idx}-->', replacement)
        html_text = html_text.replace(f'<p>&lt;!--MERMAID_BLOCK_{idx}--&gt;</p>', replacement)
        html_text = html_text.replace(f'&lt;!--MERMAID_BLOCK_{idx}--&gt;', replacement)

    # Ensure major sections and diagrams 2 & 3 start on clean pages for maximum readability
    html_text = re.sub(r'<h2>(.*?[§\d].*?)</h2>', r'<h2 style="page-break-before: always; break-before: always;">\1</h2>', html_text)
    html_text = re.sub(r'<h3>(.*?[Dd]iagrama [2345].*?)</h3>', r'<h3 style="page-break-before: always; break-before: always;">\1</h3>', html_text)

    return html_text

def build_full_html(body_html: str, vendor_dir: str, title: str = "Relatório Técnico"):
    """
    Wrap rendered body in modern styled HTML template.
    """
    mathjax_path = os.path.abspath(os.path.join(vendor_dir, "mathjax-tex-svg.js"))
    mermaid_path = os.path.abspath(os.path.join(vendor_dir, "mermaid.min.js"))

    # Read JS contents directly to inline them so file:// protocol doesn't have cross-origin or loading issues
    with open(mathjax_path, 'r', encoding='utf-8') as f:
        mathjax_js = f.read()
    with open(mermaid_path, 'r', encoding='utf-8') as f:
        mermaid_js = f.read()

    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>{html.escape(title)}</title>
  <style>
    @page {{
      size: A4 portrait;
      margin: 18mm 16mm 18mm 16mm;
      @bottom-right {{
        content: counter(page);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 9pt;
        color: #64748b;
      }}
    }}
    
    * {{
      box-sizing: border-box;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.6;
      color: #0f172a;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }}

    h1, h2, h3, h4, h5, h6 {{
      color: #0f172a;
      font-weight: 700;
      margin-top: 1.4em;
      margin-bottom: 0.5em;
      page-break-after: avoid;
      break-after: avoid;
      line-height: 1.3;
    }}

    h1 {{
      font-size: 20pt;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 0.3em;
      margin-top: 0;
    }}

    h2 {{
      font-size: 15pt;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 0.2em;
    }}

    h3 {{
      font-size: 12.5pt;
    }}

    h4 {{
      font-size: 11pt;
    }}

    p {{
      margin-top: 0.4em;
      margin-bottom: 0.8em;
    }}

    blockquote {{
      margin: 1em 0;
      padding: 0.8em 1.2em;
      color: #1e293b;
      background: #f8fafc;
      border-left: 4px solid #3b82f6;
      border-radius: 0 6px 6px 0;
      font-style: italic;
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    blockquote p {{
      margin: 0;
    }}

    ul, ol {{
      margin-top: 0.4em;
      margin-bottom: 0.8em;
      padding-left: 1.5em;
    }}

    li {{
      margin-bottom: 0.3em;
    }}

    hr {{
      border: 0;
      height: 1px;
      background: #e2e8f0;
      margin: 1.5em 0;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1.2em 0;
      font-size: 9.5pt;
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    th, td {{
      border: 1px solid #cbd5e1;
      padding: 7px 10px;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background-color: #f1f5f9;
      font-weight: 600;
      color: #1e293b;
    }}

    tr:nth-child(even) {{
      background-color: #f8fafc;
    }}

    pre {{
      background: #0f172a;
      color: #f8fafc;
      padding: 10px 14px;
      border-radius: 6px;
      overflow-x: auto;
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 9pt;
      line-height: 1.45;
      page-break-inside: avoid;
      break-inside: avoid;
      margin: 1em 0;
    }}

    code {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 9pt;
      background: #f1f5f9;
      color: #0f172a;
      padding: 2px 5px;
      border-radius: 4px;
      border: 1px solid #e2e8f0;
    }}

    pre code {{
      background: transparent;
      color: inherit;
      padding: 0;
      border: none;
    }}

    /* MathJax LaTeX styling */
    .math-display {{
      display: flex;
      justify-content: center;
      align-items: center;
      margin: 1.2em 0;
      page-break-inside: avoid;
      break-inside: avoid;
      overflow-x: auto;
    }}

    mjx-container[jax="SVG"][display="true"] {{
      margin: 0.6em 0 !important;
      max-width: 100%;
    }}

    mjx-container svg {{
      max-width: 100% !important;
      height: auto !important;
    }}

    /* Mermaid diagrams styling */
    .mermaid-container {{
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      margin: 1.8em 0;
      page-break-inside: avoid;
      break-inside: avoid;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}

    .mermaid {{
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }}

    .mermaid svg {{
      max-width: 100% !important;
      height: auto !important;
      display: block;
      margin: 0 auto;
    }}

    /* Custom high-contrast vibrant styles for Mermaid nodes and state classes */
    g.state.ok rect, g.statediagram-state.ok rect, g.node.ok rect, g.node.ok polygon {{
      fill: #059669 !important;
      stroke: #10b981 !important;
      stroke-width: 2px !important;
    }}
    g.state.ok text, g.statediagram-state.ok text, g.node.ok text, g.node.ok span {{
      fill: #ffffff !important;
      color: #ffffff !important;
      font-weight: 600 !important;
    }}

    g.state.warn rect, g.statediagram-state.warn rect, g.node.warn rect, g.node.warn polygon {{
      fill: #d97706 !important;
      stroke: #fbbf24 !important;
      stroke-width: 2px !important;
    }}
    g.state.warn text, g.statediagram-state.warn text, g.node.warn text, g.node.warn span {{
      fill: #ffffff !important;
      color: #ffffff !important;
      font-weight: 600 !important;
    }}

    g.state.err rect, g.statediagram-state.err rect, g.node.err rect, g.node.err polygon {{
      fill: #b91c1c !important;
      stroke: #f87171 !important;
      stroke-width: 2px !important;
    }}
    g.state.err text, g.statediagram-state.err text, g.node.err text, g.node.err span {{
      fill: #ffffff !important;
      color: #ffffff !important;
      font-weight: 600 !important;
    }}

    g.state.neutral rect, g.statediagram-state.neutral rect, g.node.neutral rect {{
      fill: #1e293b !important;
      stroke: #475569 !important;
      stroke-width: 2px !important;
    }}
    g.state.neutral text, g.statediagram-state.neutral text, g.node.neutral text, g.node.neutral span {{
      fill: #f8fafc !important;
      color: #f8fafc !important;
    }}

    a {{
      color: #2563eb;
      text-decoration: none;
    }}

    a:hover {{
      text-decoration: underline;
    }}
  </style>
  <script>
    window.MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
        processEscapes: true
      }},
      svg: {{
        fontCache: 'local'
      }},
      startup: {{
        typeset: false
      }}
    }};
  </script>
  <script>
    {mathjax_js}
  </script>
  <script>
    {mermaid_js}
  </script>
</head>
<body>
  {body_html}

  <script>
    window.renderDiagramsAndMath = async function() {{
      try {{
        // 1. Initialize & render Mermaid diagrams
        mermaid.initialize({{
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'basis' }},
          sequence: {{ useMaxWidth: true, showSequenceNumbers: true, actorMargin: 40 }}
        }});

        const mermaidNodes = document.querySelectorAll('.mermaid');
        if (mermaidNodes.length > 0) {{
          await mermaid.run({{
            nodes: mermaidNodes
          }});
          
          // Post-process SVG to guarantee 100% width fit, responsive viewBox and vibrant colors
          mermaidNodes.forEach(node => {{
            const svg = node.querySelector('svg');
            if (svg) {{
              svg.style.maxWidth = '100%';
              svg.style.height = 'auto';
              if (!svg.getAttribute('viewBox')) {{
                const bbox = svg.getBBox();
                if (bbox && bbox.width > 0) {{
                  svg.setAttribute('viewBox', `${{bbox.x}} ${{bbox.y}} ${{bbox.width}} ${{bbox.height}}`);
                }}
              }}

              // Enrich diagram states and nodes with semantic theme colors
              svg.querySelectorAll('g.statediagram-state, g.state, g.node').forEach(g => {{
                const text = g.textContent || '';
                const rects = g.querySelectorAll('rect, polygon');
                if (text.includes('APPROVED')) {{
                  rects.forEach(r => {{
                    r.style.setProperty('fill', '#059669', 'important');
                    r.style.setProperty('stroke', '#10b981', 'important');
                    r.style.setProperty('stroke-width', '2px', 'important');
                  }});
                  g.querySelectorAll('text, span, div').forEach(t => {{
                    t.style.setProperty('fill', '#ffffff', 'important');
                    t.style.setProperty('color', '#ffffff', 'important');
                  }});
                }} else if (text.includes('Stale')) {{
                  rects.forEach(r => {{
                    r.style.setProperty('fill', '#d97706', 'important');
                    r.style.setProperty('stroke', '#fbbf24', 'important');
                    r.style.setProperty('stroke-width', '2px', 'important');
                  }});
                  g.querySelectorAll('text, span, div').forEach(t => {{
                    t.style.setProperty('fill', '#ffffff', 'important');
                    t.style.setProperty('color', '#ffffff', 'important');
                  }});
                }} else if (text.includes('Divergence') || text.includes('404 NOT FOUND')) {{
                  rects.forEach(r => {{
                    r.style.setProperty('fill', '#b91c1c', 'important');
                    r.style.setProperty('stroke', '#f87171', 'important');
                    r.style.setProperty('stroke-width', '2px', 'important');
                  }});
                  g.querySelectorAll('text, span, div').forEach(t => {{
                    t.style.setProperty('fill', '#ffffff', 'important');
                    t.style.setProperty('color', '#ffffff', 'important');
                  }});
                }} else if (text.includes('ProposalSubmitted') || text.includes('CheckRules')) {{
                  rects.forEach(r => {{
                    r.style.setProperty('fill', '#1e293b', 'important');
                    r.style.setProperty('stroke', '#475569', 'important');
                    r.style.setProperty('stroke-width', '2px', 'important');
                  }});
                  g.querySelectorAll('text, span, div').forEach(t => {{
                    t.style.setProperty('fill', '#f8fafc', 'important');
                    t.style.setProperty('color', '#f8fafc', 'important');
                  }});
                }}
              }});
            }}
          }});
        }}

        // 2. Typeset LaTeX with MathJax 3
        if (window.MathJax && window.MathJax.typesetPromise) {{
          await window.MathJax.typesetPromise();
        }}

        return {{ success: true, mermaidCount: mermaidNodes.length }};
      }} catch (err) {{
        return {{ success: false, error: err.toString() }};
      }}
    }};
  </script>
</body>
</html>
"""
    return template

async def convert_md_to_pdf(md_path: str, pdf_path: str, vendor_dir: str):
    """
    Orchestrate reading markdown, rendering HTML, loading in Playwright, and emitting PDF.
    """
    print(f"Reading {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        raw_md = f.read()

    # Preprocess
    pre_md, math_blocks, math_inlines, mermaid_blocks = preprocess_markdown(raw_md)
    print(f"Detected: {len(math_blocks)} display equations, {len(math_inlines)} inline equations, {len(mermaid_blocks)} mermaid diagrams.")

    # Markdown to HTML
    md_parser = MarkdownIt('commonmark', {'html': True}).enable('table').enable('strikethrough')
    body_html = md_parser.render(pre_md)

    # Postprocess
    body_html = postprocess_html(body_html, math_blocks, math_inlines, mermaid_blocks)

    # Full HTML
    title = Path(md_path).stem.replace('_', ' ').title()
    full_html = build_full_html(body_html, vendor_dir, title=title)

    # Save temp HTML for Playwright
    temp_html_path = os.path.abspath("temp_preview.html")
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Intermediate HTML written to {temp_html_path}")

    # Launch Playwright Chromium
    print("Launching Chromium via Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path='/data/data/com.termux/files/usr/bin/chromium-browser',
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--font-render-hinting=medium'
            ]
        )
        page = await browser.new_page(viewport={'width': 1200, 'height': 1600})
        
        # Navigate to file
        await page.goto(f"file://{temp_html_path}", wait_until="load")

        # Run client-side rendering
        print("Rendering Mermaid diagrams and MathJax equations...")
        render_res = await page.evaluate("() => window.renderDiagramsAndMath()")
        print(f"Client render result: {render_res}")

        # Wait a brief moment for fonts/rendering to settle
        await page.wait_for_timeout(1500)

        # Generate PDF
        print(f"Printing to PDF: {pdf_path}...")
        await page.pdf(
            path=pdf_path,
            format='A4',
            print_background=True,
            margin={
                'top': '18mm',
                'bottom': '18mm',
                'left': '16mm',
                'right': '16mm'
            }
        )
        print("PDF generation complete!")
        await browser.close()

    # Clean up temp HTML
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "/home/sukata/ip-nft/PLAYWRIGHT_E2E_TEST_REPORT.md"
    dst = sys.argv[2] if len(sys.argv) > 2 else "/home/sukata/ip-nft/PLAYWRIGHT_E2E_TEST_REPORT.pdf"
    vendor = "/home/sukata/ip-nft/vendor"
    asyncio.run(convert_md_to_pdf(src, dst, vendor))
