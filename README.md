<div align="center">

# 4R022 Ear Control

**Uygulama Bazlı Profesyonel Ses Yönetimi** · **Per-App Professional Volume Management**

![Version](https://img.shields.io/badge/s%C3%BCr%C3%BCm%20%2F%20version-1.8.0-7a1f2b?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-1b1b1f?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-8a2332?style=flat-square)
![License](https://img.shields.io/badge/license-Proprietary-c23348?style=flat-square)

</div>

---

## 🇹🇷 Türkçe

### 4R022 Ear Control Nedir?

**4R022 Ear Control**, çalışan her uygulamanın sesini **ayrı ayrı** görmenizi,
yükseltmenizi, kısmanızı ve susturmanızı sağlayan; **EarTrumpet** tarzında
çalışan, arka planda sessizce duran ve sistem tepsisinden anında erişilebilen
profesyonel bir masaüstü ses karıştırıcısıdır.

Windows'un kendi Ses Karıştırıcısı ile **aynı sistem API'lerini** kullanır;
bu yüzden EarTrumpet gibi başka ses araçlarıyla **çakışmadan, uyumlu bir
şekilde** birlikte çalışır.

Bu projeyi tercih ettiğiniz için teşekkürler — bkz. [TEŞEKKÜRLER](TESEKKURLER.md).

### ✨ Özellikler

- 🎚️ **Uygulama bazlı ses kontrolü** — her uygulama için ayrı, animasyonlu ses çubuğu
- 🔇 **Tek tıkla sessize alma** — her kart üzerinde yuvarlak mute düğmesi
- 📊 **Gerçek zamanlı ses ölçer** — her kartın altında anlık ses seviyesi (peak meter)
- 🃏 **Özenle tasarlanmış kartlar** — birleşik değil, her uygulama kendi kartında; ikon, isim, yüzde göstergesi; uzun uygulama adları taşmaz, sonu "…" ile kırpılır (tam ad üzerine gelince görünür)
- ⚡ **Tümünü Sustur / Tümünü Aç** — tek tuşla tüm uygulamaları kontrol edin
- 🖥️ **Sistem tepsisi entegrasyonu** — sağ altta çalışır, tıklayınca EarTrumpet tarzı Hızlı Panel açılır
- 🎛️ **Tam Kontrol Paneli** — Uygulamalar, Ayarlar ve Hakkında sekmeleri
- 🌍 **Türkçe / İngilizce** — anlık dil değişimi, yeniden başlatma gerektirmez
- 🔄 **EarTrumpet uyumluluğu** — çalışırken algılanır, çakışmadan birlikte kullanılabilir
- 🚀 **Windows ile otomatik başlatma** — arka planda sessizce açılır
- 💾 **Kendi kendini onaran ayarlar** — bozulma durumunda otomatik yedekten kurtarma
- 🖥️🐧 **2 platform desteği** — Windows ve Linux (bkz. platform tablosu)
- ⚙️ **Daha düşük arka plan CPU kullanımı** — pencereler gizliyken tarama/ölçüm otomatik olarak yavaşlar veya durur

### 🖥️ Platform Desteği

| Platform | Uygulama Başına Ses | Sessize Alma | Ses Ölçer |
|---|:---:|:---:|:---:|
| **Windows** | ✅ Tam destek (pycaw) | ✅ | ✅ Gerçek zamanlı |
| **Linux** | ✅ Tam destek (pactl) — çoklu akışlı uygulamalarda (ör. Chrome sekmeleri) birleşik kontrol | ✅ | ⚠️ Yaklaşık (aktiflik göstergesi) |

<sub>macOS bu sürümde desteklenmemektedir: işletim sistemi uygulama
başına ses kontrolü için genel bir API sunmadığından, bu platformda
uygulama açıldığında net bir "desteklenmiyor" bildirimi gösterilir.</sub>

### 📦 Kurulum

#### Windows
```bash
pip install -r requirements.txt
python Main/main.py
```

#### Linux
`pactl` komutunun kurulu olduğundan emin olun (PulseAudio veya
PipeWire-Pulse ile birlikte gelir — çoğu dağıtımda zaten hazırdır):
```bash
sudo apt install pulseaudio-utils   # Debian/Ubuntu örneği
pip install -r requirements.txt
python Main/main.py
```

### 🔨 Otomatik Build (.exe / çalıştırılabilir dosya)

Tüm build araçları **`Build/`** klasöründe toplanmıştır. Betikler nereden
çalıştırılırsa çalıştırılsın otomatik olarak proje köküne geçer,
bağımlılıkları izole bir sanal ortama (`.venv`) kurar, `Build/4R022_EarControl.spec`
dosyasını kullanarak doğru platforma özel ikonu seçer ve derler. Elle
PyInstaller komutu yazmanıza gerek yoktur.

#### Windows
`Build\build.bat` dosyasına **çift tıklayın**, ya da terminalden:
```bat
Build\build.bat
```
Çıktı: proje kökünde `dist\4R022_EarControl.exe`

#### Linux
```bash
./Build/build.sh
```
Çıktı: proje kökünde `dist/4R022_EarControl`

#### Elle (ileri seviye)
Proje kökünden çalıştırın:
```bash
pip install -r requirements.txt
pyinstaller --noconfirm Build/4R022_EarControl.spec
```

> 🤖 **Otomatik CI/CD**: Depoya bir sürüm etiketi (`v*.*.*`) push edildiğinde,
> `.github/workflows/build.yml` GitHub Actions üzerinden Windows ve Linux
> için otomatik olarak 2 ayrı build üretir ve Artifact olarak yükler —
> hiçbir yerel kurulum gerekmeden.

### 🧩 Mimari

```
4R022_EarControl/
├── Main/
│   └── main.py                # Giriş noktası, sinyal kablolaması, tek örnek koruması
├── Build/
│   ├── 4R022_EarControl.spec   # PyInstaller derleme tarifi (2 platform, otomatik ikon seçimi)
│   ├── build.bat                # Windows için tek tıkla otomatik build
│   └── build.sh                 # Linux için tek komutla otomatik build
├── requirements.txt
├── core/
│   ├── assets.py                 # assets/ klasörünün yolunu çözen ortak yardımcı (dev + paketlenmiş)
│   ├── config.py                 # Atomik/kendi kendini onaran JSON ayar yöneticisi
│   ├── i18n.py                   # Türkçe / İngilizce metinler
│   ├── theme.py                  # Siyah / Bordo / Gri marka teması (QSS)
│   ├── widgets.py                # AnimatedVolumeSlider, MeterBar, AppCard, ElidingLabel
│   ├── dashboard.py              # Ana pencere: Uygulamalar / Ayarlar / Hakkında
│   ├── tray.py                   # Sistem tepsisi + Hızlı Panel (EarTrumpet tarzı flyout)
│   ├── audio_engine.py           # Platformdan bağımsız facade
│   └── audio_backends/
│       ├── base.py                # Ortak veri yapısı, arayüz ve UnsupportedAudioBackend
│       ├── windows_backend.py      # pycaw tabanlı tam destek
│       └── linux_backend.py        # pactl tabanlı tam destek (çoklu akış gruplama dahil)
└── assets/                     # app.ico, tray_icon.ico, logo_full.png
```

### ⚠️ Bilinen Sınırlamalar

- **macOS desteklenmiyor**: Uygulama, macOS'ta çalıştırıldığında açıkça
  "platform desteklenmiyor" uyarısı gösterir.
- **Linux**: Ses ölçer, gerçek RMS/peak değeri yerine "aktiflik göstergesi"
  (ayarlı ses seviyesine dayalı) olarak çalışır.

Detaylar için [CHANGELOG.md](CHANGELOG.md) dosyasına bakın.

### 📄 Lisans

Bu proje tescillidir. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.
Tersine mühendislik ve izinsiz yeniden dağıtım yasaktır.

### 🙏 Teşekkürler

Bu projeyi seçtiğiniz için içtenlikle teşekkür ederim — detaylar için
[TEŞEKKÜRLER.md](TESEKKURLER.md).

---
---

## 🇬🇧 English

### What is 4R022 Ear Control?

**4R022 Ear Control** is a professional desktop audio mixer that lets you
see, raise, lower, and mute the volume of every running application
**individually** — EarTrumpet-style, running quietly in the background
and instantly accessible from the system tray.

It uses the **same system APIs** as the Windows Volume Mixer, so it works
**alongside tools like EarTrumpet without conflict**.

Thank you for choosing this project — see [TESEKKURLER.md](TESEKKURLER.md).

### ✨ Features

- 🎚️ **Per-application volume control** — a separate, animated volume bar for each app
- 🔇 **One-click mute** — a round mute button on every card
- 📊 **Real-time peak meter** — live volume level shown under each card
- 🃏 **Carefully designed cards** — each app in its own distinct card, not merged into a flat list; icon, name, percentage readout; long app names no longer overflow — they're elided with "…" (full name shown on hover)
- ⚡ **Mute All / Unmute All** — control every app with one button
- 🖥️ **System tray integration** — runs in the background, click to open an EarTrumpet-style Quick Panel
- 🎛️ **Full Dashboard** — Applications, Settings, and About tabs
- 🌍 **Turkish / English** — instant language switching, no restart needed
- 🔄 **EarTrumpet compatibility** — detected automatically, coexists without conflict
- 🚀 **Start with Windows** — launches quietly in the background
- 💾 **Self-healing settings** — automatically recovers from a corrupted config file
- 🖥️🐧 **2-platform support** — Windows and Linux (see platform table)
- ⚙️ **Lower background CPU usage** — session scanning and metering automatically slow down or pause while all windows are hidden

### 🖥️ Platform Support

| Platform | Per-App Volume | Mute | Peak Meter |
|---|:---:|:---:|:---:|
| **Windows** | ✅ Full support (pycaw) | ✅ | ✅ Real-time |
| **Linux** | ✅ Full support (pactl) — apps with multiple streams (e.g. Chrome tabs) are controlled as one unit | ✅ | ⚠️ Approximate (activity indicator) |

<sub>macOS is not supported in this release: the OS does not expose a
public API for per-application volume control, so launching the app on
macOS shows a clear "platform not supported" notice.</sub>

### 📦 Installation

#### Windows
```bash
pip install -r requirements.txt
python Main/main.py
```

#### Linux
Make sure `pactl` is installed (ships with PulseAudio or
PipeWire-Pulse — already present on most distributions):
```bash
sudo apt install pulseaudio-utils   # Debian/Ubuntu example
pip install -r requirements.txt
python Main/main.py
```

### 🔨 Automatic Build (.exe / executable)

All build tooling lives in the **`Build/`** folder. The scripts
automatically move to the project root regardless of where they're run
from, install dependencies into an isolated virtual environment
(`.venv`), and build using `Build/4R022_EarControl.spec`, which picks the
correct platform-specific icon on its own. No need to type a manual
PyInstaller command.

#### Windows
**Double-click** `Build\build.bat`, or from a terminal:
```bat
Build\build.bat
```
Output: `dist\4R022_EarControl.exe` (at the project root)

#### Linux
```bash
./Build/build.sh
```
Output: `dist/4R022_EarControl` (at the project root)

#### Manual (advanced)
Run from the project root:
```bash
pip install -r requirements.txt
pyinstaller --noconfirm Build/4R022_EarControl.spec
```

> 🤖 **Automatic CI/CD**: Pushing a version tag (`v*.*.*`) to the repo
> triggers `.github/workflows/build.yml`, which builds Windows and Linux
> binaries automatically via GitHub Actions and uploads them as artifacts
> — no local setup required.

### 🧩 Architecture

```
4R022_EarControl/
├── Main/
│   └── main.py                # Entry point, signal wiring, single-instance guard
├── Build/
│   ├── 4R022_EarControl.spec   # PyInstaller build spec (2 platforms, auto icon selection)
│   ├── build.bat                # One-click automatic build for Windows
│   └── build.sh                 # One-command automatic build for Linux
├── requirements.txt
├── core/
│   ├── assets.py                 # Shared assets/ path resolver (dev + frozen)
│   ├── config.py                 # Atomic, self-healing JSON settings manager
│   ├── i18n.py                   # Turkish / English strings
│   ├── theme.py                  # Black / Bordeaux / Gray brand theme (QSS)
│   ├── widgets.py                # AnimatedVolumeSlider, MeterBar, AppCard, ElidingLabel
│   ├── dashboard.py              # Main window: Applications / Settings / About
│   ├── tray.py                   # System tray + Quick Panel (EarTrumpet-style flyout)
│   ├── audio_engine.py           # Platform-independent facade
│   └── audio_backends/
│       ├── base.py                # Shared data structure, interface, and UnsupportedAudioBackend
│       ├── windows_backend.py      # Full support via pycaw
│       └── linux_backend.py        # Full support via pactl (with multi-stream grouping)
└── assets/                     # app.ico, tray_icon.ico, logo_full.png
```

### ⚠️ Known Limitations

- **macOS is not supported**: the app shows a clear "platform not
  supported" warning when launched on macOS.
- **Linux**: The peak meter works as an "activity indicator" (based on the
  configured volume level) rather than a true RMS/peak value.

See [CHANGELOG.md](CHANGELOG.md) for details.

### 📄 License

This project is proprietary software. See [LICENSE](LICENSE) for details.
Reverse engineering and unauthorized redistribution are prohibited.

### 🙏 Thanks

Sincere thanks for choosing this project — see
[TESEKKURLER.md](TESEKKURLER.md) for details.

---

<div align="center">

**4R022** © 2026 — Kaan Kross

</div>
