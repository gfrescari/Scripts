from textual.app import App, ComposeResult
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical
import subprocess
import sys

from youtube import search

class YouTubeTUI(App):
    CSS = """
    Screen {
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(
                placeholder="Search YouTube and press Enter",
                id="search",
            ),
            ListView(id="results"),
        )

    def on_input_submitted(self, event: Input.Submitted):
        results = search(event.value)

        list_view = self.query_one("#results", ListView)
        list_view.clear()

        for r in results:
            item = ListItem(Label(r["title"]))
            item.video_id = r["video_id"]
            list_view.append(item)

    def on_list_view_selected(self, event: ListView.Selected):
        video_id = event.item.video_id

        subprocess.Popen([
            sys.executable,
            "player.py",
            video_id,
        ])

if __name__ == "__main__":
    YouTubeTUI().run()
