"""
Rekaren v8 – Exam Preparation & Swedish Harvard Reference Manager
-----------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import tkinter.font as tkfont
import sqlite3, os, sys, shutil, threading, json
import urllib.request, webbrowser, subprocess
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════
# PATHS
# ══════════════════════════════════════════════════════════════════════
class Paths:
    APP_VERSION = "8.0.0"
    UPDATE_URL = "https://raw.githubusercontent.com/DITTNAMN/rekaren/main/version.json"
    DOWNLOAD_URL = "https://github.com/DITTNAMN/rekaren/releases/latest"

    @staticmethod
    def data_dir():
        if sys.platform == "win32":
            base = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Rekaren")
        elif sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Application Support/Rekaren")
        else:
            base = os.path.expanduser("~/.local/share/Rekaren")
        os.makedirs(base, exist_ok=True)
        try:
            t = os.path.join(base, ".wtest")
            open(t, "w").close()
            os.remove(t)
        except Exception:
            base = os.path.join(os.path.expanduser("~"), "Rekaren")
            os.makedirs(base, exist_ok=True)
        return base

    @classmethod
    def db_path(cls):
        return os.path.join(cls.data_dir(), "rekaren.db")


# ══════════════════════════════════════════════════════════════════════
# FONTS
# ══════════════════════════════════════════════════════════════════════
class Fonts:
    """Global typography — family depends on platform."""

    FAMILY = "Segoe UI" if sys.platform == "win32" else ("SF Pro Text" if sys.platform == "darwin" else "Ubuntu")

    BASE        = (FAMILY, 10)
    BASE_BOLD   = (FAMILY, 10, "bold")
    SMALL       = (FAMILY, 9)
    SMALL_ITAL  = (FAMILY, 9, "italic")
    HEADING     = (FAMILY, 12, "bold")
    TITLE       = (FAMILY, 14, "bold")
    TAB         = (FAMILY, 10, "bold")
    MONO        = ("Consolas" if sys.platform == "win32" else "Menlo", 10)

    @classmethod
    def install(cls, root):
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
            try:
                tkfont.nametofont(name).configure(family=cls.FAMILY, size=10)
            except tk.TclError:
                pass
        try:
            tkfont.nametofont("TkFixedFont").configure(family=cls.MONO[0], size=10)
        except tk.TclError:
            pass


# ══════════════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════════════
class Theme:
    LIGHT = {
        "name": "light",
        "bg": "#f5f6f8",
        "fg": "#1a1a1a",
        "fg_muted": "#666666",
        "field_bg": "#ffffff",
        "field_fg": "#1a1a1a",
        "select_bg": "#cce4ff",
        "select_fg": "#000000",
        "btn_bg": "#e8e8e8",
        "btn_fg": "#1a1a1a",
        "btn_active": "#d8d8d8",
        "accent_bg": "#2d7d46",
        "accent_fg": "#ffffff",
        "accent_active": "#3a9d5a",
        "danger_bg": "#b03a3a",
        "danger_fg": "#ffffff",
        "danger_active": "#c94a4a",
        "border": "#c8c8c8",
        "tree_bg": "#ffffff",
        "tree_fg": "#1a1a1a",
        "tree_stripe": "#f0f0f0",
        "entry_bg": "#ffffff",
        "entry_fg": "#1a1a1a",
        "separator": "#d8d8d8",
        "status_bg": "#e8e8e8",
        "status_fg": "#333333",
        "placeholder": "#999999",
        "listbox_placeholder": "#999999",
        "w0": "#9e9e9e",
        "w1": "#9e9e9e",
        "w2": "#5c9ce0",
        "w3": "#2f7fd6",
        "w4": "#1a63b8",
        "w5": "#0a3d85",
    }

    DARK = {
        "name": "dark",
        "bg": "#1e1e1e",
        "fg": "#e6e6e6",
        "fg_muted": "#9a9a9a",
        "field_bg": "#2a2a2a",
        "field_fg": "#e6e6e6",
        "select_bg": "#3a5c8c",
        "select_fg": "#ffffff",
        "btn_bg": "#2e2e2e",
        "btn_fg": "#e6e6e6",
        "btn_active": "#3a3a3a",
        "accent_bg": "#3a9d5a",
        "accent_fg": "#ffffff",
        "accent_active": "#4dbf6b",
        "danger_bg": "#c94a4a",
        "danger_fg": "#ffffff",
        "danger_active": "#e05a5a",
        "border": "#404040",
        "tree_bg": "#252525",
        "tree_fg": "#e6e6e6",
        "tree_stripe": "#2c2c2c",
        "entry_bg": "#2a2a2a",
        "entry_fg": "#e6e6e6",
        "separator": "#3a3a3a",
        "status_bg": "#2a2a2a",
        "status_fg": "#b0b0b0",
        "placeholder": "#777777",
        "listbox_placeholder": "#777777",
        "w0": "#777777",
        "w1": "#8e8e8e",
        "w2": "#6da8e0",
        "w3": "#4f93d6",
        "w4": "#3a80c8",
        "w5": "#7ab8ff",
    }

    @classmethod
    def colors(cls, name):
        return cls.DARK if name == "dark" else cls.LIGHT

    @classmethod
    def apply(cls, root, name):
        c = cls.colors(name)
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        root.configure(bg=c["bg"])

        # ---- base ----
        style.configure(".",
                        background=c["bg"],
                        foreground=c["fg"],
                        fieldbackground=c["field_bg"],
                        font=Fonts.BASE)
        style.configure("TFrame", background=c["bg"])
        style.configure("TLabel", background=c["bg"], foreground=c["fg"], font=Fonts.BASE)
        style.configure("Muted.TLabel", background=c["bg"], foreground=c["fg_muted"], font=Fonts.SMALL)
        style.configure("Heading.TLabel", background=c["bg"], foreground=c["fg"], font=Fonts.HEADING)
        style.configure("TLabelframe", background=c["bg"], foreground=c["fg"],
                        bordercolor=c["border"], relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=c["bg"], foreground=c["fg"],
                        font=Fonts.BASE_BOLD)
        style.configure("TSeparator", background=c["separator"])

        # ---- buttons ----
        style.configure("TButton",
                        background=c["btn_bg"], foreground=c["btn_fg"],
                        bordercolor=c["border"], focuscolor=c["btn_bg"],
                        padding=(10, 6), font=Fonts.BASE)
        style.map("TButton",
                  background=[("active", c["btn_active"]), ("pressed", c["btn_active"])],
                  foreground=[("active", c["btn_fg"])])

        style.configure("Accent.TButton",
                        background=c["accent_bg"], foreground=c["accent_fg"],
                        bordercolor=c["accent_bg"],
                        padding=(12, 7), font=Fonts.BASE_BOLD)
        style.map("Accent.TButton",
                  background=[("active", c["accent_active"]), ("pressed", c["accent_active"])],
                  foreground=[("active", c["accent_fg"])])

        style.configure("Danger.TButton",
                        background=c["danger_bg"], foreground=c["danger_fg"],
                        bordercolor=c["danger_bg"],
                        padding=(10, 6), font=Fonts.BASE)
        style.map("Danger.TButton",
                  background=[("active", c["danger_active"]), ("pressed", c["danger_active"])],
                  foreground=[("active", c["danger_fg"])])

        # ---- entries ----
        style.configure("TEntry",
                        fieldbackground=c["entry_bg"], foreground=c["entry_fg"],
                        bordercolor=c["border"], insertcolor=c["fg"],
                        padding=4)
        style.configure("TCombobox",
                        fieldbackground=c["entry_bg"], background=c["entry_bg"],
                        foreground=c["entry_fg"], arrowcolor=c["fg"],
                        bordercolor=c["border"], padding=4)
        style.map("TCombobox",
                  fieldbackground=[("readonly", c["entry_bg"])],
                  foreground=[("readonly", c["entry_fg"])])

        # ---- radio ----
        style.configure("TRadiobutton",
                        background=c["bg"], foreground=c["fg"], focuscolor=c["bg"])
        style.map("TRadiobutton", background=[("active", c["bg"])])

        # ---- notebook ----
        style.configure("TNotebook", background=c["bg"], bordercolor=c["border"])
        style.configure("TNotebook.Tab",
                        background=c["btn_bg"], foreground=c["btn_fg"],
                        padding=[16, 8], font=Fonts.TAB,
                        bordercolor=c["border"])
        style.map("TNotebook.Tab",
                  background=[("selected", c["bg"]), ("active", c["btn_active"])],
                  foreground=[("selected", c["fg"])])

        # ---- treeview ----
        style.configure("Treeview",
                        background=c["tree_bg"], fieldbackground=c["tree_bg"],
                        foreground=c["tree_fg"], bordercolor=c["border"],
                        rowheight=26, font=Fonts.BASE)
        style.configure("Treeview.Heading",
                        background=c["btn_bg"], foreground=c["btn_fg"],
                        bordercolor=c["border"], font=Fonts.BASE_BOLD,
                        padding=(6, 6))
        style.map("Treeview",
                  background=[("selected", c["select_bg"])],
                  foreground=[("selected", c["select_fg"])])
        style.map("Treeview.Heading",
                  background=[("active", c["btn_active"])])

        # ---- scrollbar ----
        style.configure("TScrollbar",
                        background=c["btn_bg"], troughcolor=c["bg"],
                        bordercolor=c["border"], arrowcolor=c["fg"])
        style.map("TScrollbar", background=[("active", c["btn_active"])])

        # ---- status bar ----
        style.configure("Status.TLabel",
                        background=c["status_bg"], foreground=c["status_fg"],
                        font=Fonts.SMALL, padding=(8, 4))

        # ---- tk widgets ----
        for w in cls._walk(root):
            cls._style_tk_widget(w, c)

    @classmethod
    def _walk(cls, widget):
        yield widget
        for child in widget.winfo_children():
            yield from cls._walk(child)

    @classmethod
    def _style_tk_widget(cls, w, c):
        try:
            if isinstance(w, tk.Listbox):
                w.configure(
                    bg=c["tree_bg"], fg=c["tree_fg"],
                    selectbackground=c["select_bg"], selectforeground=c["select_fg"],
                    highlightbackground=c["border"], highlightcolor=c["border"],
                    bd=1, relief="solid",
                    font=Fonts.BASE, activestyle="none")
            elif isinstance(w, tk.Text):
                w.configure(
                    bg=c["entry_bg"], fg=c["entry_fg"],
                    insertbackground=c["fg"],
                    selectbackground=c["select_bg"], selectforeground=c["select_fg"],
                    highlightbackground=c["border"], highlightcolor=c["border"],
                    bd=1, relief="solid",
                    font=Fonts.BASE)
            elif isinstance(w, tk.Menu):
                w.configure(
                    bg=c["btn_bg"], fg=c["btn_fg"],
                    activebackground=c["select_bg"], activeforeground=c["select_fg"],
                    bd=0, font=Fonts.BASE)
            elif isinstance(w, tk.Frame):
                w.configure(bg=c["bg"])
            elif isinstance(w, tk.Toplevel):
                w.configure(bg=c["bg"])
            elif isinstance(w, tk.Label):
                w.configure(bg=c["bg"], fg=c["fg"])
        except tk.TclError:
            pass


# ══════════════════════════════════════════════════════════════════════
# PLACEHOLDER ENTRY
# ══════════════════════════════════════════════════════════════════════
class PlaceholderEntry(ttk.Entry):
    """ttk.Entry with a grey placeholder shown when empty & unfocused."""

    def __init__(self, master, placeholder="", **kw):
        super().__init__(master, **kw)
        self.placeholder = placeholder
        self._showing = False
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self._show()

    def _show(self):
        if not self.get():
            self._showing = True
            self.insert(0, self.placeholder)
            try:
                self.configure(foreground="#999999")
            except tk.TclError:
                pass

    def _on_focus_in(self, _=None):
        if self._showing:
            self.delete(0, tk.END)
            self._showing = False
            try:
                self.configure(foreground="")
            except tk.TclError:
                pass

    def _on_focus_out(self, _=None):
        if not self.get():
            self._show()

    def value(self):
        return "" if self._showing else self.get().strip()


# ══════════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════════
class Database:
    def __init__(self, path):
        self.path = path
        self._init_schema()

    def _conn(self):
        return sqlite3.connect(self.path)

    def _has_col(self, cur, table, col):
        cur.execute(f"PRAGMA table_info({table})")
        return any(r[1] == col for r in cur.fetchall())

    def _init_schema(self):
        with self._conn() as conn:
            c = conn.cursor()
            c.executescript("""
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS examinationspunkter (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS premisser (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    weight INTEGER NOT NULL CHECK(weight BETWEEN 0 AND 5),
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS references_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER NOT NULL,
                    ref_type TEXT NOT NULL,
                    author TEXT, year TEXT, title TEXT, container TEXT,
                    publisher TEXT, place TEXT, edition TEXT, pages TEXT,
                    url TEXT, doi TEXT, accessed TEXT, extra TEXT,
                    formatted TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT);
            """)
            for tbl in ("examinationspunkter", "premisser", "references_table"):
                if not self._has_col(c, tbl, "assignment_id"):
                    c.execute(f"ALTER TABLE {tbl} ADD COLUMN assignment_id INTEGER")
            if not self._has_col(c, "premisser", "citation"):
                c.execute("ALTER TABLE premisser ADD COLUMN citation TEXT")
            if not self._has_col(c, "premisser", "category"):
                c.execute("ALTER TABLE premisser ADD COLUMN category TEXT")

            c.execute("SELECT COUNT(*) FROM assignments")
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO assignments (name) VALUES (?)", ("Min uppgift",))

    def get_setting(self, key, default=None):
        with self._conn() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        with self._conn() as conn:
            conn.execute("""INSERT INTO settings (key, value) VALUES (?, ?)
                            ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                         (key, value))

    def assignments(self):
        with self._conn() as conn:
            return conn.execute("SELECT id, name FROM assignments ORDER BY id").fetchall()

    def add_assignment(self, name):
        with self._conn() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO assignments (name) VALUES (?)", (name,))
            return c.lastrowid

    def rename_assignment(self, aid, name):
        with self._conn() as conn:
            conn.execute("UPDATE assignments SET name=? WHERE id=?", (name, aid))

    def delete_assignment(self, aid):
        with self._conn() as conn:
            conn.execute("DELETE FROM examinationspunkter WHERE assignment_id=?", (aid,))
            conn.execute("DELETE FROM premisser WHERE assignment_id=?", (aid,))
            conn.execute("DELETE FROM references_table WHERE assignment_id=?", (aid,))
            conn.execute("DELETE FROM assignments WHERE id=?", (aid,))
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM assignments")
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO assignments (name) VALUES (?)", ("Min uppgift",))

    def exam_points(self, aid):
        with self._conn() as conn:
            return conn.execute(
                "SELECT id, text FROM examinationspunkter WHERE assignment_id=? ORDER BY id", (aid,)
            ).fetchall()

    def add_exam(self, aid, text):
        with self._conn() as conn:
            conn.execute("INSERT INTO examinationspunkter (assignment_id, text) VALUES (?, ?)", (aid, text))

    def update_exam(self, eid, text):
        with self._conn() as conn:
            conn.execute("UPDATE examinationspunkter SET text=? WHERE id=?", (text, eid))

    def delete_exam(self, eid):
        with self._conn() as conn:
            conn.execute("DELETE FROM examinationspunkter WHERE id=?", (eid,))

    def clear_exam(self, aid):
        with self._conn() as conn:
            conn.execute("DELETE FROM examinationspunkter WHERE assignment_id=?", (aid,))

    def premisser_filtered(self, aid, category=None):
        with self._conn() as conn:
            if category and category != "Alla":
                return conn.execute("""
                    SELECT id, text, weight, COALESCE(citation, ''), COALESCE(category, '')
                    FROM premisser WHERE assignment_id=? AND COALESCE(category, '')=?
                    ORDER BY weight DESC, id""", (aid, category)).fetchall()
            return conn.execute("""
                SELECT id, text, weight, COALESCE(citation, ''), COALESCE(category, '')
                FROM premisser WHERE assignment_id=?
                ORDER BY weight DESC, id""", (aid,)).fetchall()

    def premisser_categories(self, aid):
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT DISTINCT category FROM premisser
                WHERE assignment_id=? AND category IS NOT NULL AND TRIM(category) != ''
                ORDER BY category COLLATE NOCASE""", (aid,)).fetchall()
        return [r[0] for r in rows]

    def add_prem(self, aid, text, weight, citation, category):
        with self._conn() as conn:
            conn.execute("""INSERT INTO premisser
                            (assignment_id, text, weight, citation, category)
                            VALUES (?, ?, ?, ?, ?)""",
                         (aid, text, weight, citation or None, category or None))

    def update_prem(self, pid, text, weight, citation, category):
        with self._conn() as conn:
            conn.execute("""UPDATE premisser SET text=?, weight=?, citation=?, category=? WHERE id=?""",
                         (text, weight, citation or None, category or None, pid))

    def delete_prem(self, pid):
        with self._conn() as conn:
            conn.execute("DELETE FROM premisser WHERE id=?", (pid,))

    def clear_prem(self, aid):
        with self._conn() as conn:
            conn.execute("DELETE FROM premisser WHERE assignment_id=?", (aid,))

    def references(self, aid, search=None):
        with self._conn() as conn:
            if search:
                like = f"%{search}%"
                return conn.execute("""
                    SELECT id, ref_type, formatted FROM references_table
                    WHERE assignment_id=? AND (
                        author    LIKE ? COLLATE NOCASE OR
                        year      LIKE ? COLLATE NOCASE OR
                        title     LIKE ? COLLATE NOCASE OR
                        container LIKE ? COLLATE NOCASE OR
                        publisher LIKE ? COLLATE NOCASE OR
                        formatted LIKE ? COLLATE NOCASE
                    )
                    ORDER BY author COLLATE NOCASE, year""",
                    (aid, like, like, like, like, like, like)).fetchall()
            return conn.execute("""
                SELECT id, ref_type, formatted FROM references_table
                WHERE assignment_id=? ORDER BY author COLLATE NOCASE, year""", (aid,)).fetchall()

    def references_full(self, aid, search=None):
        with self._conn() as conn:
            if search:
                like = f"%{search}%"
                return conn.execute("""
                    SELECT ref_type, author, year, title, container, publisher, place,
                           edition, pages, url, doi, accessed, extra
                    FROM references_table
                    WHERE assignment_id=? AND (
                        author    LIKE ? COLLATE NOCASE OR
                        year      LIKE ? COLLATE NOCASE OR
                        title     LIKE ? COLLATE NOCASE OR
                        container LIKE ? COLLATE NOCASE OR
                        publisher LIKE ? COLLATE NOCASE OR
                        formatted LIKE ? COLLATE NOCASE
                    )
                    ORDER BY author COLLATE NOCASE, year""",
                    (aid, like, like, like, like, like, like)).fetchall()
            return conn.execute("""
                SELECT ref_type, author, year, title, container, publisher, place,
                       edition, pages, url, doi, accessed, extra
                FROM references_table WHERE assignment_id=?
                ORDER BY author COLLATE NOCASE, year""", (aid,)).fetchall()

    def add_reference(self, aid, data, formatted):
        cols = ["assignment_id", "ref_type", "author", "year", "title", "container",
                "publisher", "place", "edition", "pages", "url", "doi", "accessed",
                "extra", "formatted"]
        vals = [aid] + [data.get(k, "") for k in cols[1:-1]] + [formatted]
        with self._conn() as conn:
            conn.execute(f"INSERT INTO references_table ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})", vals)

    def delete_reference(self, rid):
        with self._conn() as conn:
            conn.execute("DELETE FROM references_table WHERE id=?", (rid,))

    def clear_references(self, aid):
        with self._conn() as conn:
            conn.execute("DELETE FROM references_table WHERE assignment_id=?", (aid,))

    def wipe_all(self):
        with self._conn() as conn:
            for t in ("examinationspunkter", "premisser", "references_table", "assignments"):
                conn.execute(f"DELETE FROM {t}")
            conn.execute("INSERT INTO assignments (name) VALUES (?)", ("Min uppgift",))


# ══════════════════════════════════════════════════════════════════════
# HARVARD FORMATTER
# ══════════════════════════════════════════════════════════════════════
class HarvardFormatter:
    @staticmethod
    def format(d):
        t = (d.get("ref_type") or "").strip()
        a = (d.get("author") or "").strip()
        y = (d.get("year") or "").strip()
        title = (d.get("title") or "").strip()
        cont = (d.get("container") or "").strip()
        pub = (d.get("publisher") or "").strip()
        place = (d.get("place") or "").strip()
        ed = (d.get("edition") or "").strip()
        pages = (d.get("pages") or "").strip()
        url = (d.get("url") or "").strip()
        doi = (d.get("doi") or "").strip()
        acc = (d.get("accessed") or "").strip()
        extra = (d.get("extra") or "").strip()

        def au_yr():
            if a and y: return f"{a} ({y})."
            if a: return f"{a}."
            if y: return f"({y})."
            return ""

        if t == "Bok":
            tail = ""
            if place and pub: tail = f"{place}: {pub}."
            elif pub: tail = f"{pub}."
            elif place: tail = f"{place}."
            parts = [au_yr(), f"{title}." if title else "",
                     f"{ed} uppl.," if ed else "", tail]
        elif t == "Kapitel i bok":
            parts = [au_yr(), f"{title}." if title else "",
                     f"I {cont}." if cont else "",
                     f"{pub}, s. {pages}." if pub and pages else
                     f"{pub}." if pub else f"s. {pages}." if pages else ""]
        elif t == "Tidskriftsartikel":
            parts = [au_yr(), f"{title}." if title else "",
                     f"{cont}," if cont else "",
                     f"s. {pages}." if pages else "",
                     f"doi:{doi}" if doi else ""]
        elif t == "Tidningsartikel":
            parts = [au_yr(), f"{title}." if title else "",
                     f"{cont}," if cont else "", f"{extra}," if extra else "",
                     f"s. {pages}." if pages else "", url,
                     f"[{acc}]" if acc else ""]
        elif t == "Webbsida":
            parts = [au_yr(), f"{title}." if title else "", url,
                     f"[{acc}]" if acc else ""]
        elif t == "Rapport":
            parts = [au_yr(), f"{title}." if title else "",
                     f"({extra})." if extra else "",
                     f"{pub}." if pub else "", url, f"[{acc}]" if acc else ""]
        elif t in ("Doktorsavhandling", "Licentiatavhandling", "Uppsats"):
            label = {"Doktorsavhandling": "Diss.", "Licentiatavhandling": "Lic.-avh.",
                     "Uppsats": extra or "Uppsats"}[t]
            parts = [au_yr(), f"{title}." if title else "", label,
                     f"{pub}." if pub else "", url, f"[{acc}]" if acc else ""]
        elif t == "Konferensbidrag":
            parts = [au_yr(), f"{title}." if title else "",
                     f"I {cont}." if cont else "", f"{extra}," if extra else "",
                     f"s. {pages}." if pages else "",
                     f"doi:{doi}" if doi else ""]
        elif t in ("Video", "Podd", "TV", "Radioprogram"):
            bracket = {"Video": "[video]", "Podd": "[podcast]",
                       "TV": "[TV-program]", "Radioprogram": "[radioprogram]"}[t]
            parts = [au_yr(), title, bracket, f"{extra}," if extra else "",
                     url, f"[{acc}]" if acc else ""]
        else:
            parts = [a, y, title, cont, pub, place, ed, pages, url, doi, acc, extra]

        out = " ".join(p for p in parts if p)
        return out.replace(" .", ".").replace(" ,", ",").replace("..", ".").strip()


# ══════════════════════════════════════════════════════════════════════
# EXPORTERS
# ══════════════════════════════════════════════════════════════════════
class RisExporter:
    TYPES = {"Bok": "BOOK", "Kapitel i bok": "CHAP", "Tidskriftsartikel": "JOUR",
             "Tidningsartikel": "NEWS", "Webbsida": "ELEC", "Rapport": "RPRT",
             "Doktorsavhandling": "THES", "Licentiatavhandling": "THES",
             "Uppsats": "THES", "Konferensbidrag": "CPAPER", "Video": "VIDEO",
             "Podd": "SOUND", "TV": "VIDEO", "Radioprogram": "SOUND"}

    @classmethod
    def _authors(cls, s):
        for sep in (" & ", " och ", " AND ", " and "):
            if sep in s:
                return [p.strip() for p in s.split(sep)]
        return [s.strip()] if s else []

    @classmethod
    def export(cls, rows, path):
        with open(path, "w", encoding="utf-8") as f:
            for (ref_type, a, y, title, cont, pub, place, ed, pages,
                 url, doi, acc, extra) in rows:
                f.write(f"TY  - {cls.TYPES.get(ref_type, 'GEN')}\n")
                for x in cls._authors(a or ""):
                    f.write(f"AU  - {x}\n")
                if y: f.write(f"PY  - {y}\nDA  - {y}\n")
                if title: f.write(f"TI  - {title}\n")
                if cont:
                    tag = "JO" if ref_type in ("Tidskriftsartikel", "Tidningsartikel") else "T2"
                    f.write(f"{tag}  - {cont}\n")
                if pub: f.write(f"PB  - {pub}\n")
                if place: f.write(f"CY  - {place}\n")
                if ed: f.write(f"ET  - {ed}\n")
                if pages:
                    p = pages.replace("–", "-").replace("—", "-")
                    if "-" in p:
                        sp, ep = p.split("-", 1)
                        f.write(f"SP  - {sp.strip()}\nEP  - {ep.strip()}\n")
                    else:
                        f.write(f"SP  - {p.strip()}\n")
                if doi: f.write(f"DO  - {doi}\n")
                if url: f.write(f"UR  - {url}\n")
                if acc: f.write(f"Y2  - {acc}\n")
                if extra: f.write(f"N1  - {extra}\n")
                f.write("ER  - \n\n")


class BibtexExporter:
    TYPES = {"Bok": "book", "Kapitel i bok": "incollection", "Tidskriftsartikel": "article",
             "Tidningsartikel": "article", "Webbsida": "misc", "Rapport": "techreport",
             "Doktorsavhandling": "phdthesis", "Licentiatavhandling": "mastersthesis",
             "Uppsats": "mastersthesis", "Konferensbidrag": "inproceedings",
             "Video": "misc", "Podd": "misc", "TV": "misc", "Radioprogram": "misc"}

    @staticmethod
    def _key(a, y, title):
        surname = "unknown"
        if a:
            first = a.split("&")[0].split(" och ")[0].split(",")[0].strip()
            surname = "".join(ch for ch in first if ch.isalnum()) or "unknown"
        yr = y or "n.d."
        word = "untitled"
        if title:
            ws = [w for w in title.split() if len(w) > 3 and w[0].isalpha()]
            if ws: word = "".join(ch for ch in ws[0] if ch.isalnum())
        return f"{surname}{yr}{word}"

    @staticmethod
    def _esc(s):
        if not s: return ""
        return "".join({"\\": "\\textbackslash{}", "&": "\\&", "%": "\\%",
                        "$": "\\$", "#": "\\#", "_": "\\_",
                        "{": "\\{", "}": "\\}"}.get(c, c) for c in s)

    @classmethod
    def export(cls, rows, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"% Rekaren export – {datetime.now():%Y-%m-%d %H:%M}\n\n")
            for (ref_type, a, y, title, cont, pub, place, ed, pages,
                 url, doi, acc, extra) in rows:
                f.write(f"@{cls.TYPES.get(ref_type, 'misc')}{{{cls._key(a, y, title)},\n")
                if a:
                    f.write(f"  author    = {{{cls._esc(a.replace(' & ', ' and ').replace(' och ', ' and '))}}},\n")
                if title: f.write(f"  title     = {{{cls._esc(title)}}},\n")
                if y: f.write(f"  year      = {{{y}}},\n")
                if cont:
                    tag = "journal" if ref_type in ("Tidskriftsartikel", "Tidningsartikel") else "booktitle"
                    f.write(f"  {tag}   = {{{cls._esc(cont)}}},\n")
                if pub: f.write(f"  publisher = {{{cls._esc(pub)}}},\n")
                if place: f.write(f"  address   = {{{cls._esc(place)}}},\n")
                if ed: f.write(f"  edition   = {{{cls._esc(ed)}}},\n")
                if pages: f.write(f"  pages     = {{{pages.replace('–', '--')}}},\n")
                if doi: f.write(f"  doi       = {{{doi}}},\n")
                if url: f.write(f"  url       = {{{url}}},\n")
                if acc: f.write(f"  urldate   = {{{acc}}},\n")
                if extra: f.write(f"  note      = {{{cls._esc(extra)}}},\n")
                f.write("}\n\n")


# ══════════════════════════════════════════════════════════════════════
# UPDATE CHECKER
# ══════════════════════════════════════════════════════════════════════
class UpdateChecker:
    @staticmethod
    def _ver(v):
        try: return tuple(int(x) for x in str(v).split("."))
        except Exception: return (0,)

    @classmethod
    def check(cls, current, url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rekaren/8"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
            if cls._ver(data.get("version", "0")) > cls._ver(current):
                return data
        except Exception as e:
            print(f"[updater] {e}")
        return None


# ══════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════
class AssignmentBar(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=(12, 10))
        self.app = app
        self.var = tk.StringVar()

        ttk.Label(self, text="Uppgift:", font=Fonts.BASE_BOLD).pack(side="left", padx=(0, 6))
        self.combo = ttk.Combobox(self, textvariable=self.var, state="readonly", width=42,
                                  font=Fonts.BASE)
        self.combo.pack(side="left", padx=(0, 10))
        self.combo.bind("<<ComboboxSelected>>", self._on_change)

        ttk.Button(self, text="➕  Ny uppgift", command=app.new_assignment).pack(side="left", padx=3)
        ttk.Button(self, text="✏️  Byt namn", command=app.rename_assignment).pack(side="left", padx=3)
        ttk.Button(self, text="🗑️  Ta bort", command=app.delete_assignment,
                   style="Danger.TButton").pack(side="left", padx=3)

        ttk.Separator(self, orient="vertical").pack(side="left", fill="y", padx=12)

        ttk.Button(self, text="💾  Backup", command=app.backup_db).pack(side="left", padx=3)

    def _on_change(self, _=None):
        name = self.var.get()
        if name in self.app.assignments_map:
            self.app.current_aid = self.app.assignments_map[name]
            self.app.refresh_all()
            self.app.set_status(f"Aktiv uppgift: {name}")

    def set_names(self, names, current):
        self.combo["values"] = names
        self.var.set(current)


class BaseTab(ttk.Frame):
    def __init__(self, master, app, title):
        super().__init__(master)
        self.app = app
        self.frame = ttk.LabelFrame(self, text=title)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh(self):
        pass


# ─────────────────────────── EXAM TAB ───────────────────────────
class ExamTab(BaseTab):
    def __init__(self, master, app):
        super().__init__(master, app, "  Lärandemål / Examinationspunkter  ")
        self._row_ids = []

        # left: list
        left = ttk.Frame(self.frame)
        left.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        self.listbox = tk.Listbox(left, height=15, font=Fonts.BASE,
                                  activestyle="none", selectmode="browse")
        self.listbox.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.listbox.yview)
        sb.pack(side="left", fill="y")
        self.listbox.config(yscrollcommand=sb.set)

        # right: form
        right = ttk.Frame(self.frame)
        right.pack(side="left", fill="y", padx=(0, 12), pady=12)

        ttk.Label(right, text="Ny examinationspunkt:",
                  font=Fonts.BASE_BOLD).pack(anchor="w", pady=(0, 6))
        self.entry = tk.Text(right, width=38, height=4, wrap="word", font=Fonts.BASE)
        self.entry.pack(pady=(0, 8), ipady=4)

        ttk.Button(right, text="➕  Lägg till", style="Accent.TButton",
                   command=self.add).pack(fill="x", pady=3)
        ttk.Button(right, text="✏️  Redigera vald",
                   command=self.edit).pack(fill="x", pady=3)
        ttk.Button(right, text="🗑️  Ta bort vald", style="Danger.TButton",
                   command=self.delete).pack(fill="x", pady=3)

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=12)

        ttk.Button(right, text="🧹  Rensa flik",
                   command=self.clear).pack(fill="x", pady=3)
        ttk.Button(right, text="📤  Exportera .txt",
                   command=self.export).pack(fill="x", pady=3)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self._row_ids = []
        if not self.app.current_aid:
            return
        rows = self.app.db.exam_points(self.app.current_aid)
        if not rows:
            self.listbox.insert(tk.END, "  (Inga examinationspunkter ännu)")
            self.listbox.itemconfig(0, foreground="#999999")
            return
        for eid, text in rows:
            self.listbox.insert(tk.END, f"  {text}")
            self._row_ids.append(eid)

    def _selected_id(self):
        sel = self.listbox.curselection()
        if not sel: return None
        idx = sel[0]
        if idx >= len(self._row_ids): return None
        return self._row_ids[idx]

    def add(self):
        text = self.entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Tom text", "Skriv en examinationspunkt först.")
            return
        self.app.db.add_exam(self.app.current_aid, text)
        self.entry.delete("1.0", tk.END)
        self.refresh()
        self.app.set_status(f"Tillagd: {text[:40]}")

    def edit(self):
        eid = self._selected_id()
        if eid is None:
            messagebox.showinfo("Ingen vald", "Välj en rad först.")
            return
        sel = self.listbox.curselection()
        old = self.listbox.get(sel[0]).strip()
        new = simpledialog.askstring("Redigera", "Uppdatera texten:",
                                     initialvalue=old, parent=self.app)
        if not new: return
        self.app.db.update_exam(eid, new.strip())
        self.refresh()

    def delete(self):
        eid = self._selected_id()
        if eid is None:
            messagebox.showinfo("Ingen vald", "Välj en rad först.")
            return
        if not messagebox.askyesno("Ta bort", "Ta bort denna examinationspunkt?"):
            return
        self.app.db.delete_exam(eid)
        self.refresh()

    def clear(self):
        if not self.app.current_aid: return
        if not messagebox.askyesno("Rensa", "Rensa ALLA examinationspunkter för denna uppgift?"):
            return
        self.app.db.clear_exam(self.app.current_aid)
        self.refresh()

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text", "*.txt")])
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            for _, t in self.app.db.exam_points(self.app.current_aid):
                f.write(f"- {t}\n")
        self.app.set_status(f"Exporterat: {os.path.basename(path)}")


# ─────────────────────────── PREMISS TAB ───────────────────────────
class PremissTab(BaseTab):
    def __init__(self, master, app):
        super().__init__(master, app, "  Premisser  ")

        # filter row
        filter_row = ttk.Frame(self.frame)
        filter_row.pack(fill="x", padx=12, pady=(12, 0))
        ttk.Label(filter_row, text="Kategori:", font=Fonts.BASE_BOLD).pack(side="left", padx=(0, 6))
        self.filter_var = tk.StringVar(value="Alla")
        self.filter_combo = ttk.Combobox(filter_row, textvariable=self.filter_var,
                                         state="readonly", width=28, font=Fonts.BASE)
        self.filter_combo.pack(side="left")
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        ttk.Button(filter_row, text="🔄  Rensa filter",
                   command=self._clear_filter).pack(side="left", padx=8)

        body = ttk.Frame(self.frame)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        # left: tree
        left = ttk.Frame(body); left.pack(side="left", fill="both", expand=True)
        cols = ("text", "weight", "category", "citation")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=15)
        self.tree.heading("text", text="Premiss")
        self.tree.column("text", width=380, anchor="w")
        self.tree.heading("weight", text="Vikt")
        self.tree.column("weight", width=60, anchor="center")
        self.tree.heading("category", text="Kategori")
        self.tree.column("category", width=130, anchor="w")
        self.tree.heading("citation", text="Citat")
        self.tree.column("citation", width=220, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        sb.pack(side="left", fill="y"); self.tree.config(yscrollcommand=sb.set)

        # right: form
        right = ttk.Frame(body); right.pack(side="left", fill="y", padx=(12, 0))
        ttk.Label(right, text="Ny premiss:",
                  font=Fonts.BASE_BOLD).pack(anchor="w", pady=(0, 6))
        self.entry = tk.Text(right, width=38, height=3, wrap="word", font=Fonts.BASE)
        self.entry.pack(pady=(0, 8), ipady=4)

        ttk.Label(right, text="Vikt:", font=Fonts.BASE_BOLD).pack(anchor="w")
        self.weight = tk.IntVar(value=3)
        wf = ttk.Frame(right); wf.pack(fill="x", pady=4)
        for i in range(6):
            ttk.Radiobutton(wf, text=str(i), variable=self.weight, value=i).pack(side="left", padx=3)

        ttk.Label(right, text="Kategori (valfritt):",
                  font=Fonts.BASE_BOLD).pack(anchor="w", pady=(8, 0))
        self.category = ttk.Combobox(right, width=36, font=Fonts.BASE)
        self.category.pack(pady=(4, 8))

        ttk.Label(right, text="Citat (valfritt):",
                  font=Fonts.BASE_BOLD).pack(anchor="w")
        self.citation = ttk.Entry(right, width=38, font=Fonts.BASE)
        self.citation.pack(pady=(4, 8))

        ttk.Button(right, text="➕  Lägg till", style="Accent.TButton",
                   command=self.add).pack(fill="x", pady=3)
        ttk.Button(right, text="✏️  Redigera",
                   command=self.edit).pack(fill="x", pady=3)
        ttk.Button(right, text="🗑️  Ta bort vald", style="Danger.TButton",
                   command=self.delete).pack(fill="x", pady=3)

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=12)
        ttk.Button(right, text="🧹  Rensa flik",
                   command=self.clear).pack(fill="x", pady=3)
        ttk.Button(right, text="📤  Exportera .txt",
                   command=self.export).pack(fill="x", pady=3)

        self._configure_weight_tags()

    def _configure_weight_tags(self):
        c = Theme.colors(self.app.theme_name)
        for i in range(6):
            self.tree.tag_configure(f"w{i}", foreground=c[f"w{i}"])

    def _clear_filter(self):
        self.filter_var.set("Alla")
        self.refresh()

    def _refresh_category_dropdown(self):
        if not self.app.current_aid: return
        cats = self.app.db.premisser_categories(self.app.current_aid)
        values = ["Alla"] + cats
        self.filter_combo["values"] = values
        self.category["values"] = cats
        if self.filter_var.get() not in values:
            self.filter_var.set("Alla")

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        self._refresh_category_dropdown()
        self._configure_weight_tags()
        if not self.app.current_aid: return

        cat_filter = self.filter_var.get()
        rows = self.app.db.premisser_filtered(self.app.current_aid, cat_filter)
        if not rows:
            return
        for pid, text, weight, citation, category in rows:
            tag = f"w{min(max(int(weight), 0), 5)}"
            self.tree.insert("", tk.END, iid=str(pid),
                             values=(text, weight, category, citation),
                             tags=(tag,))

    def _selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def add(self):
        text = self.entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Tom text", "Skriv en premiss först.")
            return
        self.app.db.add_prem(self.app.current_aid, text, self.weight.get(),
                             self.citation.get().strip(),
                             self.category.get().strip())
        self.entry.delete("1.0", tk.END)
        self.citation.delete(0, tk.END)
        self.category.set("")
        self.refresh()
        self.app.set_status(f"Premiss tillagd: {text[:40]}")

    def edit(self):
        pid = self._selected_id()
        if pid is None:
            messagebox.showinfo("Ingen vald", "Välj en rad först.")
            return
        vals = self.tree.item(str(pid))["values"]
        old_text = vals[0]
        old_weight = int(vals[1])
        old_cat = vals[2] if len(vals) > 2 else ""
        old_cit = vals[3] if len(vals) > 3 else ""

        dlg = tk.Toplevel(self.app)
        dlg.title("Redigera premiss")
        dlg.transient(self.app)
        dlg.grab_set()
        dlg.configure(bg=Theme.colors(self.app.theme_name)["bg"])

        ttk.Label(dlg, text="Text:", font=Fonts.BASE_BOLD).grid(row=0, column=0, sticky="w", padx=12, pady=8)
        te = tk.Text(dlg, width=50, height=4, wrap="word", font=Fonts.BASE)
        te.grid(row=0, column=1, padx=12, pady=8)
        te.insert("1.0", old_text)

        ttk.Label(dlg, text="Vikt:", font=Fonts.BASE_BOLD).grid(row=1, column=0, sticky="w", padx=12, pady=8)
        wv = tk.IntVar(value=old_weight)
        wf = ttk.Frame(dlg); wf.grid(row=1, column=1, sticky="w", padx=12, pady=8)
        for i in range(6):
            ttk.Radiobutton(wf, text=str(i), variable=wv, value=i).pack(side="left", padx=3)

        ttk.Label(dlg, text="Kategori:", font=Fonts.BASE_BOLD).grid(row=2, column=0, sticky="w", padx=12, pady=8)
        cat_e = ttk.Combobox(dlg, width=48,
                             values=self.app.db.premisser_categories(self.app.current_aid))
        cat_e.grid(row=2, column=1, sticky="w", padx=12, pady=8)
        cat_e.set(old_cat)

        ttk.Label(dlg, text="Citat:", font=Fonts.BASE_BOLD).grid(row=3, column=0, sticky="w", padx=12, pady=8)
        ce = ttk.Entry(dlg, width=50)
        ce.grid(row=3, column=1, sticky="w", padx=12, pady=8)
        ce.insert(0, old_cit)

        def save():
            self.app.db.update_prem(pid, te.get("1.0", tk.END).strip(), wv.get(),
                                    ce.get().strip(), cat_e.get().strip())
            dlg.destroy(); self.refresh()
            self.app.set_status("Premiss uppdaterad")

        bf = ttk.Frame(dlg); bf.grid(row=4, column=0, columnspan=2, pady=14)
        ttk.Button(bf, text="💾  Spara", style="Accent.TButton", command=save).pack(side="left", padx=4)
        ttk.Button(bf, text="Avbryt", command=dlg.destroy).pack(side="left", padx=4)
        dlg.wait_window()

    def delete(self):
        pid = self._selected_id()
        if pid is None:
            messagebox.showinfo("Ingen vald", "Välj en rad först.")
            return
        if messagebox.askyesno("Ta bort", "Ta bort denna premiss?"):
            self.app.db.delete_prem(pid); self.refresh()
            self.app.set_status("Premiss borttagen")

    def clear(self):
        if not self.app.current_aid: return
        if messagebox.askyesno("Rensa", "Rensa ALLA premisser för denna uppgift?"):
            self.app.db.clear_prem(self.app.current_aid); self.refresh()

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text", "*.txt")])
        if not path: return
        cat_filter = self.filter_var.get()
        rows = self.app.db.premisser_filtered(self.app.current_aid, cat_filter)
        with open(path, "w", encoding="utf-8") as f:
            if cat_filter != "Alla":
                f.write(f"Kategori: {cat_filter}\n\n")
            for _, text, w, cit, cat in rows:
                prefix = f"[{cat}] " if cat else ""
                line = f"[Vikt {w}] {prefix}{text}"
                if cit: line += f"  ({cit})"
                f.write(line + "\n")
        self.app.set_status(f"Exporterat: {os.path.basename(path)}")


# ─────────────────────────── REFERENCE TAB ───────────────────────────
class ReferenceTab(BaseTab):
    # Fältordning per källtyp (progressiv disclosure)
    FIELDS_BY_TYPE = {
        "Bok":                  ["author", "year", "title", "publisher", "place", "edition"],
        "Kapitel i bok":        ["author", "year", "title", "container", "publisher", "pages"],
        "Tidskriftsartikel":    ["author", "year", "title", "container", "pages", "doi"],
        "Tidningsartikel":      ["author", "year", "title", "container", "extra", "pages", "url", "accessed"],
        "Webbsida":             ["author", "year", "title", "url", "accessed"],
        "Rapport":              ["author", "year", "title", "extra", "publisher", "url", "accessed"],
        "Doktorsavhandling":    ["author", "year", "title", "publisher", "url", "accessed"],
        "Licentiatavhandling":  ["author", "year", "title", "publisher", "url", "accessed"],
        "Uppsats":              ["author", "year", "title", "extra", "publisher", "url", "accessed"],
        "Konferensbidrag":      ["author", "year", "title", "container", "extra", "pages", "doi"],
        "Video":                ["author", "year", "title", "extra", "url", "accessed"],
        "Podd":                 ["author", "year", "title", "extra", "url", "accessed"],
        "TV":                   ["author", "year", "title", "extra", "url", "accessed"],
        "Radioprogram":         ["author", "year", "title", "extra", "url", "accessed"],
        "Övrigt":               ["author", "year", "title", "container", "publisher", "place",
                                 "edition", "pages", "url", "doi", "accessed", "extra"],
    }

    FIELD_LABELS = {
        "author":    "Författare (Efternamn, F.)",
        "year":      "År",
        "title":     "Titel",
        "container": "I / Tidskrift / Boktitel",
        "publisher": "Förlag / Utgivare",
        "place":     "Ort",
        "edition":   "Upplaga",
        "pages":     "Sidor (t.ex. 12–34)",
        "url":       "URL",
        "doi":       "DOI",
        "accessed":  "Läst datum (ÅÅÅÅ-MM-DD)",
        "extra":     "Övrigt (serie, konferens, datum)",
    }

    def __init__(self, master, app):
        super().__init__(master, app, "  Referenser – Svensk Harvard  ")

        # ---- left: form ----
        form = ttk.LabelFrame(self.frame, text="  Ny referens  ")
        form.pack(side="left", fill="y", padx=12, pady=12)

        self.type_var = tk.StringVar(value="Bok")
        ttk.Label(form, text="Typ av källa:", font=Fonts.BASE_BOLD).grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        type_combo = ttk.Combobox(form, textvariable=self.type_var, state="readonly",
                                  width=30, font=Fonts.BASE,
                                  values=list(self.FIELDS_BY_TYPE.keys()))
        type_combo.grid(row=0, column=1, sticky="w", padx=8, pady=(8, 4))
        type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        # Dynamiskt fält-ramverk
        self.field_widgets = {}
        self.fields_container = ttk.Frame(form)
        self.fields_container.grid(row=1, column=0, columnspan=2, sticky="nsew",
                                   padx=4, pady=4)
        form.rowconfigure(1, weight=1)
        form.columnconfigure(1, weight=1)

        for key, label in self.FIELD_LABELS.items():
            lbl = ttk.Label(self.fields_container, text=label + ":", font=Fonts.BASE)
            ent = ttk.Entry(self.fields_container, width=34, font=Fonts.BASE)
            self.field_widgets[key] = (lbl, ent)

        ttk.Button(form, text="💾  Spara referens", style="Accent.TButton",
                   command=self.add).grid(row=2, column=0, columnspan=2,
                                          pady=12, sticky="ew", padx=8)

        # ---- right: list ----
        right = ttk.LabelFrame(self.frame, text="  Sparade referenser  ")
        right.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=12)

        # search
        search_row = ttk.Frame(right)
        search_row.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(search_row, text="🔍", font=("Segoe UI", 12)).pack(side="left", padx=(0, 6))
        self.search_entry = PlaceholderEntry(search_row, placeholder="Sök i referenser…",
                                             width=40, font=Fonts.BASE)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())
        ttk.Button(search_row, text="✖", command=self._clear_search).pack(side="left", padx=6)

        # tree
        self.tree = ttk.Treeview(right, columns=("type", "formatted"), show="headings")
        self.tree.heading("type", text="Typ")
        self.tree.column("type", width=130, anchor="w")
        self.tree.heading("formatted", text="Referens")
        self.tree.column("formatted", width=620, anchor="w")
        self.tree.pack(side="top", fill="both", expand=True, padx=8, pady=(4, 8))
        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y", pady=(4, 8))
        self.tree.config(yscrollcommand=sb.set)

        # buttons
        btn_row1 = ttk.Frame(right); btn_row1.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Button(btn_row1, text="🗑️  Ta bort vald", style="Danger.TButton",
                   command=self.delete).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row1, text="📋  Kopiera vald",
                   command=self.copy).pack(side="left", padx=4)
        ttk.Button(btn_row1, text="📤  Exportera .txt",
                   command=self.export_txt).pack(side="left", padx=4)

        btn_row2 = ttk.Frame(right); btn_row2.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Button(btn_row2, text="🧹  Rensa flik",
                   command=self.clear).pack(side="left", padx=(0, 4))

        btn_row3 = ttk.Frame(right); btn_row3.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(btn_row3, text="📚  Zotero (.ris)",
                   command=self.export_ris).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row3, text="📚  BibTeX (.bib)",
                   command=self.export_bibtex).pack(side="left", padx=4)

        # init fields
        self._on_type_change()

    def _on_type_change(self, _=None):
        # hide all
        for lbl, ent in self.field_widgets.values():
            lbl.grid_forget()
            ent.grid_forget()
        # show relevant
        fields = self.FIELDS_BY_TYPE.get(self.type_var.get(), [])
        for r, key in enumerate(fields):
            lbl, ent = self.field_widgets[key]
            lbl.grid(row=r, column=0, sticky="w", padx=(8, 6), pady=4)
            ent.grid(row=r, column=1, sticky="ew", padx=(0, 8), pady=4)
        self.fields_container.columnconfigure(1, weight=1)

    def _clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.search_entry._showing = False
        self.refresh()

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        if not self.app.current_aid: return
        search = self.search_entry.value() or None
        for rid, rtype, formatted in self.app.db.references(self.app.current_aid, search):
            self.tree.insert("", tk.END, iid=str(rid), values=(rtype, formatted))
        if search:
            self.app.set_status(f"Söker: '{search}'")

    def add(self):
        data = {k: v.get().strip() for k, (_, v) in self.field_widgets.items()}
        data["ref_type"] = self.type_var.get()
        if not any(data.values()):
            messagebox.showwarning("Tomt", "Fyll i minst ett fält.")
            return
        formatted = HarvardFormatter.format(data)
        self.app.db.add_reference(self.app.current_aid, data, formatted)
        for _, ent in self.field_widgets.values():
            ent.delete(0, tk.END)
        self.refresh()
        self.app.set_status(f"Referens sparad: {data.get('author', '')} {data.get('year', '')}")

    def _selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def delete(self):
        rid = self._selected_id()
        if rid is None:
            messagebox.showinfo("Ingen vald", "Välj en referens först.")
            return
        if messagebox.askyesno("Ta bort", "Ta bort denna referens?"):
            self.app.db.delete_reference(rid)
            self.refresh()
            self.app.set_status("Referens borttagen")

    def copy(self):
        rid = self._selected_id()
        if rid is None: return
        for r_id, _, formatted in self.app.db.references(self.app.current_aid):
            if r_id == rid:
                self.app.clipboard_clear()
                self.app.clipboard_append(formatted)
                messagebox.showinfo("Kopierat", "Referensen finns i urklipp.")
                self.app.set_status("Kopierat till urklipp")
                return

    def clear(self):
        if not self.app.current_aid: return
        if messagebox.askyesno("Rensa", "Rensa ALLA referenser för denna uppgift?"):
            self.app.db.clear_references(self.app.current_aid); self.refresh()

    def export_txt(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text", "*.txt")])
        if not path: return
        search = self.search_entry.value() or None
        rows = self.app.db.references(self.app.current_aid, search)
        with open(path, "w", encoding="utf-8") as f:
            for _, _, formatted in rows:
                f.write(formatted + "\n\n")
        self.app.set_status(f"Exporterat: {os.path.basename(path)}")

    def export_ris(self):
        search = self.search_entry.value() or None
        rows = self.app.db.references_full(self.app.current_aid, search)
        if not rows:
            messagebox.showinfo("Tomt", "Inga referenser att exportera.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".ris",
                                            filetypes=[("RIS (Zotero)", "*.ris")])
        if not path: return
        RisExporter.export(rows, path)
        messagebox.showinfo("Klart", f"Sparat till:\n{path}\n\nZotero: Arkiv → Importera…")
        self.app.set_status(f"Zotero-export: {os.path.basename(path)}")

    def export_bibtex(self):
        search = self.search_entry.value() or None
        rows = self.app.db.references_full(self.app.current_aid, search)
        if not rows:
            messagebox.showinfo("Tomt", "Inga referenser att exportera.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".bib",
                                            filetypes=[("BibTeX", "*.bib")])
        if not path: return
        BibtexExporter.export(rows, path)
        messagebox.showinfo("Klart", f"Sparat till:\n{path}")
        self.app.set_status(f"BibTeX-export: {os.path.basename(path)}")


# ══════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════
class RekarenApp(tk.Tk):
    def __init__(self):
        super().__init__()

        Fonts.install(self)

        self.title("Rekaren – Examinationsförberedelse & Referenser")
        self.minsize(1100, 700)

        self.db = Database(Paths.db_path())
        self.current_aid = None
        self.assignments_map = {}
        self.theme_name = self.db.get_setting("theme", "light")
        self.theme_var = tk.StringVar(value=self.theme_name)

        # assign a callback for status messages from tabs
        self._status_var = tk.StringVar(value="Redo")

        # --- top bar ---
        self.assignment_bar = AssignmentBar(self, self)
        self.assignment_bar.pack(fill="x")

        # --- notebook ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        self.exam_tab = ExamTab(self.notebook, self)
        self.prem_tab = PremissTab(self.notebook, self)
        self.ref_tab = ReferenceTab(self.notebook, self)

        self.notebook.add(self.exam_tab, text="  🎯  Mål  ")
        self.notebook.add(self.prem_tab, text="  ⚖️  Begrepp  ")
        self.notebook.add(self.ref_tab, text="  📚  Källor  ")

        # --- status bar ---
        status = ttk.Label(self, textvariable=self._status_var, style="Status.TLabel",
                           anchor="w")
        status.pack(side="bottom", fill="x")

        self._build_menu()
        self.apply_theme(self.theme_name)
        self.center_window(1200, 800)

        self.refresh_assignments()
        self.refresh_all()
        self.after(1500, lambda: self._check_update(manual=False))

    # ---------- window ----------
    def center_window(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = max((self.winfo_screenheight() - h) // 3, 20)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def set_status(self, msg):
        self._status_var.set(f"  {msg}")
        self.after(4000, lambda: self._status_var.set("  Redo"))

    # ---------- menu ----------
    def _build_menu(self):
        mb = tk.Menu(self)

        fm = tk.Menu(mb, tearoff=0)
        fm.add_command(label="💾  Backup databas…", accelerator="Ctrl+B",
                       command=self.backup_db)
        fm.add_command(label="📂  Återställ från backup…", command=self.restore_db)
        fm.add_separator()
        fm.add_command(label="🔍  Sök uppdatering",
                       command=lambda: self._check_update(manual=True))
        fm.add_separator()
        fm.add_command(label="🗑️  RADERA ALLT", command=self.wipe_everything)
        fm.add_separator()
        fm.add_command(label="🚪  Avsluta", command=self.destroy)
        mb.add_cascade(label="Fil", menu=fm)

        vm = tk.Menu(mb, tearoff=0)
        vm.add_radiobutton(label="☀️  Ljust läge", variable=self.theme_var,
                           value="light", command=lambda: self.apply_theme("light"))
        vm.add_radiobutton(label="🌙  Mörkt läge", variable=self.theme_var,
                           value="dark", command=lambda: self.apply_theme("dark"))
        vm.add_separator()
        vm.add_command(label="🔄  Växla tema", accelerator="Ctrl+T",
                       command=self.toggle_theme)
        mb.add_cascade(label="Visa", menu=vm)

        em = tk.Menu(mb, tearoff=0)
        em.add_command(label="📚  Zotero (.ris)",
                       command=lambda: self.ref_tab.export_ris())
        em.add_command(label="📚  BibTeX (.bib)",
                       command=lambda: self.ref_tab.export_bibtex())
        mb.add_cascade(label="Exportera", menu=em)

        hm = tk.Menu(mb, tearoff=0)
        hm.add_command(label="Om Rekaren", command=self.about)
        hm.add_command(label="Öppna datamapp", command=self.open_data_folder)
        mb.add_cascade(label="Hjälp", menu=hm)

        self.config(menu=mb)

        # shortcuts
        self.bind_all("<Control-t>", lambda e: self.toggle_theme())
        self.bind_all("<Control-b>", lambda e: self.backup_db())

    # ---------- theme ----------
    def apply_theme(self, name):
        self.theme_name = name
        self.theme_var.set(name)
        Theme.apply(self, name)
        self.db.set_setting("theme", name)
        # re-apply weight tags after theme change
        try:
            self.prem_tab._configure_weight_tags()
        except Exception:
            pass

    def toggle_theme(self):
        self.apply_theme("dark" if self.theme_name == "light" else "light")
        self.set_status(f"Tema: {self.theme_name}")

    # ---------- assignments ----------
    def refresh_assignments(self):
        rows = self.db.assignments()
        self.assignments_map = {name: aid for aid, name in rows}
        if self.current_aid is None and rows:
            self.current_aid = rows[0][0]
        current_name = next((n for a, n in rows if a == self.current_aid),
                            rows[0][1] if rows else "")
        self.assignment_bar.set_names([n for _, n in rows], current_name)

    def new_assignment(self):
        name = simpledialog.askstring("Ny uppgift", "Namn på uppgiften:", parent=self)
        if not name: return
        self.current_aid = self.db.add_assignment(name.strip())
        self.refresh_assignments()
        self.refresh_all()
        self.set_status(f"Ny uppgift skapad: {name}")

    def rename_assignment(self):
        old = self.assignment_bar.var.get()
        new = simpledialog.askstring("Byt namn", "Nytt namn:", initialvalue=old, parent=self)
        if new:
            self.db.rename_assignment(self.current_aid, new.strip())
            self.refresh_assignments()

    def delete_assignment(self):
        name = self.assignment_bar.var.get()
        if not messagebox.askyesno("Ta bort", f"Ta bort '{name}' och allt innehåll?"):
            return
        self.db.delete_assignment(self.current_aid)
        self.current_aid = None
        self.refresh_assignments()
        self.refresh_all()

    def refresh_all(self):
        for t in (self.exam_tab, self.prem_tab, self.ref_tab):
            t.refresh()

    # ---------- data ops ----------
    def backup_db(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Rekaren databas", "*.db")],
            initialfile=f"rekaren_{datetime.now():%Y%m%d_%H%M}.db")
        if path:
            shutil.copy2(Paths.db_path(), path)
            self.set_status(f"Backup: {os.path.basename(path)}")
            messagebox.showinfo("Backup klar", f"Sparat:\n{path}")

    def restore_db(self):
        path = filedialog.askopenfilename(filetypes=[("Rekaren", "*.db")])
        if not path: return
        if not messagebox.askyesno("Återställ",
                "Ersätter all nuvarande data med innehållet i backupen.\n\nFortsätt?"):
            return
        shutil.copy2(path, Paths.db_path())
        self.db = Database(Paths.db_path())
        self.current_aid = None
        self.theme_name = self.db.get_setting("theme", "light")
        self.apply_theme(self.theme_name)
        self.refresh_assignments()
        self.refresh_all()
        self.set_status("Databas återställd")
        messagebox.showinfo("Klart", "Databasen har återställts.")

    def wipe_everything(self):
        if not messagebox.askyesno("RADERA ALLT",
                "All data raderas permanent:\n\n"
                "• Alla uppgifter\n• Alla mål\n• Alla begrepp\n• Alla källor\n\n"
                "Detta kan INTE ångras. Fortsätta?") or \
           not messagebox.askyesno("Bekräfta", "Sista chansen. Radera allt?"):
            return
        self.db.wipe_all()
        self.current_aid = None
        self.refresh_assignments()
        self.refresh_all()
        self.set_status("All data raderad")

    def open_data_folder(self):
        d = Paths.data_dir()
        if sys.platform == "win32":
            os.startfile(d)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", d])
        else:
            subprocess.Popen(["xdg-open", d])

    # ---------- update ----------
    def _check_update(self, manual):
        def worker():
            res = UpdateChecker.check(Paths.APP_VERSION, Paths.UPDATE_URL)
            self.after(0, lambda: self._show_update(res, manual))
        threading.Thread(target=worker, daemon=True).start()

    def _show_update(self, res, manual):
        if res:
            msg = f"Ny version: {res.get('version')}\n\n{res.get('changelog','')}\n\nÖppna?"
            if messagebox.askyesno("Uppdatering", msg):
                webbrowser.open(res.get("download_url", Paths.DOWNLOAD_URL))
        elif manual:
            messagebox.showinfo("Ingen uppdatering", f"Du har senaste ({Paths.APP_VERSION}).")

    def about(self):
        messagebox.showinfo("Om Rekaren",
            f"Rekaren v{Paths.APP_VERSION}\n\n"
            "• Mål, begrepp och källor i en app\n"
            "• Kategorier och vikter för begrepp\n"
            "• Referenser i svensk Harvard (Högskolan i Borås)\n"
            "• Export till Zotero (.ris) och BibTeX (.bib)\n"
            "• Mörkt / ljust läge (Ctrl+T)\n\n"
            f"Databas:\n{Paths.db_path()}")


# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"[rekaren] Database: {Paths.db_path()}")
    RekarenApp().mainloop()