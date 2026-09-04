"""
4R022 Ear Control - Dil Modülü (i18n)
======================================
Türkçe varsayılan, İngilizce alternatif. Tüm arayüz metinleri buradan çekilir.
"""

from __future__ import annotations

STRINGS = {
    "tr": {
        "app_title": "4R022 Ear Control",
        "app_subtitle": "Uygulama Bazlı Ses Yönetimi",
        "tab_mixer": "Uygulamalar",
        "tab_settings": "Ayarlar",
        "tab_about": "Hakkında",
        "mute_all": "Tümünü Sustur",
        "unmute_all": "Tümünü Aç",
        "no_sessions": "Şu anda ses çalan bir uygulama yok.",
        "no_sessions_hint": "Bir uygulama ses çalmaya başladığında burada görünecek.",
        "system_sounds": "Sistem Sesleri",
        "muted": "Sessiz",
        "settings_language": "Dil",
        "settings_language_hint": "Arayüz dilini değiştirin.",
        "settings_startup": "Windows ile başlat",
        "settings_startup_hint": "Bilgisayar açıldığında 4R022 Ear Control arka planda otomatik başlar.",
        "settings_start_minimized": "Simge durumunda başlat",
        "settings_start_minimized_hint": "Uygulama açılışta doğrudan sistem tepsisine küçültülür.",
        "settings_notifications": "Bildirimleri göster",
        "settings_notifications_hint": "Tümünü sustur / aç gibi işlemlerde tepsi bildirimi göster.",
        "settings_reset": "Sıfırla",
        "settings_reset_hint": "Tüm ayarları ve hatırlanan ses seviyelerini varsayılana döndürür.",
        "settings_reset_confirm_title": "Ayarları Sıfırla",
        "settings_reset_confirm_body": "Tüm ayarlar ve hatırlanan uygulama ses seviyeleri silinecek. Emin misiniz?",
        "settings_saved": "Ayarlar kaydedildi.",
        "about_desc": (
            "4R022 Ear Control, çalışan her uygulamanın sesini ayrı ayrı görmenizi, "
            "yükseltmenizi, kısmanızı ve susturmanızı sağlayan profesyonel bir "
            "ses karıştırıcısıdır. Windows Ses Karıştırıcısı ile aynı sistem "
            "arayüzlerini kullanır; EarTrumpet gibi diğer ses araçlarıyla "
            "çakışmadan birlikte çalışır."
        ),
        "about_developer": "Geliştirici",
        "about_version": "Sürüm",
        "about_license": "Lisans",
        "about_license_text": "Tescilli Yazılım — 4R022 / Kaan Kross. Tersine mühendislik yapılamaz.",
        "about_github": "GitHub",
        "tray_open_dashboard": "Kontrol Panelini Aç",
        "tray_mute_all": "Tümünü Sustur",
        "tray_unmute_all": "Tümünü Aç",
        "tray_language": "Dil / Language",
        "tray_exit": "Çıkış",
        "tray_tooltip": "4R022 Ear Control — Ses Yönetimi",
        "notif_muted_all_title": "Tüm Sesler Susturuldu",
        "notif_muted_all_body": "Tüm uygulamaların sesi susturuldu.",
        "notif_unmuted_all_title": "Tüm Sesler Açıldı",
        "notif_unmuted_all_body": "Tüm uygulamaların sesi geri açıldı.",
        "search_placeholder": "Uygulama ara...",
        "hide_app": "Listeden Gizle",
        "show_hidden": "Gizlenenleri Göster",
        "hidden_apps_count": "Şu anda {n} uygulama gizli.",
        "eartrumpet_detected": "EarTrumpet algılandı — uyumlu modda çalışılıyor.",
        "restore_defaults": "Varsayılana Getir",
        "quick_panel_title": "Hızlı Ses Kontrolü",
        "platform_note_unsupported_title": "Platform Desteklenmiyor",
        "platform_note_unsupported_body": (
            "4R022 Ear Control şu anda yalnızca Windows ve Linux'u "
            "destekliyor. Bu platformda uygulama başına ses kontrolü "
            "kullanılamıyor."
        ),
        "platform_windows": "Windows",
        "platform_linux": "Linux",
        "platform_unsupported": "Desteklenmiyor",
        "platform_label": "Platform",
    },
    "en": {
        "app_title": "4R022 Ear Control",
        "app_subtitle": "Per-App Volume Management",
        "tab_mixer": "Applications",
        "tab_settings": "Settings",
        "tab_about": "About",
        "mute_all": "Mute All",
        "unmute_all": "Unmute All",
        "no_sessions": "No application is currently playing audio.",
        "no_sessions_hint": "It will appear here once an app starts playing sound.",
        "system_sounds": "System Sounds",
        "muted": "Muted",
        "settings_language": "Language",
        "settings_language_hint": "Change the interface language.",
        "settings_startup": "Start with Windows",
        "settings_startup_hint": "4R022 Ear Control launches automatically in the background at boot.",
        "settings_start_minimized": "Start minimized",
        "settings_start_minimized_hint": "The app launches straight into the system tray.",
        "settings_notifications": "Show notifications",
        "settings_notifications_hint": "Show a tray notification for actions like Mute All / Unmute All.",
        "settings_reset": "Reset",
        "settings_reset_hint": "Restores all settings and remembered app volumes to default.",
        "settings_reset_confirm_title": "Reset Settings",
        "settings_reset_confirm_body": "All settings and remembered app volumes will be deleted. Are you sure?",
        "settings_saved": "Settings saved.",
        "about_desc": (
            "4R022 Ear Control is a professional audio mixer that lets you see, "
            "raise, lower, and mute the volume of every running application "
            "individually. It uses the same system APIs as the Windows Volume "
            "Mixer, so it works alongside tools like EarTrumpet without conflict."
        ),
        "about_developer": "Developer",
        "about_version": "Version",
        "about_license": "License",
        "about_license_text": "Proprietary Software — 4R022 / Kaan Kross. Reverse engineering prohibited.",
        "about_github": "GitHub",
        "tray_open_dashboard": "Open Dashboard",
        "tray_mute_all": "Mute All",
        "tray_unmute_all": "Unmute All",
        "tray_language": "Language / Dil",
        "tray_exit": "Exit",
        "tray_tooltip": "4R022 Ear Control — Volume Manager",
        "notif_muted_all_title": "All Sounds Muted",
        "notif_muted_all_body": "All applications have been muted.",
        "notif_unmuted_all_title": "All Sounds Unmuted",
        "notif_unmuted_all_body": "All applications have been unmuted.",
        "search_placeholder": "Search apps...",
        "hide_app": "Hide from List",
        "show_hidden": "Show Hidden",
        "hidden_apps_count": "{n} app(s) currently hidden.",
        "eartrumpet_detected": "EarTrumpet detected — running in compatible mode.",
        "restore_defaults": "Restore Default",
        "quick_panel_title": "Quick Volume Control",
        "platform_note_unsupported_title": "Platform Not Supported",
        "platform_note_unsupported_body": (
            "4R022 Ear Control currently supports Windows and Linux only. "
            "Per-application volume control is not available on this "
            "platform."
        ),
        "platform_windows": "Windows",
        "platform_linux": "Linux",
        "platform_unsupported": "Unsupported",
        "platform_label": "Platform",
    },
}


class Translator:
    def __init__(self, language: str = "tr") -> None:
        self.language = language if language in STRINGS else "tr"

    def set_language(self, language: str) -> None:
        self.language = language if language in STRINGS else "tr"

    def t(self, key: str) -> str:
        return STRINGS.get(self.language, STRINGS["tr"]).get(key, key)

    def __call__(self, key: str) -> str:
        return self.t(key)
