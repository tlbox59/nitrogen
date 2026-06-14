#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nitro Generator Pro - Génère et vérifie des codes Discord Nitro
Interface graphique moderne, validation en temps réel
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import random
import string
import time
import requests
from datetime import datetime

# ==================== CONFIGURATION ====================
API_BASE = "https://discord.com/api/v9/entitlements/gift-codes/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# ==================== LOGIQUE ====================
def generate_code():
    """Génère un code Discord Nitro aléatoire (format classique)"""
    chars = string.ascii_uppercase + string.digits
    # Format: XXXX-XXXX-XXXX (exemple: 8H3K-5P9Q-2M7R)
    parts = [''.join(random.choices(chars, k=4)) for _ in range(3)]
    return '-'.join(parts)

def check_code(code):
    """Vérifie si un code Nitro est valide via l'API Discord"""
    try:
        url = API_BASE + code
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Récupérer les infos du gift
            uses = data.get('uses', 0)
            max_uses = data.get('max_uses', 1)
            if uses >= max_uses:
                return "invalid_used"
            # Vérifier si c'est un nitro (classique ou boost)
            subscription_plan = data.get('subscription_plan', {})
            plan_name = subscription_plan.get('name', 'Nitro')
            duration = subscription_plan.get('duration', '1 mois')
            return "valid", plan_name, duration, uses, max_uses
        elif resp.status_code == 404:
            return "invalid"
        elif resp.status_code == 429:
            return "rate_limit"
        else:
            return "error"
    except Exception:
        return "error"

# ==================== INTERFACE GRAPHIQUE ====================
class NitroGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nitro Generator by t!box59")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.configure(bg="#2c2f33")

        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#2c2f33", foreground="#ffffff", font=("Segoe UI", 10))
        self.style.configure("TButton", background="#7289da", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("TButton", background=[("active", "#5b6eae")])
        self.style.configure("TFrame", background="#2c2f33")
        self.style.configure("TNotebook", background="#2c2f33")
        self.style.configure("TNotebook.Tab", background="#23272a", foreground="white", padding=[10, 2])
        self.style.map("TNotebook.Tab", background=[("selected", "#7289da")])

        # Variables
        self.generation_count = tk.IntVar(value=50)
        self.threads_count = tk.IntVar(value=5)
        self.results = []  # (code, status, details)
        self.is_running = False

        # Widgets
        self.create_widgets()

    def create_widgets(self):
        # En-tête
        header = tk.Frame(self.root, bg="#23272a", height=60)
        header.pack(fill=tk.X)
        title = tk.Label(header, text="Nitro Generator by t!box59", font=("Segoe UI", 18, "bold"), bg="#23272a", fg="#ffffff")
        title.pack(pady=10)

        # Panneau de contrôle
        control_frame = ttk.LabelFrame(self.root, text="Paramètres", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Ligne 1 : Nombre de codes
        row1 = tk.Frame(control_frame, bg="#2c2f33")
        row1.pack(fill=tk.X, pady=5)
        tk.Label(row1, text="Codes à générer :", bg="#2c2f33", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        spin1 = tk.Spinbox(row1, from_=1, to=1000, textvariable=self.generation_count, width=10, bg="#40444b", fg="white", relief=tk.FLAT)
        spin1.pack(side=tk.LEFT, padx=5)

        # Ligne 2 : Threads
        row2 = tk.Frame(control_frame, bg="#2c2f33")
        row2.pack(fill=tk.X, pady=5)
        tk.Label(row2, text="Threads simultanés :", bg="#2c2f33", fg="white").pack(side=tk.LEFT, padx=5)
        spin2 = tk.Spinbox(row2, from_=1, to=20, textvariable=self.threads_count, width=10, bg="#40444b", fg="white", relief=tk.FLAT)
        spin2.pack(side=tk.LEFT, padx=5)

        # Boutons d'action
        btn_frame = tk.Frame(control_frame, bg="#2c2f33")
        btn_frame.pack(fill=tk.X, pady=10)
        self.start_btn = tk.Button(btn_frame, text="▶ DÉMARRER", command=self.start_generation, bg="#7289da", fg="white", font=("Segoe UI", 10, "bold"), padx=20, pady=5, relief=tk.FLAT, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = tk.Button(btn_frame, text="⏹ ARRÊTER", command=self.stop_generation, bg="#f04747", fg="white", font=("Segoe UI", 10, "bold"), padx=20, pady=5, relief=tk.FLAT, cursor="hand2", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.clear_btn = tk.Button(btn_frame, text="🗑 EFFACER", command=self.clear_results, bg="#4e5d94", fg="white", font=("Segoe UI", 10, "bold"), padx=20, pady=5, relief=tk.FLAT, cursor="hand2")
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Zone de résultat
        result_frame = ttk.LabelFrame(self.root, text="Résultats", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("Consolas", 9), bg="#23272a", fg="#ffffff", insertbackground="white")
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Barre de progression
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Statut
        self.status_label = tk.Label(self.root, text="Prêt", bg="#2c2f33", fg="#b9bbbe", font=("Segoe UI", 9))
        self.status_label.pack(pady=5)

        # Configuration des couleurs de texte
        self.result_text.tag_config("valid", foreground="#43b581")
        self.result_text.tag_config("invalid", foreground="#f04747")
        self.result_text.tag_config("used", foreground="#faa61a")
        self.result_text.tag_config("error", foreground="#f04747")
        self.result_text.tag_config("rate", foreground="#faa61a")
        self.result_text.tag_config("info", foreground="#7289da")

    def log_result(self, code, status, details=""):
        """Ajoute une ligne colorée dans la zone de résultat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if status == "valid":
            self.result_text.insert(tk.END, f"[{timestamp}] ✅ VALIDE  : {code} - {details}\n", "valid")
        elif status == "invalid":
            self.result_text.insert(tk.END, f"[{timestamp}] ❌ INVALIDE : {code}\n", "invalid")
        elif status == "invalid_used":
            self.result_text.insert(tk.END, f"[{timestamp}] ⚠ DÉJÀ UTILISÉ : {code}\n", "used")
        elif status == "rate_limit":
            self.result_text.insert(tk.END, f"[{timestamp}] ⚠ RATE LIMIT - Pause...\n", "rate")
        else:
            self.result_text.insert(tk.END, f"[{timestamp}] 🟡 ERREUR    : {code}\n", "error")
        self.result_text.see(tk.END)

    def update_progress(self, current, total):
        self.progress['value'] = (current / total) * 100
        self.root.update_idletasks()

    def clear_results(self):
        self.result_text.delete(1.0, tk.END)
        self.results.clear()

    def start_generation(self):
        if self.is_running:
            return
        total = self.generation_count.get()
        if total <= 0:
            messagebox.showwarning("Attention", "Le nombre de codes doit être supérieur à 0.")
            return
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_label.config(text=f"Génération de {total} codes en cours...")
        threading.Thread(target=self._worker, args=(total,), daemon=True).start()

    def stop_generation(self):
        self.is_running = False
        self.status_label.config(text="Arrêt demandé...")

    def _worker(self, total):
        threads = self.threads_count.get()
        generated = 0
        valid_found = 0
        self.results = []

        def check_worker(code):
            nonlocal valid_found
            if not self.is_running:
                return
            status = check_code(code)
            if status == "valid":
                valid_found += 1
                self.log_result(code, "valid", f"{status[1]} - {status[2]} (used {status[3]}/{status[4]})")
            elif status == "invalid":
                self.log_result(code, "invalid")
            elif status == "invalid_used":
                self.log_result(code, "invalid_used")
            elif status == "rate_limit":
                self.log_result(code, "rate_limit")
                time.sleep(2)
            else:
                self.log_result(code, "error")
            self.update_progress(generated, total)

        # On génère et on vérifie en parallèle
        while generated < total and self.is_running:
            codes_batch = []
            for _ in range(min(threads, total - generated)):
                code = generate_code()
                codes_batch.append(code)
                generated += 1
                self.update_progress(generated, total)

            # Vérification avec threads
            thread_list = []
            for code in codes_batch:
                if not self.is_running:
                    break
                t = threading.Thread(target=check_worker, args=(code,))
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()
            # Pause courte pour éviter rate limit
            time.sleep(0.5)

        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"Terminé. {valid_found} codes valides trouvés sur {total} générés.")
        if valid_found > 0:
            messagebox.showinfo("Succès", f"{valid_found} code(s) valide(s) détecté(s) !")

# ==================== LANCEMENT ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = NitroGeneratorApp(root)
    root.mainloop()