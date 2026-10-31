"""
=============================================================================
MARCÃO PERSONAL — HYPERFRAMES MOTION GRAPHICS & INFOGRAPHIC ENGINE
=============================================================================
Motor determinístico de motion design de alta retenção visual (HTML5 + GSAP + HyperFrames).
Gera ganchos cinéticos virais, infográficos biológicos/científicos e cards de conversão
para os Reels e Stories do Instagram @marcaopersonalfitness.

Zero custo de GPU • 1080x1920 Full HD • 30/60fps • Tipografia Nítida & Agressiva
=============================================================================
"""

import os
import sys
import json
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

import requests
import dotenv

logger = logging.getLogger("marcao_hyperframes")

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
dotenv.load_dotenv(ROOT_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


class MarcaoHyperFramesEngine:
    def __init__(self):
        self.output_dir = BASE_DIR / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.vendor_gsap = BASE_DIR / "vendor" / "gsap.min.js"

    def get_templates(self) -> Dict[str, Any]:
        """Catálogo de modelos de alta conversão para o ecossistema Marcão Personal."""
        return {
            "marcao_kinetic_hook": {
                "id": "marcao_kinetic_hook",
                "name": "⚡ Gancho Cinético de Alta Retenção (0 a 4s)",
                "category": "Hooks & Retenção",
                "default_duration": 3.8,
                "description": "Tipografia de alto impacto para os primeiros 3 a 4 segundos do Reel, quebrando a rolagem do feed.",
                "fields": [
                    {"id": "badge", "label": "Badge Superior", "default": "⚡ METODOLOGIA MARCÃO PERSONAL"},
                    {"id": "hero_text", "label": "Texto Principal (Caixa Alta)", "default": "VOCÊ TOMA CREATINA ERRADO?"},
                    {"id": "highlight_word", "label": "Palavra Chave Destaque", "default": "ERRADO?"},
                    {"id": "subtext", "label": "Subtítulo de Curiosidade", "default": "O ERRO QUE DESTRÓI SEUS GANHOS SEM VOCÊ PERCEBER"}
                ]
            },
            "marcao_balanca_bioimpedancia": {
                "id": "marcao_balanca_bioimpedancia",
                "name": "⚖️ Infográfico Balança Inteligente (13 Biomarcadores)",
                "category": "Produtos & Ciência",
                "default_duration": 4.5,
                "description": "Animação holográfica demonstrando o escaneamento de bioimpedância e os 13 biomarcadores.",
                "fields": [
                    {"id": "badge", "label": "Tag", "default": "📊 ESCANEAMENTO BIOIMPEDÂNCIA BIA"},
                    {"id": "main_title", "label": "Título da Métrica", "default": "13 BIOMARCADORES DE PRECISÃO"},
                    {"id": "biomarkers", "label": "Lista de Métricas", "default": "Gordura Visceral • Massa Muscular • Idade Metabólica • Água"},
                    {"id": "offer_price", "label": "Custo por Dia", "default": "APENAS R$ 0,09 POR DIA"},
                    {"id": "bonus_tag", "label": "Bônus Exclusivo", "default": "🎁 3 MESES DE MENTORIA VIP GRÁTIS"}
                ]
            },
            "marcao_creatina_science": {
                "id": "marcao_creatina_science",
                "name": "🧬 Infográfico Científico Creatina & ATP",
                "category": "Nutrição & Biohacking",
                "default_duration": 4.2,
                "description": "Ilustração biológica de síntese celular, ressíntese de fosfocreatina e saturação muscular.",
                "fields": [
                    {"id": "badge", "label": "Badge", "default": "🔬 CIÊNCIA APLICADA AO SHAPE"},
                    {"id": "title", "label": "Conceito Científico", "default": "RESSÍNTESE DE ATP CELULAR"},
                    {"id": "stat", "label": "Métrica de Ganho", "default": "+28% DE FORÇA REAL"},
                    {"id": "note", "label": "Nota Didática", "default": "Saturação Contínua: Não pare aos finais de semana!"}
                ]
            },
            "marcao_myth_buster": {
                "id": "marcao_myth_buster",
                "name": "📰 Manchete Editorial Vox: Destruindo Mitos",
                "category": "Mitos & Quebra de Objeções",
                "default_duration": 4.0,
                "description": "Estilo jornalístico com manchete serifada e marca-texto amarelo destruindo mitos populares.",
                "fields": [
                    {"id": "source", "label": "Fonte / Arquivo", "default": "REVISTA CIENTÍFICA MARCÃO • EDIÇÃO 2026"},
                    {"id": "headline", "label": "Mito a Ser Destruído", "default": "O PESO DA BALANÇA COMUM NÃO MEDE SEU RESULTADO"},
                    {"id": "highlight", "label": "Trecho Marcado", "default": "NÃO MEDE SEU RESULTADO"},
                    {"id": "tagline", "label": "Conclusão", "default": "Músculo é denso. Você perdeu gordura e ganhou massa!"}
                ]
            }
        }

    def render_template(self, template_id: str, params: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Renderiza um template específico via HyperFrames CLI."""
        templates = self.get_templates()
        if template_id not in templates:
            raise ValueError(f"Template '{template_id}' não encontrado.")

        import uuid
        job_id = f"marcao_{template_id}_{uuid.uuid4().hex[:8]}"
        project_dir = self.output_dir / f"proj_{job_id}"
        project_dir.mkdir(parents=True, exist_ok=True)

        if not output_path:
            output_path = str(self.output_dir / f"{job_id}.mp4")

        # Injeta GSAP local
        if self.vendor_gsap.exists():
            shutil.copy(self.vendor_gsap, project_dir / "gsap.min.js")

        tmpl = templates[template_id]
        dur = float(params.get("duration", tmpl.get("default_duration", 4.0)))
        w, h = 1080, 1920

        with open(project_dir / "hyperframes.json", "w", encoding="utf-8") as f:
            json.dump({
                "$schema": "https://hyperframes.heygen.com/hyperframes.schema.json",
                "fps": 30,
                "width": w,
                "height": h,
                "duration": dur
            }, f, indent=2)

        with open(project_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump({"name": tmpl["name"]}, f, indent=2)

        html_code = self._build_html(template_id, params, w, h, dur)
        with open(project_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html_code)

        self._execute_render(str(project_dir), output_path)
        return output_path

    def compose_with_ai(self, prompt: str, duration: float = 4.0, output_path: Optional[str] = None) -> str:
        """Usa Gemini para programar uma cena em código e renderiza em MP4."""
        import uuid
        job_id = f"marcao_ai_{uuid.uuid4().hex[:8]}"
        project_dir = self.output_dir / f"proj_{job_id}"
        project_dir.mkdir(parents=True, exist_ok=True)

        if not output_path:
            output_path = str(self.output_dir / f"{job_id}.mp4")

        if self.vendor_gsap.exists():
            shutil.copy(self.vendor_gsap, project_dir / "gsap.min.js")

        w, h = 1080, 1920
        with open(project_dir / "hyperframes.json", "w", encoding="utf-8") as f:
            json.dump({
                "$schema": "https://hyperframes.heygen.com/hyperframes.schema.json",
                "fps": 30,
                "width": w,
                "height": h,
                "duration": duration
            }, f, indent=2)

        with open(project_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump({"name": f"Marcão AI: {prompt[:30]}"}, f, indent=2)

        raw_html = self._generate_html_via_gemini(prompt, w, h, duration)
        html_code = self._sanitize_and_validate_html(raw_html, prompt, w, h, duration)
        with open(project_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html_code)

        self._execute_render(str(project_dir), output_path)
        return output_path

    def overlay_on_video(self, background_video: str, motion_video: str, output_path: str, position: str = "center", start_time: float = 0.0) -> str:
        """Sobrepõe o motion graphic em um vídeo com FFmpeg."""
        if not os.path.exists(background_video):
            raise FileNotFoundError(f"Vídeo de fundo não encontrado: {background_video}")
        if not os.path.exists(motion_video):
            raise FileNotFoundError(f"Vídeo motion não encontrado: {motion_video}")

        if position == "bottom":
            pos_filter = "(W-w)/2:H-h-140"
        elif position == "top":
            pos_filter = "(W-w)/2:140"
        else:
            pos_filter = "(W-w)/2:(H-h)/2"

        filter_complex = (
            f"[1:v]setpts=PTS-STARTPTS+{start_time}/TB[ovrl];"
            f"[0:v][ovrl]overlay={pos_filter}:enable='between(t,{start_time},{start_time}+12)'[v]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", background_video,
            "-i", motion_video,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-c:a", "copy",
            output_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg overlay error: {res.stderr}")
        return output_path

    def _execute_render(self, project_dir: str, output_path: str):
        npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
        cmd = [npx_cmd, "hyperframes", "render", "-o", output_path]
        logger.info(f"Renderizando HyperFrames: {' '.join(cmd)}")
        res = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"Erro no render HyperFrames: {res.stderr}")
            raise RuntimeError(f"Falha na renderização HyperFrames: {res.stderr or res.stdout}")

    def _build_html(self, template_id: str, params: Dict[str, Any], w: int, h: int, dur: float) -> str:
        if template_id == "marcao_kinetic_hook":
            badge = params.get("badge", "⚡ METODOLOGIA MARCÃO PERSONAL")
            hero_text = params.get("hero_text", "VOCÊ TOMA CREATINA ERRADO?")
            highlight = params.get("highlight_word", "ERRADO?")
            subtext = params.get("subtext", "O ERRO QUE DESTRÓI SEUS GANHOS SEM VOCÊ PERCEBER")

            if highlight and highlight in hero_text:
                formatted_hero = hero_text.replace(highlight, f'<br/><span class="hero-hl">{highlight}</span>')
            else:
                formatted_hero = f'{hero_text} <br/><span class="hero-hl">{highlight}</span>' if highlight else hero_text

            return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={w}, height={h}" />
  <script src="gsap.min.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{
      width: {w}px;
      height: {h}px;
      overflow: hidden;
      background: #060d1b;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    #root {{
      position: relative;
      width: {w}px;
      height: {h}px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 220px 60px;
      background: radial-gradient(circle at center, #0b1a30 0%, #030712 100%);
      color: #ffffff;
    }}
    .top-box {{ width: 100%; display: flex; justify-content: center; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 12px;
      padding: 16px 36px;
      background: rgba(0, 229, 255, 0.15);
      border: 2px solid #00e5ff;
      border-radius: 9999px;
      font-size: 26px;
      font-weight: 900;
      color: #00e5ff;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }}
    .center-box {{
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
    }}
    .hero-title {{
      font-size: 80px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: -0.02em;
      line-height: 1.12;
      max-width: 960px;
      color: #ffffff;
      text-shadow: 0 0 50px rgba(0, 0, 0, 0.8);
    }}
    .hero-hl {{
      display: inline-block;
      background: #facc15;
      color: #000000;
      padding: 6px 28px;
      border-radius: 8px;
      margin-top: 14px;
      text-shadow: none;
      box-shadow: 0 0 40px rgba(250, 204, 21, 0.4);
    }}
    .bottom-box {{ width: 100%; display: flex; justify-content: center; }}
    .subtext {{
      font-size: 32px;
      font-weight: 700;
      color: #94a3b8;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      max-width: 860px;
      line-height: 1.3;
    }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{w}" data-height="{h}">
    <div class="top-box">
      <div id="badge" class="clip badge" data-start="0" data-duration="{dur}">{badge}</div>
    </div>
    
    <div class="center-box">
      <div id="title" class="clip hero-title" data-start="0" data-duration="{dur}">
        {formatted_hero}
      </div>
    </div>

    <div class="bottom-box">
      <div id="sub" class="clip subtext" data-start="0" data-duration="{dur}">
        {subtext}
      </div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});

    tl.fromTo('#badge', {{ opacity: 0.7, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: 'back.out(2)' }}, 0);
    tl.fromTo('#title', {{ y: 40, opacity: 0.6, filter: 'blur(8px)' }}, {{ y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.45, ease: 'power4.out' }}, 0.15);
    tl.fromTo('#sub', {{ y: 25, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.45, ease: 'power2.out' }}, 0.6);
    tl.to('.hero-hl', {{ scale: 1.08, duration: 0.4, yoyo: true, repeat: 1, ease: 'sine.inOut' }}, 1.8);

    window.__timelines['main'] = tl;
    tl.seek(0);
  </script>
</body>
</html>"""

        elif template_id == "marcao_balanca_bioimpedancia":
            badge = params.get("badge", "📊 ESCANEAMENTO BIOIMPEDÂNCIA BIA")
            title = params.get("main_title", "13 BIOMARCADORES DE PRECISÃO")
            biomarkers = params.get("biomarkers", "Gordura Visceral • Massa Muscular • Idade Metabólica • Água")
            price = params.get("offer_price", "APENAS R$ 0,09 POR DIA")
            bonus = params.get("bonus_tag", "🎁 3 MESES DE MENTORIA VIP GRÁTIS")

            return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={w}, height={h}" />
  <script src="gsap.min.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{
      width: {w}px;
      height: {h}px;
      overflow: hidden;
      background: #030712;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    #root {{
      position: relative;
      width: {w}px;
      height: {h}px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 220px 60px;
      background: radial-gradient(ellipse at bottom, #0f2b48 0%, #030712 100%);
      color: #ffffff;
    }}
    .tag-box {{ width: 100%; display: flex; justify-content: center; }}
    .tag {{
      display: inline-block;
      padding: 14px 32px;
      background: rgba(0, 229, 255, 0.15);
      border: 2px solid #00e5ff;
      border-radius: 9999px;
      font-size: 26px;
      font-weight: 800;
      color: #00e5ff;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    .main-block {{
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 20px;
    }}
    .main-title {{
      font-size: 64px;
      font-weight: 900;
      color: #ffffff;
      text-transform: uppercase;
      letter-spacing: -0.01em;
      max-width: 900px;
      line-height: 1.15;
    }}
    .bio-list {{
      font-size: 32px;
      font-weight: 600;
      color: #38bdf8;
      max-width: 860px;
      line-height: 1.4;
      background: rgba(15, 23, 42, 0.7);
      padding: 16px 28px;
      border-radius: 16px;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }}
    .bottom-block {{
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
    }}
    .price-pill {{
      display: inline-block;
      padding: 12px 28px;
      background: rgba(34, 197, 94, 0.15);
      border: 2px solid #22c55e;
      border-radius: 12px;
      font-size: 30px;
      font-weight: 900;
      color: #22c55e;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .bonus-pill {{
      font-size: 32px;
      font-weight: 800;
      color: #facc15;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{w}" data-height="{h}">
    <div class="tag-box">
      <div id="tg" class="clip tag" data-start="0" data-duration="{dur}">{badge}</div>
    </div>

    <div class="main-block">
      <div id="mt" class="clip main-title" data-start="0" data-duration="{dur}">{title}</div>
      <div id="bl" class="clip bio-list" data-start="0" data-duration="{dur}">{biomarkers}</div>
    </div>

    <div class="bottom-block">
      <div id="pr" class="clip price-pill" data-start="0" data-duration="{dur}">{price}</div>
      <div id="bn" class="clip bonus-pill" data-start="0" data-duration="{dur}">{bonus}</div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});

    tl.fromTo('#tg', {{ opacity: 0.7, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: 'back.out(2)' }}, 0);
    tl.fromTo('#mt', {{ opacity: 0.6, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' }}, 0.15);
    tl.fromTo('#bl', {{ opacity: 0, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: 'power3.out' }}, 0.45);
    tl.fromTo('#pr', {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }}, 0.8);
    tl.fromTo('#bn', {{ opacity: 0, scale: 1.15 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.8)' }}, 1.1);

    window.__timelines['main'] = tl;
    tl.seek(0);
  </script>
</body>
</html>"""

        elif template_id == "marcao_creatina_science":
            badge = params.get("badge", "🔬 BIOHACKING & NUTRIÇÃO CIENTÍFICA")
            title = params.get("title", "RESSÍNTESE DE ATP CELULAR")
            stat = params.get("stat", "+28% DE FORÇA REAL")
            note = params.get("note", "Saturação Contínua: 5g Todo Santo Dia!")

            return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={w}, height={h}" />
  <script src="gsap.min.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{
      width: {w}px;
      height: {h}px;
      overflow: hidden;
      background: #021a15;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    #root {{
      position: relative;
      width: {w}px;
      height: {h}px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 220px 60px;
      background: radial-gradient(ellipse at center, #064e3b 0%, #021a15 100%);
      color: #ffffff;
    }}
    .tag-box {{ width: 100%; display: flex; justify-content: center; }}
    .tag {{
      display: inline-block;
      padding: 14px 34px;
      background: rgba(16, 185, 129, 0.15);
      border: 2px solid #10b981;
      border-radius: 9999px;
      font-size: 26px;
      font-weight: 800;
      color: #34d399;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .main-block {{
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 24px;
    }}
    .main-title {{
      font-size: 60px;
      font-weight: 900;
      color: #ffffff;
      text-transform: uppercase;
      letter-spacing: -0.01em;
      max-width: 920px;
      line-height: 1.15;
    }}
    .science-card {{
      background: rgba(6, 78, 59, 0.4);
      border: 1px solid rgba(52, 211, 153, 0.4);
      border-radius: 24px;
      padding: 30px 48px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      backdrop-filter: blur(10px);
    }}
    .stat-number {{
      font-size: 76px;
      font-weight: 900;
      color: #facc15;
      text-shadow: 0 0 25px rgba(250, 204, 21, 0.4);
      letter-spacing: -0.02em;
    }}
    .formula-tag {{
      font-size: 26px;
      font-weight: 700;
      color: #6ee7b7;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}
    .bottom-block {{
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .note-pill {{
      display: inline-block;
      padding: 16px 36px;
      background: rgba(2, 44, 34, 0.9);
      border: 2px solid #34d399;
      border-radius: 16px;
      font-size: 30px;
      font-weight: 800;
      color: #ffffff;
      text-align: center;
      max-width: 900px;
    }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{w}" data-height="{h}">
    <div class="tag-box">
      <div id="tg" class="clip tag" data-start="0" data-duration="{dur}">{badge}</div>
    </div>

    <div class="main-block">
      <div id="mt" class="clip main-title" data-start="0" data-duration="{dur}">{title}</div>
      <div id="sc" class="clip science-card" data-start="0" data-duration="{dur}">
        <div class="stat-number">{stat}</div>
        <div class="formula-tag">Fosfocreatina ➔ ADP + Pi ➔ ATP Celular</div>
      </div>
    </div>

    <div class="bottom-block">
      <div id="nt" class="clip note-pill" data-start="0" data-duration="{dur}">{note}</div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});

    tl.fromTo('#tg', {{ opacity: 0.7, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: 'back.out(2)' }}, 0);
    tl.fromTo('#mt', {{ opacity: 0.6, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' }}, 0.15);
    tl.fromTo('#sc', {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(1.6)' }}, 0.45);
    tl.fromTo('#nt', {{ opacity: 0, y: 25 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }}, 0.85);

    window.__timelines['main'] = tl;
    tl.seek(0);
  </script>
</body>
</html>"""

        elif template_id == "marcao_myth_buster":
            source = params.get("source", "REVISTA CIENTÍFICA MARCÃO • EDIÇÃO 2026")
            headline = params.get("headline", "O PESO DA BALANÇA COMUM NÃO MEDE SEU RESULTADO")
            highlight = params.get("highlight", "NÃO MEDE SEU RESULTADO")
            tagline = params.get("tagline", "Músculo é denso. Você perdeu gordura e ganhou massa!")

            if highlight and highlight in headline:
                formatted_hl = headline.replace(highlight, f'<mark class="vox-mark">{highlight}</mark>')
            else:
                formatted_hl = headline

            return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={w}, height={h}" />
  <script src="gsap.min.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{
      width: {w}px;
      height: {h}px;
      overflow: hidden;
      background: #f5f5f4;
      font-family: 'Georgia', serif;
    }}
    #root {{
      position: relative;
      width: {w}px;
      height: {h}px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 200px 80px;
      background: #fafaf9;
      border: 24px solid #1c1917;
      color: #1c1917;
    }}
    .hdr {{
      width: 100%;
      border-bottom: 4px double #1c1917;
      padding-bottom: 20px;
      text-align: center;
      font-size: 30px;
      font-weight: 900;
      font-family: sans-serif;
      letter-spacing: 0.15em;
      text-transform: uppercase;
    }}
    .hl-box {{ width: 100%; text-align: center; padding: 30px 0; }}
    .headline {{
      font-size: 68px;
      font-weight: 900;
      line-height: 1.18;
      text-transform: uppercase;
      letter-spacing: -0.01em;
    }}
    .vox-mark {{
      background: #fde047;
      color: #1c1917;
      padding: 2px 14px;
      display: inline-block;
      border-radius: 4px;
    }}
    .ftr {{
      width: 100%;
      border-top: 4px double #1c1917;
      padding-top: 24px;
      text-align: center;
      font-family: sans-serif;
      font-size: 30px;
      font-weight: 700;
      color: #44403c;
    }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{w}" data-height="{h}">
    <div id="hdr" class="clip hdr" data-start="0" data-duration="{dur}">{source}</div>
    <div class="hl-box">
      <h1 id="hl" class="clip headline" data-start="0" data-duration="{dur}">{formatted_hl}</h1>
    </div>
    <div id="ftr" class="clip ftr" data-start="0" data-duration="{dur}">{tagline}</div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});

    tl.fromTo('#hdr', {{ opacity: 0.7, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }}, 0);
    tl.fromTo('#hl', {{ opacity: 0.6, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: 'power4.out' }}, 0.2);
    tl.fromTo('.vox-mark', {{ opacity: 0.5 }}, {{ opacity: 1, duration: 0.4 }}, 0.7);
    tl.fromTo('#ftr', {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45 }}, 0.9);

    window.__timelines['main'] = tl;
    tl.seek(0);
  </script>
</body>
</html>"""

        else:
            raise ValueError(f"Template '{template_id}' não implementado.")

    def _generate_html_via_gemini(self, prompt: str, w: int, h: int, dur: float) -> str:
        """Gera composição HyperFrames para Marcão Personal com layout 3-Tier grandioso e zero sobreposição."""
        system_instruction = f"""
You are an ELITE Motion Designer and HyperFrames video developer creating ultra-high-retention 9:16 vertical motion graphics (1080x1920) for the Marcão Personal fitness & biohacking brand (@marcaopersonalfitness).

CRITICAL CANVAS & SCREEN UTILIZATION (ZERO DEAD SPACE, ZERO OVERLAPS):
1. Target dimensions: {w}px width by {h}px height. Duration: {dur}s at 30fps.
2. Link local GSAP in head: <script src="gsap.min.js"></script>
3. In #root: <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{w}" data-height="{h}">
   Styling for #root MUST BE:
   #root {{
     position: relative;
     width: {w}px;
     height: {h}px;
     display: flex;
     flex-direction: column;
     justify-content: space-between;
     align-items: center;
     padding: 180px 70px 160px 70px;
     box-sizing: border-box;
     overflow: hidden;
     background: #030712;
     color: #ffffff;
     font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
   }}

4. MANDATORY 3-TIER VERTICAL HIERARCHY:
   - TIER 1: TOP BADGE (~15% height)
     * Pill badge (e.g. `<div class="badge">⚡ METODOLOGIA MARCÃO</div>` or `🔬 CIÊNCIA & BIOLOGIA` or `🔥 HIPERTROFIA DE VERDADE`).
     * Styling: padding: 14px 38px; border-radius: 9999px; background: rgba(255,255,255,0.06); border: 2px solid rgba(255,255,255,0.18); font-size: 30px; font-weight: 800; letter-spacing: 0.15em; text-transform: uppercase; color: #38bdf8;

   - TIER 2: CENTER HERO CORE (~65% height - The Grandiose Focus)
     * Centered flex column filling the middle of the screen.
     * MEGA HERO TITLE: 96px to 116px; font-weight: 900; line-height: 1.08; text-transform: uppercase; color: #ffffff.
     * VIBRANT ACCENT HIGHLIGHT: Highlight punchy keyword in Electric Cyan `#38bdf8`, Canary Yellow `#facc15`, or Neon Emerald `#34d399` with glow (`text-shadow: 0 0 45px rgba(56, 189, 248, 0.45);`).
     * GLASSMORPHIC CONCEPT / DETAIL CARD:
       width: 100%; border-radius: 30px; background: rgba(15, 23, 42, 0.75); border: 2px solid rgba(255,255,255,0.12); backdrop-filter: blur(20px); padding: 45px 55px; box-sizing: border-box; font-size: 40px; line-height: 1.45; font-weight: 500; color: #e2e8f0; text-align: center;

   - TIER 3: BOTTOM ANCHOR (~20% height)
     * Institutional brand anchor: `<div class="footer-pill">@MARCAOPERSONALFITNESS</div>` + subtitle `<div class="sub-note">Metodologia Baseada em Evidências Científicas</div>`.
     * Styling: font-size: 28px - 32px; font-weight: 700; color: #64748b; letter-spacing: 0.1em; text-transform: uppercase;

5. STRICT ZERO-OVERLAP & SPACING RULES:
   - ALL text and content elements MUST be standard in-flow flexbox items.
   - NEVER use `position: absolute` for any text, title, card, or content container.
   - NEVER add `class="clip"` to child divs or text! ONLY `#root` is the HyperFrames root.
   - Use CSS flex gap, padding, and margins so elements NEVER touch, collide, or overlap.

6. GSAP TIMELINE & FRAME 0 RULE:
   - Frame 0 MUST have high contrast visible content (opacity >= 0.7 on all main text/titles).
   - Register the paused timeline on window.__timelines:
     window.__timelines = window.__timelines || {{}};
     const tl = gsap.timeline({{ paused: true }});
     tl.fromTo('.badge', {{ y: -30, opacity: 0.7, scale: 0.95 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.5, ease: 'power3.out' }}, 0);
     tl.fromTo('.hero-title', {{ y: 40, opacity: 0.7, scale: 0.96 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.2)' }}, 0.2);
     tl.fromTo('.concept-card', {{ y: 50, opacity: 0.7 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: 'power3.out' }}, 0.5);
     tl.fromTo('.bottom-tier', {{ y: 30, opacity: 0.5 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' }}, 0.8);
     window.__timelines["main"] = tl;
     tl.seek(0);

7. Return ONLY the clean, raw HTML string, starting with <!doctype html> and ending with </html>.
"""
        model = "gemini-flash-lite-latest"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"User request for Marcão Personal: {prompt}\nAuthor the complete valid HTML HyperFrames composition now."}]
            }],
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "maxOutputTokens": 8192,
                "temperature": 0.4
            }
        }

        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini error ({resp.status_code}): {resp.text}")

        html_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        if html_text.startswith("```"):
            lines = html_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            html_text = "\n".join(lines).strip()

        return html_text

    def _sanitize_and_validate_html(self, html_code: str, prompt: str, w: int, h: int, dur: float) -> str:
        """Garante conformidade 100% com o runtime do HyperFrames, evitando erros de sobreposição, duração zero ou timeline inexistente."""
        import re

        is_complete = html_code and ("</html>" in html_code.lower()) and (len(html_code) > 600)
        if not is_complete:
            logger.warning("AI gerou HTML incompleto. Acionando template nativo garantido.")
            return self._generate_template_html("marcao_kinetic_hook", {
                "badge": "⚡ METODOLOGIA MARCÃO PERSONAL",
                "hero_text": prompt.upper(),
                "highlight_word": prompt.split()[-1].upper() if prompt.split() else "FOCO",
                "subtext": "CIÊNCIA, HIPERTROFIA E ALTA PERFORMANCE"
            }, w, h, dur)

        # 1. Remover classe clip de elementos filhos para evitar sobreposição ou stacking
        html_code = re.sub(r'\bclip\b', '', html_code)

        # 2. Garantir script do GSAP no <head>
        if "gsap.min.js" not in html_code:
            html_code = re.sub(r'(<head[^>]*>)', r'\1\n  <script src="gsap.min.js"></script>', html_code, flags=re.IGNORECASE)

        # 3. Injetar CSS de coerência vertical e prevenção de sobreposição de texto
        guard_css = f"""
  <style id="hf-vertical-safety">
    html, body {{
      margin: 0 !important;
      padding: 0 !important;
      width: {w}px !important;
      height: {h}px !important;
      overflow: hidden !important;
      background: #030712 !important;
    }}
    #root {{
      position: relative !important;
      width: {w}px !important;
      height: {h}px !important;
      min-height: {h}px !important;
      display: flex !important;
      flex-direction: column !important;
      justify-content: space-between !important;
      align-items: center !important;
      padding: 180px 70px 160px 70px !important;
      box-sizing: border-box !important;
      overflow: hidden !important;
    }}
    /* Previne sobreposição acidental de tipografia e caixas */
    h1, h2, h3, h4, p, span, .badge, .title, .hero-title, .concept-card, .top-tier, .center-tier, .bottom-tier {{
      position: relative !important;
    }}
  </style>
"""
        if "</head>" in html_code:
            html_code = re.sub(r'(</head>)', guard_css + r'\1', html_code, count=1, flags=re.IGNORECASE)

        # 4. Garantir atributos data-composition-id="main" e data-duration no elemento raiz
        def fix_root(match):
            tag = match.group(0)
            if 'data-composition-id' not in tag:
                tag = tag.replace('id="root"', 'id="root" data-composition-id="main"')
            if 'data-duration' not in tag:
                tag = tag[:-1] + f' data-start="0" data-duration="{dur}" data-width="{w}" data-height="{h}">'
            return tag

        if 'id="root"' in html_code:
            html_code = re.sub(r'<div[^>]*id=["\']root["\'][^>]*>', fix_root, html_code, count=1)
        else:
            html_code = re.sub(
                r'(<body[^>]*>)',
                rf'\1\n<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{w}" data-height="{h}" style="position:relative;width:{w}px;height:{h}px;overflow:hidden;">',
                html_code,
                flags=re.IGNORECASE
            )
            html_code = re.sub(r'(</body>)', r'</div>\n\1', html_code, flags=re.IGNORECASE)

        # 5. Injetar guardião de timeline antes do fechamento do body
        safety_script = f"""
  <script>
    window.__timelines = window.__timelines || {{}};
    if (!window.__timelines["main"]) {{
      try {{
        if (typeof tl !== "undefined" && tl && typeof tl.seek === "function") {{
          window.__timelines["main"] = tl;
          tl.seek(0);
        }} else {{
          const _safeTl = gsap.timeline({{ paused: true }});
          _safeTl.to("#root", {{ opacity: 1, duration: {dur} }});
          window.__timelines["main"] = _safeTl;
          _safeTl.seek(0);
        }}
      }} catch (e) {{
        const _safeTl = gsap.timeline({{ paused: true }});
        _safeTl.to("#root", {{ opacity: 1, duration: {dur} }});
        window.__timelines["main"] = _safeTl;
        _safeTl.seek(0);
      }}
    }}
  </script>
"""
        html_code = re.sub(r'(</body>)', safety_script + r'\1', html_code, flags=re.IGNORECASE)
        return html_code
