import numpy as np
import soundfile as sf
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sr = 44100
duration = 10.2  # 10.2 segundos
t = np.linspace(0, duration, int(sr * duration), endpoint=False)

# 1. Cinematic Fitness Sub-Bass Drone (warm 50Hz root note + 100Hz harmonic)
drone = 0.25 * np.sin(2 * np.pi * 50 * t) + 0.12 * np.sin(2 * np.pi * 100 * t)
# Rhythmic subtle pulse (LFO a cada 1 segundo simulando batimento/foco)
lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 1.0 * t)
drone = drone * lfo

# 2. Epic Rise / Atmospheric Wash (suave som estéreo espacial)
sweep = np.linspace(80, 240, len(t))
tone_sweep = 0.08 * np.sin(2 * np.pi * sweep * t)

# 3. Textura de fundo suave
noise = np.random.normal(0, 0.02, len(t))
# Low-pass filter simples
window_size = 60
noise_filtered = np.convolve(noise, np.ones(window_size)/window_size, mode='same')

# Fade-in e Fade-out suaves (0.8s)
fade_len = int(sr * 0.8)
fade_in = np.linspace(0, 1, fade_len)
fade_out = np.linspace(1, 0, fade_len)

ambience = drone + tone_sweep + noise_filtered
ambience[:fade_len] *= fade_in
ambience[-fade_len:] *= fade_out

# Normalizar para -16dB
max_val = np.max(np.abs(ambience))
if max_val > 0:
    ambience = ambience / max_val * 0.30

out_path = "c:/Users/User/Desktop/Agentes de venda/apps/api/video_engine/takes/ambience.wav"
sf.write(out_path, ambience, sr)
print(f"Ambiente sonoro fitness gerado em: {out_path}")
