import tkinter as tk
from tkinter import ttk
import subprocess

root = tk.Tk()
root.title("Menu Navigation")
root.geometry("800x600")

# --- Configure ttk Styles and Theme ---
style = ttk.Style(root)
style.theme_use("clam")  # Try other themes like 'alt' or 'default' if you wish
style.configure("TButton", font=("Helvetica", 12), padding=6)
style.configure("TLabel", font=("Helvetica", 14), padding=6)
style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), padding=10)

# --- Frames: Menu and Content ---
menu_frame = ttk.Frame(root, padding=10)
menu_frame.pack(side="left", fill="y")

content_frame = ttk.Frame(root, padding=10)
content_frame.pack(side="right", fill="both", expand=True)

# --- Navigation Functions ---
def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def show_menu(menu_name):
    clear_content()
    menu_builders[menu_name]()

# --- Exit Button ---
exit_button = ttk.Button(root, text="Exit", command=root.quit)
# Using place to anchor at bottom-right; adjust as needed
exit_button.place(relx=0.98, rely=0.98, anchor="se")

# --- Main Menu Widgets ---
ttk.Label(menu_frame, text="Main Menu", style="Title.TLabel").pack(pady=10)
ttk.Button(menu_frame, text="Install Modules", 
           command=lambda: show_menu("install_modules")).pack(pady=5)
ttk.Button(menu_frame, text="Active Directory", 
           command=lambda: show_menu("active_directory")).pack(pady=5)
ttk.Button(menu_frame, text="Exchange Online", 
           command=lambda: show_menu("exchange_online")).pack(pady=5)
ttk.Button(menu_frame, text="Graph", 
           command=lambda: show_menu("graph")).pack(pady=5)

# --- Submenu Builders ---
def build_main_menu():
    ttk.Label(content_frame, text="Welcome to the Toolbox", style="Title.TLabel").pack(pady=10)

def build_install_modules():
    ttk.Label(content_frame, text="Install Modules Menu", style="Title.TLabel").pack(pady=10)
    
    def check_and_install_nuget(next_action):
        def wrapper():
            completed = subprocess.run(
                ["powershell", "-Command", "Get-PackageProvider -Name NuGet"],
                capture_output=True, text=True
            )
            if completed.returncode != 0:
                install_prompt = tk.Toplevel(root)
                install_prompt.title("NuGet Required")
                ttk.Label(install_prompt, text="NuGet is not installed. Install it now?").pack(pady=10)
                ttk.Button(
                    install_prompt, text="Yes",
                    command=lambda: [install_nuget_module(), install_prompt.destroy(), next_action()]
                ).pack(side="left", padx=10, pady=10)
                ttk.Button(
                    install_prompt, text="No", command=install_prompt.destroy
                ).pack(side="right", padx=10, pady=10)
            else:
                next_action()
        return wrapper

    ttk.Button(content_frame, text="Install Exchange Online Module",
               command=check_and_install_nuget(install_exchange_online_module)).pack(pady=5)
    ttk.Button(content_frame, text="Install Graph Module",
               command=check_and_install_nuget(install_graph_module)).pack(pady=5)
    ttk.Button(content_frame, text="Back to Main Menu", 
               command=lambda: show_menu("main_menu")).pack(pady=5)

def build_active_directory():
    ttk.Label(content_frame, text="Active Directory Menu", style="Title.TLabel").pack(pady=10)
    ttk.Button(content_frame, text="Option 1").pack(pady=5)
    ttk.Button(content_frame, text="Option 2").pack(pady=5)
    ttk.Button(content_frame, text="Back to Main Menu", 
               command=lambda: show_menu("main_menu")).pack(pady=5)

def build_exchange_online():
    ttk.Label(content_frame, text="Exchange Online Menu", style="Title.TLabel").pack(pady=10)
    ttk.Button(content_frame, text="Connect to Exchange Online", 
               command=connect_to_exchange_online).pack(pady=5)
    ttk.Button(content_frame, text="Option 2").pack(pady=5)
    ttk.Button(content_frame, text="Back to Main Menu", 
               command=lambda: show_menu("main_menu")).pack(pady=5)

def build_graph_menu():
    ttk.Label(content_frame, text="Graph Menu", style="Title.TLabel").pack(pady=10)
    ttk.Button(content_frame, text="Connect to Microsoft Graph", 
               command=connect_to_graph).pack(pady=5)
    ttk.Button(content_frame, text="Option 2").pack(pady=5)
    ttk.Button(content_frame, text="Back to Main Menu", 
               command=lambda: show_menu("main_menu")).pack(pady=5)

# --- Module Installation Functions ---
def install_exchange_online_module():
    run_powershell_command("Install-Module -Name ExchangeOnline -Force -Scope CurrentUser")

def install_graph_module():
    run_powershell_command("Install-Module -Name Microsoft.Graph -Force -Confirm:$False -Scope CurrentUser")

def install_nuget_module():
    run_powershell_command("Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope CurrentUser")

# --- Powershell Execution Helpers ---
def run_powershell_script(script_path):
    try:
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running PowerShell script: {e}")

def run_powershell_command(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd],
                               capture_output=True, text=True)
    if completed.returncode == 0:
        print("Script executed successfully")
    else:
        print(f"Error: {completed.stderr}")

# --- Connection Functions ---
def connect_to_exchange_online():
    try:
        run_powershell_command("Import-Module ExchangeOnlineManagement")
        run_powershell_command("Connect-ExchangeOnline")
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to Exchange Online: {e}")

def connect_to_graph():
    try:
        run_powershell_command("Connect-MgGraph -Scopes 'User.Read.All, Directory.Read.All'")
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to Microsoft Graph: {e}")

# --- Menu Builders Dictionary ---
menu_builders = {
    "main_menu": build_main_menu,
    "install_modules": build_install_modules,
    "active_directory": build_active_directory,
    "exchange_online": build_exchange_online,
    "graph": build_graph_menu
}

# --- Initialize with the Main Menu ---
show_menu("main_menu")

root.mainloop()
