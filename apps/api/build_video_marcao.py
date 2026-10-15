"""
Pipeline de Montagem Automatizada de Vídeo Reels (50s) com Marcão Personal
===========================================================================
- Junta voz sintetizada de alta fidelidade do Marcão (ElevenLabs)
- Trilha instrumental em segundo plano com volume suave (15%)
- Clipes verticais 1080x1920 (9:16) dinâmicos com corte de câmera a cada 10-12s
- Tarjas e stickers visuais do site oficial marcaopersonal.com
- Renderização via FFmpeg em formato H.264 / AAC padrão Instagram Reels
- Upload no Supabase Storage para obtenção de URL pública
# POSTAGEM DE VÍDEOS CANCELADA POR ORDEM DO DIRETOR EVANDRO GALLINA
# (Foco total transferido para Carrosséis/Cards de Alta Conversão no Feed e Stories com rosto de Evandro)
VIDEO_POSTING_CANCELADO = True

if __name__ == "__main__":
    print("[VÍDEOS CANCELADOS] A postagem e geração de vídeos foi cancelada pelo Diretor Evandro Gallina.")
    print("Foco da operação: Feed editorial de alta conversão e Instagram Stories diários.")
    import sys; sys.exit(0)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMAGES_DIR = os.path.join(os.path.dirname(BASE_DIR), "site", "public", "images")
IMG_MARCAO = os.path.join(IMAGES_DIR, "posts", "test_marcao_gen.png")
IMG_MASCOTE = os.path.join(IMAGES_DIR, "mascote_marcao.jpg")
IMG_CREATINA = os.path.join(IMAGES_DIR, "creatina.jpg")
IMG_LOGO = os.path.join(IMAGES_DIR, "logo_marcao.jpg")

VOICE_PATH = os.path.join(OUTPUT_DIR, "marcao_pilot_voice.mp3")
MUSIC_PATH = os.path.join(OUTPUT_DIR, "fitness_bg_music.wav")
FINAL_VIDEO = os.path.join(OUTPUT_DIR, "marcao_reels_50s_pilot.mp4")

# Resolução vertical Instagram Reels
WIDTH = 1080
HEIGHT = 1920


def criar_frame_vertical(img_path, titulo_cena, subtitulo_cena, cta_rodape="🔗 SITE OFICIAL: marcaopersonal.com • LINK NA BIO"):
    """
    Cria uma imagem composta vertical 1080x1920 perfeita para Reels,
    com a imagem principal centralizada, fundo cinematográfico escuro,
    branding no topo e tarjas de legenda/CTA de alta legibilidade.
    """
    canvas = Image.new("RGB", (WIDTH, HEIGHT), (6, 13, 27))
    draw = ImageDraw.Draw(canvas)

    # 1. Carrega imagem central e redimensiona mantendo proporção
    if os.path.exists(img_path):
        raw_img = Image.open(img_path).convert("RGBA")
        # Ajusta para caber com elegância (ex: 980x980 ou similar)
        target_size = (940, 940)
        raw_img = raw_img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Cria moldura futurista neon
        frame_box = Image.new("RGBA", (target_size[0] + 16, target_size[1] + 16), (0, 229, 255, 180))
        canvas.paste(frame_box, (70 - 8, 450 - 8))
        canvas.paste(raw_img, (70, 450), raw_img)

    # 2. Top Header Branding
    # Tarja superior
    draw.rectangle([(0, 0), (WIDTH, 140)], fill=(3, 7, 18))
    draw.line([(0, 140), (WIDTH, 140)], fill=(0, 229, 255), width=3)
    
    # Logo pequeno no topo
    if os.path.exists(IMG_LOGO):
        logo = Image.open(IMG_LOGO).resize((90, 90), Image.Resampling.LANCZOS)
        canvas.paste(logo, (50, 25))

    # Textos do Header (usando fonte default ajustada)
    draw.text((160, 40), "MARCÃO PERSONAL", fill=(255, 255, 255))
    draw.text((160, 80), "METODOLOGIA OFICIAL • BIOHACKING & DEFINIÇÃO", fill=(0, 255, 136))

    # 3. Título da Cena (Abaixo do Header)
    draw.rectangle([(50, 180), (WIDTH - 50, 390)], fill=(11, 22, 44), outline=(0, 229, 255), width=2)
    draw.text((80, 210), titulo_cena, fill=(0, 229, 255))
    draw.text((80, 280), subtitulo_cena, fill=(248, 250, 252))

    # 4. Box Inferior com CTA Permanente
    draw.rectangle([(0, HEIGHT - 220), (WIDTH, HEIGHT)], fill=(3, 7, 18))
    draw.line([(0, HEIGHT - 220), (WIDTH, HEIGHT - 220)], fill=(0, 255, 136), width=4)
    draw.rectangle([(60, HEIGHT - 180), (WIDTH - 60, HEIGHT - 60)], fill=(37, 211, 102), outline=(255, 255, 255), width=2)
    draw.text((100, HEIGHT - 135), cta_rodape, fill=(6, 13, 27))

    return canvas


def renderizar_video_completo():
    """Renderiza os 5 blocos com FFmpeg e faz o mix do áudio."""
    print("[RENDER] Criando frames de cada ato...")
    cenas = [
        {
            "img": IMG_MARCAO,
            "titulo": "VOCÊ TOMA CREATINA ERRADO?",
            "sub": "Mito vs Ciência: Por que parar no fim de semana destrói seus ganhos.",
            "dur": 11.5
        },
        {
            "img": IMG_MASCOTE,
            "titulo": "NÃO É ENERGIA INSTANTÂNEA!",
            "sub": "A Creatina age por saturação celular acumulada.",
            "dur": 11.5
        },
        {
            "img": IMG_MARCAO,
            "titulo": "RESSÍNTESE DE ATP NO MÚSCULO",
            "sub": "Mais força real na última repetição sem retenção líquida prejudicial.",
            "dur": 13.0
        },
        {
            "img": IMG_CREATINA,
            "titulo": "5 GRAMAS TODO SANTO DIA",
            "sub": "Creatina 100% Pura • Absorção Máxima • Conformidade ANVISA.",
            "dur": 12.0
        },
        {
            "img": IMG_MARCAO,
            "titulo": "QUER MINHA CONSULTORIA VIP?",
            "sub": "Toque no link da Bio e entre no site oficial: marcaopersonal.com",
            "dur": 10.7
        }
    ]

    clipes_mp4 = []
    for idx, c in enumerate(cenas):
        frame = criar_frame_vertical(c["img"], c["titulo"], c["sub"])
        frame_path = os.path.join(OUTPUT_DIR, f"frame_{idx}.png")
        frame.save(frame_path)

        clipe_path = os.path.join(OUTPUT_DIR, f"clip_{idx}.mp4")
        # Gera clipe estático vertical com FFmpeg
        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1", "-i", frame_path,
            "-t", str(c["dur"]),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-r", "30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            clipe_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        clipes_mp4.append(clipe_path)

    # Cria lista de concatenação
    concat_list = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list, "w") as f:
        for cl in clipes_mp4:
            f.write(f"file '{cl.replace(chr(92), '/')}'\n")

    video_mudo = os.path.join(OUTPUT_DIR, "video_mudo_concat.mp4")
    print("[RENDER] Concatenando os 5 atos em vídeo contínuo...")
    cmd_concat = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        video_mudo
    ]
    subprocess.run(cmd_concat, check=True, capture_output=True)

    print("[RENDER] Mixando voz do Marcão + música de fundo (15% volume)...")
    # Mix de áudio: voz a 1.0, música a 0.15, truncado na duração do vídeo
    cmd_mix = [
        FFMPEG_EXE, "-y",
        "-i", video_mudo,
        "-i", VOICE_PATH,
        "-i", MUSIC_PATH,
        "-filter_complex",
        "[1:a]volume=1.0[a1];[2:a]volume=0.15[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        FINAL_VIDEO
    ]
    subprocess.run(cmd_mix, check=True, capture_output=True)
    print(f"[RENDER] VÍDEO FINAL RENDERIZADO COM SUCESSO: {FINAL_VIDEO}")
    return FINAL_VIDEO


if __name__ == "__main__":
    renderizar_video_completo()
