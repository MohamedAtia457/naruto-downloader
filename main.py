import os
import threading
import webbrowser
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout

KV = r"""
<RootWidget>:
    orientation: "vertical"
    padding: "20dp"
    spacing: "12dp"
    canvas.before:
        Color:
            rgba: (0.055, 0.075, 0.12, 1)
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "🎬 تنزيل الفيديوهات"
        font_size: "25sp"
        bold: True
        size_hint_y: None
        height: "55dp"
        color: (0.35, 0.8, 1, 1)

    Label:
        text: "أدخل رابط فيديو تملك حق تنزيله"
        font_size: "16sp"
        size_hint_y: None
        height: "32dp"
        color: (0.9, 0.93, 1, 1)

    TextInput:
        id: url_input
        hint_text: "https://..."
        multiline: False
        size_hint_y: None
        height: "52dp"
        font_size: "15sp"
        padding: ["12dp", "14dp"]
        background_color: (0.12, 0.15, 0.22, 1)
        foreground_color: (1, 1, 1, 1)
        cursor_color: (0.35, 0.8, 1, 1)

    Button:
        text: "بدء التنزيل"
        size_hint_y: None
        height: "52dp"
        font_size: "18sp"
        bold: True
        background_normal: ""
        background_color: (0.08, 0.52, 0.78, 1)
        disabled: root.busy
        on_release: root.start_download(url_input.text)

    Button:
        text: "فتح قناة المطوّر على تيليجرام"
        size_hint_y: None
        height: "44dp"
        font_size: "15sp"
        background_normal: ""
        background_color: (0.18, 0.22, 0.31, 1)
        on_release: root.open_channel()

    Label:
        text: root.status
        font_size: "15sp"
        color: (0.9, 0.94, 1, 1)
        text_size: self.width, None
        halign: "center"
        valign: "middle"

    Widget:

    Label:
        text: "يحفظ التطبيق الملفات داخل مجلد بيانات التطبيق. قد لا تعمل بعض الروابط المحمية أو الخاصة."
        font_size: "12sp"
        color: (0.65, 0.7, 0.8, 1)
        size_hint_y: None
        height: "44dp"
        text_size: self.width, None
        halign: "center"
"""

class RootWidget(BoxLayout):
    status = StringProperty("جاهز للتنزيل")
    busy = BooleanProperty(False)

    def open_channel(self):
        webbrowser.open("https://t.me/na_tltl")

    def start_download(self, url):
        url = (url or "").strip()
        if not url:
            self.status = "من فضلك أدخل رابط الفيديو أولاً."
            return
        if not (url.startswith("https://") or url.startswith("http://")):
            self.status = "الرابط غير صحيح. استخدم رابطاً يبدأ بـ http أو https."
            return
        self.busy = True
        self.status = "جارٍ تجهيز التنزيل..."
        threading.Thread(target=self._download_worker, args=(url,), daemon=True).start()

    def _download_worker(self, url):
        try:
            import yt_dlp
            from kivy.app import App
            app = App.get_running_app()
            download_dir = os.path.join(app.user_data_dir, "NARUTO")
            os.makedirs(download_dir, exist_ok=True)

            def progress_hook(data):
                if data.get("status") == "downloading":
                    total = data.get("total_bytes") or data.get("total_bytes_estimate")
                    done = data.get("downloaded_bytes", 0)
                    if total:
                        pct = int(done * 100 / total)
                        Clock.schedule_once(lambda dt, p=pct: self._set_status(f"جارٍ التنزيل... {p}%"))
                elif data.get("status") == "finished":
                    Clock.schedule_once(lambda dt: self._set_status("اكتمل التنزيل، جارٍ حفظ الملف..."))

            opts = {
                "outtmpl": os.path.join(download_dir, "%(title).150s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "progress_hooks": [progress_hook],
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            Clock.schedule_once(lambda dt: self._finish("انتهى التنزيل. ستجد الملف داخل بيانات التطبيق في مجلد NARUTO."))
        except Exception as exc:
            message = str(exc).strip().replace("\n", " ")
            if len(message) > 180:
                message = message[:177] + "..."
            Clock.schedule_once(lambda dt, m=message: self._finish("فشل التنزيل: " + (m or "تحقق من الرابط والإنترنت.")))

    def _set_status(self, value):
        self.status = value

    def _finish(self, value):
        self.status = value
        self.busy = False

class NarutoDownloaderApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootWidget()

if __name__ == "__main__":
    NarutoDownloaderApp().run()
