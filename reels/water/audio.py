import numpy as np, wave, os
from scipy.signal import butter, sosfilt, fftconvolve
SR = 44100; T = 85.0; N = int(SR * T)
r = np.random.default_rng(3)
t = np.arange(N) / SR

def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def env(points):
    xs, ys = zip(*points); return np.interp(t, xs, ys)

L = np.zeros(N); Rr = np.zeros(N)
def mix(sig, gain=1.0, pan=0.0):
    L[:] += sig * gain * (1 - pan) ; Rr[:] += sig * gain * (1 + pan)

white = lambda: r.standard_normal(N)
# ambient wind bed
wind = lp(white(), 400) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 9.0))
mix(wind, 0.05 * env([(0, 0), (2, 1), (82, 1), (85, 0)]))
# ocean swells (throne, seas)
ocean = bp(white(), 150, 1800) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 6.5) ** 2)
mix(ocean, 0.07 * env([(0, 0), (13, 0), (14.5, 1), (21.5, 0.4), (29, 0), (46, 0), (47.5, 1.1), (55.5, 0)]), -0.2)
mix(bp(white(), 150, 1800) * (0.5 + 0.5 * np.cos(2 * np.pi * t / 7.3) ** 2),
    0.07 * env([(0, 0), (13, 0), (14.5, 1), (21.5, 0.4), (29, 0), (46, 0), (47.5, 1.1), (55.5, 0)]), 0.2)
# rain
rain = hp(white(), 1500) * 0.5 + bp(white(), 300, 3000) * 0.5
rainenv = env([(0, 0), (29, 0), (30.5, 1), (37.2, 1), (39.5, 0.6), (40.8, 0), (85, 0)])
mix(rain, 0.09 * rainenv, -0.1)
mix(hp(white(), 1500) * 0.5 + bp(white(), 300, 3000) * 0.5, 0.09 * rainenv, 0.1)
# thunder
for th, g in ((31.6, 1.0), (34.6, 0.7)):
    i0 = int(th * SR); n = int(5 * SR)
    seg = lp(r.standard_normal(n), 120, 4) * np.exp(-np.arange(n) / SR * 0.9) * (1 - np.exp(-np.arange(n) / SR * 12))
    seg += lp(r.standard_normal(n), 900) * np.exp(-np.arange(n) / SR * 6) * 0.3
    s = np.zeros(N); s[i0:i0 + n] = seg[:N - i0]; mix(s, 0.9 * g)
# underground rumble + trickle (67:30)
mix(lp(white(), 80, 4), 1.2 * env([(0, 0), (64, 0), (65.5, 1), (68.5, 1), (70, 0.3), (72.5, 0)]))
trick = bp(white(), 2000, 6000) * (0.4 + 0.6 * (r.random(N) > 0.97))
mix(lp(trick, 7000), 0.05 * env([(0, 0), (68.6, 0), (70, 1), (72.4, 0.6), (73, 0)]))

# drops
IR_n = int(2.2 * SR)
IR = r.standard_normal(IR_n) * np.exp(-np.arange(IR_n) / SR * 3.0); IR = lp(IR, 5000); IR /= np.abs(IR).sum() ** 0.5 * 30
drops = np.zeros(N)
def drop(at, g=1.0, f0=None):
    f0 = f0 or r.uniform(500, 900)
    n = int(0.18 * SR); tt = np.arange(n) / SR
    f = f0 * (1 + 1.6 * (1 - np.exp(-tt / 0.03)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-tt / 0.035) * (1 - np.exp(-tt / 0.002))
    i0 = int(at * SR); drops[i0:i0 + n] += s[:N - i0] * g
drop(1.5, 1.0, 650)
for k in range(63):
    drop(7.2 + 3.6 * k / 63 + r.uniform(0, 0.02), 0.18, r.uniform(900, 1600))
for at in (21.6, 23.5, 26.0, 55.7, 59.9):
    drop(at, 0.5)
for at in (72.0, 73.0, 73.8, 74.7, 75.4):
    drop(at, 0.6)
wet = fftconvolve(drops, IR)[:N]
mix(drops * 0.35 + wet * 1.0, 0.8)

out = np.stack([L, Rr], -1)
out *= env([(0, 0), (0.3, 1), (83.5, 1), (85, 0)])[:, None]
out /= np.abs(out).max() / 0.85
w = wave.open(os.path.join(os.path.dirname(__file__), 'audio.wav'), 'wb')
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
print('ok')
