import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import re
import win32com.client
import time
import requests
import xml.etree.ElementTree as ET
import socket
import threading
import queue
import webbrowser

class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.settings_window = tk.Toplevel(parent.root)
        self.settings_window.title("Log4TheMiddleAged Settings")
        self.settings_window.transient(parent.root)
        self.settings_window.grab_set()
        self.settings_window.resizable(True, True)  
        self.conn = sqlite3.connect('settings.db')
        self.cursor = self.conn.cursor()
        self.init_settings_db()
        self.load_settings()
        self.create_settings_gui()
        
        self.settings_window.update_idletasks()
        
        width = self.settings_window.winfo_reqwidth()
        height = self.settings_window.winfo_reqheight()
        
        x = (self.settings_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.settings_window.winfo_screenheight() // 2) - (height // 2)
        self.settings_window.geometry(f"{width}x{height}+{x}+{y}")
    def init_settings_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.conn.commit()
    def create_settings_gui(self):
        
        main_frame = ttk.Frame(self.settings_window, padding="10")
        main_frame.pack(fill="both", expand=True)

        
        program_frame = ttk.LabelFrame(main_frame, text="Program Settings", padding="10")
        program_frame.pack(fill="x", padx=5, pady=5)
        
        
        ttk.Label(program_frame, text="Program Name:").pack(anchor="w")
        self.program_name_var = tk.StringVar(value=self.settings.get('program_name', 'Log4TMA'))
        self.program_name_entry = ttk.Entry(program_frame, textvariable=self.program_name_var, width=40)
        self.program_name_entry.pack(fill="x", pady=5)
        
        
        omnirig_frame = ttk.LabelFrame(main_frame, text="OmniRig Settings", padding="10")
        omnirig_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(omnirig_frame, text="Select Rig:").pack(anchor="w")
        self.omnirig_selection = tk.StringVar(value=self.settings.get('omnirig_selection', 'Rig 1'))
        rig_combo = ttk.Combobox(omnirig_frame, 
                                textvariable=self.omnirig_selection,
                                values=['Rig 1', 'Rig 2'],
                                state='readonly',
                                width=40)
        rig_combo.pack(fill="x", pady=5)

        
        qrz_frame = ttk.LabelFrame(main_frame, text="QRZ Settings", padding="10")
        qrz_frame.pack(fill="x", padx=5, pady=5)

        self.qrz_enabled_var = tk.BooleanVar(value=self.settings.get('qrz_enabled', '0') == '1')
        self.qrz_enabled_cb = ttk.Checkbutton(
            qrz_frame, 
            text="Enable QRZ Lookups", 
            variable=self.qrz_enabled_var
        )
        self.qrz_enabled_cb.pack(anchor="w", pady=(0, 5))

        ttk.Label(qrz_frame, text="Your Callsign:").pack(anchor="w")
        self.station_callsign_var = tk.StringVar(value=self.settings.get('station_callsign', ''))
        self.station_callsign_entry = ttk.Entry(qrz_frame, textvariable=self.station_callsign_var, width=40)
        self.station_callsign_entry.pack(fill="x", pady=5)

        ttk.Label(qrz_frame, text="QRZ Username:").pack(anchor="w")
        self.qrz_username_var = tk.StringVar(value=self.settings.get('qrz_username', ''))
        self.qrz_username_entry = ttk.Entry(qrz_frame, textvariable=self.qrz_username_var, width=40)
        self.qrz_username_entry.pack(fill="x", pady=5)

        ttk.Label(qrz_frame, text="QRZ Password:").pack(anchor="w")
        self.qrz_password_var = tk.StringVar(value=self.settings.get('qrz_password', ''))
        self.qrz_password_entry = ttk.Entry(qrz_frame, textvariable=self.qrz_password_var, width=40, show="*")
        self.qrz_password_entry.pack(fill="x", pady=5)

        
        cluster_frame = ttk.LabelFrame(main_frame, text="DX Cluster Settings", padding="10")
        cluster_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(cluster_frame, text="DX Cluster Host:").pack(anchor="w")
        self.cluster_host_var = tk.StringVar(value=self.settings.get('cluster_host', 'dxspider.co.uk'))
        self.cluster_host_entry = ttk.Entry(cluster_frame, textvariable=self.cluster_host_var, width=40)
        self.cluster_host_entry.pack(fill="x", pady=5)
        
        ttk.Label(cluster_frame, text="DX Cluster Port:").pack(anchor="w")
        self.cluster_port_var = tk.StringVar(value=self.settings.get('cluster_port', '7300'))
        self.cluster_port_entry = ttk.Entry(cluster_frame, textvariable=self.cluster_port_var, width=40)
        self.cluster_port_entry.pack(fill="x", pady=5)

        
        save_button = ttk.Button(main_frame, text="Save Settings", command=self.save_settings)
        save_button.pack(pady=10)
    def load_settings(self):
        self.settings = {}
        self.cursor.execute('SELECT key, value FROM settings')
        for key, value in self.cursor.fetchall():
            self.settings[key] = value
    
    def save_settings(self):
        settings_to_save = [
            ('program_name', self.program_name_var.get().strip() or 'Log4TMA'),
            ('qrz_username', self.qrz_username_var.get().strip()),
            ('qrz_password', self.qrz_password_var.get().strip()),
            ('station_callsign', self.station_callsign_var.get().strip().upper()),
            ('qrz_enabled', '1' if self.qrz_enabled_var.get() else '0'),
            ('cluster_host', self.cluster_host_var.get().strip()),
            ('cluster_port', self.cluster_port_var.get().strip()),
            ('omnirig_selection', self.omnirig_selection.get())
        ]
        
        for key, value in settings_to_save:
            self.cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
        
        self.conn.commit()
        
        
        self.parent.reconnect_omnirig()
        
        self.settings_window.destroy()

class DXClusterWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("DX Cluster")
        self.window.geometry("800x600")
        
        
        self.create_gui()
        
        
        self.connected = False
        self.socket = None
        self.receive_queue = queue.Queue()
        
    def create_gui(self):
        
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        
        columns = ('time', 'dx', 'freq', 'comment', 'spotter')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        
        self.tree.heading('time', text='Time')
        self.tree.heading('dx', text='DX')
        self.tree.heading('freq', text='Frequency')
        self.tree.heading('comment', text='Comment')
        self.tree.heading('spotter', text='Spotter')
        
        
        self.tree.column('time', width=100)
        self.tree.column('dx', width=100)
        self.tree.column('freq', width=100)
        self.tree.column('comment', width=300)
        self.tree.column('spotter', width=100)
        
        
        self.tree.bind('<Double-1>', self.on_double_click)
        
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        
        self.status_var = tk.StringVar(value="Not Connected")
        self.status_label = ttk.Label(self.window, textvariable=self.status_var)
        self.status_label.pack(pady=5)

        
        self.connect_button = ttk.Button(self.window, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(pady=5)
            
    def toggle_connection(self):
        if not self.connected:
            self.connect_to_cluster()
        else:
            self.disconnect_from_cluster()
            
    def connect_to_cluster(self):
        try:
            
            self.parent.settings_cursor.execute('SELECT value FROM settings WHERE key = ?', ('cluster_host',))
            host_result = self.parent.settings_cursor.fetchone()
            self.parent.settings_cursor.execute('SELECT value FROM settings WHERE key = ?', ('cluster_port',))
            port_result = self.parent.settings_cursor.fetchone()
            self.parent.settings_cursor.execute('SELECT value FROM settings WHERE key = ?', ('station_callsign',))
            callsign_result = self.parent.settings_cursor.fetchone()
            
            host = host_result[0] if host_result else 'dxspider.co.uk'
            port = int(port_result[0]) if port_result else 7300
            callsign = callsign_result[0] if callsign_result else ''
            
            if not callsign:
                messagebox.showerror("Connection Error", "Please set your callsign in Settings first")
                return
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  
            self.socket.connect((host, port))
            
            
            initial_data = self.socket.recv(4096).decode('utf-8', errors='ignore')
            print(f"Received: {initial_data}")  
            
            if 'login:' in initial_data.lower():
                
                self.socket.send(f"{callsign}\n".encode('utf-8'))
                print(f"Sent callsign: {callsign}")  
            
            self.connected = True
            self.connect_button.configure(text="Disconnect")
            self.status_var.set(f"Connected to {host}:{port} as {callsign}")
            
            
            self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
            self.receive_thread.start()
            
            
            self.process_thread = threading.Thread(target=self.process_queue, daemon=True)
            self.process_thread.start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            self.status_var.set("Connection Failed")
            if self.socket:
                self.socket.close()
            self.socket = None
            
    def disconnect_from_cluster(self):
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.socket.close()
        self.connected = False
        self.connect_button.configure(text="Connect")
        self.status_var.set("Disconnected")
                
    def receive_data(self):
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if data:
                    self.receive_queue.put(data)
                else:
                    
                    self.window.after(0, self.handle_disconnect)
                    break
            except socket.timeout:
                continue
            except:
                if self.connected:
                    self.window.after(0, self.handle_disconnect)
                break
                
    def handle_disconnect(self):
        """Handle unexpected disconnection"""
        self.disconnect_from_cluster()
        self.status_var.set("Connection Lost")
                
    def process_queue(self):
        while self.connected:
            try:
                data = self.receive_queue.get(timeout=1)
                self.window.after(0, self.process_dx_spot, data)
            except queue.Empty:
                continue
                
    def process_dx_spot(self, data):
        """Process DX spot data and add to treeview"""
        lines = data.split('\n')
        for line in lines:
            if 'DX de' in line:
                try:
                    
                    
                    parts = line.split()
                    spotter_idx = parts.index('de') + 1
                    spotter = parts[spotter_idx].rstrip(':')
                    
                    
                    freq = None
                    for part in parts:
                        try:
                            freq = float(part)
                            break
                        except ValueError:
                            continue
                    
                    
                    freq_idx = parts.index(str(freq))
                    dx_call = parts[freq_idx + 1]
                    
                    
                    comment = ' '.join(parts[freq_idx + 2:])
                    
                    
                    time_str = datetime.now().strftime('%H:%M:%S')
                    
                    
                    self.tree.insert('', 0, values=(time_str, dx_call, f"{freq:.1f}", comment, spotter))
                    
                    
                    if len(self.tree.get_children()) > 100:
                        last_item = self.tree.get_children()[-1]
                        self.tree.delete(last_item)
                        
                except Exception as e:
                    print(f"Error processing spot: {str(e)}")
                    continue

    def on_closing(self):
        """Handle window closing"""
        self.disconnect_from_cluster()
        self.window.destroy()

    def on_double_click(self, event):
        """Handle double-click on a spot"""
        try:
            item = self.tree.selection()[0]
            values = self.tree.item(item)['values']
            
            if not values:
                return
                
            
            freq_str = str(values[2])
            print(f"Raw frequency from DX spot: {freq_str} KHz")
            
            
            freq_str = ''.join(c for c in freq_str if c.isdigit() or c == '.')
            freq_khz = float(freq_str)
            
            
            freq_hz = int(freq_khz * 1000)
            print(f"Converting {freq_khz} KHz to {freq_hz} Hz")
            
            
            if self.parent.rig and self.parent.omnirig_enabled.get():
                try:
                    
                    current_freq = self.parent.rig.FreqA
                    print(f"Current rig frequency: {current_freq} Hz")
                    
                    
                    print(f"Setting rig to: {freq_hz} Hz")
                    self.parent.rig.FreqA = freq_hz
                    
                    
                    new_freq = self.parent.rig.FreqA
                    print(f"New rig frequency: {new_freq} Hz")
                    
                    
                    freq_mhz = freq_hz / 1000000
                    if freq_mhz >= 10:
                        self.parent.mode_var.set('USB')
                    else:
                        self.parent.mode_var.set('LSB')
                    
                    self.status_var.set(f"Frequency set to {freq_khz} KHz")
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"Detailed error setting frequency: {error_msg}")
                    self.status_var.set(f"Error setting frequency")
            else:
                self.status_var.set("OmniRig not available")
                
        except (ValueError, IndexError) as e:
            print(f"Error processing frequency: {str(e)}")
            self.status_var.set("Invalid frequency format")

class Log4TMA:
    VERSION = "1.0.0"  
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Log4TheMiddleAged")
        self.root.geometry("900x600")
        self.init_settings_db()
        self.load_settings()
        
        
        self.omnirig = None
        self.rig = None
        self.omnirig_enabled = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="OmniRig Not Connected")
        self.lookup_timer = None  
        
        
        self.connect_to_omnirig()
        
        
        self.init_database()
        self.qrz_session = None
        self.last_lookup = ""
        self.create_gui()
        self.update_frequency()
        self.update_title()
    def init_settings_db(self):
        """Initialize settings database connection"""
        self.settings_conn = sqlite3.connect('settings.db')
        self.settings_cursor = self.settings_conn.cursor()
        self.settings_cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.settings_conn.commit()
    def load_settings(self):
        """Load settings from database"""
        self.settings = {}
        self.settings_cursor.execute('SELECT key, value FROM settings')
        for key, value in self.settings_cursor.fetchall():
            self.settings[key] = value
    def init_database(self):
        self.conn = sqlite3.connect('logbook.db')
        self.cursor = self.conn.cursor()
        
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS db_version (
                version INTEGER PRIMARY KEY
            )
        ''')
        
        
        self.cursor.execute('SELECT version FROM db_version')
        result = self.cursor.fetchone()
        current_version = result[0] if result else 0
        
        
        if current_version < 1:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    callsign TEXT NOT NULL,
                    locator TEXT,           -- Removed NOT NULL constraint
                    frequency REAL,
                    mode TEXT,
                    notes TEXT
                )
            ''')
            self.cursor.execute('INSERT OR REPLACE INTO db_version (version) VALUES (1)')
        
        
        if current_version < 2:
            self.cursor.execute('ALTER TABLE contacts ADD COLUMN name TEXT')
            self.cursor.execute('UPDATE db_version SET version = 2')
        
        self.conn.commit()

        
        if current_version > 0:
            try:
                
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contacts_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        callsign TEXT NOT NULL,
                        name TEXT,
                        locator TEXT,       -- No NOT NULL constraint
                        frequency REAL,
                        mode TEXT,
                        notes TEXT
                    )
                ''')
                
                
                self.cursor.execute('''
                    INSERT INTO contacts_new 
                    SELECT * FROM contacts
                ''')
                
                
                self.cursor.execute('DROP TABLE contacts')
                self.cursor.execute('ALTER TABLE contacts_new RENAME TO contacts')
                
                self.conn.commit()
            except Exception as e:
                print(f"Error updating database schema: {str(e)}")
                self.conn.rollback()
    def create_gui(self):
        
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=5, pady=5)
        
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side="left", padx=5)
        
        
        self.omnirig_button = ttk.Button(status_frame, text="Enable OmniRig", command=self.toggle_omnirig)
        self.omnirig_button.pack(side="right", padx=5)
        self.update_omnirig_button_text()
        
        settings_frame = ttk.Frame(self.root)
        settings_frame.pack(fill="x", padx=10, pady=5)
        self.settings_button = ttk.Button(settings_frame, text="Settings", command=self.open_settings)
        self.settings_button.pack(side="right")
        input_frame = ttk.LabelFrame(self.root, text="Contact Details", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)

        
        entry_width = 15    
        name_width = 50     
        mode_width = 20     

        
        ttk.Label(input_frame, text="Callsign:").grid(row=0, column=0, sticky="w", padx=(0,5))
        self.callsign_var = tk.StringVar()
        self.callsign_var.trace_add("write", self.on_callsign_change)
        self.callsign_entry = ttk.Entry(input_frame, textvariable=self.callsign_var, width=entry_width)
        self.callsign_entry.grid(row=0, column=1, padx=5, pady=2)
        
        qrz_button = ttk.Button(input_frame, text="QRZ Lookup", command=self.open_qrz_lookup)
        qrz_button.grid(row=0, column=2, padx=5)

        
        ttk.Label(input_frame, text="Name:").grid(row=0, column=3, sticky="w", padx=(10,5))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(input_frame, textvariable=self.name_var, width=name_width)
        self.name_entry.grid(row=0, column=4, pady=2, sticky="w")

        
        ttk.Label(input_frame, text="Locator:").grid(row=1, column=0, sticky="w", padx=(0,5))
        self.locator_var = tk.StringVar()
        self.locator_entry = ttk.Entry(input_frame, textvariable=self.locator_var, width=entry_width)
        self.locator_entry.grid(row=1, column=1, padx=5, pady=2)

        
        ttk.Label(input_frame, text="Frequency (MHz):").grid(row=2, column=0, sticky="w", padx=(0,5))
        self.freq_var = tk.StringVar()
        self.freq_entry = ttk.Entry(input_frame, textvariable=self.freq_var, width=entry_width)
        self.freq_entry.grid(row=2, column=1, padx=5, pady=2)
        
        
        self.omnirig_button = ttk.Button(input_frame, text="Disable OmniRig", command=self.toggle_omnirig)
        self.omnirig_button.grid(row=2, column=2, padx=5)

        
        ttk.Label(input_frame, text="Mode:").grid(row=2, column=3, sticky="w", padx=(10,5))
        self.mode_var = tk.StringVar()
        self.mode_combo = ttk.Combobox(input_frame, textvariable=self.mode_var, width=mode_width)
        self.mode_combo['values'] = ('LSB', 'USB', 'AM', 'FM', 'CW', 'RTTY', 'PSK31', 'FT8')
        self.mode_combo.grid(row=2, column=4, pady=2, sticky="w")

        
        ttk.Label(input_frame, text="Notes:").grid(row=3, column=0, sticky="w", padx=(0,5))
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(input_frame, textvariable=self.notes_var, width=entry_width)
        self.notes_entry.grid(row=3, column=1, padx=5, pady=2)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        self.add_button = ttk.Button(button_frame, text="Log Contact", command=self.add_contact)
        self.add_button.pack(side="left", padx=5)
        self.export_button = ttk.Button(button_frame, text="Export ADIF", command=self.export_adif)
        self.export_button.pack(side="left", padx=5)
        self.dx_cluster_button = ttk.Button(button_frame, text="DX Cluster", command=self.open_dx_cluster)
        self.dx_cluster_button.pack(side="left", padx=5)
        self.create_treeview()
    def create_treeview(self):
        
        columns = ('timestamp', 'callsign', 'name', 'locator', 'frequency', 'mode', 'notes')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        
        
        self.tree.heading('timestamp', text='Time')
        self.tree.heading('callsign', text='Callsign')
        self.tree.heading('name', text='Name')
        self.tree.heading('locator', text='Locator')
        self.tree.heading('frequency', text='Frequency (MHz)')
        self.tree.heading('mode', text='Mode')
        self.tree.heading('notes', text='Notes')
        
        
        self.tree.column('timestamp', width=150)
        self.tree.column('callsign', width=100)
        self.tree.column('name', width=150)
        self.tree.column('locator', width=100)
        self.tree.column('frequency', width=100)
        self.tree.column('mode', width=70)
        self.tree.column('notes', width=150)
        
        
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.load_contacts()
    def connect_to_omnirig(self):
        """Connect to OmniRig using the rig selected in settings"""
        try:
            
            selected_rig = self.settings.get('omnirig_selection', 'Rig 1')
            print(f"Attempting to connect to {selected_rig}")  
            
            
            self.omnirig = win32com.client.Dispatch("OmniRig.OmniRigX")
            
            
            if selected_rig == 'Rig 2':
                self.rig = self.omnirig.Rig2
            else:
                self.rig = self.omnirig.Rig1
            
            
            try:
                _ = self.rig.Freq
                self.omnirig_enabled.set(True)
                self.status_var.set(f"Connected to {selected_rig}")
                print(f"Successfully connected to {selected_rig}")  
            except Exception as e:
                self.status_var.set(f"{selected_rig} Not Responding")
                print(f"Rig not responding: {str(e)}")  
                self.omnirig_enabled.set(False)
                
        except Exception as e:
            print(f"OmniRig initialization error: {str(e)}")  
            self.status_var.set("OmniRig Not Available")
            self.omnirig = None
            self.rig = None
            self.omnirig_enabled.set(False)

    def toggle_omnirig(self):
        """Toggle OmniRig polling on/off"""
        if self.omnirig_enabled.get():
            
            self.omnirig_enabled.set(False)
            self.status_var.set("OmniRig Disabled")
        else:
            
            self.connect_to_omnirig()
        
        self.update_omnirig_button_text()

    def update_omnirig_button_text(self):
        """Update the OmniRig button text based on current state"""
        if self.omnirig_enabled.get():
            self.omnirig_button.configure(text="Disable OmniRig")
        else:
            self.omnirig_button.configure(text="Enable OmniRig")

    def update_frequency(self):
        """Update the frequency display from OmniRig only if enabled and connected"""
        if self.rig and self.omnirig_enabled.get():
            try:
                freq = self.rig.FreqA
                if freq > 0:
                    freq_mhz = freq / 1000000  
                    new_freq = f"{freq_mhz:.6f}"
                    
                    
                    self.last_valid_freq = new_freq
                    
                    
                    current_freq = self.freq_var.get().strip()
                    if not current_freq or new_freq != current_freq:
                        self.freq_var.set(new_freq)
                        
                        
                        if not self.mode_combo.get():
                            if freq_mhz >= 10:
                                self.mode_var.set('USB')
                            else:
                                self.mode_var.set('LSB')
            except Exception as e:
                print(f"Error reading frequency: {str(e)}")  
                self.omnirig_enabled.set(False)
                self.status_var.set("Rig Not Responding")
                self.update_omnirig_button_text()
                
        
        self.root.after(1000, self.update_frequency)

    def enable_manual_frequency(self):
        """Enable manual frequency entry when OmniRig is not available"""
        self.rig_status_var.set("Rig Status: Not Connected")
        self.freq_entry.configure(state='normal')  
    def validate_input(self):
        
        if not self.callsign_var.get().strip():
            return False, "Callsign is required"
        
        
        freq = self.freq_var.get().strip()
        if freq:
            try:
                float(freq)
            except ValueError:
                return False, "Frequency must be a valid number"
            
        return True, ""
    def add_contact(self):
        valid, message = self.validate_input()
        if not valid:
            tk.messagebox.showerror("Error", message)
            return
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        
        values = [
            timestamp,
            self.callsign_var.get().strip().upper(),
            self.name_var.get().strip() or None,
            self.locator_var.get().strip().upper() or None,  
            self.freq_var.get().strip() or None,
            self.mode_var.get() or None,
            self.notes_var.get().strip() or None
        ]
        
        
        self.cursor.execute('''
            INSERT INTO contacts 
            (timestamp, callsign, name, locator, frequency, mode, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', values)
        self.conn.commit()
        
        
        self.callsign_var.set("")
        self.name_var.set("")
        self.locator_var.set("")
        self.notes_var.set("")
        
        
        self.load_contacts()
    def load_contacts(self):
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        
        self.cursor.execute('''
            SELECT timestamp, callsign, name, locator, frequency, mode, notes 
            FROM contacts 
            ORDER BY timestamp DESC
        ''')
        
        for contact in self.cursor.fetchall():
            
            values = ['' if v is None else v for v in contact]
            self.tree.insert('', 'end', values=values)
    def export_adif(self):
        """Export the log to ADIF format"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".adi",
            filetypes=[("ADIF files", "*.adi"), ("All files", "*.*")],
            title="Export ADIF File"
        )
        if not filename:
            return
    
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                header = f"""Generated by Log4TheMiddleAged
<ADIF_VER:5>3.1.0
<PROGRAMID:8>Log4TMA
<PROGRAMVERSION:3>{self.VERSION}
<EOH>
"""
                f.write(header)
                self.cursor.execute('SELECT * FROM contacts ORDER BY timestamp')
                contacts = self.cursor.fetchall()
                for contact in contacts:
                    _, timestamp, callsign, name, locator, frequency, mode, notes = contact
    
    
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    qso_date = dt.strftime('%Y%m%d')
                    time_on = dt.strftime('%H%M%S')
    
    
                    adif_record = (
                        f"<QSO_DATE:{len(qso_date)}>{qso_date}\n"
                        f"<TIME_ON:{len(time_on)}>{time_on}\n"
                        f"<CALL:{len(callsign)}>{callsign}\n"
                        f"<NAME:{len(name)}>{name}\n"
                        f"<GRIDSQUARE:{len(locator)}>{locator}\n"
                        f"<FREQ:{len(str(frequency))}>{frequency}\n"
                        f"<MODE:{len(mode)}>{mode}\n"
                    )
    
    
                    if notes:
                        adif_record += f"<COMMENT:{len(notes)}>{notes}\n"
    
                    adif_record += "<EOR>\n\n"
                    f.write(adif_record)
            messagebox.showinfo("Export Successful", 
                              f"Log successfully exported to {filename}")
      
        except Exception as e:
            messagebox.showerror("Export Error", 
                               f"Error exporting log: {str(e)}")
    def run(self):
        self.root.mainloop()
    def __del__(self):
        """Cleanup database connections"""
        if hasattr(self, 'conn'):
            self.conn.close()
        if hasattr(self, 'settings_conn'):
            self.settings_conn.close()
    def open_settings(self):
        """Open the settings window"""
        settings_window = SettingsWindow(self)
    def on_callsign_change(self, *args):
        """Handle callsign field changes with delay"""
        
        if self.lookup_timer is not None:
            self.root.after_cancel(self.lookup_timer)
        
        
        self.lookup_timer = self.root.after(500, self.perform_callsign_lookup)
    
    def perform_callsign_lookup(self):
        """Perform the actual QRZ lookup after delay"""
        self.lookup_timer = None  
        
        
        self.settings_cursor.execute('SELECT value FROM settings WHERE key = ?', ('qrz_enabled',))
        result = self.settings_cursor.fetchone()
        if not result or result[0] != '1':
            return
        
        callsign = self.callsign_var.get().strip().upper()
        if len(callsign) >= 3:
            self.lookup_callsign(callsign)
    def qrz_login(self):
        """Login to QRZ and get session key"""
        self.settings_cursor.execute('SELECT value FROM settings WHERE key = ?', ('qrz_enabled',))
        result = self.settings_cursor.fetchone()
        if not result or result[0] != '1':
            print("QRZ lookups are disabled")
            return False
    
        self.settings_cursor.execute('SELECT value FROM settings WHERE key = ?', ('qrz_username',))
        username = self.settings_cursor.fetchone()
        self.settings_cursor.execute('SELECT value FROM settings WHERE key = ?', ('qrz_password',))
        password = self.settings_cursor.fetchone()
        if not username or not password:
            print("Missing QRZ credentials in settings")
            return False
    
        try:
            headers = {
                'User-Agent': f'Log4TMA/{self.VERSION}'
            }
    
            response = requests.get(
                'https://xmldata.qrz.com/xml/current/',
                headers=headers,
                params={
                    'username': username[0].strip(),
                    'password': password[0].strip(),
                }
            )
    
            print(f"QRZ Login Response Status Code: {response.status_code}")
            print(f"QRZ Login Response Content: {response.content.decode()}")
    
            root = ET.fromstring(response.content)
    
    
            ns = {'qrz': 'http://xmldata.qrz.com'}
    
    
            error = root.find('.//qrz:Error', namespaces=ns)
            if error is not None:
                print(f"QRZ Error: {error.text}")
                return False
    
    
            session_key = root.find('.//qrz:Key', namespaces=ns)
            if session_key is not None:
                self.qrz_session = session_key.text.strip()
                print(f"Successfully got QRZ session key: {self.qrz_session}")
                return True
            else:
                print("No session key found in QRZ response")
                return False
        except Exception as e:
            print(f"QRZ login error: {str(e)}")
            return False
    def lookup_callsign(self, callsign):
        """Look up callsign on QRZ"""
        if not hasattr(self, 'qrz_session') or not self.qrz_session:
            if not self.qrz_login():
                return
    
        try:
            headers = {
                'User-Agent': f'Log4TMA/{self.VERSION}'
            }
    
            response = requests.get(
                'https://xmldata.qrz.com/xml/current/',
                headers=headers,
                params={
                    's': self.qrz_session,
                    'callsign': callsign.strip(),
                }
            )
    
            print(f"QRZ Lookup Response Content: {response.content.decode()}")  
    
    
            xml_content = response.content.decode()
    
    
            if "<Error>" in xml_content:
                if "Session Timeout" in xml_content:
                    if self.qrz_login():  
                        return self.lookup_callsign(callsign)  
                print(f"QRZ Error in response")
                return
    
    
            grid_start = xml_content.find("<grid>")
            grid_end = xml_content.find("</grid>")
    
    
            fname_start = xml_content.find("<fname>")
            fname_end = xml_content.find("</fname>")
            name_start = xml_content.find("<name>")
            name_end = xml_content.find("</name>")
    
    
            if grid_start != -1 and grid_end != -1:
                grid = xml_content[grid_start + 6:grid_end].strip()
                if grid:
                    self.locator_var.set(grid)
                    print(f"Found grid: {grid} for {callsign}")
                else:
                    print(f"Empty grid value for {callsign}")
            else:
                print(f"No grid tags found for {callsign}")
    
            fname = ""
            if fname_start != -1 and fname_end != -1:
                fname = xml_content[fname_start + 7:fname_end].strip()
            lastname = ""
            if name_start != -1 and name_end != -1:
                lastname = xml_content[name_start + 6:name_end].strip()
    
            full_name = " ".join(filter(None, [fname, lastname]))
            if full_name:
                self.name_var.set(full_name)
                print(f"Found name: {full_name} for {callsign}")
            else:
                print(f"No name found for {callsign}")
        except Exception as e:
            print(f"QRZ lookup error: {str(e)}")
            print(f"Response content: {response.content.decode()}")
            import traceback
            traceback.print_exc()
    def update_title(self):
        """Update the window title based on settings"""
        self.settings_cursor.execute('SELECT value FROM settings WHERE key = ?', ('program_name',))
        result = self.settings_cursor.fetchone()
        program_name = result[0] if result else 'Log4TMA'
        self.root.title(program_name)
    def open_dx_cluster(self):
        """Open the DX Cluster window"""
        cluster_window = DXClusterWindow(self)
        cluster_window.window.protocol("WM_DELETE_WINDOW", cluster_window.on_closing)

    def reconnect_omnirig(self):
        """Reconnect to OmniRig after settings change"""
        print("Reconnecting to OmniRig with new settings")  
        
        
        self.omnirig_enabled.set(False)
        self.rig = None
        self.omnirig = None
        
        
        self.connect_to_omnirig()
        
        
        self.update_omnirig_button_text()

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Edit Entry", command=self.edit_entry)
            menu.add_command(label="Delete Entry", command=self.delete_entry)
            
            
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def edit_entry(self):
        """Edit the selected entry"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        item = selected_items[0]
        values = self.tree.item(item)['values']
        
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Contact")
        edit_window.geometry("400x500")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        
        frame = ttk.Frame(edit_window, padding="10")
        frame.pack(fill="both", expand=True)
        
        
        timestamp_var = tk.StringVar(value=values[0])
        callsign_var = tk.StringVar(value=values[1])
        name_var = tk.StringVar(value=values[2] if values[2] else '')
        locator_var = tk.StringVar(value=values[3] if values[3] else '')
        frequency_var = tk.StringVar(value=values[4] if values[4] else '')
        mode_var = tk.StringVar(value=values[5] if values[5] else '')
        notes_var = tk.StringVar(value=values[6] if values[6] else '')
        
        
        ttk.Label(frame, text="Time:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=timestamp_var, state='readonly').grid(row=0, column=1, sticky="ew", pady=2)
        
        ttk.Label(frame, text="Callsign:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=callsign_var).grid(row=1, column=1, sticky="ew", pady=2)
        
        ttk.Label(frame, text="Name:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=name_var).grid(row=2, column=1, sticky="ew", pady=2)
        
        ttk.Label(frame, text="Locator:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=locator_var).grid(row=3, column=1, sticky="ew", pady=2)
        
        ttk.Label(frame, text="Frequency:").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=frequency_var).grid(row=4, column=1, sticky="ew", pady=2)
        
        ttk.Label(frame, text="Mode:").grid(row=5, column=0, sticky="w", pady=2)
        mode_combo = ttk.Combobox(frame, textvariable=mode_var, values=['LSB', 'USB', 'AM', 'FM', 'CW', 'RTTY', 'PSK31', 'FT8'])
        mode_combo.grid(row=5, column=1, sticky="ew", pady=2)
        
        ttk.Label(frame, text="Notes:").grid(row=6, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=notes_var).grid(row=6, column=1, sticky="ew", pady=2)
        
        
        frame.columnconfigure(1, weight=1)
        
        def save_changes():
            
            self.cursor.execute('''
                UPDATE contacts 
                SET callsign=?, name=?, locator=?, frequency=?, mode=?, notes=?
                WHERE timestamp=?
            ''', (
                callsign_var.get().strip().upper(),
                name_var.get().strip(),
                locator_var.get().strip().upper(),
                frequency_var.get().strip(),
                mode_var.get(),
                notes_var.get().strip(),
                timestamp_var.get()
            ))
            self.conn.commit()
            
            
            self.load_contacts()
            edit_window.destroy()
        
        
        ttk.Button(frame, text="Save", command=save_changes).grid(row=7, column=0, columnspan=2, pady=10)

    def delete_entry(self):
        """Delete the selected entry"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?"):
            item = selected_items[0]
            values = self.tree.item(item)['values']
            
            
            self.cursor.execute('DELETE FROM contacts WHERE timestamp=?', (values[0],))
            self.conn.commit()
            
            
            self.load_contacts()

    def open_qrz_lookup(self):
        """Open QRZ.com database page for the entered callsign"""
        callsign = self.callsign_var.get().strip().upper()
        if callsign:
            url = f"https://www.qrz.com/db/{callsign}"
            webbrowser.open(url)
        else:
            messagebox.showinfo("QRZ Lookup", "Please enter a callsign first")

if __name__ == "__main__":
    app = Log4TMA()
    app.run()