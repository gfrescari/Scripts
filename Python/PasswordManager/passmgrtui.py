import json
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Input, Static, Button
from textual.containers import Vertical, Horizontal
import pyperclip
import pyautogui
import asyncio
from textual import on


DATA_FILE = "passwords.json"

class PassMgr(App):
    # Declare global vars
    TITLE = "Ari's Password Manager"
    # CSS_PATH is enough to load css file
    CSS_PATH = "passmgr.css"
    chosenservice = ""
    parallelList = []

    def compose(self) -> ComposeResult:
        
        # Declare and define containers and widgets
        # Top row of tab buttons
        self.tab_buttons = Horizontal(
            Button("Services", id="services_btn"),
            Button("Add New", id="addnew_btn"),
            id="tabButtons"
        )
        
        
        # Input box for adding new items
        self.tabAddNew = Vertical(
            Input(placeholder="Type service name",id="service_input"),
            Input(placeholder="Type userneame",id="usern_input"),
            Input(placeholder="Type password",id="pass_input"),
            Button("Add New", id="newServ_btn"),
            id="tabAddNew"
        )
        

        # Load data
        items = self.load_items()
        self.listPasswd = ListView(
                *[ListItem(Label(item)) for item in items],
                id="listPasswd"
            )
        
        self.tabList=Vertical(
            # List view
            self.listPasswd,
            id="tabList",
        )
        
        
        self.debug_label = Static("Debug: Ready",id="debug_label")
        self.msg_label = Static("System Messages",id="msg_label")
        
        # Create all objects above
        yield Header()
        
        yield Vertical(
            self.tab_buttons,
            self.tabAddNew,
            self.tabList,

            id="main_container"
        )
        
        yield Vertical(
            self.debug_label,
            self.msg_label,
            id="bottom_container"
        )
        
        yield Footer()
        
        self.show_tab("tabList")
        self.parallelList = list(self.load_items().keys())

    # ---------- Data Handling ----------
    def load_items(self):
        try:
            with open(DATA_FILE, "r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def save_items(self):
        with open(DATA_FILE, "w",encoding="utf-8") as f:
            json.dump(self.items, f, indent=2)
    
    def save_passwords(self,passwords):
        with open(DATA_FILE, "w",encoding="utf-8") as file:
            json.dump(passwords, file, indent=4)
            
    def refresh_listView(self):
        for child in self.listPasswd.children[:]:
            child.remove()  # fully removes from widget tree
        self.parallelList.clear()
        self.items = self.load_items()
        for item in self.items:
            list_item = ListItem(Label(item))  # ID = service name
            self.listPasswd.append(list_item)
        self.parallelList = list(self.items.keys())
        # self.parallelList = list(self.load_items().keys()) # this is the oneliner to get list from json. not used to avoid double json load
        
    # ---------- Add Item ----------
    
    def on_input_submitted(self, event: Input.Submitted):
        # not used but a good example of single input field 
        text = event.value.strip()
        if text:
            self.items.append(text)
            self.list_view.append(ListItem(Label(text)))
            self.input_box.value = ""
    
    
    
    # ---------- Remove Selected ----------
    def action_delete_selected(self):
        # used to remove from listView, but not from json file
        if self.list_view.index is not None:
            index = self.list_view.index
            self.items.pop(index)
            self.list_view.pop(index)
    
    def action_delete_password(self):
        service=self.chosenservice
        passwords = self.load_items()
        del passwords[service]
        self.save_passwords(passwords)
        self.msg_label.update(f"Password of {service} has been deleted")
        self.refresh_listView()
         

    # ---------- Save ----------
    def action_save(self):
        service = self.query_one("#service_input", Input).value
        username = self.query_one("#usern_input", Input).value
        password = self.query_one("#pass_input", Input).value
        if not service or not username or not password:
            self.msg_label.update("Cannot save new password. Must fill all fields.")
            return
        passwords = self.load_items()
        passwords[service] = {"username": username, "password": password}
        self.save_passwords(passwords)
        result = f"Service: {service}, Username: {username} password is saved."
        self.msg_label.update(result)
    
    # Copy password to clipboard
    def action_copytoclipboard(self):
        service=self.chosenservice
        passwords = self.load_items()
        if service in passwords:
            entry = passwords[service]
            pyperclip.copy(entry["password"])
            self.msg_label.update(f"{entry['username']} password has been copied to clipboard.")
        else:
            self.msg_label.update("Nothing selected")
    
    # Replacement of time.sleep
    def action_autopassword(self):
        self.run_worker(self._autopassword_task())
    
    # Replacement of time.sleep
    async def _autopassword_task(self):
        service=self.chosenservice
        passwords = self.load_items()
        if service in passwords:
            entry = passwords[service]
            self.start_countdown(5, "Five seconds to focus to app/web and click username field")   
            await asyncio.sleep(5)
            pyperclip.copy(entry["username"])
            await asyncio.sleep(0.5)
            pyautogui.hotkey("ctrl", "v")
            await asyncio.sleep(0.5)
            pyautogui.press("tab")
            pyperclip.copy(entry["password"])
            await asyncio.sleep(0.5)
            pyautogui.hotkey("ctrl", "v")
            await asyncio.sleep(0.5)
            pyautogui.press("enter")
    
    # Displaying countdown
    def start_countdown(self, seconds: int, message: str):
        self.countdown = seconds

        def update():
            if self.countdown > 0:
                self.msg_label.update(f"{message} ({self.countdown}s)")
                self.countdown -= 1
            else:
                self.msg_label.update("Ready")
                self.timer.stop()

        # run every 1 second
        self.timer = self.set_interval(1, update)
    # ---------- Debug ----------
    # This method only works if the item is selected by mouse
    def on_list_view_selected(self, event:ListView.Selected):
        selected_index = event.index
        self.chosenservice=self.parallelList[selected_index]
        self.debug_label.update(f"Selected: {self.chosenservice}")
        
    # This method only works if the item highlighted by arrow keys
    def on_list_view_highlighted(self, event:ListView.Highlighted):
        if event.item:
            selected_index = self.listPasswd.children.index(event.item)
            if selected_index is not None:
                self.chosenservice=self.parallelList[selected_index]
                self.debug_label.update(f"Highlighted: {self.chosenservice}")
    
    # Handle button clicks
    def on_button_pressed(self, event):
        if event.button.id == "services_btn":
            self.show_tab("tabList")
        elif event.button.id == "addnew_btn":
            self.show_tab("tabAddNew")
    
    # different way to handle button clicks. using decorator "on"
    @on(Button.Pressed, "#newServ_btn")
    def add_new_service(self, event: Button.Pressed):
        # query_one is used to find elements with the id, best used in dynamic fields. query_one(#<id>,<element-type>)
        service = self.query_one("#service_input", Input).value
        username = self.query_one("#usern_input", Input).value
        password = self.query_one("#pass_input", Input).value
        if not service or not username or not password:
            self.msg_label.update("Cannot save new password. Must fill all fields.")
            return
        passwords = self.load_items()
        passwords[service] = {"username": username, "password": password}
        self.save_passwords(passwords)
        result = f"Service: {service}, Username: {username} password is saved."
        self.msg_label.update(result)
        self.refresh_listView()
        
     # Show a tab and hide the others
    def show_tab(self, tab_id):
        for tab in [self.tabList, self.tabAddNew]:
            tab.display = (tab.id == tab_id)

    # ---------- Key Bindings ----------
    BINDINGS = [
        ("c", "copytoclipboard", "Copy Password"),
        ("x", "autopassword", "Auto Type"),
        ("d", "delete_password", "Delete item"),
        ("s", "save", "Save password"),
        ("q", "quit", "Quit"),
    ]


if __name__ == "__main__":
    PassMgr().run()
