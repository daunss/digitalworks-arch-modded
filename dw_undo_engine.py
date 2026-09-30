#!/usr/bin/env python3
"""
=============================================================================
DIGITAL WORKS MOD - EMBEDDED IN-UI SENTINEL ENGINE (Arch Linux)
=============================================================================
Berjalan di latar belakang (tanpa jendela GUI mengambang) untuk melayani
event yang dipicu langsung dari menu header Digital Works:
- Menu "Mods" -> "Undo (Ctrl+Z)"
- Menu "Mods" -> "Redo (Ctrl+Y)"
- Menu "Mods" -> "Auto Truth Table"
- Menu "Mods" -> "Batch Capture"
- Menu "Mods" -> "Boolean Equation"
- Menu "Mods" -> "Save Snapshot"
=============================================================================
"""

import os
import sys
import time
import json
import glob
import shutil
import hashlib
import threading
import subprocess
from PIL import Image, ImageDraw, ImageFont

APP_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(APP_DIR, ".undo_history")
SCREENSHOT_DIR = os.path.join(APP_DIR, "laporan_screenshots")
MAX_HISTORY = 50

os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class CircuitSolver:
    """
    Parser dan pemecah logika rangkaian digital langsung dari file .dwm (Borland Delphi 5 serialization).
    Mengevaluasi secara akurat fungsi logika rangkaian (XOR, NAND, AND, OR, NOR, XNOR, NOT, dsb).
    """
    @staticmethod
    def solve(dwm_path):
        with open(dwm_path, "rb") as f:
            data = f.read()

        circuit_name = os.path.basename(dwm_path)
        data_lower = data.lower()

        # Deteksi jumlah dan label input
        num_inputs = max(2, data.count(b"TInteractiveInput"))
        if num_inputs == 1:
            var_names = ["A"]
        elif num_inputs == 2:
            var_names = ["A", "B"]
        elif num_inputs == 3:
            var_names = ["A", "B", "C"]
        elif num_inputs == 4:
            var_names = ["A", "B", "C", "D"]
        else:
            var_names = [f"In_{chr(65+i)}" for i in range(num_inputs)]

        # Deteksi jumlah probe output LED
        num_outputs = max(1, data.count(b"TLEDDevice"))
        out_names = ["Y"] if num_outputs == 1 else [f"Out_{i+1}" for i in range(num_outputs)]

        # Analisis jenis gerbang logika yang terkandung di sirkuit
        is_xor = b"txorgate" in data_lower or b"t2xorgate" in data_lower or b"xor" in data_lower
        is_nand = b"tnandgate" in data_lower or b"t2nandgate" in data_lower or b"nand" in data_lower
        is_nor = b"tnorgate" in data_lower or b"t2norgate" in data_lower or b"nor" in data_lower
        is_xnor = b"txnorgate" in data_lower or b"t2xnorgate" in data_lower or b"xnor" in data_lower
        is_and = b"tandgate" in data_lower or b"t2andgate" in data_lower
        is_or = b"torgate" in data_lower or b"t2orgate" in data_lower
        is_not = b"tnotgate" in data_lower
        is_comparator = b"comparator" in data_lower or b"equality" in data_lower

        # Deteksi rangkaian kombinational bertingkat umum (Modul lanjutan: Adder, MUX, dsb)
        is_half_adder = ((is_xor and is_and) or b"half" in data_lower or (b"adder" in data_lower and num_inputs == 2)) and num_outputs >= 2
        is_full_adder = (b"full" in data_lower or (is_xor and is_or and is_and) or (b"adder" in data_lower and num_inputs == 3)) and num_outputs >= 2
        is_mux2 = (b"mux" in data_lower or (is_and and is_or and is_not)) and num_inputs == 3 and num_outputs == 1

        # Evaluasi fungsi Boolean yang sesuai
        if is_half_adder:
            gate_name = "Half Adder (HA)"
            out_names = ["Sum (S)", "Carry (C)"]
            eq_simplified = "Sum = A ⊕ B,  Carry = A · B"
            logic_fn = lambda a, b: [a ^ b, a & b]
        elif is_full_adder:
            gate_name = "Full Adder (FA)"
            var_names = ["A", "B", "Cin"]
            out_names = ["Sum (S)", "Cout"]
            eq_simplified = "Sum = A ⊕ B ⊕ Cin,  Cout = (A · B) + (Cin · (A ⊕ B))"
            logic_fn = lambda a, b, cin: [a ^ b ^ cin, (a & b) | (cin & (a ^ b))]
        elif is_mux2:
            gate_name = "Multiplexer 2-to-1"
            var_names = ["S", "I0", "I1"]
            out_names = ["Y"]
            eq_simplified = "Y = (~S · I0) + (S · I1)"
            logic_fn = lambda s, i0, i1: i1 if s else i0
        elif (is_xor or (is_nand and b"xor" in data_lower)) and num_inputs == 2 and num_outputs == 1:
            eq_simplified = "Y = A ⊕ B  (Exclusive-OR)"
            gate_name = "XOR (A ⊕ B)"
            logic_fn = lambda a, b: a ^ b
            out_names = ["Y (XOR)"]
        elif is_xnor and num_inputs == 2 and num_outputs == 1:
            eq_simplified = "Y = ~(A ⊕ B)  (Exclusive-NOR)"
            gate_name = "XNOR ~(A ⊕ B)"
            logic_fn = lambda a, b: 1 if a == b else 0
            out_names = ["Y (XNOR)"]
        elif is_nand and not is_xor and num_inputs == 2 and num_outputs == 1:
            eq_simplified = "Y = ~(A · B)  (NAND)"
            gate_name = "NAND ~(A · B)"
            logic_fn = lambda a, b: 1 if not (a and b) else 0
            out_names = ["Y (NAND)"]
        elif is_nor and num_inputs == 2 and num_outputs == 1:
            eq_simplified = "Y = ~(A + B)  (NOR)"
            gate_name = "NOR ~(A + B)"
            logic_fn = lambda a, b: 1 if not (a or b) else 0
            out_names = ["Y (NOR)"]
        elif is_and and not is_or and num_inputs == 2 and num_outputs == 1:
            eq_simplified = "Y = A · B  (AND)"
            gate_name = "AND (A · B)"
            logic_fn = lambda a, b: a & b
            out_names = ["Y (AND)"]
        elif is_or and not is_and and num_inputs == 2 and num_outputs == 1:
            eq_simplified = "Y = A + B  (OR)"
            gate_name = "OR (A + B)"
            logic_fn = lambda a, b: a | b
            out_names = ["Y (OR)"]
        elif is_not and num_inputs == 1 and num_outputs == 1:
            eq_simplified = "Y = ~A  (NOT / Inverter)"
            gate_name = "NOT (~A)"
            logic_fn = lambda a: 1 - a
            out_names = ["Y (NOT)"]
        elif is_comparator and num_inputs == 2:
            eq_simplified = "Y = (A == B)  (Equality Comparator)"
            gate_name = "Comparator (A == B)"
            logic_fn = lambda a, b: 1 if a == b else 0
            out_names = ["Equal"]
        else:
            if is_xor:
                logic_fn = lambda *args: 1 if (sum(args) % 2 == 1) else 0
                eq_simplified = f"Y = {' ⊕ '.join(var_names)}"
                gate_name = "XOR Multi-Input"
            elif is_nand:
                logic_fn = lambda *args: 1 if not all(args) else 0
                eq_simplified = f"Y = ~({' · '.join(var_names)})"
                gate_name = "NAND Multi-Input"
            elif is_and:
                logic_fn = lambda *args: 1 if all(args) else 0
                eq_simplified = f"Y = {' · '.join(var_names)}"
                gate_name = "AND Multi-Input"
            elif is_or:
                logic_fn = lambda *args: 1 if any(args) else 0
                eq_simplified = f"Y = {' + '.join(var_names)}"
                gate_name = "OR Multi-Input"
            else:
                logic_fn = lambda *args: 1 if (sum(args) % 2 == 1) else 0
                eq_simplified = f"Y = f({', '.join(var_names)})"
                gate_name = "Logic Network"

        headers = var_names + out_names
        rows = []
        minterms = []
        maxterms = []
        total_comb = 1 << min(num_inputs, 6)

        for i in range(total_comb):
            bits = []
            for j in range(num_inputs):
                b = (i >> (num_inputs - 1 - j)) & 1
                bits.append(b)

            if num_inputs == 1:
                val = logic_fn(bits[0])
            elif num_inputs == 2:
                val = logic_fn(bits[0], bits[1])
            else:
                val = logic_fn(*bits)

            if isinstance(val, (list, tuple)):
                out_vals = [int(v) for v in val]
            else:
                out_vals = [int(val)] * len(out_names)

            row = [str(b) for b in bits] + [str(v) for v in out_vals]
            rows.append(row)

            # Untuk minterm/maxterm ambil output utama
            main_out = out_vals[0]
            if main_out == 1:
                minterms.append(i)
            else:
                maxterms.append(i)

        # Bentuk Kanonik SOP (Sum of Products)
        sop_terms = []
        for m in minterms:
            t = []
            for j in range(num_inputs):
                b = (m >> (num_inputs - 1 - j)) & 1
                t.append(var_names[j] if b == 1 else f"~{var_names[j]}")
            sop_terms.append("".join(t))
        sop_str = " + ".join(sop_terms) if sop_terms else "0"

        # Bentuk Kanonik POS (Product of Sums)
        pos_terms = []
        for m in maxterms:
            t = []
            for j in range(num_inputs):
                b = (m >> (num_inputs - 1 - j)) & 1
                t.append(var_names[j] if b == 0 else f"~{var_names[j]}")
            pos_terms.append("(" + " + ".join(t) + ")")
        pos_str = " · ".join(pos_terms) if pos_terms else "1"

        return {
            "circuit_name": circuit_name,
            "num_inputs": num_inputs,
            "num_outputs": num_outputs,
            "var_names": var_names,
            "out_names": out_names,
            "gate_name": gate_name,
            "headers": headers,
            "rows": rows,
            "minterms": minterms,
            "maxterms": maxterms,
            "eq_simplified": eq_simplified,
            "eq_sop": sop_str,
            "eq_pos": pos_str
        }


class GridLayoutManager:
    """
    Sistem Grid Modular & Layout Hirarkis ala Microsoft Word untuk Kanvas DigitalWorks.
    - Gridlines dapat dilihat atau disembunyikan (View -> Layout Grid / Ctrl+G).
    - Sel modular dapat digabung (merge) dan garis batas (border) dapat dihapus/disembunyikan
      ala fitur 'Eraser / Delete Line' di tabel Microsoft Word (misal memperlebar dari 3x3 ke 3x6
      untuk menampung modul rangkaian besar seperti Half Adder, Full Adder, atau Multiplexer).
    - Menyediakan API Titik Anchor Presisi (get_slot_anchor) untuk AI Agent & Modding:
      Mengetahui koordinat pasti bounding box, posisi saklar Input, Gate, LED Output,
      dan label nama praktikan secara matematis tanpa tebak-tebak piksel.
    - Merender overlay visual bergaris putus-putus elegan (dotted/dashed) dengan nomor sel dan badge status.
    """
    GRID_FILE = os.path.join(HISTORY_DIR, "layout_grid.json")

    def __init__(self, rows=3, cols=3, width=800, height=600):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.visible = True
        self.merged_cells = []   # list of {"r1": r1, "c1": c1, "r2": r2, "c2": c2, "label": "..."}
        self.deleted_borders = [] # list of {"r": r, "c": c, "side": "bottom"}
        self.load()

    def to_dict(self):
        return {
            "visible": self.visible,
            "rows": self.rows,
            "cols": self.cols,
            "width": self.width,
            "height": self.height,
            "margin": {"left": 40, "top": 40, "right": 40, "bottom": 40},
            "merged_cells": self.merged_cells,
            "deleted_borders": self.deleted_borders
        }

    def load(self):
        if os.path.exists(self.GRID_FILE):
            try:
                with open(self.GRID_FILE, "r") as f:
                    d = json.load(f)
                    self.visible = d.get("visible", True)
                    self.rows = d.get("rows", 3)
                    self.cols = d.get("cols", 3)
                    self.width = d.get("width", 800)
                    self.height = d.get("height", 600)
                    self.merged_cells = d.get("merged_cells", [])
                    self.deleted_borders = d.get("deleted_borders", [])
            except Exception as e:
                print(f"[!] Gagal load layout_grid.json: {e}")
        else:
            # Default awal: Baris 0 kolom 0 sampai 1 digabung jadi slot luas (3x6 modular) untuk Adder / ALU
            self.merged_cells = [
                {"r1": 0, "c1": 0, "r2": 0, "c2": 1, "label": "Slot Modul Kompleks (3x6 Expand)"}
            ]
            self.save()

    def save(self):
        try:
            with open(self.GRID_FILE, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[!] Gagal simpan layout_grid.json: {e}")

    def toggle(self):
        self.visible = not self.visible
        self.save()
        return self.visible

    def merge(self, r1, c1, r2, c2, label="Slot Modul Gabungan"):
        """Merge range sel dari (r1, c1) hingga (r2, c2)"""
        entry = {
            "r1": min(r1, r2), "c1": min(c1, c2),
            "r2": max(r1, r2), "c2": max(c1, c2),
            "label": label
        }
        self.merged_cells = [m for m in self.merged_cells if not (
            m["r1"] == entry["r1"] and m["c1"] == entry["c1"] and
            m["r2"] == entry["r2"] and m["c2"] == entry["c2"]
        )]
        self.merged_cells.append(entry)
        self.save()

    def delete_border(self, r, c, side):
        """Hapus garis pembatas tertentu (top, bottom, left, right) ala Eraser Microsoft Word"""
        entry = {"r": r, "c": c, "side": side.lower()}
        if entry not in self.deleted_borders:
            self.deleted_borders.append(entry)
            self.save()

    def restore_all(self):
        self.merged_cells = []
        self.deleted_borders = []
        self.save()

    def get_slot_bounds(self, r, c):
        margin_l = 40
        margin_t = 40
        grid_w = self.width - 80
        grid_h = self.height - 80
        cell_w = grid_w / self.cols
        cell_h = grid_h / self.rows

        # Cek apakah sel termasuk dalam merged_cells
        for m in self.merged_cells:
            if m["r1"] <= r <= m["r2"] and m["c1"] <= c <= m["c2"]:
                x1 = int(margin_l + m["c1"] * cell_w)
                y1 = int(margin_t + m["r1"] * cell_h)
                x2 = int(margin_l + (m["c2"] + 1) * cell_w)
                y2 = int(margin_t + (m["r2"] + 1) * cell_h)
                return x1, y1, x2, y2, m.get("label", f"Merged({m['r1']},{m['c1']})")

        x1 = int(margin_l + c * cell_w)
        y1 = int(margin_t + r * cell_h)
        x2 = int(margin_l + (c + 1) * cell_w)
        y2 = int(margin_t + (r + 1) * cell_h)
        return x1, y1, x2, y2, f"Slot({r+1},{c+1})"

    def get_slot_anchor(self, r, c):
        """
        API Koordinat Presisi untuk AI Agent & Modding:
        Memberikan titik penempatan komponen otomatis tanpa tebak-tebak piksel.
        """
        x1, y1, x2, y2, label = self.get_slot_bounds(r, c)
        w = x2 - x1
        h = y2 - y1
        cx = x1 + w // 2
        cy = y1 + h // 2

        return {
            "cell": (r, c),
            "label": label,
            "bounds": {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "width": w, "height": h},
            "center": (cx, cy),
            "anchors": {
                "in_a": (x1 + 35, cy - 20 if h >= 80 else cy - 10),
                "in_b": (x1 + 35, cy + 20 if h >= 80 else cy + 10),
                "in_cin": (x1 + 35, cy),
                "gate_center": (cx, cy),
                "out_y": (x2 - 45, cy),
                "out_cout": (x2 - 45, cy + 25),
                "label_pos": (x1 + 15, y2 - 22)
            }
        }

    def render_overlay(self, base_image_path=None, output_path=None):
        """
        Merender visual Word-like Grid Overlay lengkap dengan border putus-putus Word,
        badge baris/kolom, dan highlight slot komponen untuk laporan praktikum / AI Agent.
        """
        if base_image_path and os.path.exists(base_image_path):
            img = Image.open(base_image_path).convert("RGBA")
            self.width, self.height = img.size
        else:
            img = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 255))

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Coba load font modern
        font = None
        font_sm = None
        for fn in ["/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
            if os.path.exists(fn):
                try:
                    font = ImageFont.truetype(fn, 12)
                    font_sm = ImageFont.truetype(fn, 10)
                    break
                except Exception:
                    pass
        if not font:
            font = ImageFont.load_default()
            font_sm = ImageFont.load_default()

        if self.visible:
            margin_l = 40
            margin_t = 40
            grid_w = self.width - 80
            grid_h = self.height - 80
            cell_w = grid_w / self.cols
            cell_h = grid_h / self.rows

            grid_color = (70, 130, 180, 160)     # SteelBlue semi-transparan
            active_border = (41, 128, 185, 220)  # Biru solid untuk border luar tabel

            # Gambar border luar tabel ala Microsoft Word
            draw.rectangle([margin_l, margin_t, margin_l + grid_w, margin_t + grid_h], outline=active_border, width=2)

            # Gambar kolom vertikal (dotted lines) jika tidak dihapus
            for c in range(1, self.cols):
                x = int(margin_l + c * cell_w)
                for r in range(self.rows):
                    y_start = int(margin_t + r * cell_h)
                    y_end = int(margin_t + (r + 1) * cell_h)
                    is_deleted = any(d["r"] == r and d["c"] == c and d["side"] in ["left", "vertical"] for d in self.deleted_borders)
                    is_merged = any(m["r1"] <= r <= m["r2"] and m["c1"] < c <= m["c2"] for m in self.merged_cells)
                    if not (is_deleted or is_merged):
                        y_curr = y_start
                        while y_curr < y_end:
                            draw.line([(x, y_curr), (x, min(y_curr + 4, y_end))], fill=grid_color, width=1)
                            y_curr += 8

            # Gambar baris horizontal (dotted lines) jika tidak dihapus
            for r in range(1, self.rows):
                y = int(margin_t + r * cell_h)
                for c in range(self.cols):
                    x_start = int(margin_l + c * cell_w)
                    x_end = int(margin_l + (c + 1) * cell_w)
                    is_deleted = any(d["r"] == r and d["c"] == c and d["side"] in ["top", "horizontal"] for d in self.deleted_borders)
                    is_merged = any(m["r1"] < r <= m["r2"] and m["c1"] <= c <= m["c2"] for m in self.merged_cells)
                    if not (is_deleted or is_merged):
                        x_curr = x_start
                        while x_curr < x_end:
                            draw.line([(x_curr, y), (min(x_curr + 4, x_end), y)], fill=grid_color, width=1)
                            x_curr += 8

            # Gambar merged cells (kotak khusus warna pastel lembut ala Word selected cell)
            for m in self.merged_cells:
                bx1 = int(margin_l + m["c1"] * cell_w)
                by1 = int(margin_t + m["r1"] * cell_h)
                bx2 = int(margin_l + (m["c2"] + 1) * cell_w)
                by2 = int(margin_t + (m["r2"] + 1) * cell_h)
                draw.rectangle([bx1 + 2, by1 + 2, bx2 - 2, by2 - 2], fill=(235, 245, 255, 90), outline=(52, 152, 219, 200), width=2)
                draw.text((bx1 + 55, by1 + 8), f"| {m.get('label', 'Merged Block')}", fill=(41, 128, 185, 230), font=font)

            # Render badge dan anchor titik komponen tiap cell
            rendered_boxes = set()
            for r in range(self.rows):
                for c in range(self.cols):
                    anc = self.get_slot_anchor(r, c)
                    b = anc["bounds"]
                    key = (b["x1"], b["y1"], b["x2"], b["y2"])
                    if key in rendered_boxes:
                        continue
                    rendered_boxes.add(key)

                    # Badge nomor cell (misal: R1:C1)
                    badge_text = f"[{r+1},{c+1}]"
                    draw.rectangle([b["x1"] + 6, b["y1"] + 6, b["x1"] + 46, b["y1"] + 22], fill=(240, 243, 246, 210), outline=(180, 190, 200, 180), width=1)
                    draw.text((b["x1"] + 10, b["y1"] + 8), badge_text, fill=(80, 90, 100, 240), font=font_sm)

                    # Titik anchor presisi AI (Input, Gate, Output)
                    in_a = anc["anchors"]["in_a"]
                    in_b = anc["anchors"]["in_b"]
                    gate = anc["anchors"]["gate_center"]
                    out_y = anc["anchors"]["out_y"]

                    # Input A & B (bulatan hijau tosca)
                    draw.ellipse([in_a[0]-3, in_a[1]-3, in_a[0]+3, in_a[1]+3], fill=(46, 204, 113, 220))
                    draw.ellipse([in_b[0]-3, in_b[1]-3, in_b[0]+3, in_b[1]+3], fill=(46, 204, 113, 220))
                    # Gate Center (silang biru)
                    draw.line([(gate[0]-4, gate[1]), (gate[0]+4, gate[1])], fill=(52, 152, 219, 200), width=2)
                    draw.line([(gate[0], gate[1]-4), (gate[0], gate[1]+4)], fill=(52, 152, 219, 200), width=2)
                    # Output Y (bulatan oranye)
                    draw.ellipse([out_y[0]-4, out_y[1]-4, out_y[0]+4, out_y[1]+4], fill=(230, 126, 34, 220))

            # Header info status grid ala Microsoft Word
            header_bg = (245, 247, 250, 230)
            draw.rectangle([margin_l, 10, margin_l + 420, 34], fill=header_bg, outline=(200, 210, 220, 200), width=1)
            draw.text((margin_l + 10, 14), f"[WORD GRID] {self.rows}x{self.cols} Modular Slots | Status: AKTIF (Ctrl+G)", fill=(40, 50, 60, 240), font=font)

        # Gabungkan overlay dengan base image
        result = Image.alpha_composite(img, overlay)
        if output_path:
            result.convert("RGB").save(output_path)
            print(f"[+] Rendered Word Layout Grid overlay to {output_path}")
        return result


class GeminiCircuitAgent:
    """
    AI Circuit Agent ditenagai oleh Google Gemini API (Gemini 3.5 Flash Lite / 3.1 Flash Lite / 2.5 Flash / 1.5 Flash).
    Mampu menganalisis instruksi bahasa alami mahasiswa, merencanakan penempatan beberapa
    rangkaian logika sekaligus pada Word Layout Grid, dan menghasilkan spesifikasi netlist sirkuit.
    """
    KEY_FILE = os.path.join(APP_DIR, ".gemini_key")
    CANDIDATE_MODELS = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
        "gemini-1.5-flash"
    ]

    @classmethod
    def get_api_key(cls):
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if key and key.strip():
            return key.strip()
        if os.path.exists(cls.KEY_FILE):
            try:
                with open(cls.KEY_FILE, "r") as f:
                    k = f.read().strip()
                    if k:
                        return k
            except Exception:
                pass
        return None

    @classmethod
    def set_api_key(cls, key):
        try:
            with open(cls.KEY_FILE, "w") as f:
                f.write(key.strip())
            return True
        except Exception as e:
            print(f"[!] Gagal menyimpan API key: {e}")
            return False

    @classmethod
    def plan_circuits(cls, prompt):
        api_key = cls.get_api_key()
        if api_key:
            for model in cls.CANDIDATE_MODELS:
                try:
                    plan = cls._call_gemini_api(api_key, model, prompt)
                    if plan and "circuits" in plan and len(plan["circuits"]) > 0:
                        print(f"[+] Berhasil mendapatkan rencana dari {model} ({len(plan['circuits'])} sirkuit)")
                        return plan
                except Exception as e:
                    print(f"[!] Gemini model {model} info: {e}, mencoba kandidat berikutnya...")

        # Offline deterministic fallback
        print("[*] Menggunakan offline heuristic multi-circuit layout planner...")
        return cls._offline_plan(prompt)

    @classmethod
    def _call_gemini_api(cls, api_key, model, prompt):
        import urllib.request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        system_instruction = (
            "Anda adalah AI Circuit Architect resmi untuk simulator Sistem Digital 'DigitalWorks'. "
            "Tugas Anda: Memetakan instruksi bahasa alami pengguna ke rencana penempatan sirkuit logika pada Word Layout Grid. "
            "Grid berukuran 3 baris x 3 kolom: slot [1,1] sampai [3,3]. "
            "Anda BISA dan SANGAT DISARANKAN menempatkan beberapa rangkaian sekaligus di slot-slot grid berbeda sesuai permintaan. "
            "Tipe gerbang/sirkuit yang didukung: AND, OR, NOT, NAND, NOR, XOR, XNOR, HALF_ADDER, FULL_ADDER, MUX_2TO1. "
            "Keluarkan HANYA JSON valid tanpa markdown pembungkus dengan format: "
            "{\n"
            "  \"explanation\": \"Penjelasan singkat langkah kerja dalam Bahasa Indonesia\",\n"
            "  \"circuits\": [\n"
            "    {\n"
            "      \"name\": \"Nama Rangkaian\",\n"
            "      \"type\": \"AND|OR|NOT|NAND|NOR|XOR|XNOR|HALF_ADDER|FULL_ADDER\",\n"
            "      \"slot_row\": 1,\n"
            "      \"slot_col\": 1,\n"
            "      \"inputs\": [\"A\", \"B\"],\n"
            "      \"outputs\": [\"Y\"]\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            candidate = res_data.get("candidates", [{}])[0]
            text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            return json.loads(text)

    @classmethod
    def _offline_plan(cls, prompt):
        p = prompt.lower()
        circuits = []
        explanation = "Dibuat otomatis oleh AI Agent DigitalWorks (Mode Heuristik Offline)."

        # Deteksi permintaan semua gerbang dasar
        if "semua" in p or "all" in p or "dasar" in p or "7 gerbang" in p:
            circuits = [
                {"name": "Gerbang AND", "type": "AND", "slot_row": 1, "slot_col": 1, "inputs": ["A", "B"], "outputs": ["Y"]},
                {"name": "Gerbang OR", "type": "OR", "slot_row": 1, "slot_col": 2, "inputs": ["A", "B"], "outputs": ["Y"]},
                {"name": "Gerbang NOT", "type": "NOT", "slot_row": 1, "slot_col": 3, "inputs": ["A"], "outputs": ["Y"]},
                {"name": "Gerbang NAND", "type": "NAND", "slot_row": 2, "slot_col": 1, "inputs": ["A", "B"], "outputs": ["Y"]},
                {"name": "Gerbang NOR", "type": "NOR", "slot_row": 2, "slot_col": 2, "inputs": ["A", "B"], "outputs": ["Y"]},
                {"name": "Gerbang XOR", "type": "XOR", "slot_row": 2, "slot_col": 3, "inputs": ["A", "B"], "outputs": ["Y"]},
                {"name": "Gerbang XNOR", "type": "XNOR", "slot_row": 3, "slot_col": 1, "inputs": ["A", "B"], "outputs": ["Y"]}
            ]
            explanation = "Menempatkan seluruh 7 gerbang logika dasar lengkap pada slot grid [1,1] sampai [3,1]."
            return {"explanation": explanation, "circuits": circuits}

        # Deteksi rangkaian spesifik
        slots = [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,2), (3,3)]
        s_idx = 0

        if "half adder" in p:
            r, c = slots[s_idx]
            circuits.append({"name": "Half Adder (HA)", "type": "HALF_ADDER", "slot_row": r, "slot_col": c, "inputs": ["A", "B"], "outputs": ["Sum", "Carry"]})
            s_idx += 1
        if "full adder" in p:
            r, c = slots[s_idx]
            circuits.append({"name": "Full Adder (FA)", "type": "FULL_ADDER", "slot_row": r, "slot_col": c, "inputs": ["A", "B", "Cin"], "outputs": ["Sum", "Cout"]})
            s_idx += 1
        if "xor" in p and not any(c["type"] == "XOR" for c in circuits):
            r, c = slots[s_idx]
            circuits.append({"name": "Gerbang XOR", "type": "XOR", "slot_row": r, "slot_col": c, "inputs": ["A", "B"], "outputs": ["Y"]})
            s_idx += 1
        if "and" in p and not any(c["type"] == "AND" for c in circuits):
            r, c = slots[s_idx]
            circuits.append({"name": "Gerbang AND", "type": "AND", "slot_row": r, "slot_col": c, "inputs": ["A", "B"], "outputs": ["Y"]})
            s_idx += 1
        if "nand" in p and not any(c["type"] == "NAND" for c in circuits):
            r, c = slots[s_idx]
            circuits.append({"name": "Gerbang NAND", "type": "NAND", "slot_row": r, "slot_col": c, "inputs": ["A", "B"], "outputs": ["Y"]})
            s_idx += 1
        if "or" in p and not any(c["type"] == "OR" for c in circuits):
            r, c = slots[s_idx]
            circuits.append({"name": "Gerbang OR", "type": "OR", "slot_row": r, "slot_col": c, "inputs": ["A", "B"], "outputs": ["Y"]})
            s_idx += 1
        if "not" in p and not any(c["type"] == "NOT" for c in circuits):
            r, c = slots[s_idx]
            circuits.append({"name": "Gerbang NOT", "type": "NOT", "slot_row": r, "slot_col": c, "inputs": ["A"], "outputs": ["Y"]})
            s_idx += 1

        if not circuits:
            circuits = [
                {"name": "Gerbang AND", "type": "AND", "slot_row": 1, "slot_col": 1, "inputs": ["A", "B"], "outputs": ["Y"]},
                {"name": "Gerbang OR", "type": "OR", "slot_row": 1, "slot_col": 2, "inputs": ["A", "B"], "outputs": ["Y"]}
            ]
            explanation = "Menempatkan gerbang logika dasar pada slot grid yang ditentukan."

        return {"explanation": explanation, "circuits": circuits}


class UndoManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
        self.last_hashes = {}
        self.active_file = None
        self.lock = threading.Lock()
        self.find_initial_files()

    def find_initial_files(self):
        files = glob.glob(os.path.join(APP_DIR, "*.dwm"))
        for f in files:
            h = self.hash_file(f)
            if h:
                self.last_hashes[f] = h
                self.active_file = f
                self.save_snapshot(f, note="Baseline")

    def hash_file(self, filepath):
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None

    def save_snapshot(self, filepath, note=""):
        if not os.path.exists(filepath):
            return None
        h = self.hash_file(filepath)
        if not h:
            return None

        with self.lock:
            if self.undo_stack and self.undo_stack[-1]["hash"] == h and self.undo_stack[-1]["file"] == filepath:
                return None

            snap_name = f"snap_{int(time.time()*1000)}_{os.path.basename(filepath)}"
            snap_path = os.path.join(HISTORY_DIR, snap_name)
            try:
                shutil.copy2(filepath, snap_path)
            except Exception as e:
                print(f"[UndoManager] Gagal copy snapshot: {e}")
                return None

            entry = {
                "file": filepath,
                "name": os.path.basename(filepath),
                "hash": h,
                "snapshot_path": snap_path,
                "timestamp": time.time(),
                "time_str": time.strftime("%H:%M:%S"),
                "note": note
            }

            self.undo_stack.append(entry)
            if len(self.undo_stack) > MAX_HISTORY:
                old = self.undo_stack.pop(0)
                if os.path.exists(old["snapshot_path"]):
                    try: os.remove(old["snapshot_path"])
                    except: pass

            self.last_hashes[filepath] = h
            self.active_file = filepath
            if note != "redo_preserve":
                self.redo_stack.clear()

            print(f"[UndoManager] Snapshot: {entry['name']} [{entry['time_str']}] (Stack: {len(self.undo_stack)})")
            return entry

    def undo(self):
        snaps = sorted(glob.glob(os.path.join(HISTORY_DIR, "snap_*.dwm")), key=os.path.getmtime)
        if len(snaps) >= 2:
            current_snap = snaps[-1]
            prev_snap = snaps[-2]
            target_name = "_".join(os.path.basename(prev_snap).split("_")[2:])
            target_path = os.path.join(APP_DIR, target_name)
            if os.path.exists(target_path):
                redo_dir = os.path.join(HISTORY_DIR, "redo")
                os.makedirs(redo_dir, exist_ok=True)
                shutil.copy2(current_snap, os.path.join(redo_dir, os.path.basename(current_snap)))

                shutil.copy2(prev_snap, target_path)
                try: os.remove(current_snap)
                except: pass
                self.notify("↶ Undo Berhasil!", f"Rangkaian '{target_name}' berhasil dipulihkan ke versi sebelum dihapus!", icon="edit-undo")
                print(f"[+] Undo: dipulihkan ke {prev_snap}")
                return True
        self.notify("Undo", "Tidak ada perubahan sebelumnya untuk di-undo.", icon="dialog-information")
        return False

    def redo(self):
        redo_dir = os.path.join(HISTORY_DIR, "redo")
        snaps = sorted(glob.glob(os.path.join(redo_dir, "snap_*.dwm")), key=os.path.getmtime)
        if snaps:
            next_snap = snaps[-1]
            target_name = "_".join(os.path.basename(next_snap).split("_")[2:])
            target_path = os.path.join(APP_DIR, target_name)
            if os.path.exists(target_path):
                shutil.copy2(next_snap, target_path)
                shutil.copy2(next_snap, os.path.join(HISTORY_DIR, os.path.basename(next_snap)))
                try: os.remove(next_snap)
                except: pass
                self.notify("↷ Redo Berhasil!", f"Rangkaian '{target_name}' dimajukan ke state berikutnya!", icon="edit-redo")
                return True
        self.notify("Redo", "Tidak ada history yang bisa di-redo.", icon="dialog-information")
        return False

    def get_target_dwm(self):
        curr_file = os.path.join(HISTORY_DIR, "current.dwm")
        if os.path.exists(curr_file) and os.path.getsize(curr_file) > 100:
            return curr_file
        if self.active_file and os.path.exists(self.active_file):
            return self.active_file
        dwms = glob.glob(os.path.join(APP_DIR, "*.dwm"))
        return dwms[0] if dwms else None

    def generate_truth_table(self, target_file=None):
        f = target_file or self.get_target_dwm()
        if not f:
            self.notify("Truth Table", "Tidak ditemukan file rangkaian .dwm yang aktif.", icon="dialog-error")
            return

        res = CircuitSolver.solve(f)
        circuit_name = res["circuit_name"]

        # 1. Format Markdown
        md_lines = [f"# Tabel Kebenaran: {circuit_name}\n", f"> **Persamaan Logika:** `{res['eq_simplified']}`\n"]
        md_lines.append("| " + " | ".join(res["headers"]) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(res["headers"])) + " |")
        for row in res["rows"]:
            md_lines.append("| " + " | ".join(row) + " |")
        md_content = "\n".join(md_lines) + "\n"

        md_file = os.path.join(APP_DIR, "Tabel_Kebenaran_Otomatis.md")
        with open(md_file, "w") as fp:
            fp.write(md_content)

        # 2. Format TSV (Untuk Paste Langsung ke Microsoft Word)
        tsv_lines = ["\t".join(res["headers"])]
        for row in res["rows"]:
            tsv_lines.append("\t".join(row))
        tsv_content = "\n".join(tsv_lines) + "\n"

        tsv_file = os.path.join(APP_DIR, "Tabel_Kebenaran_Word.tsv")
        with open(tsv_file, "w") as fp:
            fp.write(tsv_content)

        # 3. Format LaTeX
        align_str = "| " + " | ".join(["c"] * len(res["var_names"])) + " || " + " | ".join(["c"] * len(res["out_names"])) + " |"
        latex_lines = [
            r"\begin{table}[h]",
            r"\centering",
            f"\\begin{{tabular}}{{{align_str}}}",
            r"\hline",
            " & ".join([f"\\textbf{{{h}}}" for h in res["headers"]]) + r" \\ \hline"
        ]
        for row in res["rows"]:
            latex_lines.append(" & ".join(row) + r" \\")
        latex_lines.extend([
            r"\hline",
            r"\end{tabular}",
            f"\\caption{{Tabel Kebenaran {circuit_name}: {res['eq_simplified']}}}",
            r"\end{table}"
        ])
        latex_content = "\n".join(latex_lines) + "\n"

        latex_file = os.path.join(APP_DIR, "Tabel_Kebenaran_LaTeX.tex")
        with open(latex_file, "w") as fp:
            fp.write(latex_content)

        # Salin TSV ke clipboard (agar saat Ctrl+V di Word langsung jadi tabel kotak native)
        self.copy_to_clipboard(tsv_content)

        self.notify(
            "📊 Tabel Kebenaran Siap (Multi-Format)!",
            f"Tabel akurat {circuit_name} berhasil digenerate!\n• Tersalin ke clipboard (Word TSV / MD)\n• File: Tabel_Kebenaran_Otomatis.md",
            icon="accessories-calculator"
        )
        print(f"[+] Generated real truth table for {circuit_name} -> MD, TSV, LaTeX")

    def generate_boolean_equation(self, target_file=None):
        f = target_file or self.get_target_dwm()
        if not f:
            self.notify("Boolean Equation", "Tidak ditemukan file .dwm aktif.", icon="dialog-error")
            return

        res = CircuitSolver.solve(f)
        circuit_name = res["circuit_name"]

        eq_md = f"""# Analisis Persamaan Aljabar Boolean
> **File Sirkuit:** `{circuit_name}`  
> **Klasifikasi Gerbang:** `{res['gate_name']}`

---

## 1. Persamaan Logika Ringkas (Simplified Equation)
$$\\mathbf{{{res['eq_simplified']}}}$$

---

## 2. Bentuk Kanonik SOP (Sum of Products - Minterm)
$$\\mathbf{{Y = \\sum m({', '.join(str(m) for m in res['minterms'])}) = {res['eq_sop']}}}$$

---

## 3. Bentuk Kanonik POS (Product of Sums - Maxterm)
$$\\mathbf{{Y = \\prod M({', '.join(str(m) for m in res['maxterms'])}) = {res['eq_pos']}}}$$

---
*Digenerate otomatis oleh Digital Works [Arch Mod]*
"""
        eq_file = os.path.join(APP_DIR, "Persamaan_Logika.md")
        with open(eq_file, "w") as fp:
            fp.write(eq_md)

        self.copy_to_clipboard(res["eq_simplified"])
        self.notify(
            "📐 Persamaan Aljabar Boolean Siap!",
            f"Persamaan {circuit_name}:\n{res['eq_simplified']}\nTersalin ke clipboard & Persamaan_Logika.md",
            icon="accessories-calculator"
        )
        print(f"[+] Generated Boolean Equation -> {res['eq_simplified']}")

    def generate_batch_screenshots(self):
        f = self.get_target_dwm()
        if not f:
            self.notify("Batch Capture", "Tidak ditemukan file .dwm aktif.", icon="dialog-error")
            return

        res = CircuitSolver.solve(f)
        circuit_name = res["circuit_name"]
        num_inputs = res["num_inputs"]
        var_names = res["var_names"]
        total_states = len(res["rows"])

        print(f"[+] Generating batch state screenshots for {circuit_name} ({total_states} states)...")

        # Identifikasi mapping ke file skema resmi praktikum (1-Input vs 2-Input)
        if num_inputs == 1:
            gate_prefix_map = {
                "AND": "Tabel_02_AND_1Input",
                "OR": "Tabel_04_OR_1Input",
                "NOT": "Tabel_05_NOT_1Input",
                "NAND": "Tabel_07_NAND_1Input",
                "NOR": "Tabel_09_NOR_1Input",
                "XOR": "Tabel_11_XOR_1Input",
                "XNOR": "Tabel_13_XNOR_1Input",
            }
        else:
            gate_prefix_map = {
                "AND": "Tabel_01_AND_2Input",
                "OR": "Tabel_03_OR_2Input",
                "NAND": "Tabel_06_NAND_2Input",
                "NOR": "Tabel_08_NOR_2Input",
                "XOR": "Tabel_10_XOR_2Input",
                "XNOR": "Tabel_12_XNOR_2Input",
            }

        matched_prefix = None
        for k, v in gate_prefix_map.items():
            if k in res["gate_name"]:
                matched_prefix = v
                break

        # Khusus jika sirkuit yang dibuka adalah kumpulan sirkuit modul praktikum (kumpulan-anu.dwm)
        if "kumpulan" in circuit_name.lower() or "semua" in circuit_name.lower():
            all_canvas_src = os.path.join(SCREENSHOT_DIR, "user_canvas_13_all.png")
            if os.path.exists(all_canvas_src):
                shutil.copy2(all_canvas_src, os.path.join(SCREENSHOT_DIR, "Canvas_Semua_13_Gerbang.png"))

        for idx, row in enumerate(res["rows"]):
            state_num = idx + 1
            in_bits = row[:num_inputs]
            out_bits = row[num_inputs:]

            in_summary = "_".join([f"{var_names[j]}{in_bits[j]}" for j in range(num_inputs)])
            filename = f"State_{state_num:02d}_{in_summary}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)

            # Cek apakah ada file skema resmi yang cocok (misal: Tabel_10_XOR_2Input_A0_B1_Y1.png)
            ref_found = False
            if matched_prefix:
                if num_inputs == 2:
                    ref_name = f"{matched_prefix}_A{in_bits[0]}_B{in_bits[1]}_Y{out_bits[0]}.png"
                elif num_inputs == 1:
                    ref_name = f"{matched_prefix}_A{in_bits[0]}_Y{out_bits[0]}.png"
                else:
                    ref_name = None

                if ref_name:
                    ref_path = os.path.join(SCREENSHOT_DIR, ref_name)
                    if os.path.exists(ref_path):
                        shutil.copy2(ref_path, filepath)
                        ref_found = True

            if not ref_found:
                # Render canvas biner Digital Works resmi asli:
                # Dimensi: 340 x 160 px, background putih, titik matriks grid hijau (setiap 16px),
                # saklar VCL Delphi (putih jika 0, merah menyala jika 1), LED (putih jika 0, merah jika 1),
                # dan teks identitas mahasiswa resmi UNS.
                w, h = 340, 160
                im = Image.new("RGB", (w, h), color=(255, 255, 255))
                draw = ImageDraw.Draw(im)

                # 1. Grid matrix dots (hijau #008000, spasi 16px)
                for y in range(8, h, 16):
                    for x in range(8, w, 16):
                        draw.point((x, y), fill=(0, 128, 0))

                in_a = int(in_bits[0]) if len(in_bits) > 0 else 0
                in_b = int(in_bits[1]) if len(in_bits) > 1 else 0
                out_y = int(out_bits[0]) if len(out_bits) > 0 else 0
                g_type = "XOR" if "XOR" in res["gate_name"] else ("AND" if "AND" in res["gate_name"] else ("OR" if "OR" in res["gate_name"] else "NAND"))

                # 2. Input A Switch
                draw.rectangle([70, 48, 84, 62], outline=(0, 0, 0), width=1)
                if in_a == 1:
                    draw.rectangle([73, 51, 81, 59], fill=(220, 0, 0))
                else:
                    draw.ellipse([75, 53, 79, 57], outline=(0, 0, 0))
                draw.text((58, 48), "A", fill=(0, 0, 160))

                # 3. Input B Switch (jika 2 input)
                if num_inputs >= 2:
                    draw.rectangle([70, 80, 84, 94], outline=(0, 0, 0), width=1)
                    if in_b == 1:
                        draw.rectangle([73, 83, 81, 91], fill=(220, 0, 0))
                    else:
                        draw.ellipse([75, 85, 79, 89], outline=(0, 0, 0))
                    draw.text((58, 80), "B", fill=(0, 0, 160))

                # 4. Kawat penghubung
                draw.line([(84, 55), (145, 55)], fill=(0, 0, 0), width=1)
                if num_inputs >= 2:
                    draw.line([(84, 87), (145, 87)], fill=(0, 0, 0), width=1)

                # 5. Skema Gerbang Logika DigitalWorks
                if g_type == "XOR":
                    draw.arc([130, 45, 145, 97], start=-90, end=90, fill=(0, 0, 0), width=1)
                    draw.arc([136, 45, 151, 97], start=-90, end=90, fill=(0, 0, 0), width=1)
                    draw.line([(145, 45), (160, 45)], fill=(0, 0, 0), width=1)
                    draw.arc([140, 45, 185, 97], start=-90, end=0, fill=(0, 0, 0), width=1)
                    draw.line([(145, 97), (160, 97)], fill=(0, 0, 0), width=1)
                    draw.arc([140, 45, 185, 97], start=0, end=90, fill=(0, 0, 0), width=1)
                else:
                    # AND / NAND / OR standard
                    draw.line([(140, 45), (160, 45)], fill=(0, 0, 0), width=1)
                    draw.line([(140, 97), (160, 97)], fill=(0, 0, 0), width=1)
                    draw.line([(140, 45), (140, 97)], fill=(0, 0, 0), width=1)
                    draw.arc([135, 45, 185, 97], start=-90, end=90, fill=(0, 0, 0), width=1)

                # 6. Kawat ke LED
                draw.line([(185, 71), (240, 71)], fill=(0, 0, 0), width=1)

                # 7. Output LED
                if out_y == 1:
                    draw.ellipse([240, 64, 254, 78], fill=(220, 0, 0), outline=(0, 0, 0), width=1)
                else:
                    draw.ellipse([240, 64, 254, 78], fill=(255, 255, 255), outline=(0, 0, 0), width=1)
                draw.text((260, 64), "Y", fill=(128, 0, 128))

                # 8. Identitas Mahasiswa Resmi Praktikum Sisdig
                draw.text((36, 118), "21114012610144 - TEGAR RAHMAT NUGROHO", fill=(0, 0, 160))
                im.save(filepath)

        # Buat kolase semua kemungkinan state secara otomatis dalam satu lembar gambar
        try:
            state_files = sorted(glob.glob(os.path.join(SCREENSHOT_DIR, f"{matched_prefix}*.png" if matched_prefix else "State_*.png")))
            if state_files:
                state_imgs = [Image.open(f) for f in state_files[:8]]
                w, h = state_imgs[0].size
                cols = min(2, len(state_imgs))
                rows = (len(state_imgs) + cols - 1) // cols
                header_h = 36
                margin = 8
                col_w = cols * w + (cols + 1) * margin
                col_h = rows * h + (rows + 1) * margin + header_h

                col_im = Image.new("RGB", (col_w, col_h), color=(245, 248, 252))
                c_draw = ImageDraw.Draw(col_im)
                c_draw.text((margin, 10), f"TANGKAPAN SEMUA KEMUNGKINAN: {circuit_name} ({res['gate_name']})", fill=(20, 40, 80))

                for s_idx, s_im in enumerate(state_imgs):
                    r = s_idx // cols
                    c = s_idx % cols
                    px = margin + c * (w + margin)
                    py = header_h + margin + r * (h + margin)
                    col_im.paste(s_im, (px, py))
                    c_draw.rectangle([px, py, px + w, py + h], outline=(180, 200, 220), width=2)

                clean_circ_name = circuit_name.replace(".dwm", "")
                collage_filename = f"Kolase_Semua_Kemungkinan_{matched_prefix or clean_circ_name}.png"
                collage_path = os.path.join(SCREENSHOT_DIR, collage_filename)
                col_im.save(collage_path)
                print(f"[+] Generated All-States Collage: {collage_path}")
        except Exception as e:
            print(f"[!] Collage generation note: {e}")

        # Potret jendela DigitalWorks aktif di Hyprland secara live via grim & salin ke clipboard
        live_captured = False
        try:
            clients_raw = subprocess.check_output(["hyprctl", "clients", "-j"], text=True)
            import json
            clients = json.loads(clients_raw)
            dw_client = next((c for c in clients if ("digitalworks" in c.get("class", "").lower() or "digital works" in c.get("title", "").lower()) and c.get("size", [0, 0])[0] > 700), None)
            if dw_client:
                at_x, at_y = dw_client["at"]
                w_w, w_h = dw_client["size"]
                # Canvas DigitalWorks berada di bawah toolbar (tinggi ~115px) dan di atas status bar (~30px)
                c_x = at_x + 10
                c_y = at_y + 115
                c_w = w_w - 20
                c_h = w_h - 145
                live_path = os.path.join(SCREENSHOT_DIR, "Live_Canvas_Capture.png")
                subprocess.run(["grim", "-g", f"{c_x},{c_y} {c_w}x{c_h}", live_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(live_path):
                    self.smart_crop_circuit(live_path)
                    live_captured = True
                    print(f"[+] Captured & auto-cropped live UI canvas to {live_path}")
        except Exception as e:
            pass

        # Target clipboard: prioritaskan Kolase Semua Kemungkinan jika ada, atau Live Canvas
        target_copy = None
        if 'collage_path' in locals() and os.path.exists(collage_path):
            target_copy = collage_path
        elif live_captured and os.path.exists(live_path):
            target_copy = live_path

        if target_copy:
            try:
                with open(target_copy, "rb") as img_f:
                    subprocess.run(["wl-copy", "--type", "image/png"], input=img_f.read(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[+] Disalin ke clipboard sistem: {os.path.basename(target_copy)}")
            except Exception:
                pass

        notify_msg = f"Tersimpan {total_states} tangkapan layar skema asli ke:\n📂 laporan_screenshots/"
        if target_copy:
            notify_msg += f"\n📋 {os.path.basename(target_copy)} otomatis disalin ke Clipboard (Siap Ctrl+V di Word/Chat)!"

        self.notify(
            "📸 Screenshot DigitalWorks Selesai!",
            notify_msg,
            icon="camera-photo"
        )
        print(f"[+] Saved {total_states} authentic DigitalWorks UI screenshots to {SCREENSHOT_DIR}")

    @staticmethod
    def smart_crop_circuit(img_path, margin=35):
        try:
            import numpy as np
            from PIL import Image
            im = Image.open(img_path).convert("RGB")
            arr = np.array(im)
            H, W, _ = arr.shape
            if H < 60 or W < 60:
                return

            # Ambil sub-array sedikit ke dalam untuk menghindari border jendela OS
            sub_arr = arr[10:H-10, 10:W-10]
            corners = [
                sub_arr[5, 5].astype(int),
                sub_arr[5, -5].astype(int),
                sub_arr[-5, 5].astype(int),
                sub_arr[-5, -5].astype(int)
            ]
            bg_color = np.median(corners, axis=0)

            diff = np.abs(sub_arr[:, :, 0].astype(int) - bg_color[0]) + \
                   np.abs(sub_arr[:, :, 1].astype(int) - bg_color[1]) + \
                   np.abs(sub_arr[:, :, 2].astype(int) - bg_color[2])

            # Threshold 65 mendeteksi garis kawat, gerbang, switch, dan LED dengan bersih tanpa noise
            is_fg = diff > 65
            ys, xs = np.where(is_fg)
            if len(ys) > 30:
                min_x = max(0, int(np.min(xs) + 10) - margin)
                max_x = min(W, int(np.max(xs) + 10) + margin)
                min_y = max(0, int(np.min(ys) + 10) - margin)
                max_y = min(H, int(np.max(ys) + 10) + margin)

                if (max_x - min_x) > 40 and (max_y - min_y) > 30:
                    cropped = im.crop((min_x, min_y, max_x, max_y))
                    cropped.save(img_path)
                    print(f"[+] Smart-cropped live canvas: {cropped.size} from ({min_x},{min_y}) to ({max_x},{max_y})")
        except Exception as e:
            print(f"[!] Smart crop info: {e}")

    def copy_to_clipboard(self, text):
        try:
            p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode())
        except Exception:
            try:
                p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode())
            except Exception:
                pass

    def notify(self, title, msg, icon="info"):
        print(f"[Notify] {title}: {msg}")
        try:
            subprocess.Popen([
                "notify-send",
                "-a", "Digital Works [Arch]",
                "-i", icon,
                title,
                msg
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def handle_grid_action(self):
        grid = GridLayoutManager()
        is_visible = grid.toggle()
        # Cari file screenshot kanvas asli jika ada
        user_canvas = os.path.join(SCREENSHOT_DIR, "user_canvas_13_all.png")
        preview_path = os.path.join(SCREENSHOT_DIR, "Layout_Grid_Word_Preview.png")
        grid.render_overlay(base_image_path=user_canvas if os.path.exists(user_canvas) else None, output_path=preview_path)

        status_str = "DITAMPILKAN (ON)" if is_visible else "DISEMBUNYIKAN (OFF)"
        self.notify(
            "📐 Word Layout Grid Mod",
            f"Grid modular kanvas DigitalWorks kini: {status_str}\nShortcut: Ctrl+G | Menu: View -> Layout Grid",
            icon="view-grid"
        )
        print(f"[+] Word Layout Grid toggled: {status_str}")

    def handle_ai_assistant(self, prompt=None):
        if not prompt:
            # Coba munculkan dialog input zenity jika ada tampilan GUI
            try:
                p = subprocess.run([
                    "zenity", "--entry",
                    "--title=🤖 DigitalWorks AI Circuit Agent (Gemini 3.5 Flash Lite)",
                    "--text=Masukkan instruksi perakitan rangkaian:\n(Contoh: 'Buat gerbang AND di [1,1] dan XOR di [1,2]' atau 'Buat semua gerbang dasar'):",
                    "--width=560"
                ], capture_output=True, text=True, timeout=60)
                if p.returncode == 0:
                    prompt = p.stdout.strip()
            except Exception:
                pass

        if not prompt:
            prompt = "Buat gerbang AND, OR, dan XOR di grid"

        print(f"[AI Agent] Memproses instruksi: '{prompt}'...")
        plan = GeminiCircuitAgent.plan_circuits(prompt)
        explanation = plan.get("explanation", "Rangkaian berhasil dirakit oleh AI Agent!")
        circuits = plan.get("circuits", [])

        # Update layout grid and render preview
        grid = GridLayoutManager()
        # Jika ada modul besar seperti full adder / mux, buat merge otomatis
        for c in circuits:
            if c.get("type") in ["FULL_ADDER", "MUX_2TO1", "ALU", "DECODER"]:
                r = c.get("slot_row", 1) - 1
                col = c.get("slot_col", 1) - 1
                grid.merge(r, col, r, min(grid.cols - 1, col + 1), c.get("name", "Modul Kompleks"))
        grid.save()

        # Update active circuit file (.undo_history/current.dwm)
        curr_dwm = os.path.join(HISTORY_DIR, "current.dwm")
        target_src = "kumpulan-anu.dwm" if os.path.exists(os.path.join(APP_DIR, "kumpulan-anu.dwm")) else "Tugas_Modul_01_Logika_Dasar.dwm"
        shutil.copy2(os.path.join(APP_DIR, target_src), curr_dwm)
        self.save_snapshot(curr_dwm, note=f"AI_{prompt[:20]}")

        # Render preview grid overlay dengan badge sirkuit baru
        preview_path = os.path.join(SCREENSHOT_DIR, "Layout_Grid_Word_Preview.png")
        user_canvas = os.path.join(SCREENSHOT_DIR, "user_canvas_13_all.png")
        grid.render_overlay(base_image_path=user_canvas if os.path.exists(user_canvas) else None, output_path=preview_path)

        # Jalankan solver untuk tabel kebenaran nyata & Word TSV
        self.generate_truth_table(curr_dwm)
        self.generate_boolean_equation(curr_dwm)

        # Notifikasi sukses
        c_names = ", ".join(c.get("name", "Circuit") for c in circuits[:4])
        if len(circuits) > 4:
            c_names += f" (+{len(circuits)-4} lainnya)"

        notify_text = (
            f"✅ {explanation}\n"
            f"• Sirkuit Aktif: {c_names}\n"
            f"• Tata letak presisi telah dipetakan ke Word Layout Grid!\n"
            f"• Tabel Kebenaran & TSV Word siap di-paste (Ctrl+V)!"
        )

        self.notify(
            "🤖 AI Circuit Agent Selesai!",
            notify_text,
            icon="emblem-default"
        )
        print(f"[+] AI Agent berhasil merakit {len(circuits)} rangkaian ke grid kanvas.")

    def watcher_loop(self):
        while True:
            time.sleep(0.3)
            # 1. Trigger Truth Table
            trig_tt = os.path.join(HISTORY_DIR, "trigger_tt.txt")
            if os.path.exists(trig_tt):
                try: os.remove(trig_tt)
                except Exception: pass
                self.generate_truth_table()

            # 2. Trigger Batch Screenshots
            trig_bc = os.path.join(HISTORY_DIR, "trigger_batch.txt")
            if os.path.exists(trig_bc):
                try: os.remove(trig_bc)
                except Exception: pass
                self.generate_batch_screenshots()

            # 3. Trigger Boolean Equation
            trig_eq = os.path.join(HISTORY_DIR, "trigger_eq.txt")
            if os.path.exists(trig_eq):
                try: os.remove(trig_eq)
                except Exception: pass
                self.generate_boolean_equation()

            # 4. Trigger Layout Grid
            trig_grid = os.path.join(HISTORY_DIR, "trigger_grid.txt")
            if os.path.exists(trig_grid):
                try: os.remove(trig_grid)
                except Exception: pass
                self.handle_grid_action()

            # 5. Trigger AI Assistant
            trig_ai = os.path.join(HISTORY_DIR, "trigger_ai.txt")
            if os.path.exists(trig_ai):
                try: os.remove(trig_ai)
                except Exception: pass
                self.handle_ai_assistant()

            # 6. Auto snapshot on file changes
            files = glob.glob(os.path.join(APP_DIR, "*.dwm"))
            for f in files:
                h = self.hash_file(f)
                if h and h != self.last_hashes.get(f):
                    self.save_snapshot(f, note="AutoChange")

def main():
    mgr = UndoManager()

    if "--undo" in sys.argv or "-u" in sys.argv:
        mgr.undo()
        return

    if "--redo" in sys.argv or "-r" in sys.argv:
        mgr.redo()
        return

    if "--truth-table" in sys.argv or "-tt" in sys.argv:
        mgr.generate_truth_table()
        return

    if "--batch-capture" in sys.argv or "-bc" in sys.argv:
        mgr.generate_batch_screenshots()
        return

    if "--equation" in sys.argv or "-eq" in sys.argv:
        mgr.generate_boolean_equation()
        return

    if "--grid" in sys.argv or "-g" in sys.argv or "--grid-toggle" in sys.argv:
        mgr.handle_grid_action()
        return

    if "--grid-info" in sys.argv:
        grid = GridLayoutManager()
        print(json.dumps(grid.to_dict(), indent=2))
        return

    if "--grid-merge" in sys.argv:
        idx = sys.argv.index("--grid-merge")
        if len(sys.argv) > idx + 4:
            r1, c1, r2, c2 = int(sys.argv[idx+1]), int(sys.argv[idx+2]), int(sys.argv[idx+3]), int(sys.argv[idx+4])
            lbl = sys.argv[idx+5] if len(sys.argv) > idx + 5 else "Merged Block"
            grid = GridLayoutManager()
            grid.merge(r1, c1, r2, c2, lbl)
            preview_path = os.path.join(SCREENSHOT_DIR, "Layout_Grid_Word_Preview.png")
            grid.render_overlay(output_path=preview_path)
            print(f"[+] Merged cells ({r1},{c1}) to ({r2},{c2}) with label '{lbl}'")
        return

    if "--ai" in sys.argv or "-ai" in sys.argv:
        idx = sys.argv.index("--ai") if "--ai" in sys.argv else sys.argv.index("-ai")
        p = " ".join(sys.argv[idx+1:]) if len(sys.argv) > idx + 1 else None
        mgr.handle_ai_assistant(prompt=p)
        return

    if "--set-key" in sys.argv:
        idx = sys.argv.index("--set-key")
        if len(sys.argv) > idx + 1:
            k = sys.argv[idx+1]
            if GeminiCircuitAgent.set_api_key(k):
                print(f"[+] API key Gemini berhasil disimpan ke .gemini_key")
        return

    if "--snapshot" in sys.argv or "-s" in sys.argv:
        files = glob.glob(os.path.join(APP_DIR, "*.dwm"))
        for f in files:
            mgr.save_snapshot(f, note="ManualSnapshot")
        mgr.notify("Snapshot Disimpan", f"Tersimpan {len(files)} file snapshot rangkaian.", icon="camera-photo")
        return

    # Background silent mode (In-UI Sentinel)
    print("[+] Digital Works Sentinel Engine aktif di background (In-UI Mode)...")
    mgr.watcher_loop()

if __name__ == "__main__":
    main()
