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


def format_ass_time(sec):
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    centis = int(round((sec - int(sec)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{centis:02d}"


def create_ass_subtitles(subtitles, ass_path, keywords=None):
    if keywords is None:
        keywords = ["balança", "bioimpedância", "Xiaomi", "gordura", "músculo", "creatina", "saturação", "1,68", "força", "métrica", "strava", "batimentos", "proteína", "24g", "ia", "mentoria", "vip", "grátis", "shape", "shopee", "0,09"]

    ass_header = """[Script Info]
Title: Legendas Dinamicas Marcao Personal
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,Arial,52,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,3,2,50,50,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    for item in subtitles:
        st = format_ass_time(item.get("start", 0.0))
        et = format_ass_time(item.get("end", 5.0))
        txt = item.get("text", "")
        for kw in keywords:
            if kw.lower() in txt.lower():
                idx = txt.lower().find(kw.lower())
                orig_kw = txt[idx:idx+len(kw)]
                txt = txt[:idx] + "{\\c&H00D7FF&}" + orig_kw + "{\\c&H00FFFFFF&}" + txt[idx+len(kw):]
                break
        dialogues.append(f"Dialogue: 0,{st},{et},Hormozi,,0,0,0,,{txt}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues) + "\n")


def assemble_master_reel_hd(
    image_path,
    narration_path,
    subtitles,
    output_path,
    ambience_path=None,
    motion_intro_path=None,
    enable_punch_zoom=True
):
    print("\n=======================================================")
    print("🎬 COMPONDO REEL MASTER COM MOTOR HIPER-RETENÇÃO (HYPERFRAMES + PUNCH ZOOM)")
    print("=======================================================")

    video_take_path = image_path
    if str(video_take_path).lower().endswith(('.png', '.jpg', '.jpeg')):
        base_name = os.path.splitext(os.path.basename(video_take_path))[0]
        cand1 = os.path.join(TAKES_DIR, f"ltx_{base_name.replace('evandro_', '')}.mp4")
        cand2 = os.path.join(TAKES_DIR, f"ltx_{base_name.replace('evandro_', '').replace('_take', '')}_motion_take.mp4")
        cand3 = os.path.join(TAKES_DIR, "ltx_creatina_motion_take.mp4")
        if os.path.exists(cand1):
            video_take_path = cand1
        elif os.path.exists(cand2):
            video_take_path = cand2
        elif "creatina" in base_name:
            video_take_path = cand3
        elif "smartwatch" in base_name:
            video_take_path = os.path.join(TAKES_DIR, "ltx_smartwatch_motion_take.mp4")
        elif "whey" in base_name:
            video_take_path = os.path.join(TAKES_DIR, "ltx_whey_motion_take.mp4")
        elif "balanca" in base_name:
            video_take_path = os.path.join(TAKES_DIR, "ltx_animated_take1.mp4")
        else:
            video_take_path = os.path.join(TAKES_DIR, "take1_real_ltx.mp4")
        print(f"🔄 Entrada estática substituída por Take de Vídeo Real: {video_take_path}")

    vox_dur = get_media_duration(narration_path)
    total_video_dur = vox_dur + 0.6
    print(f"🎥 Vídeo Fonte: {video_take_path}")
    print(f"🎤 Duração da Fala: {vox_dur:.2f}s | Duração Total: {total_video_dur:.2f}s")

    bg_music = r"c:\Users\User\Desktop\Agentes de venda\apps\api\output\fitness_bg_music.wav"
    if ambience_path is None or not os.path.exists(ambience_path):
        ambience_path = bg_music if os.path.exists(bg_music) else os.path.join(TAKES_DIR, "ambience.wav")

    # Legendas dinâmicas ASS
    ass_path = output_path.replace(".mp4", "_subs.ass")
    create_ass_subtitles(subtitles, ass_path)
    ass_filter_path = ass_path.replace("\\", "/").replace(":", "\\:")

    punch_filter = ""
    if enable_punch_zoom:
        punch_filter = ",crop=w='if(mod(floor(t/3.5),2),938,1080)':h='if(mod(floor(t/3.5),2),1668,1920)':x='(in_w-out_w)/2':y='(in_h-out_h)/2',scale=1080:1920,setsar=1"

    is_concat = str(video_take_path).lower().endswith(".txt")

    if motion_intro_path and os.path.exists(motion_intro_path):
        intro_dur = get_media_duration(motion_intro_path)
        print(f"⚡ INSERINDO GANCHO CINÉTICO HYPERFRAMES NA ABERTURA ({intro_dur:.2f}s): {motion_intro_path}")

        # Se for concat .txt
        if is_concat:
            input_args = [
                "-i", motion_intro_path,
                "-f", "concat", "-safe", "0", "-i", video_take_path,
                "-i", narration_path,
                "-stream_loop", "-1", "-i", ambience_path
            ]
            filter_complex = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v_intro];"
                f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,"
                f"trim=duration={total_video_dur},setpts=PTS-STARTPTS{punch_filter}[v_main];"
                f"[v_intro][v_main]concat=n=2:v=1:a=0[v_seq];"
                f"[v_seq]ass='{ass_filter_path}',format=yuv420p[outv];"
                f"[2:a]volume=1.35,apad=pad_dur=1.0,adelay={int(intro_dur*1000)}|{int(intro_dur*1000)}[vox_a];"
                f"[3:a]volume=0.18,afade=t=out:st={total_video_dur + intro_dur - 1.5:.2f}:d=1.5[bg_a];"
                f"[vox_a][bg_a]amix=inputs=2:duration=first[outa]"
            )
        else:
            input_args = [
                "-i", motion_intro_path,
                "-i", video_take_path,
                "-i", narration_path,
                "-stream_loop", "-1", "-i", ambience_path
            ]
            filter_complex = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v_intro];"
                f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
                f"split[fwd][bwd];[bwd]reverse[rev];[fwd][rev]concat=n=2:v=1[pp];"
                f"[pp]loop=loop=10:size=200:start=0,trim=duration={total_video_dur},setpts=PTS-STARTPTS{punch_filter}[v_main];"
                f"[v_intro][v_main]concat=n=2:v=1:a=0[v_seq];"
                f"[v_seq]ass='{ass_filter_path}',format=yuv420p[outv];"
                f"[2:a]volume=1.35,apad=pad_dur=1.0,adelay={int(intro_dur*1000)}|{int(intro_dur*1000)}[vox_a];"
                f"[3:a]volume=0.18,afade=t=out:st={total_video_dur + intro_dur - 1.5:.2f}:d=1.5[bg_a];"
                f"[vox_a][bg_a]amix=inputs=2:duration=first[outa]"
            )
        render_dur = total_video_dur + intro_dur
    else:
        if is_concat:
            print(f"🎬 MODO MULTI-CENAS ATIVO: {video_take_path}")
            filter_complex = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,"
                f"trim=duration={total_video_dur},setpts=PTS-STARTPTS{punch_filter}[v_cuts];"
                f"[v_cuts]ass='{ass_filter_path}',format=yuv420p[outv];"
                f"[1:a]volume=1.35,apad=pad_dur=1.0[vox_a];"
                f"[2:a]volume=0.15,afade=t=out:st={total_video_dur - 1.5:.2f}:d=1.5[bg_a];"
                f"[vox_a][bg_a]amix=inputs=2:duration=first[outa]"
            )
            input_args = ["-f", "concat", "-safe", "0", "-i", video_take_path]
        else:
            filter_complex = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
                f"split[fwd][bwd];[bwd]reverse[rev];[fwd][rev]concat=n=2:v=1[pp];"
                f"[pp]loop=loop=10:size=200:start=0,trim=duration={total_video_dur},setpts=PTS-STARTPTS{punch_filter}[v_loop];"
                f"[v_loop]ass='{ass_filter_path}',format=yuv420p[outv];"
                f"[1:a]volume=1.35,apad=pad_dur=1.0[vox_a];"
                f"[2:a]volume=0.15,afade=t=out:st={total_video_dur - 1.5:.2f}:d=1.5[bg_a];"
                f"[vox_a][bg_a]amix=inputs=2:duration=first[outa]"
            )
            input_args = ["-i", video_take_path]

        input_args.extend([
            "-i", narration_path,
            "-stream_loop", "-1", "-i", ambience_path
        ])
        render_dur = total_video_dur

    cmd = [
        FFMPEG_EXE, "-y",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{render_dur:.2f}",
        output_path
    ]

    print("🚀 Executando renderização FFmpeg Master...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Erro FFmpeg: {res.stderr[-2000:]}")
        raise RuntimeError(f"FFmpeg falhou com código {res.returncode}")

    print(f"✅ Reel master renderizado com sucesso: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path


# Alias para compatibilidade
assemble_master_reel = assemble_master_reel_hd
