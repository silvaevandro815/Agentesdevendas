import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

base_dir = r"c:\Users\User\Desktop\Agentes de venda\apps\api\video_engine"
takes_dir = os.path.join(base_dir, "takes")
output_dir = os.path.join(base_dir, "output")
os.makedirs(output_dir, exist_ok=True)

ffmpeg_exe = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
ffprobe_exe = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffprobe.exe"

def get_duration(file_path):
    cmd = [
        ffprobe_exe, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def assemble_master_reel(
    take1_raw, take2_raw, take3_raw,
    narration_mp3, ambience_wav,
    text1="A MOTIVACAO TE FAZ COMECAR...",
    text2="MAS E A CONSTANCIA QUE CRIA O SHAPE!",
    text3="NUNCA DESISTA DE VOCE!",
    output_path=None
):
    if output_path is None:
        output_path = os.path.join(output_dir, "reel_evandro_motivacional_10s.mp4")

    print("\n=======================================================")
    print("🎬 INICIANDO COMPOSIÇÃO DE VÍDEO INTELIGENTE (SEM CORTES)")
    print("=======================================================")

    # 1. Medir duração exata da narração
    vox_dur = get_duration(narration_mp3)
    # Folga de segurança de 0.8s para a voz respirar e terminar com perfeição
    target_video_dur = vox_dur + 0.8
    print(f"🎤 Duração da Narração: {vox_dur:.2f}s | Meta de Vídeo com Folga: {target_video_dur:.2f}s")

    take1_ready = os.path.join(takes_dir, "take1_reel.mp4")
    take2_ready = os.path.join(takes_dir, "take2_reel.mp4")
    take3_ready = os.path.join(takes_dir, "take3_reel.mp4")

    # Duração base dos takes 1 e 2
    take1_dur = get_duration(take1_raw)
    take2_dur = get_duration(take2_raw)
    take3_dur = get_duration(take3_raw)

    print(f"Takes Brutos: Take1={take1_dur:.2f}s | Take2={take2_dur:.2f}s | Take3={take3_dur:.2f}s")

    # 1/5. Formatar Take 1 (9:16 vertical + texto)
    print("1/5. Formatando Take 1...")
    subprocess.run([
        ffmpeg_exe, "-y",
        "-i", take1_raw,
        "-vf", (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "unsharp=3:3:0.5:3:3:0.0,"
            f"drawtext=text='{text1}':font=Arial:fontsize=48:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-420:enable='between(t,0.3,{take1_dur - 0.2:.2f})'"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30",
        take1_ready
    ], check=True)

    # 2/5. Formatar Take 2 (9:16 vertical + texto)
    print("2/5. Formatando Take 2...")
    subprocess.run([
        ffmpeg_exe, "-y",
        "-i", take2_raw,
        "-vf", (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "unsharp=3:3:0.5:3:3:0.0,"
            f"drawtext=text='{text2}':font=Arial:fontsize=46:fontcolor=0xFFD700:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-420:enable='between(t,0.3,{take2_dur - 0.2:.2f})'"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30",
        take2_ready
    ], check=True)

    # 3/5. Formatar Take 3 com ajuste dinâmico para cobrir 100% da narração restante
    needed_take3_dur = max(take3_dur, target_video_dur - (take1_dur + take2_dur))
    print(f"3/5. Formatando Take 3 (Duração estendida para {needed_take3_dur:.2f}s para cobrir fala)...")
    
    # Se precisar de tempo extra, estende suavemente o último frame (clone) ou reduz velocidade
    pts_factor = needed_take3_dur / take3_dur if needed_take3_dur > take3_dur else 1.0
    
    subprocess.run([
        ffmpeg_exe, "-y",
        "-i", take3_raw,
        "-vf", (
            f"setpts={pts_factor:.4f}*PTS,"
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "unsharp=3:3:0.5:3:3:0.0,"
            f"drawtext=text='{text3}':font=Arial:fontsize=50:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-420:enable='between(t,0.3,{needed_take3_dur - 0.3:.2f})'"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30",
        "-t", f"{needed_take3_dur:.2f}",
        take3_ready
    ], check=True)

    # 4/5. Master Audio Mix (Narração completa + Trilha sonora com fade out)
    soundtrack_master = os.path.join(takes_dir, "soundtrack_master.aac")
    total_video_actual = take1_dur + take2_dur + needed_take3_dur
    print(f"4/5. Mixando Áudio (Vídeo Real: {total_video_actual:.2f}s | Voz: {vox_dur:.2f}s)...")

    subprocess.run([
        ffmpeg_exe, "-y",
        "-i", narration_mp3,
        "-stream_loop", "-1", "-i", ambience_wav,
        "-filter_complex", (
            f"[0:a]volume=1.30,apad=pad_dur=2.0[vox];"
            f"[1:a]volume=0.28,afade=t=out:st={total_video_actual - 1.0:.2f}:d=1.0[bg];"
            f"[vox][bg]amix=inputs=2:duration=first[outa]"
        ),
        "-map", "[outa]",
        "-t", f"{total_video_actual:.2f}",
        "-c:a", "aac", "-b:a", "256k",
        soundtrack_master
    ], check=True)

    # 5/5. Concatenação e Render Final
    concat_list = os.path.join(takes_dir, "concat_takes_real.txt")
    with open(concat_list, "w") as f:
        f.write(f"file '{take1_ready.replace(os.sep, '/')}'\n")
        f.write(f"file '{take2_ready.replace(os.sep, '/')}'\n")
        f.write(f"file '{take3_ready.replace(os.sep, '/')}'\n")

    print("5/5. Renderizando Reel Master 9:16 Final...")
    subprocess.run([
        ffmpeg_exe, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-i", soundtrack_master,
        "-vf", "eq=contrast=1.06:brightness=0.01:saturation=1.10,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "copy",
        "-t", f"{total_video_actual:.2f}",
        output_path
    ], check=True)

    final_dur = get_duration(output_path)
    print(f"\n🎉 REEL CONCLUÍDO COM ZERO CORTES DE ÁUDIO!")
    print(f"Arquivo gerado: {output_path}")
    print(f"Duração Final: {final_dur:.2f}s (Narração: {vox_dur:.2f}s — Folga de respiração: {final_dur - vox_dur:.2f}s)")
    return output_path

if __name__ == "__main__":
    take1 = os.path.join(takes_dir, "take1_video.mp4")
    take2 = os.path.join(takes_dir, "take2_video.mp4")
    take3 = os.path.join(takes_dir, "take3_video.mp4")
    narr = os.path.join(takes_dir, "narration.mp3")
    amb = os.path.join(takes_dir, "ambience.wav")
    assemble_master_reel(take1, take2, take3, narr, amb)
