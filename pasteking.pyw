import tkinter as tk
import tkinter.filedialog as fd
import tkinter.simpledialog as sd
import tkinter.messagebox as mb
import os
import subprocess
import platform
import webbrowser
import re
import sys

# ─── Config & Path Logic ──────────────────────────────────────────────────────
APP_NAME = "PasteKing"

if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PATH_FILE = os.path.join(_BASE_DIR, "Path")
DATA_DIR  = os.path.join(_BASE_DIR, "Data")

def get_active_filepath():
    """Reads the Path file to determine the active profile."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(PATH_FILE):
        try:
            with open(PATH_FILE, "r", encoding="utf-8") as f:
                rel_path = f.read().strip()
            if rel_path:
                return os.path.abspath(os.path.join(_BASE_DIR, rel_path))
        except Exception:
            pass

    # Fallback if Path is missing or empty
    default_rel = os.path.join("Data", "default.txt")
    default_abs = os.path.join(_BASE_DIR, default_rel)
    
    try:
        with open(PATH_FILE, "w", encoding="utf-8") as f:
            f.write(default_rel)
    except Exception:
        pass
        
    return default_abs

INITIAL_DATA_FILE = get_active_filepath()


# ─── Theme ──────────────────────────────────────────────────────────────────
THEMES = {
    "Light": {
        "bg": "ivory2",
        "panel": "#DCDCDC",
        "text": "#222222",
        "muted": "#666666",
        "entry_bg": "#FFFFFF",
        "entry_fg": "#111111",
        "text_bg": "#FFFFFF",
        "text_fg": "#111111",
        "disabled_bg": "#E8E8E8",
        "button_bg": "#D3D3D3",
        "button_fg": "#111111",
        "top_on": "#50C878",
        "top_off": "#D3D3D3",
        "separator": "#BBBBBB",
    },
    "Dark": {
        "bg": "#1E1E1E",
        "panel": "#252526",
        "text": "#FFFFFF",
        "muted": "#C0CDCE",
        "entry_bg": "#2A2A2A",
        "entry_fg": "#FFFFFF",
        "text_bg": "#2A2A2A",
        "text_fg": "#FFFFFF",
        "disabled_bg": "#333338",
        "button_bg": "#3C4C85",
        "button_fg": "#FFFFFF",
        "top_on": "#DAB71F",
        "top_off": "#3C4C85",
        "separator": "#C0CDCE",
    },
}

def get_theme_from_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        return "Light"
    m = re.search(r'^# Theme:\s*(Dark|Light)\s*$', raw, re.MULTILINE | re.IGNORECASE)
    return m.group(1).capitalize() if m else "Light"

def set_theme_in_file(filepath, theme):
    theme = "Dark" if str(theme).lower() == "dark" else "Light"
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()
        else:
            raw = ""
        
        if re.search(r'^# Theme:\s*(Dark|Light)\s*$', raw, re.MULTILINE | re.IGNORECASE):
            raw = re.sub(r'^# Theme:\s*(Dark|Light)\s*$',
                         f"# Theme: {theme}", raw, count=1,
                         flags=re.MULTILINE | re.IGNORECASE)
        else:
            raw = re.sub(r'(?m)^(###\s*My Details)', f'# Theme: {theme}\n\n\\1', raw, count=1)
            if raw == "" or f"# Theme: {theme}" not in raw:
                raw = f"# Theme: {theme}\n\n{raw}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(raw)
        return True
    except Exception:
        return False

CURRENT_THEME_MODE = get_theme_from_file(INITIAL_DATA_FILE)
CURRENT_THEME = THEMES[CURRENT_THEME_MODE]

def apply_theme_globals(mode):
    global CURRENT_THEME_MODE, CURRENT_THEME
    global COL_BG, COL_A, COL_B, COL_C, COL_FOLDER, COL_HOME, COL_BACK
    global COL_TOP_ON, COL_TOP_OFF, COL_EDIT, COL_UP, COL_NEW
    global TYPE_PALETTE

    mode = "Dark" if str(mode).lower() == "dark" else "Light"
    CURRENT_THEME_MODE = mode
    CURRENT_THEME = THEMES[mode]
    COL_BG      = CURRENT_THEME["bg"]

    if mode == "Dark":
        COL_A       = "#789044"
        COL_B       = "#3C4C85"
        COL_C       = "#964444"
        COL_FOLDER  = "#B08F1A"
        COL_HOME    = "#F08080"
        COL_BACK    = "#4E5D9A"
        COL_TOP_ON  = CURRENT_THEME["top_on"]
        COL_TOP_OFF = CURRENT_THEME["top_off"]
        COL_EDIT    = "#3C4C85"
        COL_UP      = "#5F6A6C"
        COL_NEW     = "#789044"
        TYPE_PALETTE = {
            "CopyText":  "#789044",
            "Link":      "#3C4C85",
            "LocalPath": "#3C4C85",
            "folder":    "#B08F1A",
            "Command":   "#964444",
        }
    else:
        COL_A       = "#90EE90"
        COL_B       = "#ADD8E6"
        COL_C       = "#FFB6C1"
        COL_FOLDER  = "#FFD700"
        COL_HOME    = "#F08080"
        COL_BACK    = "#D3D3D3"
        COL_TOP_ON  = "#50C878"
        COL_TOP_OFF = "#D3D3D3"
        COL_EDIT    = "#DCDCDC"
        COL_UP      = "#E4E4E4"
        COL_NEW     = "#BEBEBE"
        TYPE_PALETTE = {
            "CopyText":  "#90EE90",
            "Link":      "#ADD8E6",
            "LocalPath": "#B8D8F0",
            "folder":    "#FFD700",
            "Command":   "#FFB6C1",
        }

apply_theme_globals(CURRENT_THEME_MODE)

TYPES = [
    ("CopyText",  "📋 Text",    "#90EE90"),
    ("Link",      "🌐 Website", "#ADD8E6"),
    ("LocalPath", "📂 Local",   "#B8D8F0"),
    ("folder",    "📁 Group",   "#FFD700"),
    ("Command",   "⚡ Cmd",     "#FFB6C1"),
]
TYPE_KINDS = {t[0] for t in TYPES}


# ─── Node ────────────────────────────────────────────────────────────────────
class Node:
    def __init__(self, kind, label, content="", parent=None):
        self.kind     = kind
        self.label    = label
        self.content  = content
        self.children = []
        self.parent   = parent

    def add_child(self, node):
        node.parent = self
        self.children.append(node)


# ─── Parser ──────────────────────────────────────────────────────────────────
def parse_data_file(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    except UnicodeDecodeError:
        return None

    root  = Node("folder", "Root")
    stack = [root]
    sec_re = re.compile(r'^###\s*(.+)$', re.MULTILINE)
    secs   = [(m.start(), m.end(), m.group(1).strip()) for m in sec_re.finditer(raw)]

    if not secs:
        return root

    for i, (pos, end_pos, name) in enumerate(secs):
        body_start = end_pos
        if body_start < len(raw):
            if raw.startswith('\r\n', body_start):
                body_start += 2
            elif raw[body_start] in '\r\n':
                body_start += 1
        body_end = secs[i + 1][0] if i + 1 < len(secs) else len(raw)
        body = raw[body_start:body_end]

        if name.lower() == "end_of_this_folder":
            if len(stack) > 1:
                stack.pop()
        else:
            folder = Node("folder", name)
            stack[-1].add_child(folder)
            stack.append(folder)
            for entry in re.split(r'^---\s*$', body, flags=re.MULTILINE):
                lines = [l for l in entry.splitlines()
                         if not l.strip().startswith('#')]
                entry = "\n".join(lines).strip()
                if not entry:
                    continue
                kind    = "CopyText"
                label   = ""
                content = ""
                m = re.search(r'^type:\s*(\w+)', entry, re.MULTILINE)
                if m:
                    kind = m.group(1).strip()
                if kind == "Folder":
                    continue
                m = re.search(r'^"([^"]+)"', entry, re.MULTILINE)
                if m:
                    label = m.group(1).strip()
                m = re.search(r'"""(.*?)"""', entry, re.DOTALL)
                if m:
                    content = m.group(1).strip()
                if label:
                    folder.add_child(Node(kind, label, content))
    return root


# ─── Serialiser ──────────────────────────────────────────────────────────────
def _write_node(node, out):
    if node.kind != "folder":
        return
    out.append(f"### {node.label}")
    out.append("")
    leaves = [c for c in node.children if c.kind != "folder"]
    folders = [c for c in node.children if c.kind == "folder"]
    for i, leaf in enumerate(leaves):
        out.extend([
            f"type: {leaf.kind}",
            f'"{leaf.label}"',
            f'"""{leaf.content}"""',
        ])
        if i < len(leaves) - 1:
            out.extend(["", "---", ""])
    if leaves and folders:
        out.append("")
    for sub in folders:
        _write_node(sub, out)
    out.extend([f"### End_Of_This_Folder", ""])


def save_tree(root, filepath):
    theme = get_theme_from_file(filepath) if os.path.exists(filepath) else CURRENT_THEME_MODE
    out = [
        "# ============================================================",
        f"# {APP_NAME} - Data File",
        "# ============================================================",
        f"# Theme: {theme}",
        "",
    ]
    for child in root.children:
        _write_node(child, out)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def create_default_data(filepath):
    rows = [
        "# ============================================================",
        f"# {APP_NAME} - Data File",
        "# ============================================================",
        "# Theme: Light",
        "# Use the Edit (✏) buttons in the app, or edit this file directly.",
        "", "",
        "### My Details", "",
        "type: CopyText",
        '"Full Name"',
        '"""Your Full Name Here"""',
        "",
        "---",
        "",
        "type: CopyText",
        '"Email"',
        '"""your@email.com"""',
        "",
        "### End_Of_This_Folder",
        "", "",
        "### Links",
        "",
        "type: Link",
        '"My Website"',
        '"""https://www.yourwebsite.com"""',
        "",
        "### End_Of_This_Folder",
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))


# ─── Scrollable Frame ────────────────────────────────────────────────────────
class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg=COL_BG, **kwargs):
        tk.Frame.__init__(self, parent, bg=bg, **kwargs)
        self.canvas  = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner   = tk.Frame(self.canvas, bg=bg)
        self._win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfig(self._win_id, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self._bind_scroll(self.inner)

    def _bind_scroll(self, w):
        w.bind("<MouseWheel>", self._scroll)
        w.bind("<Button-4>",   self._scroll)
        w.bind("<Button-5>",   self._scroll)

    def _scroll(self, event):
        # FIX: Only scroll if content is long enough to activate the bar
        if self.canvas.yview() == (0.0, 1.0):
            return
        if   event.num == 4: self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: self.canvas.yview_scroll( 1, "units")
        else: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_widget(self, w):
        self._bind_scroll(w)

    def refresh_theme(self):
        self.configure(bg=COL_BG)
        self.canvas.configure(bg=COL_BG, highlightthickness=0, bd=0)
        self.inner.configure(bg=COL_BG)
        self.scrollbar.configure(bg=COL_BG, troughcolor=COL_BG,
                                 activebackground=COL_NEW,
                                 highlightthickness=0, bd=0)
        try:
            self.canvas.itemconfig(self._win_id, width=self.canvas.winfo_width())
        except tk.TclError:
            pass

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()


# ─── Top Bar ─────────────────────────────────────────────────────────────────
class TopBar(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COL_BG)
        self.controller = controller
        self.on_top = False
        self.on_credits = False

        self.left_group = tk.Frame(self, bg=COL_BG)
        self.left_group.pack(side="left", padx=4, pady=2)

        self.right_group = tk.Frame(self, bg=COL_BG)
        self.right_group.pack(side="right", padx=4, pady=2)

        self.home_btn = tk.Button(
            self.left_group, text="🏠 Home", command=self.controller.go_home,
            bg=COL_HOME, fg=CURRENT_THEME["text"], font=("Arial", 8),
            relief="flat", padx=6, pady=2, activebackground=COL_HOME)
            
        self.back_btn = tk.Button(
            self.left_group, text="", command=self.controller.go_back,
            bg=COL_BACK, fg=CURRENT_THEME["text"], font=("Arial", 8),
            relief="flat", padx=6, pady=2, activebackground=COL_BACK)

        self.credits_btn = tk.Button(
            self.right_group, text="⚙ Settings", command=self.toggle_credits,
            bg=COL_TOP_OFF, fg=CURRENT_THEME["text"], font=("Arial", 8),
            relief="flat", padx=6, pady=2, activebackground=COL_TOP_ON)
        self.credits_btn.pack(side="left", padx=2)

        self.theme_btn = tk.Button(
            self.right_group, text=self._theme_label(), command=self.toggle_theme,
            bg=COL_TOP_OFF, fg=CURRENT_THEME["text"], font=("Arial", 8),
            relief="flat", padx=6, pady=2, activebackground=COL_TOP_ON)
        self.theme_btn.pack(side="left", padx=2)

        self.pin_btn = tk.Button(
            self.right_group, text="📌 Pin", command=self.toggle_top,
            bg=COL_TOP_OFF, fg=CURRENT_THEME["text"], font=("Arial", 8),
            relief="flat", padx=6, pady=2, activebackground=COL_TOP_ON)
        self.pin_btn.pack(side="left", padx=2)

    def update_nav(self, current_node, root_node):
        self.home_btn.pack_forget()
        self.back_btn.pack_forget()

        if self.on_credits:
            return

        if current_node is not root_node:
            self.home_btn.pack(side="left", padx=2)
            
        if len(self.controller._nav_stack) > 1:
            prev_node = self.controller._nav_stack[-1]
            self.back_btn.config(text=f"◀ {prev_node.label}")
            self.back_btn.pack(side="left", padx=2)

    def _theme_label(self):
        return "☀ Light" if CURRENT_THEME_MODE == "Dark" else "🌙 Dark"

    def refresh_theme(self):
        self.configure(bg=COL_BG)
        self.left_group.configure(bg=COL_BG)
        self.right_group.configure(bg=COL_BG)
        
        credits_bg = COL_TOP_ON if self.on_credits else COL_TOP_OFF
        self.credits_btn.config(bg=credits_bg, fg=CURRENT_THEME["text"], activebackground=COL_TOP_ON)
        
        self.home_btn.config(bg=COL_HOME, fg=CURRENT_THEME["text"], activebackground=COL_HOME)
        self.back_btn.config(bg=COL_BACK, fg=CURRENT_THEME["text"], activebackground=COL_BACK)
        
        pin_bg = COL_TOP_ON if self.on_top else COL_TOP_OFF
        self.pin_btn.config(bg=pin_bg, fg=CURRENT_THEME["text"], activebackground=COL_TOP_ON)
        
        self.theme_btn.config(
            text=self._theme_label(),
            bg=COL_TOP_OFF, fg=CURRENT_THEME["text"], activebackground=COL_TOP_ON)

    def toggle_theme(self):
        self.controller.toggle_theme()

    def toggle_top(self):
        self.on_top = not self.on_top
        self.controller.wm_attributes("-topmost", self.on_top)
        self.pin_btn.config(
            text="📌 Pinned!" if self.on_top else "📌 Pin",
            bg=COL_TOP_ON if self.on_top else COL_TOP_OFF,
            fg=CURRENT_THEME["text"])

    def toggle_credits(self):
        self.on_credits = not self.on_credits
        if self.on_credits:
            self.credits_btn.config(text="☰ Menu", bg=COL_TOP_ON, fg=CURRENT_THEME["text"])
            self.controller.show_credits()
        else:
            self.credits_btn.config(text="⚙ Settings", bg=COL_TOP_OFF, fg=CURRENT_THEME["text"])
            self.controller.restore_folder()
        self.update_nav(self.controller.current_node, self.controller.root_node)

    def set_credits_off(self):
        self.on_credits = False
        self.credits_btn.config(text="⚙ Settings", bg=COL_TOP_OFF, fg=CURRENT_THEME["text"])


# ─── Edit Dialog ─────────────────────────────────────────────────────────────
class EditDialog(tk.Toplevel):
    def __init__(self, parent_win, node, parent_node, controller):
        super().__init__(parent_win)
        self.controller  = controller
        self.node        = node
        self.parent_node = parent_node
        self._root_level = (parent_node.parent is None)

        self.title("✏  Edit Item" if node else "✏  New Item")
        self.configure(bg=COL_BG)
        self.resizable(True, False)
        self.minsize(340, 380)
        self.grab_set()
        self.focus_set()

        init_kind = node.kind if node else ("folder" if self._root_level else "CopyText")
        self._kind = tk.StringVar(value=init_kind)

        tk.Label(self, text="Label:", bg=COL_BG, fg=CURRENT_THEME["text"],
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 0))
        self.lbl_var   = tk.StringVar(value=node.label if node else "")
        self.lbl_entry = tk.Entry(
            self, textvariable=self.lbl_var, font=("Arial", 9),
            bg=CURRENT_THEME["entry_bg"], fg=CURRENT_THEME["entry_fg"],
            insertbackground=CURRENT_THEME["entry_fg"], relief="solid", bd=1)
        self.lbl_entry.pack(fill="x", padx=14, pady=(3, 8))

        self.content_hdr = tk.Label(self, text="Content:", bg=COL_BG, fg=CURRENT_THEME["text"],
                                    font=("Arial", 9, "bold"))
        self.content_hdr.pack(anchor="w", padx=14)
        self.txt = tk.Text(
            self, font=("Arial", 9), height=6, relief="solid", bd=1, wrap="word",
            bg=CURRENT_THEME["text_bg"], fg=CURRENT_THEME["text_fg"],
            insertbackground=CURRENT_THEME["text_fg"])
        self.txt.pack(fill="x", padx=14, pady=(3, 8))
        if node and node.kind != "folder" and node.content:
            self.txt.insert("1.0", node.content)

        tk.Label(self, text="Type:", bg=COL_BG, fg=CURRENT_THEME["text"],
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=14)
        tf = tk.Frame(self, bg=COL_BG)
        tf.pack(fill="x", padx=14, pady=(3, 10))
        self._type_btns = {}
        
        for i, (kind, lbl, _col) in enumerate(TYPES):
            col = TYPE_PALETTE.get(kind, _col)
            btn = tk.Button(tf, text=lbl, bg=col, fg=CURRENT_THEME["text"],
                            command=lambda k=kind: self._select_type(k),
                            relief="flat", font=("Arial", 8), pady=4,
                            activebackground=col)
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
            self._type_btns[kind] = btn
            
        for c in range(len(TYPES)):
            tf.grid_columnconfigure(c, weight=1)

        if self._root_level:
            for k, b in self._type_btns.items():
                if k != "folder":
                    b.config(state="disabled", fg=CURRENT_THEME["muted"])
            tk.Label(self, text="(Root-level items must be Groups)",
                     bg=COL_BG, fg=CURRENT_THEME["muted"],
                     font=("Arial", 8, "italic")).pack(padx=14, anchor="w")

        bf = tk.Frame(self, bg=COL_BG)
        bf.pack(fill="x", padx=14, pady=(4, 14))
        self.del_btn = tk.Button(
            bf, text="🗑  Delete", command=self._on_delete,
            bg="#964444" if CURRENT_THEME_MODE == "Dark" else "#FF8080", fg=CURRENT_THEME["text"], relief="flat", font=("Arial", 9, "bold"), pady=6)
        self.del_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.acc_btn = tk.Button(
            bf, text="✓  Accept", command=self._on_accept,
            bg="#789044" if CURRENT_THEME_MODE == "Dark" else "#90EE90", fg=CURRENT_THEME["text"], relief="flat", font=("Arial", 9, "bold"), pady=6)
        self.acc_btn.pack(side="right", fill="x", expand=True)

        self._select_type(init_kind)

        self.update_idletasks()
        x = parent_win.winfo_x() + (parent_win.winfo_width()  - self.winfo_width())  // 2
        y = parent_win.winfo_y() + (parent_win.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.lbl_entry.focus_set()

    def refresh_theme(self):
        self.configure(bg=COL_BG)
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=COL_BG, fg=CURRENT_THEME["text"])
            elif isinstance(child, tk.Frame):
                child.config(bg=COL_BG)
        self.lbl_entry.config(bg=CURRENT_THEME["entry_bg"], fg=CURRENT_THEME["entry_fg"],
                              insertbackground=CURRENT_THEME["entry_fg"])
        self.content_hdr.config(bg=COL_BG, fg=CURRENT_THEME["text"])
        self.txt.config(bg=CURRENT_THEME["text_bg"], fg=CURRENT_THEME["text_fg"],
                        insertbackground=CURRENT_THEME["text_fg"])
        if self._kind.get() == "folder":
            self.txt.config(bg=CURRENT_THEME["disabled_bg"])
        self.del_btn.config(fg=CURRENT_THEME["text"])
        self.acc_btn.config(fg=CURRENT_THEME["text"])
        self._select_type(self._kind.get())

    def _select_type(self, kind):
        if self._root_level and kind != "folder":
            return
        self._kind.set(kind)
        for k, b in self._type_btns.items():
            b.config(relief="solid" if k == kind else "flat",
                     bd=2         if k == kind else 0)
        is_group = (kind == "folder")
        self.txt.config(
            state="disabled" if is_group else "normal",
            bg=CURRENT_THEME["disabled_bg"] if is_group else CURRENT_THEME["text_bg"],
            fg=CURRENT_THEME["text_fg"],
            insertbackground=CURRENT_THEME["text_fg"])
        self.content_hdr.config(
            text="Content: (Groups contain sub-items)" if is_group else "Content:",
            bg=COL_BG, fg=CURRENT_THEME["text"])

    def _on_delete(self):
        self.lbl_entry.delete(0, "end")
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        if self._kind.get() == "folder":
            self.txt.config(state="disabled", bg=CURRENT_THEME["disabled_bg"])
        self._flash(0)

    def _flash(self, i=0):
        palette = ["#FFD700", "#90EE90"] * 3
        if i < len(palette):
            self.acc_btn.config(bg=palette[i])
            self.after(120, self._flash, i + 1)

    def _on_accept(self):
        label = self.lbl_var.get().strip()
        kind  = self._kind.get()
        self.txt.config(state="normal")
        content = self.txt.get("1.0", "end").strip() if kind != "folder" else ""
        folder  = self.parent_node

        if not label:
            if self.node and self.node in folder.children:
                if self.node.kind == "folder" and self.node.children:
                    idx = folder.children.index(self.node)
                    folder.children.remove(self.node)
                    for j, child in enumerate(self.node.children):
                        child.parent = folder
                        folder.children.insert(idx + j, child)
                else:
                    folder.children.remove(self.node)
        else:
            if self.node:
                old_kind = self.node.kind
                self.node.label   = label
                self.node.kind    = kind
                self.node.content = content
                if kind == "folder" and old_kind != "folder":
                    self.node.children = []
                elif kind != "folder" and old_kind == "folder":
                    self.node.children = []
            else:
                new_node = Node(kind, label, content, folder)
                folder.add_child(new_node)

        save_tree(self.controller.root_node, self.controller.data_filepath)
        self.controller.reload_and_navigate()
        self.destroy()


# ─── Folder View ─────────────────────────────────────────────────────────────
class FolderView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COL_BG)
        self.controller = controller
        self.sf = ScrollableFrame(self, bg=COL_BG)
        self.sf.pack(fill="both", expand=True)

    def refresh_theme(self):
        self.configure(bg=COL_BG)
        self.sf.refresh_theme()

    def render(self, node):
        self.refresh_theme()
        self.sf.clear()
        inner = self.sf.inner

        for idx, child in enumerate(node.children):
            self._make_row(inner, node, child, idx)

        sep = tk.Frame(inner, bg=COL_BG, height=5)
        sep.pack(fill="x")
        self.sf.add_widget(sep)

        add_btn = tk.Button(
            inner, text="＋  Blank Line",
            command=lambda n=node: EditDialog(
                self.controller, None, n, self.controller),
            bg=COL_NEW, fg=CURRENT_THEME["text"], relief="flat", pady=4,
            font=("Arial", 8, "italic"), activebackground=COL_NEW)
        add_btn.pack(fill="x", padx=6, pady=(0, 10))
        self.sf.add_widget(add_btn)

    def _make_row(self, parent_widget, folder_node, child, idx):
        dark = (CURRENT_THEME_MODE == "Dark")
        if child.kind == "folder":
            color = COL_FOLDER if idx % 2 == 0 else ("#C09F1A" if dark else "#FFE87C")
            text  = f"📁  {child.label}"
        elif child.kind == "CopyText":
            color = COL_A if idx % 2 == 0 else ("#6B823C" if dark else "#B0EEB0")
            text  = child.label
        elif child.kind in ("Link", "LocalPath"):
            color = COL_B if idx % 2 == 0 else ("#4B5E9F" if dark else "#BFE8F5")
            text  = child.label
        elif child.kind == "Command":
            color = COL_C if idx % 2 == 0 else ("#AF5959" if dark else "#FFC8D0")
            text  = child.label
        else:
            color = COL_BG
            text  = child.label

        row = tk.Frame(parent_widget, bg=COL_BG)
        row.pack(fill="x", padx=6, pady=2)
        self.sf.add_widget(row)

        main_btn = tk.Button(row, text=text,
                             bg=color, fg=CURRENT_THEME["text"], relief="flat", pady=5,
                             font=("Arial", 9), anchor="w", activebackground=color)
        
        def make_safe_cmd(kind, content, button, orig_color):
            def safe_cmd():
                try:
                    if kind == "folder":
                        self.controller.navigate_to(child)
                    elif kind == "CopyText":
                        self.controller.copy(content)
                    elif kind in ("Link", "LocalPath"):
                        self.controller.open_link(content)
                    elif kind == "Command":
                        self.controller.execute_command(content)
                except Exception:
                    fail_color = "#964444" if CURRENT_THEME_MODE == "Dark" else "#FF8080"
                    palette = [fail_color, orig_color, fail_color, orig_color]
                    def do_flash(i=0):
                        try:
                            if i < len(palette):
                                button.config(bg=palette[i], activebackground=palette[i])
                                button.after(150, lambda: do_flash(i + 1))
                            else:
                                button.config(bg=orig_color, activebackground=orig_color)
                        except tk.TclError:
                            pass
                    do_flash()
            return safe_cmd

        main_btn.config(command=make_safe_cmd(child.kind, child.content, main_btn, color))
        main_btn.pack(side="left", fill="x", expand=True)
        self.sf.add_widget(main_btn)

        edit_btn = tk.Button(
            row, text="✏",
            command=lambda c=child, fn=folder_node: EditDialog(
                self.controller, c, fn, self.controller),
            bg=COL_EDIT, fg=CURRENT_THEME["text"], relief="flat", pady=5, padx=8,
            font=("Arial", 9), activebackground=COL_EDIT)
        edit_btn.pack(side="right")
        self.sf.add_widget(edit_btn)

        is_first = (idx == 0)
        up_btn = tk.Button(
            row, text="▲",
            command=lambda i=idx, fn=folder_node: self._move_up(fn, i),
            bg=COL_UP, fg=CURRENT_THEME["text"], relief="flat", pady=5, padx=8,
            font=("Arial", 9), state="disabled" if is_first else "normal",
            disabledforeground=CURRENT_THEME["muted"], activebackground=COL_UP)
        up_btn.pack(side="right")
        self.sf.add_widget(up_btn)

    def _move_up(self, folder_node, idx):
        if idx == 0:
            return
        ch = folder_node.children
        ch[idx - 1], ch[idx] = ch[idx], ch[idx - 1]
        save_tree(self.controller.root_node, self.controller.data_filepath)
        self.controller.reload_and_navigate()


# ─── Credits & Settings Page ─────────────────────────────────────────────────
class CreditsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COL_BG)
        self.controller = controller
        self.sf = ScrollableFrame(self, bg=COL_BG)
        self.sf.pack(fill="both", expand=True)
        inner = self.sf.inner

        # Centered Headings Helper
        def heading(text, pady=(12, 4)):
            w = tk.Label(inner, text=text, bg=COL_BG, fg=CURRENT_THEME["text"],
                         wraplength=370, justify="center", anchor="center",
                         font=("Arial", 11, "bold"))
            w.pack(padx=14, pady=pady, fill="x")
            self.sf.add_widget(w)

        # Left-Justified Body Text Helper
        def body(text, pady=(2, 2), font_size=9, italic=False):
            font_style = ("Arial", font_size, "italic" if italic else "normal")
            w = tk.Label(inner, text=text, bg=COL_BG, fg=CURRENT_THEME["text"],
                         wraplength=370, justify="left", anchor="w",
                         font=font_style)
            w.pack(padx=14, pady=pady, fill="x")
            self.sf.add_widget(w)

        def link(label, url, col_key):
            col = COL_A if col_key == "COL_A" else COL_B
            b = tk.Button(inner, text=label,
                          command=lambda: webbrowser.open(url),
                          bg=col, fg=CURRENT_THEME["text"], relief="flat",
                          font=("Arial", 9), pady=4, activebackground=col)
            b._col_key = col_key
            b.pack(padx=20, pady=4, fill="x")
            self.sf.add_widget(b)

        def div():
            d = tk.Label(inner, text="─" * 46, bg=COL_BG,
                         fg=CURRENT_THEME["separator"], font=("Arial", 8))
            d.pack(pady=6)
            self.sf.add_widget(d)

        # --- Header ---
        w_title = tk.Label(inner, text="👑  PasteKing", bg=COL_BG, fg=CURRENT_THEME["text"],
                           justify="center", anchor="center", font=("Arial", 14, "bold"))
        w_title.pack(padx=14, pady=(14, 2), fill="x")
        self.sf.add_widget(w_title)
        
        w_sub = tk.Label(inner, text="Created by David William Beck", bg=COL_BG, fg=CURRENT_THEME["text"],
                         justify="center", anchor="center", font=("Arial", 10))
        w_sub.pack(padx=14, pady=(0, 4), fill="x")
        self.sf.add_widget(w_sub)
        link("🌐  www.dwbeck.com", "https://www.dwbeck.com", "COL_B")
        div()
        
        # --- Data Profiles ---
        heading("📂  Data Profiles")
        body("PasteKing lets you save and instantly recall text, web addresses, system folders, or automated commands with a single click.")
        body("You can create multiple distinct configuration files to instantly swap between home profiles, work details, or specific coding environments.")
        
        pf = tk.Frame(inner, bg=COL_BG)
        pf.pack(fill="x", padx=14, pady=6)
        self.sf.add_widget(pf)
        
        load_btn = tk.Button(pf, text="📁 Load Profile", command=self.controller.load_profile,
                             bg=COL_B, fg=CURRENT_THEME["text"], relief="flat", font=("Arial", 9), pady=3, padx=10)
        load_btn._col_key = "COL_B"
        load_btn.pack(side="left", padx=(0, 10))
        
        new_btn = tk.Button(pf, text="➕ New Profile", command=self.controller.new_profile,
                            bg=COL_A, fg=CURRENT_THEME["text"], relief="flat", font=("Arial", 9), pady=3, padx=10)
        new_btn._col_key = "COL_A"
        new_btn.pack(side="left")
        
        self.profile_lbl = tk.Label(inner, text="", bg=COL_BG, fg=CURRENT_THEME["text"],
                                    font=("Arial", 8, "italic"), anchor="w", justify="left")
        self.profile_lbl.pack(padx=14, pady=(2, 0), fill="x")
        self.sf.add_widget(self.profile_lbl)
        self.update_profile_label()
        div()
        
        # --- How to Use ---
        heading("📖  How to Use")
        body("• Click any item row to instantly run its action (copying text, launching a URL, or running code).")
        body("• Tap the up arrow (▲) to reorder items cleanly.")
        body("• Tap the pencil (✏) icon to edit labels or underlying values inside the app.")
        body("• Click '＋ Blank Line' at the bottom to add a fresh shortcut.")
        body("• Erase an item's Label entirely and hit Accept to delete it.")
        div()
        
        # --- Item Types ---
        heading("📋  Shortcut Types")
        body("📋 Text: Copies content directly onto your clipboard.")
        body("🌐 Website: Launches a secure link inside your web browser.")
        body("📂 Local: Opens a local directory paths or machine file.")
        body("⚡ Cmd: Runs customized command terminal variables safely.")
        body("📁 Group: A organizational tree containing nested items.")
        div()

        # --- Manual Editing ---
        heading("📝  Editing Profiles Manually")
        body("If you prefer structural control, edit the configuration text files directly via Notepad:")
        body("1. Each segment features a 'type', a '\"Label\"', and a '\"\"\"Content\"\"\"' script.")
        body("2. Keep modules isolated by adding a simple line break: ---")
        body("3. Instantiate sub-directories using '### Folder Name', and close them using '### End_Of_This_Folder'.")
        div()
        
        # --- Support ---
        heading("💚  Support")
        body("PasteKing is free, completely open-source software. You are encouraged to distribute or tweak it as you see fit! If it speeds up your workspace, donations are welcome.")
        link("☕  Buy David a Coffee — PayPal", "https://www.paypal.me/dwbeck", "COL_A")
        div()

        # --- Disclaimer ---
        heading("⚖️  Disclaimer")
        body("This application is provided for use strictly at your own risk. The developer assumes no legal responsibility or liability for any errors, accidental misuse, or data modifications arising from execution.", font_size=8)
        body("PasteKing is built efficiently using standard, trusted native Python libraries. It operates entirely offline without external background telemetry scripts.", font_size=8)

        # --- Footer ---
        w_foot = tk.Label(inner, text="© David William Beck  —  Free & Open Source  🐍", bg=COL_BG,
                          fg=CURRENT_THEME["text"], font=("Arial", 8), justify="center", anchor="center")
        w_foot.pack(pady=(12, 14), fill="x")
        self.sf.add_widget(w_foot)

    def update_profile_label(self):
        if hasattr(self, 'profile_lbl') and hasattr(self.controller, 'data_filepath'):
            self.profile_lbl.config(text=f"Active Profile: {os.path.basename(self.controller.data_filepath)}")

    def refresh_theme(self):
        self.configure(bg=COL_BG)
        self.sf.refresh_theme()
        for w in self.sf.inner.winfo_children():
            if isinstance(w, tk.Label):
                if w.cget("text").startswith("─"):
                    w.config(bg=COL_BG, fg=CURRENT_THEME["separator"])
                else:
                    w.config(bg=COL_BG, fg=CURRENT_THEME["text"])
            elif isinstance(w, tk.Button):
                col_key = getattr(w, "_col_key", "COL_B")
                col = COL_A if col_key == "COL_A" else COL_B
                w.config(bg=col, activebackground=col, fg=CURRENT_THEME["text"])
            elif isinstance(w, tk.Frame):
                w.config(bg=COL_BG)
                for child in w.winfo_children():
                    if isinstance(child, tk.Button):
                        col_key = getattr(child, "_col_key", "COL_B")
                        col = COL_A if col_key == "COL_A" else COL_B
                        child.config(bg=col, activebackground=col, fg=CURRENT_THEME["text"])


# ─── Controller ──────────────────────────────────────────────────────────────
class UI_Controller(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.data_filepath = get_active_filepath()
        
        if not os.path.exists(self.data_filepath):
            create_default_data(self.data_filepath)

        self.theme_mode = get_theme_from_file(self.data_filepath)
        apply_theme_globals(self.theme_mode)

        self.title(APP_NAME)
        self.geometry("420x540")
        self.configure(bg=COL_BG)
        self.resizable(True, True)

        self.root_node    = None
        self.current_node = None
        self._nav_stack   = []

        self.root_node = parse_data_file(self.data_filepath)
        if self.root_node is None:
            mb.showerror("Error", f"Could not load active profile.\n\nExpected:\n{self.data_filepath}")
            self.destroy()
            return

        self.top_bar = TopBar(self, self)
        self.top_bar.pack(side="top", fill="x")

        self.container = tk.Frame(self, bg=COL_BG)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.folder_view  = FolderView(self.container, self)
        self.folder_view.grid(row=0, column=0, sticky="nsew")

        self.credits_page = CreditsPage(self.container, self)
        self.credits_page.grid(row=0, column=0, sticky="nsew")

        self.go_home()

    def _set_data_filepath(self, new_path):
        self.data_filepath = os.path.abspath(new_path)
        try:
            rel_path = os.path.relpath(self.data_filepath, _BASE_DIR)
            with open(PATH_FILE, "w", encoding="utf-8") as f:
                f.write(rel_path)
        except Exception as e:
            print(f"Warning: Could not update Path file: {e}")

    def load_profile(self):
        path = fd.askopenfilename(
            initialdir=DATA_DIR,
            title="Select Data Profile",
            filetypes=[("Text Files", "*.txt")]
        )
        if not path:
            return
            
        test_root = parse_data_file(path)
        if test_root is None:
            mb.showerror("Error", "Invalid or corrupt file. Reverting to the previous profile.")
            return
            
        self._set_data_filepath(path)
        self._reload_full_state()

    def new_profile(self):
        name = sd.askstring("New Profile", "Enter new profile name (e.g., Work):")
        if not name:
            return
            
        name = name.strip()
        if not name.lower().endswith(".txt"):
            name += ".txt"
            
        new_path = os.path.join(DATA_DIR, name)
        if not os.path.exists(new_path):
            create_default_data(new_path)
            
        self._set_data_filepath(new_path)
        self._reload_full_state()

    def _reload_full_state(self):
        self.root_node = parse_data_file(self.data_filepath)
        
        mode = get_theme_from_file(self.data_filepath)
        self.theme_mode = mode
        apply_theme_globals(mode)
        
        self.credits_page.update_profile_label()
        self.go_home()
        self.apply_theme()

    def set_theme(self, mode):
        mode = "Dark" if str(mode).lower() == "dark" else "Light"
        self.theme_mode = mode
        apply_theme_globals(mode)
        set_theme_in_file(self.data_filepath, mode)
        self.apply_theme()

    def toggle_theme(self):
        self.set_theme("Light" if self.theme_mode == "Dark" else "Dark")

    def apply_theme(self):
        self.configure(bg=COL_BG)
        self.container.configure(bg=COL_BG)
        self.top_bar.refresh_theme()
        self.folder_view.refresh_theme()
        self.credits_page.refresh_theme()
        if self.top_bar.on_credits:
            self.credits_page.tkraise()
        else:
            if self.current_node is None:
                self.current_node = self.root_node
            self._show_folder(self.current_node)

    def _get_path(self):
        path = []
        node = self.current_node
        while node and node is not self.root_node:
            if node.kind == "folder":
                path.insert(0, node.label)
            node = node.parent
        return path

    def reload_and_navigate(self):
        path = self._get_path()
        self.root_node = parse_data_file(self.data_filepath)
        target = self.root_node
        new_stack = []
        
        for label in path:
            found = next(
                (c for c in target.children
                 if c.kind == "folder" and c.label == label), None)
            if found:
                new_stack.append(target)
                target = found
            else:
                break
                
        self._nav_stack = new_stack
        self.current_node = target
        self._show_folder(target)

    def navigate_to(self, node):
        if self.current_node:
            self._nav_stack.append(self.current_node)
        self.current_node = node
        self._show_folder(node)

    def go_home(self):
        self._nav_stack.clear()
        self.top_bar.set_credits_off()
        self.current_node = self.root_node
        self._show_folder(self.root_node)

    def go_back(self):
        if self._nav_stack:
            node = self._nav_stack.pop()
            self.current_node = node
            self._show_folder(node)

    def _show_folder(self, node):
        title = APP_NAME if node is self.root_node else f"{APP_NAME}  ·  {node.label}"
        self.title(title)
        self.top_bar.update_nav(node, self.root_node)
        self.folder_view.render(node)
        self.folder_view.tkraise()

    def show_credits(self):
        self.credits_page.tkraise()

    def restore_folder(self):
        self.folder_view.tkraise()

    def copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def open_link(self, path):
        if path.startswith(("http://", "https://")):
            webbrowser.open(path)
        else:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Linux":
                subprocess.Popen(["xdg-open", path])
            elif system == "Darwin":
                subprocess.Popen(["open", path])

    def execute_command(self, content):
        current_os = platform.system()
        if current_os == "Windows":
            os.system(content)
        elif current_os in ("Linux", "Darwin"):
            subprocess.Popen(content, shell=True)
        else:
            os.system(content)


if __name__ == "__main__":
    app = UI_Controller()
    app.mainloop()
