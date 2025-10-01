import windowlist
import borderlesswithtaskbar
import borderlessnotaskbar
import alwaysontop
import stopalwaysontop

def exitApp():
    print("Exiting App...")
    exit()
    
def getwindows():
    windowlist.enum_window_titles()

def borderless1():
    wintitle = input("Enter Window title: ")
    success=borderlesswithtaskbar.force_borderless(wintitle)
    if not success:
        print(f"The window titled {wintitle} was not found")

def borderless2():
    wintitle = input("Enter Window title: ")
    success=borderlessnotaskbar.force_borderless_cover_taskbar(wintitle)
    if not success:
        print(f"The window titled {wintitle} was not found")

def setontop():
    wintitle = input("Enter Window title: ")
    success=alwaysontop.set_always_on_top(wintitle)
    if not success:
        print(f"The window titled {wintitle} was not found")
    else:
        print(f"The window titled {wintitle} is now always on top")

def stopontop():
    wintitle = input("Enter Window title: ")
    success=stopalwaysontop.stop_always_on_top(wintitle)
    if not success:
        print(f"The window titled {wintitle} was not found")
    else:
        print(f"The window titled {wintitle} is no longer always on top")
        
if __name__ == "__main__":
    main_menu = {
    "1": {"label": "Get Windows list", "action":getwindows},
    "2": {"label": "Force borderless with taskbar", "action": borderless1},
    "3": {"label": "Force borderless no taskbar", "action": borderless2},
    "4": {"label": "Set on top", "action": setontop},
    "5": {"label": "Stop on top", "action": stopontop},
    "6": {"label": "Exit", "action": exitApp}
    }
    while True:
        print("\n\033[35mAri's Windows Border Manager\033[0m")
        
        for key,item in main_menu.items():
            print(f"{key}. {item['label']}")
            
        choice = input("Choose an option: ").strip()
        selected = main_menu.get(choice)
        
        if selected:
            selected['action']()
        else:
            print(f"{choice} is an invalid option.")
    
