import tkinter as tk
import subproces

root = tk.Tk()
root.title("Menu Navigation")
root.geometry("800x600")

menu_frame = tk.Frame(root)
menu_frame.pack(side="left", fill="y")

content_frame = tk.Frame(root)
content_frame.pack(side="right", fill="both", expand=True)

def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def show_menu(menu_name):
    clear_content()
    menu_builders[menu_name]()

# Exit Button
exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 14), width=10, height=2)
exit_button.place(relx=0.98, rely=0.98, anchor="se")

# --- Menu Button Layout ---
tk.Label(menu_frame, text="Main Menu", font=("Arial", 16)).pack(pady=10)
tk.Button(menu_frame, text="Active Directory", command=lambda: show_menu("active_directory")).pack(pady=5)
tk.Button(menu_frame, text="Exchange Online", command=lambda: show_menu("exchange_online")).pack(pady=5)
tk.Button(menu_frame, text="Graph", command=lambda: show_menu("graph")).pack(pady=5)

# --- Submenu Builders ---
def build_main_menu():
    tk.Label(content_frame, text="Welcome to the Toolbox", font=("Arial", 16)).pack(pady=10)

def build_active_directory():
    tk.Label(content_frame, text="Active Directory Menu", font=("Arial", 16)).pack(pady=10)
    tk.Button(content_frame, text="Option 1").pack(pady=5)
    tk.Button(content_frame, text="Option 2").pack(pady=5)
    tk.Button(content_frame, text="Back to Main Menu", command=lambda: show_menu("main_menu")).pack(pady=5)

def connect_to_exchange_online():
    try:
        subprocess.run(["powershell", "-Command", "Connect-ExchangeOnline"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to Exchange Online: {e}")

def build_exchange_online():
    tk.Label(content_frame, text="Exchange Online Menu", font=("Arial", 16)).pack(pady=10)
    tk.Button(content_frame, text="Connect to Exchange Online", command=connect_to_exchange_online).pack(pady=5)
    tk.Button(content_frame, text="Option 2").pack(pady=5)
    tk.Button(content_frame, text="Back to Main Menu", command=lambda: show_menu("main_menu")).pack(pady=5)

def build_graph_menu():
    tk.Label(content_frame, text="Graph Menu", font=("Arial", 16)).pack(pady=10)
    tk.Button(content_frame, text="Option 1").pack(pady=5)
    tk.Button(content_frame, text="Option 2").pack(pady=5)
    tk.Button(content_frame, text="Back to Main Menu", command=lambda: show_menu("main_menu")).pack(pady=5)

menu_builders = {
    "main_menu": build_main_menu,
    "active_directory": build_active_directory,
    "exchange_online": build_exchange_online,
    "graph": build_graph_menu
}

# Show main menu initially
show_menu("main_menu")

root.mainloop()
