"""
========================================================================================
CENTRO DE COMANDO — MARCÃO PERSONAL
MOTOR DE DESIGN DE ALTA CONVERSÃO (ADOBE CREATIVE ENGINE 2.0)
========================================================================================
Inspirado na engenharia reversa das suítes profissionais da Adobe (Illustrator / VectorCraft).
Compositor vetorial de alta definição para Instagram Feed (4:5 - 1080x1350) e Stories (9:16 - 1080x1920).
Inclui:
- Tipografia com pesos reais da Adobe (Montserrat Black / ExtraBold / SemiBold / Bebas Neue)
- Ícones vetoriais procedurais matemáticos (Raios, Estrelas, Checks, Setas) sem erros de unicode
- Selos circulares de autoridade com efeito metálico concêntrico
- Gradientes de atmosfera cinematográfica (Vignette e Mesh)
- Cartões glassmorphism com borda de luz e sombra projetada suave
- Botões de CTA 3D de alta conversão
========================================================================================
"""

import os
import re
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PUBLIC_IMG_DIR = os.path.join(BASE_DIR, "apps", "site", "public", "images")

# ======================================================================================
# PALETAS DE CORES DE ALTA CONVERSÃO (LUXO FITNESS & BIOHACKING)
# ======================================================================================
PALETTES = {
    "gold_dark": {
        "accent": (245, 158, 11),          # Dourado Solar (#F59E0B)
        "accent_bright": (253, 224, 71),   # Ouro Brilhante (#FDE047)
        "accent_deep": (180, 83, 9),       # Bronze/Ocre Escuro (#B45309)
        "text_primary": (255, 255, 255),   # Branco Puro
        "text_secondary": (203, 213, 225), # Platina Claro (#CBD5E1)
        "bg_dark": (10, 12, 16),           # Obsidiana (#0A0C10)
        "card_bg": (18, 22, 32, 215),      # Glassmorphism Escuro
        "card_border": (245, 158, 11, 90), # Borda Dourada Translúcida
        "cta_bg": (245, 158, 11),          # Botão Dourado Sólido
        "cta_text": (10, 12, 16),          # Preto Puro no Botão
    },
    "emerald_fit": {
        "accent": (16, 185, 129),          # Verde Esmeralda (#10B981)
        "accent_bright": (52, 211, 153),   # Verde Neon (#34D399)
        "accent_deep": (4, 120, 87),       # Verde Escuro (#047857)
        "text_primary": (255, 255, 255),
        "text_secondary": (203, 213, 225),
        "bg_dark": (8, 14, 12),
        "card_bg": (14, 26, 22, 215),
        "card_border": (16, 185, 129, 90),
        "cta_bg": (16, 185, 129),
        "cta_text": (6, 20, 14),
    },
    "molten_energy": {
        "accent": (249, 115, 22),          # Laranja Vulcânico (#F97316)
        "accent_bright": (253, 186, 116),  # Âmbar Brilhante (#FDBA74)
        "accent_deep": (194, 65, 12),      # Terracota Profundo (#C2410C)
        "text_primary": (255, 255, 255),
        "text_secondary": (203, 213, 225),
        "bg_dark": (14, 10, 10),
        "card_bg": (26, 16, 16, 215),
        "card_border": (249, 115, 22, 90),
        "cta_bg": (249, 115, 22),
        "cta_text": (18, 10, 10),
    }
}

# ======================================================================================
# CARREGAMENTO INTELIGENTE DE FONTES ESTÁTICAS PRO
# ======================================================================================
def get_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    """Busca fonte estática profissional com fallback seguro."""
    candidates = [
        os.path.join(FONTS_DIR, font_name),
        os.path.join(FONTS_DIR, f"{font_name}.ttf"),
        os.path.join("C:/Windows/Fonts", font_name),
        os.path.join("C:/Windows/Fonts", f"{font_name}.ttf"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    fallbacks = ["impact.ttf", "arialbd.ttf", "segoeuib.ttf", "arial.ttf"]
    for fb in fallbacks:
        fb_path = os.path.join("C:/Windows/Fonts", fb)
        if os.path.exists(fb_path):
            try:
                return ImageFont.truetype(fb_path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ======================================================================================
# DESENHO VETORIAL PROCEDURAL (ÍCONES MATEMÁTICOS DE PRECISÃO)
# ======================================================================================
def draw_vector_star(draw: ImageDraw.Draw, cx: float, cy: float, r_out: float, r_in: float, color: tuple):
    """Desenha estrela de 5 pontas matematicamente perfeita."""
    pts = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=color)

def draw_vector_checkmark(draw: ImageDraw.Draw, cx: float, cy: float, size: float, color: tuple, width: int = 4):
    """Desenha checkmark (✓) de alta precisão."""
    pts = [
        (cx - size * 0.45, cy),
        (cx - size * 0.12, cy + size * 0.40),
        (cx + size * 0.50, cy - size * 0.45)
    ]
    draw.line(pts, fill=color, width=width, joint="curve")

def draw_vector_lightning(draw: ImageDraw.Draw, cx: float, cy: float, size: float, color: tuple):
    """Desenha raio minimalista (⚡)."""
    s = size / 10.0
    pts = [
        (cx + 2 * s, cy - 8 * s),
        (cx - 5 * s, cy),
        (cx - 1 * s, cy),
        (cx - 4 * s, cy + 8 * s),
        (cx + 5 * s, cy - 1 * s),
        (cx + 1 * s, cy - 1 * s)
    ]
    draw.polygon(pts, fill=color)

def draw_vector_arrow(draw: ImageDraw.Draw, cx: float, cy: float, length: float, color: tuple, width: int = 3):
    """Desenha seta elegante para frente (→)."""
    x1 = cx - length / 2
    x2 = cx + length / 2
    draw.line([(x1, cy), (x2, cy)], fill=color, width=width)
    head_size = length * 0.4
    draw.line([(x2 - head_size, cy - head_size * 0.7), (x2, cy)], fill=color, width=width)
    draw.line([(x2 - head_size, cy + head_size * 0.7), (x2, cy)], fill=color, width=width)


# ======================================================================================
# CLASSE COMPOSITORA EM CAMADAS ADOBE (2.0)
# ======================================================================================
class AdobeLayeredCompositor:
    def __init__(self, width: int = 1080, height: int = 1350, theme: str = "gold_dark"):
        self.width = width
        self.height = height
        self.theme = PALETTES.get(theme, PALETTES["gold_dark"])
        self.canvas = Image.new("RGBA", (width, height), (10, 12, 16, 255))

    # ----------------------------------------------------------------------------------
    # 1. TRATAMENTO FOTOGRÁFICO DE FUNDO & GRADIENTE DE LEITURA
    # ----------------------------------------------------------------------------------
    def set_cinematic_background(self, bg_image_path: str = None, start_vignette: float = 0.40, end_vignette: float = 0.52):
        """Carrega e enquadra foto de estúdio, ou cria iluminação de estúdio luxuosa."""
        if bg_image_path and os.path.exists(bg_image_path):
            try:
                bg = Image.open(bg_image_path).convert("RGBA")
                bg_ratio = bg.width / bg.height
                canvas_ratio = self.width / self.height
                if bg_ratio > canvas_ratio:
                    new_h = self.height
                    new_w = int(new_h * bg_ratio)
                else:
                    new_w = self.width
                    new_h = int(new_w / bg_ratio)
                bg = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
                left = (new_w - self.width) // 2
                top = (new_h - self.height) // 2
                bg_cropped = bg.crop((left, top, left + self.width, top + self.height))
                self.canvas.paste(bg_cropped, (0, 0))
            except Exception as e:
                print(f"[ADOBE ENGINE] Aviso ao carregar BG {bg_image_path}: {e}")
                self._render_studio_lighting()
        else:
            self._render_studio_lighting()

        self._apply_cinema_vignette(start_norm=start_vignette, end_norm=end_vignette)

    def _render_studio_lighting(self):
        """Cria um fundo de iluminação de academia/estúdio com ponto de luz sutil."""
        arr = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        cx, cy = self.width // 2, int(self.height * 0.45)
        max_dist = math.sqrt(cx**2 + cy**2)

        # Gradiente radial sutil de iluminação
        y_indices, x_indices = np.indices((self.height, self.width))
        dist = np.sqrt((x_indices - cx)**2 + (y_indices - cy)**2)
        norm_dist = np.clip(dist / max_dist, 0, 1)

        accent = np.array(self.theme["accent_deep"], dtype=np.float32) * 0.4
        base_dark = np.array([10, 12, 16], dtype=np.float32)

        r = (base_dark[0] + (accent[0] * (1 - norm_dist)**2)).clip(0, 255)
        g = (base_dark[1] + (accent[1] * (1 - norm_dist)**2)).clip(0, 255)
        b = (base_dark[2] + (accent[2] * (1 - norm_dist)**2)).clip(0, 255)

        arr[:, :, 0] = r.astype(np.uint8)
        arr[:, :, 1] = g.astype(np.uint8)
        arr[:, :, 2] = b.astype(np.uint8)
        arr[:, :, 3] = 255

        self.canvas.paste(Image.fromarray(arr), (0, 0))

    def _apply_cinema_vignette(self, start_norm: float = 0.40, end_norm: float = 0.52):
        """
        LEI DA PROTEÇÃO FACIAL E DO PRODUTO (SAFE ZONES):
        - O terço superior (rosto, olhos, nariz, boca e expressão) recebe ZERO véu escuro (alpha = 0).
          Isso preserva 100% da nitidez, da iluminação dourada e da humanidade do personagem.
        - A transição suave de vinheta escura ocorre na altura do peito/meio do corpo (norm_y de start_norm a end_norm).
        - A metade inferior (norm_y >= end_norm) recebe a base escura sólida com alta opacidade para contraste
          cristalino de leitura de manchete, benefícios e CTA.
        """
        mask_arr = np.zeros((self.height, self.width), dtype=np.uint8)
        span = max(end_norm - start_norm, 0.01)
        for y in range(self.height):
            norm_y = y / self.height
            if norm_y < start_norm:
                # ZONA DE PROTEÇÃO FACIAL TOTAL (0% escurecimento nos olhos, nariz e boca)
                alpha = 0
            elif norm_y < end_norm:
                # Transição suave cinematográfica do peito para o card
                alpha = int(245 * ((norm_y - start_norm) / span))
            else:
                # Base de alta legibilidade para headline, cards e CTA
                alpha = 245
            mask_arr[y, :] = alpha

        dark_layer = Image.new("RGBA", (self.width, self.height), self.theme["bg_dark"] + (255,))
        self.canvas.paste(dark_layer, (0, 0), Image.fromarray(mask_arr))

    # ----------------------------------------------------------------------------------
    # 2. PÍLULA SUPERIOR DE CATEGORIA (GLASSMORPHISM + RAIO VETORIAL)
    # ----------------------------------------------------------------------------------
    def draw_category_badge(self, text: str, y: int = 55):
        """Pílula superior elegante com ícone de raio procedural."""
        draw = ImageDraw.Draw(self.canvas)
        font_pill = get_font("Montserrat-Bold.ttf", 20)
        clean_text = text.strip().upper()

        bbox = draw.textbbox((0, 0), clean_text, font=font_pill)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        icon_space = 28
        card_w = tw + icon_space * 2 + 50
        card_h = 46
        card_x = (self.width - card_w) // 2

        self._draw_box_shadow((card_x, y, card_x + card_w, y + card_h), radius=card_h // 2, blur=10, opacity=110)

        pill_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(pill_layer)
        pdraw.rounded_rectangle(
            [card_x, y, card_x + card_w, y + card_h],
            radius=card_h // 2,
            fill=(18, 24, 34, 230),
            outline=self.theme["accent"],
            width=2
        )
        self.canvas = Image.alpha_composite(self.canvas, pill_layer)

        draw = ImageDraw.Draw(self.canvas)
        draw_vector_lightning(draw, card_x + 24, y + card_h // 2, size=16, color=self.theme["accent_bright"])
        draw.text((card_x + 42, y + (card_h - th) // 2 - 2), clean_text, font=font_pill, fill=self.theme["accent_bright"])
        draw_vector_lightning(draw, card_x + card_w - 24, y + card_h // 2, size=16, color=self.theme["accent_bright"])

    # ----------------------------------------------------------------------------------
    # 3. SELO CIRCULAR DE AUTORIDADE METÁLICO (COM ESTRELAS PROCEDURAIS)
    # ----------------------------------------------------------------------------------
    def draw_authority_seal(self, center_xy: tuple, radius: int = 65, text_top: str = "100% PURO", text_sub: str = "LAUDO OFICIAL"):
        """Selo circular de garantia e pureza com estrelas vetoriais douradas."""
        cx, cy = center_xy
        self._draw_box_shadow((cx - radius, cy - radius, cx + radius, cy + radius), radius=radius, blur=16, opacity=170)

        seal_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(seal_layer)

        # Círculo base metálico
        sdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(16, 20, 28, 245), outline=self.theme["accent"], width=3)
        sdraw.ellipse([cx - radius + 6, cy - radius + 6, cx + radius - 6, cy + radius - 6], outline=self.theme["accent_bright"], width=1)
        sdraw.ellipse([cx - radius + 10, cy - radius + 10, cx + radius - 10, cy + radius - 10], outline=self.theme["accent_deep"], width=2)

        # 5 Estrelas douradas vetoriais no arco superior
        star_y = cy - radius + 22
        spacing = 13
        for idx, offset in enumerate([-2, -1, 0, 1, 2]):
            draw_vector_star(sdraw, cx + offset * spacing, star_y, r_out=5.5, r_in=2.5, color=self.theme["accent_bright"])

        # Texto Principal do Selo (Montserrat Black - auto-ajustável)
        size_main = 21 if len(text_top) <= 7 else (16 if len(text_top) <= 10 else 13)
        font_main = get_font("Montserrat-Black.ttf", size_main)
        bbox_m = sdraw.textbbox((0, 0), text_top, font=font_main)
        mw = bbox_m[2] - bbox_m[0]
        mh = bbox_m[3] - bbox_m[1]
        sdraw.text((cx - mw // 2, cy - (mh // 2) - 2), text_top, font=font_main, fill=self.theme["text_primary"])

        # Subtexto do Selo (Montserrat Bold)
        size_sub = 10 if len(text_sub) > 11 else 12
        font_sub = get_font("Montserrat-Bold.ttf", size_sub)
        bbox_s = sdraw.textbbox((0, 0), text_sub, font=font_sub)
        sw = bbox_s[2] - bbox_s[0]
        sdraw.text((cx - sw // 2, cy + 14), text_sub, font=font_sub, fill=self.theme["accent_bright"])

        self.canvas = Image.alpha_composite(self.canvas, seal_layer)

    # ----------------------------------------------------------------------------------
    # 4. HIERARQUIA TIPOGRÁFICA EDITORIAL (MONTSERRAT BLACK + EXTRABOLD)
    # ----------------------------------------------------------------------------------
    def draw_hero_headline(self, headline: str, subheadline: str = None, start_y: int = 150):
        """Diagrama título editorial com quebra inteligente, dupla tipografia e sombra."""
        draw = ImageDraw.Draw(self.canvas)
        palavras = headline.strip().split()

        # Definição de tamanho por contagem de palavras
        if len(palavras) <= 4:
            font_size = 52
        elif len(palavras) <= 8:
            font_size = 46
        else:
            font_size = 40

        font_extra = get_font("Montserrat-ExtraBold.ttf", font_size)
        font_black = get_font("Montserrat-Black.ttf", int(font_size * 1.05))

        # ZONA DE COLISÃO DO SELO: Se o título começar próximo do topo (< 210px),
        # restringimos a largura para 740px para NUNCA encostar no selo superior direito!
        max_largura = 740 if start_y < 210 else 940

        # Quebra inteligente com blindagem total mesmo se houver quebras manuais de linha (\n)
        raw_linhas = [l.strip().upper() for l in headline.split("\n") if l.strip()]
        linhas = []
        for raw_l in raw_linhas:
            bbox = draw.textbbox((0, 0), raw_l, font=font_extra)
            if (bbox[2] - bbox[0]) <= max_largura:
                linhas.append(raw_l)
            else:
                words_l = raw_l.split()
                cur_l = []
                for w in words_l:
                    cur_l.append(w)
                    test_str = " ".join(cur_l)
                    t_bbox = draw.textbbox((0, 0), test_str, font=font_extra)
                    if (t_bbox[2] - t_bbox[0]) > max_largura:
                        cur_l.pop()
                        if cur_l:
                            linhas.append(" ".join(cur_l))
                        cur_l = [w]
                if cur_l:
                    linhas.append(" ".join(cur_l))

        curr_y = start_y
        for i, lin in enumerate(linhas):
            # A última linha ganha o destaque em Ouro Solar e Montserrat Black
            is_accent = (i == len(linhas) - 1 and len(linhas) > 1) or (i == 0 and len(linhas) == 1)
            cor = self.theme["accent_bright"] if is_accent else self.theme["text_primary"]
            f = font_black if is_accent else font_extra

            bbox = draw.textbbox((0, 0), lin, font=f)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = (self.width - tw) // 2

            # Sombra Gaussiana pronunciada
            self._draw_text_shadow(lin, f, (tx, curr_y), blur=10, offset=(0, 5), color=(0, 0, 0, 230))
            draw = ImageDraw.Draw(self.canvas)
            draw.text((tx, curr_y), lin, font=f, fill=cor)
            curr_y += th + 18

        # Subtítulo Editorial (Montserrat SemiBold)
        if subheadline:
            curr_y += 10
            font_sub = get_font("Montserrat-SemiBold.ttf", 25)
            sub_text = subheadline.strip()
            bbox_sub = draw.textbbox((0, 0), sub_text, font=font_sub)
            stw = bbox_sub[2] - bbox_sub[0]
            sth = bbox_sub[3] - bbox_sub[1]

            if stw > self.width - 160:
                palavras_sub = sub_text.split()
                mid = len(palavras_sub) // 2
                l1 = " ".join(palavras_sub[:mid])
                l2 = " ".join(palavras_sub[mid:])
                for subl in [l1, l2]:
                    s_box = draw.textbbox((0, 0), subl, font=font_sub)
                    sw = s_box[2] - s_box[0]
                    sx = (self.width - sw) // 2
                    self._draw_text_shadow(subl, font_sub, (sx, curr_y), blur=5, offset=(0, 3), color=(0, 0, 0, 200))
                    draw = ImageDraw.Draw(self.canvas)
                    draw.text((sx, curr_y), subl, font=font_sub, fill=self.theme["text_secondary"])
                    curr_y += sth + 8
            else:
                sx = (self.width - stw) // 2
                self._draw_text_shadow(sub_text, font_sub, (sx, curr_y), blur=5, offset=(0, 3), color=(0, 0, 0, 200))
                draw = ImageDraw.Draw(self.canvas)
                draw.text((sx, curr_y), sub_text, font=font_sub, fill=self.theme["text_secondary"])
                curr_y += sth + 10

        return curr_y

    # ----------------------------------------------------------------------------------
    # 4.1 MOTOR DE REALCE INTELIGENTE DE TERMOS (KEYWORD & ENTITY HIGHLIGHTER)
    # ----------------------------------------------------------------------------------
    def parse_smart_tokens(self, text: str) -> list:
        """
        Analisa o texto do benefício e divide em tokens identificando palavras-chave,
        métricas numéricas, laudos, órgãos, termos fisiológicos e prefixos de ação
        para destacar com iluminação dourada (accent_bright).
        Suporta também sintaxe manual com asteriscos duplos: **termo destacado**.
        """
        tokens = []
        if "**" in text:
            parts = text.split("**")
            for i, p in enumerate(parts):
                if p:
                    tokens.append((p, i % 2 == 1))
            return tokens

        patterns = [
            r"(^[\dIVX]+\.\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+:)",
            r"(\b\d+%\b|\bR\$\s*[\d,.]+|\b\d+(?:\s*a\s*\d+)?\s*(?:min|minutos|doses|meses|anos|dias|ml|kg|g|mg|h)\b)",
            r"(\b(?:COX-2|óxido nítrico|corpos cavernosos|vasodilatação|ATP|síntese proteica|células satélites|sarcopenia|bioimpedância|gordura visceral|massa magra|peptídeos de colágeno|laudo oficial|sem remédios|sem taquicardia|dor tardia|DMIT|100% puro|hidratação intracelular|firmeza|rigidez máxima|vigor viril|bloqueada|paralisa o crescimento|laudo técnico|padrão ouro|zero remédios|sobrecarga química)\b)"
        ]
        master_regex = re.compile("|".join(patterns), re.IGNORECASE)

        last_idx = 0
        for m in master_regex.finditer(text):
            start, end = m.span()
            if start > last_idx:
                tokens.append((text[last_idx:start], False))
            tokens.append((text[start:end], True))
            last_idx = end
        if last_idx < len(text):
            tokens.append((text[last_idx:], False))

        return tokens

    def wrap_rich_tokens(self, tokens: list, font_normal, font_bold, max_w: int) -> list:
        """Quebra tokens estilizados em linhas equilibradas sem ultrapassar a largura útil."""
        dummy_draw = ImageDraw.Draw(self.canvas)
        lines = []
        current_line = []
        current_w = 0

        word_tokens = []
        for text, is_hl in tokens:
            parts = text.split(" ")
            for i, p in enumerate(parts):
                if i > 0:
                    word_tokens.append((" ", is_hl))
                if p:
                    word_tokens.append((p, is_hl))

        for word, is_hl in word_tokens:
            f = font_bold if is_hl else font_normal
            bbox = dummy_draw.textbbox((0, 0), word, font=f)
            ww = bbox[2] - bbox[0]
            if current_w + ww > max_w and current_line:
                lines.append(current_line)
                current_line = []
                current_w = 0
                if word == " ":
                    continue
            current_line.append((word, is_hl))
            current_w += ww

        if current_line:
            lines.append(current_line)
        return lines

    def draw_rich_line(self, line_tokens: list, x: int, y: int, font_normal, font_bold):
        """Desenha uma linha com múltiplos tokens estilizados e sombras suaves."""
        curr_x = x
        draw = ImageDraw.Draw(self.canvas)
        for word, is_hl in line_tokens:
            f = font_bold if is_hl else font_normal
            color = self.theme["accent_bright"] if is_hl else self.theme["text_primary"]
            self._draw_text_shadow(word, f, (curr_x, y), blur=5, offset=(0, 2), color=(0, 0, 0, 210))
            draw = ImageDraw.Draw(self.canvas)
            draw.text((curr_x, y), word, font=f, fill=color)
            bbox = draw.textbbox((0, 0), word, font=f)
            curr_x += (bbox[2] - bbox[0])

    # ----------------------------------------------------------------------------------
    # 5. CARTÕES DE BENEFÍCIOS INTELIGENTES (SMART VERTICAL FLEXBOX + GLASSMORPHISM)
    # ----------------------------------------------------------------------------------
    def draw_benefit_cards(
        self,
        points: list = None,
        start_y: int = 150,
        card_w: int = None,
        card_x: int = 80,
        available_height: int = None,
        max_points: int = 4,
        pontos: list = None
    ) -> int:
        """
        Cartões em vidro fosco inteligentes:
        - Distribuição proporcional adaptativa para preencher todo o espaço útil do post sem vazios
        - Altura generosa e fontes confortáveis de leitura editorial no mobile
        - Realce de palavras-chave, laudos e termos médicos em Ouro Solar
        """
        if points is None:
            points = pontos or []

        pts = points[:max_points]
        if not pts:
            return start_y

        if card_w is None:
            card_w = self.width - (card_x * 2)

        # Ajuste adaptativo de fontes conforme a largura do card
        is_wide = card_w >= 700
        f_size = 25 if is_wide else 23
        line_step = 36 if is_wide else 32
        font_normal = get_font("Montserrat-SemiBold.ttf", f_size)
        font_bold = get_font("Montserrat-Black.ttf", f_size)

        max_inner_w = card_w - 95
        cards_data = []

        # 1. Medir linhas e tokens de cada card
        for pt in pts:
            texto_pt = pt.strip()
            tokens = self.parse_smart_tokens(texto_pt)
            lines = self.wrap_rich_tokens(tokens, font_normal, font_bold, max_inner_w)
            cards_data.append((lines, len(lines)))

        num_cards = len(cards_data)
        num_gaps = max(1, num_cards - 1)

        # 2. Calcular altura dinâmica para preencher com elegância o espaço disponível
        if available_height and available_height > 250:
            target_gap = 36 if is_wide else 30
            total_gaps_h = num_gaps * target_gap
            usable_for_cards = available_height - total_gaps_h
            base_card_h = max(120, min(175, usable_for_cards // num_cards))
            gap = target_gap
        else:
            base_card_h = 130 if is_wide else 115
            gap = 26

        curr_y = start_y
        for lines, num_lines in cards_data:
            text_total_h = num_lines * line_step
            card_h = max(base_card_h, text_total_h + 46)

            # Sombra Gaussiana da caixa
            self._draw_box_shadow((card_x, curr_y, card_x + card_w, curr_y + card_h), radius=18, blur=16, opacity=130)

            # Placa de Vidro
            card_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            cdraw = ImageDraw.Draw(card_layer)
            cdraw.rounded_rectangle(
                [card_x, curr_y, card_x + card_w, curr_y + card_h],
                radius=18,
                fill=self.theme["card_bg"],
                outline=self.theme["card_border"],
                width=1
            )
            self.canvas = Image.alpha_composite(self.canvas, card_layer)

            # Círculo com Checkmark Vetorial
            draw = ImageDraw.Draw(self.canvas)
            circle_r = 19
            circle_cx = card_x + 42
            circle_cy = curr_y + card_h // 2
            draw.ellipse(
                [circle_cx - circle_r, circle_cy - circle_r, circle_cx + circle_r, circle_cy + circle_r],
                fill=self.theme["accent"],
                outline=self.theme["accent_bright"],
                width=1
            )
            draw_vector_checkmark(draw, circle_cx, circle_cy, size=21, color=(10, 12, 16), width=3)

            # Texto do benefício com palavras-chave destacadas
            tx = card_x + 78
            start_text_y = curr_y + (card_h - text_total_h) // 2 - 2

            for i, line_tokens in enumerate(lines):
                ly = start_text_y + (i * line_step)
                self.draw_rich_line(line_tokens, tx, ly, font_normal, font_bold)

            curr_y += card_h + gap

        return curr_y

        return curr_y

    # ----------------------------------------------------------------------------------
    # 5.1 RECORTE HERO DO PRODUTO (SOMBRA DE CHÃO + GLOW AURA + ALTA NITIDEZ)
    # ----------------------------------------------------------------------------------
    def draw_hero_product(self, product_img_path: str, center_xy: tuple, max_size: tuple = (340, 340), glow: bool = True, ground_shadow: bool = True):
        """Renderiza recorte hero do produto com sombra de contato e aura luminosa de luxo."""
        if not product_img_path or not os.path.exists(product_img_path):
            return

        try:
            cx, cy = center_xy
            mw, mh = max_size
            p_img = Image.open(product_img_path)

            if p_img.mode != "RGBA":
                p_img = p_img.convert("RGBA")
                mask = Image.new("L", p_img.size, 0)
                ImageDraw.Draw(mask).rounded_rectangle([0, 0, p_img.width, p_img.height], radius=24, fill=255)
                p_img.putalpha(mask)

            p_img.thumbnail((mw, mh), Image.Resampling.LANCZOS)
            pw, ph = p_img.size
            pos_x = int(cx - pw / 2)
            pos_y = int(cy - ph / 2)

            # 1. Aura luminosa / Glow suave atrás do produto
            if glow:
                glow_r = max(pw, ph) // 2 + 50
                glow_img = Image.new("RGBA", (glow_r * 2, glow_r * 2), (0, 0, 0, 0))
                gdraw = ImageDraw.Draw(glow_img)
                accent = self.theme["accent"]
                for r in range(glow_r, 0, -10):
                    alpha = int(55 * (1 - r / glow_r)**1.5)
                    gdraw.ellipse([glow_r - r, glow_r - r, glow_r + r, glow_r + r], fill=accent + (alpha,))
                glow_blurred = glow_img.filter(ImageFilter.GaussianBlur(25))
                self.canvas.paste(glow_blurred, (cx - glow_r, cy - glow_r), glow_blurred)

            # 2. Sombra de chão / Ground Shadow elíptica
            if ground_shadow:
                sw = int(pw * 1.1)
                sh = int(ph * 0.22)
                shadow_img = Image.new("RGBA", (sw + 60, sh + 60), (0, 0, 0, 0))
                sdraw = ImageDraw.Draw(shadow_img)
                sdraw.ellipse([30, 30, 30 + sw, 30 + sh], fill=(0, 0, 0, 210))
                shadow_blurred = shadow_img.filter(ImageFilter.GaussianBlur(16))
                self.canvas.paste(shadow_blurred, (int(cx - (sw + 60) / 2), pos_y + ph - int(sh * 0.6)), shadow_blurred)

            # 3. Produto Hero recortado com nitidez máxima
            self.canvas.paste(p_img, (pos_x, pos_y), p_img)
        except Exception as e:
            print(f"[ADOBE ENGINE] Aviso ao desenhar produto hero: {e}")

    # ----------------------------------------------------------------------------------
    # 6. BOTÃO CTA 3D DE ALTA CONVERSÃO (MONTSERRAT BLACK + SETA VETORIAL)
    # ----------------------------------------------------------------------------------
    def draw_cta_button_3d(self, cta_text: str = "GARANTA O SEU NO SITE OFICIAL", y: int = 1130):
        """Botão tridimensional com reflexo luminoso e contraste agressivo para cliques."""
        draw = ImageDraw.Draw(self.canvas)
        font_cta = get_font("Montserrat-Black.ttf", 25)
        clean_cta = cta_text.replace("→", "").strip().upper()

        bbox = draw.textbbox((0, 0), clean_cta, font=font_cta)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        arrow_space = 40
        btn_w = max(tw + arrow_space + 80, 620)
        btn_h = 74
        btn_x = (self.width - btn_w) // 2

        # Sombra profunda do botão
        self._draw_box_shadow((btn_x, y, btn_x + btn_w, y + btn_h), radius=btn_h // 2, blur=24, opacity=190, offset=(0, 10))

        btn_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(btn_layer)

        # Chanfro 3D inferior
        bdraw.rounded_rectangle(
            [btn_x, y + 4, btn_x + btn_w, y + btn_h + 4],
            radius=btn_h // 2,
            fill=self.theme["accent_deep"]
        )

        # Corpo dourado brilhante com borda refinada
        bdraw.rounded_rectangle(
            [btn_x, y, btn_x + btn_w, y + btn_h],
            radius=btn_h // 2,
            fill=self.theme["cta_bg"],
            outline=self.theme["accent_bright"],
            width=2
        )

        self.canvas = Image.alpha_composite(self.canvas, btn_layer)

        # Texto e Seta em Preto Puro
        draw = ImageDraw.Draw(self.canvas)
        total_content_w = tw + arrow_space
        start_content_x = btn_x + (btn_w - total_content_w) // 2
        ty = y + (btn_h - th) // 2 - 2

        draw.text((start_content_x, ty), clean_cta, font=font_cta, fill=self.theme["cta_text"])
        draw_vector_arrow(draw, start_content_x + tw + 22, y + btn_h // 2, length=24, color=self.theme["cta_text"], width=3)

    # ----------------------------------------------------------------------------------
    # 7. ASSINATURA DA MARCA MARCÃO PERSONAL (RODAPÉ OFICIAL)
    # ----------------------------------------------------------------------------------
    def draw_brand_footer(self, y: int = 1255):
        """Rodapé oficial da marca Marcão Personal com selo de verificado."""
        draw = ImageDraw.Draw(self.canvas)
        font_brand = get_font("Montserrat-ExtraBold.ttf", 20)
        font_site = get_font("Montserrat-SemiBold.ttf", 18)

        brand_text = "MARCÃO PERSONAL  •  OFICIAL"
        site_text = "marcaopersonal.com"

        bbox1 = draw.textbbox((0, 0), brand_text, font=font_brand)
        w1 = bbox1[2] - bbox1[0]
        x1 = (self.width - w1) // 2

        bbox2 = draw.textbbox((0, 0), site_text, font=font_site)
        w2 = bbox2[2] - bbox2[0]
        x2 = (self.width - w2) // 2

        draw.text((x1, y), brand_text, font=font_brand, fill=self.theme["accent_bright"])
        draw.text((x2, y + 28), site_text, font=font_site, fill=self.theme["text_secondary"])

    # ----------------------------------------------------------------------------------
    # 8. COMPONENTES EXCLUSIVOS DE CARROSSEL EDITORIAL (INÍCIO, MEIO E FIM)
    # ----------------------------------------------------------------------------------
    def draw_carousel_header(self, category: str, num_slide: int, total_slides: int, preco: str = None, y: int = 45):
        """Cabeçalho editorial ultra-refinado com proteção total de colisão e largura dinâmica."""
        draw = ImageDraw.Draw(self.canvas)
        font_pill = get_font("Montserrat-Bold.ttf", 18)
        font_counter = get_font("Montserrat-ExtraBold.ttf", 19)

        # 1. Definir rótulo de etapa narrativa limpa
        if num_slide == 1:
            step_label = "INÍCIO • O PROBLEMA"
        elif num_slide == total_slides:
            step_label = "SOLUÇÃO DEFINITIVA"
        else:
            step_label = f"PASSO 0{num_slide} • MECANISMO"

        # Limpar duplicidades caso a categoria já contenha passo ou divisor
        clean_cat = category.strip() if category else ""
        clean_cat = re.sub(r'\s*\|\s*(PASSO\s*\d+|INÍCIO|FIM|SOLUÇÃO).*$', '', clean_cat, flags=re.IGNORECASE).strip()

        # 2. Medir Pílula da Direita (Contador ou Preço)
        if preco and num_slide == total_slides:
            tag_right = f"LOTE: {preco.upper()}"
            color_right = (0, 229, 255)
        else:
            tag_right = f"0{num_slide} / 0{total_slides}"
            color_right = self.theme["accent_bright"]

        bbox_r = draw.textbbox((0, 0), tag_right, font=font_counter)
        rw = bbox_r[2] - bbox_r[0]
        rh = bbox_r[3] - bbox_r[1]
        card_h = 44
        bx_w = rw + 36
        bx_x = self.width - 60 - bx_w

        # 3. Medir Pílula da Esquerda (Garantir gap mínimo de 40px para a direita)
        max_left_w = bx_x - 60 - 40
        cat_full = f"{clean_cat.upper()}  |  {step_label}" if clean_cat else step_label
        bbox_l = draw.textbbox((0, 0), cat_full, font=font_pill)
        lw = bbox_l[2] - bbox_l[0]

        # Se ultrapassar, simplificar
        if (lw + 48) > max_left_w:
            cat_full = f"{clean_cat.upper()}  •  0{num_slide}" if clean_cat else step_label
            bbox_l = draw.textbbox((0, 0), cat_full, font=font_pill)
            lw = bbox_l[2] - bbox_l[0]
            if (lw + 48) > max_left_w:
                cat_full = clean_cat[:18].upper() + "..."
                bbox_l = draw.textbbox((0, 0), cat_full, font=font_pill)
                lw = bbox_l[2] - bbox_l[0]

        lh = bbox_l[3] - bbox_l[1]
        left_w = min(max_left_w, lw + 48)
        left_x = 60

        # Desenhar pílula esquerda
        self._draw_box_shadow((left_x, y, left_x + left_w, y + card_h), radius=card_h // 2, blur=8, opacity=110)
        p_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(p_layer)
        pdraw.rounded_rectangle([left_x, y, left_x + left_w, y + card_h], radius=card_h // 2, fill=(18, 24, 34, 230), outline=self.theme["accent"], width=2)
        self.canvas = Image.alpha_composite(self.canvas, p_layer)

        draw = ImageDraw.Draw(self.canvas)
        draw_vector_lightning(draw, left_x + 18, y + card_h // 2, size=14, color=self.theme["accent_bright"])
        draw.text((left_x + 32, y + (card_h - lh) // 2 - 2), cat_full, font=font_pill, fill=self.theme["accent_bright"])

        # Desenhar pílula direita
        self._draw_box_shadow((bx_x, y, bx_x + bx_w, y + card_h), radius=card_h // 2, blur=8, opacity=110)
        r_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        rdraw = ImageDraw.Draw(r_layer)
        rdraw.rounded_rectangle([bx_x, y, bx_x + bx_w, y + card_h], radius=card_h // 2, fill=(18, 24, 34, 230), outline=color_right, width=2)
        self.canvas = Image.alpha_composite(self.canvas, r_layer)

        draw = ImageDraw.Draw(self.canvas)
        draw.text((bx_x + 18, y + (card_h - rh) // 2 - 2), tag_right, font=font_counter, fill=color_right)

    def draw_highlight_callout(self, title: str, text: str, y: int = 960, height: int = 155, width: int = 940, x: int = 70):
        """Card de destaque científico/dica de ouro para preencher 100% da área útil sem vazios."""
        self._draw_box_shadow((x, y, x + width, y + height), radius=18, blur=18, opacity=140)

        layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(layer)
        ldraw.rounded_rectangle([x, y, x + width, y + height], radius=18, fill=(24, 20, 14, 235), outline=self.theme["accent"], width=2)
        self.canvas = Image.alpha_composite(self.canvas, layer)

        draw = ImageDraw.Draw(self.canvas)
        draw_vector_lightning(draw, x + 35, y + 36, size=18, color=self.theme["accent_bright"])

        f_title = get_font("Montserrat-Black.ttf", 20)
        draw.text((x + 55, y + 25), title.upper(), font=f_title, fill=self.theme["accent_bright"])

        f_body = get_font("Montserrat-SemiBold.ttf", 22)
        palavras = text.strip().split()
        linhas = []
        cur_l = []
        max_w = width - 70
        for w in palavras:
            cur_l.append(w)
            bbox = draw.textbbox((0, 0), " ".join(cur_l), font=f_body)
            if (bbox[2] - bbox[0]) > max_w:
                cur_l.pop()
                if cur_l:
                    linhas.append(" ".join(cur_l))
                cur_l = [w]
        if cur_l:
            linhas.append(" ".join(cur_l))

        ty = y + 62
        for lin in linhas[:3]:
            draw.text((x + 35, ty), lin, font=f_body, fill=self.theme["text_primary"])
            ty += 30

    def draw_trust_badges(self, y: int = 970, width: int = 960, x: int = 60, height: int = 90):
        """Barra de 3 selos de garantia e conversão para o slide de produto (zero espaço ocioso)."""
        self._draw_box_shadow((x, y, x + width, y + height), radius=16, blur=14, opacity=120)

        layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(layer)
        ldraw.rounded_rectangle([x, y, x + width, y + height], radius=16, fill=(16, 20, 28, 225), outline=self.theme["accent_deep"], width=1)
        self.canvas = Image.alpha_composite(self.canvas, layer)

        badges = [
            ("LAUDO OFICIAL", "100% Puro & Aprovado", "check"),
            ("ENVIO IMEDIATO", "Correios para todo Brasil", "lightning"),
            ("COMPRA SEGURA", "Garantia Marcão Personal", "star")
        ]

        col_w = width // 3
        draw = ImageDraw.Draw(self.canvas)
        f_top = get_font("Montserrat-Black.ttf", 18)
        f_sub = get_font("Montserrat-Bold.ttf", 15)

        for i, (btop, bsub, icon) in enumerate(badges):
            bx = x + (i * col_w)
            cx = bx + col_w // 2

            if i > 0:
                draw.line([(bx, y + 16), (bx, y + height - 16)], fill=(245, 158, 11, 70), width=1)

            icx = bx + 36
            icy = y + height // 2
            if icon == "check":
                draw_vector_checkmark(draw, icx, icy, size=18, color=self.theme["accent_bright"], width=3)
            elif icon == "lightning":
                draw_vector_lightning(draw, icx, icy, size=16, color=self.theme["accent_bright"])
            else:
                draw_vector_star(draw, icx, icy, r_out=9, r_in=4.5, color=self.theme["accent_bright"])

            tx = icx + 22
            draw.text((tx, y + 22), btop, font=f_top, fill=self.theme["text_primary"])
            draw.text((tx, y + 48), bsub, font=f_sub, fill=self.theme["accent_bright"])

    def draw_carousel_indicator(self, cta_text: str = "ARRASTE PARA O LADO", y: int = 1240):
        """Indicador sutil e sofisticado de arrastar carrossel com linha de respiro."""
        draw = ImageDraw.Draw(self.canvas)
        font_ind = get_font("Montserrat-ExtraBold.ttf", 20)
        clean_text = cta_text.replace("››", "").replace(">", "").strip().upper()
        if not clean_text or clean_text == "ARRASTE":
            clean_text = "ARRASTE PARA O LADO"

        # Linha divisória de respiro acima do footer
        draw.line([(60, y - 25), (self.width - 60, y - 25)], fill=(35, 48, 70, 160), width=1)

        # Assinatura à esquerda
        font_brand = get_font("Montserrat-Bold.ttf", 18)
        brand_str = "@MARCAOPERSONALFITNESS"
        draw.text((60, y + 4), brand_str, font=font_brand, fill=self.theme["text_secondary"])

        # Pílula de Arraste à direita com seta vetorial
        bbox = draw.textbbox((0, 0), clean_text, font=font_ind)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        pill_w = tw + 70
        pill_h = 44
        pill_x = self.width - 60 - pill_w
        pill_y = y - 6

        self._draw_box_shadow((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h), radius=pill_h // 2, blur=10, opacity=120)
        p_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(p_layer)
        pdraw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=pill_h // 2, fill=(245, 158, 11, 230), outline=(253, 224, 71), width=2)
        self.canvas = Image.alpha_composite(self.canvas, p_layer)

        draw = ImageDraw.Draw(self.canvas)
        draw.text((pill_x + 22, pill_y + (pill_h - th) // 2 - 2), clean_text, font=font_ind, fill=(10, 12, 16))
        draw_vector_arrow(draw, pill_x + 22 + tw + 18, pill_y + pill_h // 2, length=18, color=(10, 12, 16), width=3)


    # ----------------------------------------------------------------------------------
    # UTILITÁRIOS INTERNOS DE SOMBRA E BLUR
    # ----------------------------------------------------------------------------------
    def _draw_box_shadow(self, box: tuple, radius: int = 16, blur: int = 14, opacity: int = 140, offset: tuple = (0, 6)):
        """Desenha sombra projetada Gaussiana hiper-realista atrás de qualquer caixa."""
        x1, y1, x2, y2 = box
        ox, oy = offset
        pad = blur * 3
        sw = (x2 - x1) + pad * 2
        sh = (y2 - y1) + pad * 2

        s_img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_img)
        s_draw.rounded_rectangle([pad, pad, pad + (x2 - x1), pad + (y2 - y1)], radius=radius, fill=(0, 0, 0, opacity))
        s_blurred = s_img.filter(ImageFilter.GaussianBlur(blur))

        paste_x = x1 - pad + ox
        paste_y = y1 - pad + oy
        self.canvas.paste(s_blurred, (paste_x, paste_y), s_blurred)

    def _draw_text_shadow(self, text: str, font, xy: tuple, blur: int = 6, offset: tuple = (0, 3), color: tuple = (0, 0, 0, 200)):
        """Aplica sombra Gaussiana suave atrás de textos de impacto."""
        tx, ty = xy
        ox, oy = offset
        draw = ImageDraw.Draw(self.canvas)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        pad = blur * 3
        s_img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_img)
        s_draw.text((pad, pad), text, font=font, fill=color)
        s_blurred = s_img.filter(ImageFilter.GaussianBlur(blur))

        paste_x = tx - pad + ox
        paste_y = ty - pad + oy
        self.canvas.paste(s_blurred, (paste_x, paste_y), s_blurred)

    def save(self, output_path: str):
        """Salva a composição final em formato PNG de altíssima definição."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        final_rgb = self.canvas.convert("RGB")
        final_rgb.save(output_path, "PNG", quality=98)
        print(f"[ADOBE CREATIVE ENGINE 2.0] Arte de alta conversão salva em: {output_path}")
        return output_path


# ======================================================================================
# FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO
# ======================================================================================
def renderizar_criativo_masterpiece(
    headline: str,
    subheadline: str = None,
    pontos_beneficio: list = None,
    categoria: str = "ALTA PERFORMANCE & BIOHACKING",
    cta_texto: str = "GARANTA COM DESCONTO NA BIO",
    bg_path: str = None,
    produto_img_path: str = None,
    preco: str = None,
    nome_autor: str = "EVANDRO GALLINA",
    out_path: str = None,
    formato: str = "feed",
    estilo_cor: str = "gold_dark"
) -> str:
    """
    Renderiza Feed (4:5 - 1080x1350) ou Story (9:16 - 1080x1920) com estética de agência,
    suportando recorte do produto hero com glow âmbar/ouro, selo de laudo/preço e botões 3D.
    """
    if formato == "story":
        width, height = 1080, 1920
        # LEI DA PROTEÇÃO FACIAL E DO PRODUTO:
        # Topo livre (0 a 1050px) para o rosto, olhos, sorriso e ação atlética do personagem!
        start_headline = 1080
        start_benefits = 1260
        y_cta = 1690
        y_footer = 1815
        seal_x = width - 95
        seal_y = 110
    else: # feed 4:5 (1080x1350)
        width, height = 1080, 1350
        # LEI DA PROTEÇÃO FACIAL E DO PRODUTO:
        # Topo livre (0 a 680px) para o rosto, olhos, nariz, boca e tronco!
        start_headline = 690
        start_benefits = 845
        y_cta = 1170
        y_footer = 1275
        seal_x = width - 95
        seal_y = 85

    if not out_path:
        out_path = os.path.join(PUBLIC_IMG_DIR, f"masterpiece_{formato}_{int(os.getpid())}.png")

    compositor = AdobeLayeredCompositor(width, height, theme=estilo_cor)

    # 1. Fundo & Atmosfera Cinematográfica
    compositor.set_cinematic_background(bg_path)

    # 2. Pílula Superior de Categoria
    tag_cat = categoria if categoria else f"{nome_autor.upper()}  •  MARCÃO PERSONAL"
    compositor.draw_category_badge(tag_cat, y=70 if formato == "story" else 50)

    # 3. Selo Circular de Autoridade com Estrelas Vetoriais
    seal_top = preco if preco else "100% PURO"
    seal_sub = "LOTE OFICIAL" if preco else "LAUDO OFICIAL"
    compositor.draw_authority_seal((seal_x, seal_y), radius=55, text_top=seal_top, text_sub=seal_sub)

    # 4. Manchete de Duplo Peso com Drop Shadow
    y_after_headline = compositor.draw_hero_headline(headline, subheadline, start_y=start_headline)

    # 5. Lista de Benefícios e/ou Produto Hero Mockup com Distribuição Inteligente
    tem_produto = produto_img_path and os.path.exists(produto_img_path)
    if pontos_beneficio:
        actual_benefits_y = max(start_benefits, y_after_headline + 30)
        actual_avail_h = max(220, y_cta - actual_benefits_y - 20)
        if tem_produto:
            card_w = 580
            card_x = 60
            compositor.draw_benefit_cards(pontos_beneficio, start_y=actual_benefits_y, card_w=card_w, card_x=card_x, available_height=actual_avail_h, max_points=3)
            
            # Produto Hero no lado direito com pedestal, glow e sombra realista
            prod_cx = 855
            prod_cy = actual_benefits_y + (actual_avail_h // 2)
            compositor.draw_hero_product(produto_img_path, (prod_cx, prod_cy), max_size=(380, 420), glow=True, ground_shadow=True)
        else:
            compositor.draw_benefit_cards(pontos_beneficio, start_y=actual_benefits_y, available_height=actual_avail_h)
    elif tem_produto:
        # Se não houver bullets mas houver produto, centraliza o produto com destaque
        prod_cx = width // 2
        prod_cy = (y_after_headline + y_cta) // 2
        compositor.draw_hero_product(produto_img_path, (prod_cx, prod_cy), max_size=(460, 480), glow=True, ground_shadow=True)

    # 6. Botão CTA 3D
    final_cta = cta_texto
    if preco and ("COMPRE" in final_cta.upper() or "GARANTA" in final_cta.upper()) and preco not in final_cta:
        final_cta = f"{final_cta} POR {preco}"
    compositor.draw_cta_button_3d(final_cta, y=y_cta)

    # 7. Rodapé com Assinatura Oficial
    compositor.draw_brand_footer(y=y_footer)

    return compositor.save(out_path)


# ======================================================================================
# MOTOR DE SLIDES DE CARROSSEL MASTERPIECE 2.0 (INÍCIO, MEIO E FIM)
# ======================================================================================
def renderizar_slide_carrossel_masterpiece(
    titulo: str,
    subtitulo: str = None,
    pontos: list = None,
    cta_slide: str = None,
    num_slide: int = 1,
    total_slides: int = 3,
    categoria: str = "CIÊNCIA & RECUPERAÇÃO",
    out_path: str = None,
    bg_path: str = None,
    produto_img_path: str = None,
    preco: str = None,
    nome_autor: str = "EVANDRO GALLINA",
    formato_slide: str = "feed",
    estilo_cor: str = "gold_dark"
) -> str:
    """
    Renderiza um Slide de Carrossel de altíssimo padrão Adobe Creative Engine 2.0.
    Aplica a Lei da Proteção Facial no Slide 1, Diagramação Científica no Slide 2
    e Mockup Hero do Produto no Slide 3.
    """
    if formato_slide == "quadrado":
        width, height = 1080, 1080
    else:
        width, height = 1080, 1350  # Padrão Instagram Feed Portrait 4:5

    if not out_path:
        out_path = os.path.join(PUBLIC_IMG_DIR, f"slide_{num_slide}_{int(os.getpid())}.png")

    compositor = AdobeLayeredCompositor(width, height, theme=estilo_cor)

    # 1. Background com Safe Zone Facial
    if num_slide == 1 and bg_path and os.path.exists(bg_path):
        # Slide 1 (Início): Foto de estúdio/ação com rosto e expressão 100% protegidos
        start_vig = 0.52 if not pontos else 0.48
        end_vig = 0.64 if not pontos else 0.58
        compositor.set_cinematic_background(bg_path, start_vignette=start_vig, end_vignette=end_vig)
    else:
        # Slides 2 e 3 (Meio e Fim): Estúdio escuro premium tecnológico
        compositor.set_cinematic_background(None)

    # 2. Header do Carrossel (Pílula de Categoria / Passo e Contador / Preço)
    compositor.draw_carousel_header(categoria, num_slide, total_slides, preco=preco if num_slide == total_slides else None, y=45)

    # 3. Selo de Autoridade Metálico Concêntrico com Estrelas Vetoriais (Folga vertical garantida)
    if num_slide == 2:
        compositor.draw_authority_seal((width - 95, 148), radius=42, text_top="100% CIÊNCIA", text_sub="LAUDO TÉCNICO")
    elif num_slide == total_slides:
        # Selo de pureza/laudo (sem duplicar o preço se já estiver na pílula do cabeçalho)
        seal_top = "100% PURO" if preco else "LAUDO APROVADO"
        seal_sub = "LOTE OFICIAL" if preco else "PADRÃO OURO"
        compositor.draw_authority_seal((width - 95, 148), radius=42, text_top=seal_top, text_sub=seal_sub)

    # 4. Posicionamento de Manchete Dinâmico (Respeito rigoroso à Zona Facial e Selo)
    if num_slide == 1:
        start_y = 690 if not pontos else 650
    else:
        # Slides 2 e 3: Começa a 220px, estritamente abaixo do selo superior (termina em 190px)
        start_y = 220

    y_after_head = compositor.draw_hero_headline(titulo, subtitulo, start_y=start_y)

    # 5. Lista de Pontos / Benefícios e Mockup Hero com Distribuição Inteligente (Eliminação Total de Vazios)
    tem_produto = produto_img_path and os.path.exists(produto_img_path) and (num_slide == total_slides)

    if num_slide == 2:
        # Slide 2: 3 Cards generosos preenchendo o espaço + Banner Dica de Ouro
        top_content_y = y_after_head + 25
        card_w = 940
        card_x = (width - card_w) // 2
        avail_for_cards = 550
        y_end_cards = compositor.draw_benefit_cards(
            pontos=pontos,
            start_y=top_content_y,
            card_w=card_w,
            card_x=card_x,
            available_height=avail_for_cards,
            max_points=3
        )

        # Banner de Destaque Científico / Dica de Ouro (Elimina 100% do vazio inferior)
        callout_y = max(y_end_cards + 25, 960)
        compositor.draw_highlight_callout(
            title="DICA DE OURO DO MARCÃO • PROTOCOLO COMPROVADO",
            text="A saturação diária e o descanso celular adequado multiplicam a síntese de novas fibras musculares e previnem o catabolismo.",
            y=callout_y,
            height=160,
            width=940,
            x=card_x
        )
        compositor.draw_carousel_indicator(cta_slide if cta_slide else "ARRASTE PARA O LADO", y=height - 95)

    elif num_slide == total_slides:
        # Slide 3: Split cards + Produto Hero + Barra de Selos de Confiança + Botão 3D
        top_content_y = y_after_head + 25
        card_w = 540
        card_x = 60
        avail_for_cards = 550
        y_end_cards = compositor.draw_benefit_cards(
            pontos=pontos,
            start_y=top_content_y,
            card_w=card_w,
            card_x=card_x,
            available_height=avail_for_cards,
            max_points=3
        )

        # Produto Hero à direita perfeitamente centralizado e imponente
        if tem_produto:
            prod_cx = 835
            prod_cy = top_content_y + (avail_for_cards // 2)
            compositor.draw_hero_product(
                produto_img_path,
                (prod_cx, prod_cy),
                max_size=(440, 520),
                glow=True,
                ground_shadow=True
            )

        # Barra de Selos de Confiança (Preenchimento nobre antes do botão)
        trust_y = 965
        compositor.draw_trust_badges(y=trust_y, width=960, x=60, height=90)

        # CTA 3D de Alta Conversão
        final_cta = cta_slide if cta_slide else "GARANTA NO LINK DA BIO"
        if preco and ("COMPRE" in final_cta.upper() or "GARANTA" in final_cta.upper()) and preco not in final_cta:
            final_cta = f"{final_cta} POR {preco}"
        compositor.draw_cta_button_3d(final_cta, y=height - 180)
        compositor.draw_brand_footer(y=height - 85)

    else:
        # Slide 1 ou intermediário genérico
        top_content_y = y_after_head + 25
        card_w = 940
        card_x = (width - card_w) // 2
        compositor.draw_benefit_cards(
            pontos=pontos,
            start_y=top_content_y,
            card_w=card_w,
            card_x=card_x,
            available_height=420,
            max_points=2 if num_slide == 1 else 3
        )
        compositor.draw_carousel_indicator(cta_slide if cta_slide else "ARRASTE PARA O LADO", y=height - 95)

    return compositor.save(out_path)


if __name__ == "__main__":
    teste_feed = os.path.join(BASE_DIR, "assets", "teste_masterpiece_feed.png")
    renderizar_criativo_masterpiece(
        headline="CREATINA PURA É ESSENCIAL",
        subheadline="Protocolo científico oficial Marcão Personal para força e definição:",
        pontos_beneficio=[
            "Aumento comprovado de até 30% na força muscular.",
            "Recuperação celular acelerada e hidratação das fibras.",
            "Matéria-prima importada com laudo laboratorial 100% puro."
        ],
        categoria="ALTA PERFORMANCE & BIOHACKING",
        cta_texto="GARANTA COM DESCONTO NA BIO",
        out_path=teste_feed,
        formato="feed",
        estilo_cor="gold_dark"
    )

    teste_story = os.path.join(BASE_DIR, "assets", "teste_masterpiece_story.png")
    renderizar_criativo_masterpiece(
        headline="CREATINA PURA É ESSENCIAL",
        subheadline="Protocolo científico oficial Marcão Personal para força e definição:",
        pontos_beneficio=[
            "Aumento comprovado de até 30% na força muscular.",
            "Recuperação celular acelerada e hidratação das fibras.",
            "Matéria-prima importada com laudo laboratorial 100% puro."
        ],
        categoria="ALTA PERFORMANCE & BIOHACKING",
        cta_texto="TOQUE NO LINK PARA COMPRAR",
        out_path=teste_story,
        formato="story",
        estilo_cor="gold_dark"
    )
    print("Testes Feed e Story 2.0 concluídos com sucesso!")

    # Teste Carrossel 3 Slides (Início, Meio e Fim)
    teste_s1 = os.path.join(BASE_DIR, "assets", "teste_carrossel_s1_inicio.png")
    teste_s2 = os.path.join(BASE_DIR, "assets", "teste_carrossel_s2_meio.png")
    teste_s3 = os.path.join(BASE_DIR, "assets", "teste_carrossel_s3_fim.png")

    renderizar_slide_carrossel_masterpiece(
        titulo="TOMOU ANTI-INFLAMATÓRIO?\nSEU TREINO FOI PARA O LIXO!",
        subtitulo="A bioquímica da dor muscular explicada pelo Marcão:",
        pontos=[
            "A dor após o treino decorre de microfissuras benéficas.",
            "Remédios comuns desligam o gatilho biológico de crescimento."
        ],
        cta_slide="ARRASTE PARA O LADO ››",
        num_slide=1,
        total_slides=3,
        categoria="CIÊNCIA & RECUPERAÇÃO",
        out_path=teste_s1,
        bg_path=os.path.join(BASE_DIR, "assets", "foto_evandro_gym.png")
    )

    renderizar_slide_carrossel_masterpiece(
        titulo="O QUE ACONTECE NA FIBRA\nQUANDO VOCÊ TOMA REMÉDIO?",
        subtitulo="Bloqueio da enzima COX-2 comprovado pela fisiologia:",
        pontos=[
            "A síntese de novas fibras musculares é completamente paralisada.",
            "As células satélites não se fundem para engrossar o músculo.",
            "A inflamação fisiológica controlada é sua maior aliada."
        ],
        cta_slide="VEJA A SOLUÇÃO A SEGUIR ››",
        num_slide=2,
        total_slides=3,
        categoria="CIÊNCIA & RECUPERAÇÃO",
        out_path=teste_s2
    )

    prod_local = os.path.join(BASE_DIR, "apps", "site", "public", "images", "creatina.jpg")
    renderizar_slide_carrossel_masterpiece(
        titulo="PADRÃO OURO MARCÃO PERSONAL\nRECUPERAÇÃO SEM REMÉDIOS",
        subtitulo="Protocolo celular com Creatina Micronizada 100% Pura:",
        pontos=[
            "Creatina Micronizada 100% Pura Nature's Prime.",
            "Hidratação profunda das fibras e ressíntese acelerada de ATP.",
            "Pote oficial de 300g (100 doses oficiais)."
        ],
        cta_slide="COMPRE NO LINK DA BIO",
        num_slide=3,
        total_slides=3,
        categoria="OFERTA OFICIAL",
        out_path=teste_s3,
        produto_img_path=prod_local,
        preco="R$ 169,90"
    )
    print("Testes Carrossel 3 Slides (Início, Meio, Fim) concluídos com sucesso!")

