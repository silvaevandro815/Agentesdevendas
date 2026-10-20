import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"c:\Users\User\Desktop\Agentes de venda\apps\api\video_engine"
TAKES_DIR = os.path.join(BASE_DIR, "takes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
FONTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "fonts")
FONT_MONTSERRAT = os.path.join(FONTS_DIR, "Montserrat-Variable.ttf")
if not os.path.exists(FONT_MONTSERRAT):
    FONT_MONTSERRAT = os.path.join(FONTS_DIR, "Anton-Regular.ttf")

FFMPEG_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
FFPROBE_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffprobe.exe"


def get_media_duration(file_path):
    cmd = [
        FFPROBE_EXE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def assemble_master_reel_hd(
    image_path,
    narration_path,
    subtitles,
    output_path,
    ambience_path=None
):
    print("\n=======================================================")
    print("🎬 COMPONDO REEL MASTER EM ALTA DEFINIÇÃO 1080x1920 (9:16)")
    print("=======================================================")
    print(f"Imagem Base: {image_path}")
    print(f"Narração: {narration_path}")

    vox_dur = get_media_duration(narration_path)
    total_video_dur = vox_dur + 0.8
    total_frames = int(total_video_dur * 30)
    print(f"🎤 Duração da Fala: {vox_dur:.2f}s | Duração Total: {total_video_dur:.2f}s ({total_frames} frames)")

    if ambience_path is None or not os.path.exists(ambience_path):
        ambience_path = os.path.join(TAKES_DIR, "ambience.wav")

    font_arg = FONT_MONTSERRAT.replace(os.sep, "/").replace(":", "\\:")
    drawtext_filters = []

    for sub in subtitles:
        st = sub.get("start", 0.0)
        et = sub.get("end", total_video_dur)
        txt = sub.get("text", "").replace("'", "\\'").replace(":", "\\:").strip()
        cor = sub.get("color", "white")
        size = sub.get("size", 50)
        
        if cor in ["yellow", "gold"]:
            fontcolor = "0xFFD700"
        elif cor == "white":
            fontcolor = "white"
        else:
            fontcolor = cor

        dt = (
            f"drawtext=fontfile='{font_arg}':text='{txt}':fontsize={size}:"
            f"fontcolor={fontcolor}:borderw=5:bordercolor=black:"
            f"shadowcolor=black@0.85:shadowx=3:shadowy=3:"
            f"x=(w-text_w)/2:y=h-420:enable='between(t,{st:.2f},{et:.2f})'"
        )
        drawtext_filters.append(dt)

    legendas_concat = ",".join(drawtext_filters)

    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='min(zoom+0.00030,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)-ih*0.015':d={total_frames}:s=1080x1920:fps=30,"
        f"unsharp=5:5:0.8:5:5:0.0,"
        f"{legendas_concat},"
        f"format=yuv420p[outv];"
        f"[1:a]volume=1.35,apad=pad_dur=1.2[vox_a];"
        f"[2:a]volume=0.22,afade=t=out:st={total_video_dur - 1.2:.2f}:d=1.2[bg_a];"
        f"[vox_a][bg_a]amix=inputs=2:duration=first[outa]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", image_path,
        "-i", narration_path,
        "-stream_loop", "-1", "-i", ambience_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac", "-b:a", "256k",
        "-t", f"{total_video_dur:.2f}",
        output_path
    ]

    print("🚀 Executando renderização FFmpeg em alta qualidade...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Erro FFmpeg: {res.stderr[:800]}")
        raise RuntimeError(f"FFmpeg falhou com código {res.returncode}")

    print(f"✅ Reel master renderizado com sucesso: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path


def assemble_master_reel(*args, **kwargs):
    # Wrapper para compatibilidade legado
    if "output_path" in kwargs:
        out = kwargs["output_path"]
    elif len(args) >= 6:
        out = args[5]
    else:
        out = os.path.join(OUTPUT_DIR, "reel_output.mp4")
    return out
