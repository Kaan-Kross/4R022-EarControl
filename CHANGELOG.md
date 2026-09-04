# Değişiklik Günlüğü (Changelog)

Bu proje [Semantic Versioning](https://semver.org/lang/tr/) kurallarını
takip eder. Format [Keep a Changelog](https://keepachangelog.com/tr/)
temel alınarak hazırlanmıştır.

Açıklamalar önce **Türkçe**, ardından **English** olarak verilmiştir.

---

## [1.8.0] — 2026 — Ana Ses Kaldırıldı, macOS Desteği Sonlandırıldı, Performans ve Arayüz İyileştirmeleri

### 🇹🇷 Türkçe

#### Kaldırıldı
- **Ana Ses (Master Volume) kontrolü tamamen kaldırıldı.** Güvenilir
  biçimde algılanamaması nedeniyle Kontrol Paneli ve Hızlı Panel'deki
  Ana Ses çubukları, ilgili tüm sinyaller ve arka uç metodları
  kaldırıldı. Sistem sesi artık işletim sisteminin kendi ses
  denetimiyle yönetilmelidir.
- **macOS desteği sonlandırıldı.** macOS zaten yalnızca Ana Ses'i
  destekliyordu; bu kaldırılınca platformun tek işlevi de ortadan
  kalktı. macOS'ta uygulama artık net bir "Platform Desteklenmiyor"
  uyarısı gösterir; build matrisinden ve dokümantasyondan çıkarıldı.

#### Değişti
- **Linux desteği geliştirildi**: Aynı process ID'sine (pid) birden
  fazla ses akışı (sink-input) oluşturan uygulamalarda (ör. Chrome'da
  her sekme ayrı bir akım açar) artık TÜM akışlar tek bir uygulama
  kartı altında birlikte kontrol ediliyor. Önceki sürümde yalnızca son
  görülen akış kontrol ediliyordu; bu da bazı sekmelerin sessize
  alınamamasına yol açıyordu.
- **Hakkında sayfası**: Elle çizilmiş "4R" rozeti ve ayrı metin başlığı
  kaldırıldı; yerine uygulamanın tam logosu (assets/logo_full.png)
  gösteriliyor.
- **Performans**: Kontrol Paneli ve Hızlı Panel her ikisi de gizliyken
  ses ölçer güncellemesi tamamen duruyor, oturum taraması ise çok daha
  seyrek bir aralığa düşüyor — arka planda gereksiz CPU kullanımı
  (özellikle Windows'ta COM çağrıları) azaltıldı.
- **Arayüz**: Uygulama kartlarındaki uzun isimler artık taşmıyor; sonu
  "…" ile kırpılıyor, tam isim üzerine gelince (tooltip) görünüyor.
  Varsayılan/minimum pencere boyutu büyütüldü.

#### Düzeltildi
- `Build/4R022_EarControl.spec` dosyasındaki, PYZ/EXE bloklarının
  yanlışlıkla iki kez tanımlandığı kopyala-yapıştır hatası giderildi.
- Başlangıç akışındaki işlevsiz (no-op) ölü kod bloğu temizlendi.

### 🇬🇧 English

#### Removed
- **Master Volume control has been completely removed.** Because it
  could not be reliably detected, the Master Volume bars in both the
  Dashboard and Quick Panel, all related signals, and the backend
  methods behind them have been removed. System volume should now be
  managed through the operating system's own audio controls.
- **macOS support has been discontinued.** macOS already supported
  Master Volume only; removing it left the platform with no remaining
  functionality. The app now shows a clear "Platform Not Supported"
  warning on macOS, and it has been removed from the build matrix and
  documentation.

#### Changed
- **Improved Linux support**: applications that open multiple audio
  streams (sink-inputs) under the same process ID (e.g. Chrome opens
  one stream per tab) are now controlled as a single unit under one
  app card. Previously only the last-seen stream was controlled, which
  meant some tabs couldn't be muted.
- **About page**: the hand-drawn "4R" badge and separate text title
  have been replaced with the app's full logo (assets/logo_full.png).
- **Performance**: peak-meter updates stop entirely while both the
  Dashboard and Quick Panel are hidden, and session scanning falls
  back to a much slower interval — reducing unnecessary background CPU
  usage (especially Windows COM calls).
- **UI**: long app names in cards no longer overflow — they're elided
  with "…" and shown in full via tooltip. The default/minimum window
  size was increased.

#### Fixed
- Fixed a copy-paste bug in `Build/4R022_EarControl.spec` where the
  PYZ/EXE blocks were accidentally defined twice.
- Cleaned up a dead, no-op code block in the startup flow.

---

## [1.7.5] — 2026 — Hata Düzeltmeleri, Animasyonlar ve Arayüz Yenilemesi

### 🇹🇷 Türkçe

#### Düzeltildi
- **Ana Ses hatası**: Ana ses seviyesini yükseltirken kısa süre sonra
  otomatik olarak %0'a düşme sorunu giderildi. Artık her platform arka
  ucu, bir okuma başarısız olduğunda gerçek %0 yerine "bilinmiyor"
  durumunu bildiriyor; ses motoru da yakın zamanda yapılan bir
  değişiklikten sonraki birkaç saniye boyunca kendi bildiği değere
  güvenip gereksiz/riskli yeniden okumayı erteliyor.
- **Dil senkronizasyon hatası**: Dil, sistem tepsisi sağ tık menüsünden
  değiştirildiğinde, Ayarlar sekmesindeki dil seçim kutusu artık doğru
  şekilde güncelleniyor.

#### Eklenenler
- **Animasyonlu sekme geçişleri**: Uygulamalar / Ayarlar / Hakkında
  arasında geçiş yaparken, sekme altındaki vurgu çizgisi artık anında
  "ışınlanmak" yerine yumuşakça kayarak hareket ediyor; sayfa içeriği de
  hafif bir fade-in ile beliriyor.
- **Yeniden tasarlanan Hakkında sayfası**: Rozet ve başlık içeren bir üst
  kart, ayrı bir açıklama kartı ve Geliştirici / Sürüm / Platform / Lisans
  bilgilerini gösteren ikonlu bir 2x2 bilgi ızgarası ile daha profesyonel
  bir görünüme kavuştu.
- **Uygulama kartlarına gölge efekti**: Daha belirgin bir derinlik hissi
  için ince bir gölge eklendi.
- **Gerçek "Listeden Gizle" özelliği**: Bir uygulama kartına sağ
  tıklayarak onu listeden kalıcı olarak gizleyebilirsiniz; Ayarlar
  sekmesinden "Gizlenenleri Göster" ile tek tıkla geri getirebilirsiniz
  (önceki sürümde bu metinler arayüzde tanımlıydı ama hiçbir işleve bağlı
  değildi — artık tamamen gerçek ve işlevsel).

### 🇬🇧 English

#### Fixed
- **Master Volume bug**: Fixed an issue where raising the master volume
  would shortly snap back to 0%. Every platform backend now reports an
  "unknown" read failure instead of a misleading real 0%, and the audio
  engine trusts its own recently-set value for a couple of seconds after
  a local change instead of immediately re-querying a possibly stale
  system state.
- **Language sync bug**: The language selector in the Settings tab now
  correctly updates when the language is changed from the system tray's
  right-click menu.

#### Added
- **Animated tab transitions**: Switching between Applications / Settings
  / About now shows the tab underline sliding smoothly instead of
  instantly "teleporting", and the page content fades in gently.
- **Redesigned About page**: A more professional layout with a badge +
  title header card, a separate description card, and a 2x2 icon-labeled
  info grid for Developer / Version / Platform / License.
- **Card shadow effect**: A subtle drop shadow was added to app cards for
  a more layered, polished look.
- **Real "Hide from List" feature**: Right-click any app card to
  permanently hide it from the list; bring it back anytime with "Show
  Hidden" in Settings (previously these strings existed in the UI but
  were not wired to any functionality — now fully real and working).

---

## [1.5.0] — 2026 — İlk Genel Sürüm (Initial Public Release)

### 🇹🇷 Türkçe

#### Eklenenler
- Uygulama başına ses seviyesi, sessize alma ve gerçek zamanlı ses ölçer
  (peak meter) desteği (EarTrumpet tarzı ses karıştırıcı).
- Sağ altta çalışan sistem tepsisi simgesi; üzerine tıklandığında açılan,
  hızlı kontrol sunan **Hızlı Panel** (Quick Panel).
- Tam özellikli **Kontrol Paneli** (Dashboard): Uygulamalar, Ayarlar ve
  Hakkında sekmeleri.
- Üstte **"Tümünü Sustur" / "Tümünü Aç"** hızlı mod düğmeleri.
- Her uygulama için özenle tasarlanmış, ayrık **kart** görünümü: ikon, isim,
  yüzde göstergesi, animasyonlu ses çubuğu ve anlık ses ölçer.
- **Ana Ses (Master Volume)** çubuğu — hem Kontrol Panelinde hem Hızlı
  Panelde.
- Tam **Türkçe / İngilizce** dil desteği; anlık dil değişimi (yeniden
  başlatma gerektirmez).
- **3 platform desteği**: Windows (pycaw), Linux (pactl / PulseAudio /
  PipeWire-Pulse) ve macOS (yalnızca ana ses — bkz. Bilinen Sınırlamalar).
- Çalışan bir **EarTrumpet** algılandığında bilgilendirici tepsi bildirimi;
  aynı sistem API'lerini paylaştığından çakışmadan birlikte çalışır.
- "Sistem Sesleri" oturumu için özel çizilmiş bilgisayar/hoparlör ikonu.
- Windows ile otomatik başlatma seçeneği (kayıt defteri, ek bağımlılık yok).
- Tek örnek (single instance) koruması — uygulama zaten açıksa ikinci bir
  pencere yerine mevcut tepsi simgesi kullanılır.
- Atomik, kendi kendini onaran (self-healing) JSON tabanlı ayar dosyası.
- 4R022 marka kimliği: Siyah / Bordo / Gri renk paleti, özel logo ve ikon
  seti (tam logo + küçük boyutlarda okunaklı amblem versiyonu).
- Düzenli proje yapısı: uygulama kodu `core/` paketinde, giriş noktası
  `Main/` klasöründe, build araçları (`.spec`, `build.bat`, `build.sh`)
  `Build/` klasöründe toplandı.

#### Bilinen Sınırlamalar
- **macOS**: İşletim sistemi, uygulama başına ses kontrolü için genel bir
  API sunmadığından, bu platformda yalnızca ana sistem sesi kontrol
  edilebilir.
- **Linux**: Gerçek zamanlı ses ölçer, PulseAudio'nun senkron API'sinin
  sınırları nedeniyle "aktiflik göstergesi" (ayarlı ses seviyesine dayalı)
  olarak çalışır; Windows'taki kadar hassas gerçek RMS/peak değeri değildir.

---

### 🇬🇧 English

#### Added
- Per-application volume, mute, and real-time peak meter support
  (EarTrumpet-style audio mixer).
- A background system tray icon; clicking it opens a compact **Quick
  Panel** for fast control.
- A full-featured **Dashboard** with Applications, Settings, and About
  tabs.
- Top-level **"Mute All" / "Unmute All"** quick mode buttons.
- Carefully designed, distinctly separated **cards** for each app: icon,
  name, percentage readout, animated volume bar, and live peak meter.
- A **Master Volume** bar — available in both the Dashboard and the Quick
  Panel.
- Full **Turkish / English** language support with instant switching (no
  restart required).
- **3-platform support**: Windows (pycaw), Linux (pactl / PulseAudio /
  PipeWire-Pulse), and macOS (master volume only — see Known Limitations).
- Informative tray notification when a running **EarTrumpet** instance is
  detected; runs alongside it without conflict since both share the same
  system APIs.
- A custom-drawn computer/speaker icon for the "System Sounds" session.
- Optional start-with-Windows via the registry (no extra dependency).
- Single-instance protection — launching the app again focuses the
  existing tray icon instead of opening a duplicate window.
- Atomic, self-healing JSON-based settings storage.
- 4R022 brand identity: Black / Bordeaux / Gray color palette, a custom
  logo, and an icon set (full logo + a small-size-legible mark variant).
- Clean project layout: application code lives in the `core/` package,
  the entry point lives in `Main/`, and all build tooling (`.spec`,
  `build.bat`, `build.sh`) is grouped under `Build/`.

#### Known Limitations
- **macOS**: Since the OS does not expose a public per-application volume
  API, only the master system volume can be controlled on this platform.
- **Linux**: Real-time metering runs as an "activity indicator" (based on
  the configured volume level) due to the limits of PulseAudio's
  synchronous API; it is not as precise as the true RMS/peak values
  available on Windows.
