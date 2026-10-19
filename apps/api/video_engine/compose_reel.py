import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

base_dir = r"c:\Users\User\Desktop\Agentes de venda\apps\api\video_engine"
takes_dir = os.path.join(base_dir, "takes")
output_dir = os.path.join(base_dir, "output")
ffmpeg_exe = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"

# 1. Take 1 (0.0s - 3.4s): Dramatic Push-in (1.0 -> 1.08)
take1_img = os.path.join(takes_dir, "take1.jpg")
take1_mp4 = os.path.join(takes_dir, "take1_anim.mp4")
print("1/5. Renderizando Take 1 (Push-in)...")
subprocess.run([
    ffmpeg_exe, "-y",
    "-loop", "1", "-i", take1_img,
    "-vf", (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "zoompan=z='min(zoom+0.0008,1.08)':d=102:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
        "drawtext=text='A MOTIVAÇÃO TE FAZ COMEÇAR...':font=Arial:fontsize=48:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-450:enable='between(t,0.5,3.3)'"
    ),
    "-t", "3.4",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
    take1_mp4
], check=True)

# 2. Take 2 (3.4s - 6.8s): Pan & Tension (1.05 -> 1.12 with slight drift)
take2_img = os.path.join(takes_dir, "take2.jpg")
take2_mp4 = os.path.join(takes_dir, "take2_anim.mp4")
print("2/5. Renderizando Take 2 (Tracking Pan)...")
subprocess.run([
    ffmpeg_exe, "-y",
    "-loop", "1", "-i", take2_img,
    "-vf", (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "zoompan=z='min(zoom+0.0006,1.07)':d=102:x='iw/2-(iw/zoom/2)+sin(on/20)*15':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
        "drawtext=text='MAS É A CONSTÂNCIA QUE CRIA O SHAPE!':font=Arial:fontsize=46:fontcolor=#FFD700:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-450:enable='between(t,0.3,3.3)'"
    ),
    "-t", "3.4",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
    take2_mp4
], check=True)

# 3. Take 3 (6.8s - 10.2s): Confident Hero Push-in (1.0 -> 1.07)
take3_img = os.path.join(takes_dir, "take3.jpg")
take3_mp4 = os.path.join(takes_dir, "take3_anim.mp4")
print("3/5. Renderizando Take 3 (Hero Shot)...")
subprocess.run([
    ffmpeg_exe, "-y",
    "-loop", "1", "-i", take3_img,
    "-vf", (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "zoompan=z='min(zoom+0.0007,1.07)':d=102:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
        "drawtext=text='NUNCA DESISTA DE VOCÊ! 🦁💪':font=Arial:fontsize=50:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-450:enable='between(t,0.3,3.2)'"
    ),
    "-t", "3.4",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
    take3_mp4
], check=True)

# 4. Master Audio Mix (Narração ElevenLabs + Ambience Sub-Bass)
narration_mp3 = os.path.join(takes_dir, "narration.mp3")
ambience_wav = os.path.join(takes_dir, "ambience.wav")
soundtrack_master = os.path.join(takes_dir, "soundtrack_master.aac")

print("4/5. Mixando Master de Áudio (ElevenLabs + Soundscape)...")
# Ajusta narração para 10.2s com atempo suave (1.14x) para sincronia cirúrgica
subprocess.run([
    ffmpeg_exe, "-y",
    "-i", narration_mp3,
    "-i", ambience_wav,
    "-filter_complex", (
        "[0:a]atempo=1.14,volume=1.2[vox];"
        "[1:a]volume=0.35[bg];"
        "[vox][bg]amix=inputs=2:duration=shortest[outa]"
    ),
    "-map", "[outa]",
    "-c:a", "aac", "-b:a", "256k",
    soundtrack_master
], check=True)

# 5. Concatenação e Renderização Final 9:16 (1080x1920)
concat_list = os.path.join(takes_dir, "concat_takes.txt")
with open(concat_list, "w") as f:
    f.write(f"file '{take1_mp4}'\n")
    f.write(f"file '{take2_mp4}'\n")
    f.write(f"file '{take3_mp4}'\n")

final_reel = os.path.join(output_dir, "reel_evandro_motivacional_10s.mp4")

print("5/5. Renderizando Reel Master 9:16 Final...")
subprocess.run([
    ffmpeg_exe, "-y",
    "-f", "concat", "-safe", "0", "-i", concat_list,
    "-i", soundtrack_master,
    "-vf", (
        "eq=contrast=1.06:brightness=0.01:saturation=1.12,"
        "format=yuv420p"
    ),
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "17",
    "-c:a", "copy",
    "-shortest",
    final_reel
], check=True)

print(f"\n🎉 REEL FINAL CONCLUÍDO COM SUCESSO ABSOLUTO!")
print(f"Arquivo gerado: {final_reel}")
print(f"Tamanho: {os.path.getsize(final_reel)} bytes")
