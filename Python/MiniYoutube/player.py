import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl

def main(video_id: str):
    app = QApplication(sys.argv)

    view = QWebEngineView()
    view.setWindowTitle("Mini YouTube Player")
    view.resize(960, 540)

    # Enable fullscreen support
    settings = view.settings()
    settings.setAttribute(
        QWebEngineSettings.FullScreenSupportEnabled, True
    )

    view.page().fullScreenRequested.connect(
        lambda req: req.accept()
    )

    url = f"https://www.youtube.com/embed/{video_id}?autoplay=1"
    view.setUrl(QUrl(url))
    view.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: player.py VIDEO_ID")
        sys.exit(1)

    main(sys.argv[1])
