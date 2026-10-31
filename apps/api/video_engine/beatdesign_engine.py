"""
=============================================================================
BEATDESIGN AI CREATIVE ENGINE — MARCÃO PERSONAL (MULTI-SCENE EDITION)
MOTOR DE VÍDEOS DINÂMICOS COM MÚLTIPLAS CENAS, MOTION GRAPHICS E 3D
=============================================================================
Padrão de Qualidade Cinematográfica:
- Zero cena única / Zero loops repetitivos.
- 6 a 8 cortes rápidos e dinâmicos (a cada 3.5 a 4.5 segundos).
- Células 3D, Produto girando 360°, Músculos em contração, Smartwatch e Atleta.
- Motion graphics com cards glassmorphism, vinhetas e badges coloridos.
- Legendas dinâmicas Hormozi queimadas na tela (.ass) com palavras-chave em amarelo.
- Voz oficial brasileira com trilha sonora de performance.
- Agendamento diário às 18:00h no Instagram Reels e Stories.
=============================================================================
"""

import os
import sys
import json
import time
import requests
import subprocess
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("c:/Users/User/Desktop/Agentes de venda/.env")

BASE_DIR = r"c:\Users\User\Desktop\Agentes de venda\apps\api\video_engine"
TAKES_DIR = os.path.join(BASE_DIR, "takes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
IMAGES_DIR = r"c:\Users\User\Desktop\Agentes de venda\apps\site\public\images"
LOGO_PATH = os.path.join(IMAGES_DIR, "logo_marcao.jpg")
HISTORICO_FILE = os.path.join(BASE_DIR, "historico_beatdesign_reels.json")
BG_MUSIC = r"c:\Users\User\Desktop\Agentes de venda\apps\api\output\fitness_bg_music.wav"
if not os.path.exists(BG_MUSIC):
    BG_MUSIC = os.path.join(TAKES_DIR, "ambience.wav")

FFMPEG_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
FFPROBE_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffprobe.exe"

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qkopgftfrfftoyndhhfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "28570207812599721")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))
try:
    from marcao_voice import gerar_voz_marcao
except ImportError:
    from apps.api.marcao_voice import gerar_voz_marcao


def get_duration(fpath):
    cmd = [FFPROBE_EXE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fpath]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def render_multiscene_video(scenes_list, vox_audio_path, output_video_path, subs_list):
    print(f"\n=======================================================")
    print(f"🎬 RENDERIZANDO VÍDEO DINÂMICO MULTI-CENAS ({len(scenes_list)} CENAS)")
    print(f"=======================================================")

    font_bold = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 46)
    font_badge = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 26)
    font_sub = ImageFont.truetype(r"C:\Windows\Fonts\calibrib.ttf", 32)
    font_footer = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 24)

    logo_img = None
    if os.path.exists(LOGO_PATH):
        try:
            raw_logo = Image.open(LOGO_PATH).convert("RGBA")
            raw_logo = raw_logo.resize((100, 100), Image.Resampling.LANCZOS)
            mask = Image.new("L", (100, 100), 0)
            draw_m = ImageDraw.Draw(mask)
            draw_m.rounded_rectangle([0, 0, 100, 100], radius=24, fill=255)
            logo_img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
            logo_img.paste(raw_logo, (0, 0), mask)
        except Exception:
            pass

    rendered_clips = []
    for sc in scenes_list:
        sc_id = sc["id"]
        dur = sc["duration"]
        v_in = sc["video_in"]
        clip_out = os.path.join(TAKES_DIR, f"dyn_{sc_id}.mp4")
        ov_path = os.path.join(TAKES_DIR, f"ov_{sc_id}.png")

        ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ov)

        for y in range(300):
            alpha = int(180 * (1 - y / 300))
            draw.line([(0, y), (1080, y)], fill=(5, 10, 20, alpha))

        for y in range(1450, 1920):
            alpha = int(220 * ((y - 1450) / 470))
            draw.line([(0, y), (1080, y)], fill=(5, 10, 20, alpha))

        if logo_img:
            ov.paste(logo_img, (490, 60), logo_img)

        bb = draw.textbbox((0, 0), sc["badge"], font=font_badge)
        tb_w = bb[2] - bb[0]
        badge_w = tb_w + 50
        badge_h = 44
        badge_x = (1080 - badge_w) // 2
        badge_y = 175
        draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=14, fill=sc["badge_bg"])
        draw.text((badge_x + 25, badge_y + 8), sc["badge"], font=font_badge, fill=sc["badge_fg"])

        card_x = 40
        card_y = 1530
        card_w = 1000
        card_h = 280
        draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=24, fill=(8, 15, 30, 215), outline=(255, 122, 0, 160), width=2)
        draw.text((card_x + 36, card_y + 32), sc["headline"], font=font_bold, fill=(255, 255, 255))
        draw.line([(card_x + 36, card_y + 96), (card_x + 964, card_y + 96)], fill=(255, 122, 0, 200), width=2)
        draw.text((card_x + 36, card_y + 116), sc["sub"], font=font_sub, fill=(226, 232, 240))
        draw.text((card_x + 36, card_y + 196), "MARCÃO PERSONAL • INTELIGÊNCIA ARTIFICIAL DE PERFORMANCE", font=font_footer, fill=(255, 122, 0))

        ov.save(ov_path, "PNG")

        fc = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v_scaled];"
            "[v_scaled]split[fwd][bwd];"
            "[bwd]reverse[rev];"
            "[fwd][rev]concat=n=2:v=1[pingpong];"
            f"[pingpong]loop=loop=5:size=150:start=0,trim=duration={dur},setpts=PTS-STARTPTS[v_loop];"
            "[v_loop][1:v]overlay=0:0,format=yuv420p[v_out]"
        )

        cmd = [
            FFMPEG_EXE, "-y",
            "-i", v_in,
            "-i", ov_path,
            "-filter_complex", fc,
            "-map", "[v_out]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-r", "30",
            "-t", str(dur),
            clip_out
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        rendered_clips.append(clip_out)

    concat_txt = os.path.join(TAKES_DIR, f"concat_{int(time.time())}.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for rc in rendered_clips:
            f.write(f"file '{rc.replace(chr(92), '/')}'\n")

    merged_video = os.path.join(TAKES_DIR, f"merged_{int(time.time())}.mp4")
    subprocess.run([FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", merged_video], capture_output=True, check=True)

    ass_path = output_video_path.replace(".mp4", ".ass")
    ass_header = """[Script Info]
Title: Legendas Dinamicas Hormozi
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,Arial,52,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,430,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = [f"Dialogue: 0,{it['start']},{it['end']},Hormozi,,0,0,0,,{it['text']}" for it in subs_list]
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues) + "\n")

    ass_filter_path = ass_path.replace("\\", "/").replace(":", "\\:")
    total_dur = sum(sc["duration"] for sc in scenes_list)

    cmd_final = [
        FFMPEG_EXE, "-y",
        "-i", merged_video,
        "-i", vox_audio_path,
        "-stream_loop", "-1", "-i", BG_MUSIC,
        "-filter_complex", (
            f"[0:v]ass='{ass_filter_path}',format=yuv420p[vout];"
            f"[1:a]volume=1.35,apad=pad_dur=1.0[voxa];"
            f"[2:a]volume=0.15,afade=t=out:st={total_dur-2.0:.2f}:d=2.0[bga];"
            f"[voxa][bga]amix=inputs=2:duration=first[aout]"
        ),
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{total_dur:.2f}",
        output_video_path
    ]
    subprocess.run(cmd_final, capture_output=True, text=True, check=True)
    return output_video_path


def upload_supabase(local_path, remote_name):
    url = f"{SUPABASE_URL}/storage/v1/object/creativos/videos/{remote_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "video/mp4",
        "x-upsert": "true"
    }
    with open(local_path, "rb") as f:
        data = f.read()
    r = requests.post(url, headers=headers, data=data, timeout=90, verify=False)
    if r.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/creativos/videos/{remote_name}"
    return None
