import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime
import os

# --- PDF export ---
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def calc_cp(usl, lsl, sigma):
    return (usl - lsl) / (6 * sigma)

def calc_cpk(usl, lsl, mu, sigma):
    return min((usl - mu) / (3 * sigma), (mu - lsl) / (3 * sigma))

def get_status(cpk):
    if cpk >= 1.33:
        return "Статус: Отлично", "#00aa00"
    elif cpk >= 1.0:
        return "Статус: Удовлетворительно", "#ffa500"
    elif cpk >= 0.67:
        return "Статус: Неудовлетворительно", "#ff6600"
    else:
        return "Статус: Критично", "#cc0000"


# ─────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────

class QualityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Анализ индексов качества процесса")
        self.geometry("1000x620")
        self.resizable(True, True)
        self.configure(bg="#e8eaf6")

        self.history = []          # list of dicts
        self.current_result = None # last calculated result

        self._build_ui()

    # ── UI ──────────────────────────────────
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.tab_calc  = ttk.Frame(nb)
        self.tab_graph = ttk.Frame(nb)
        self.tab_hist  = ttk.Frame(nb)

        nb.add(self.tab_calc,  text="  Калькулятор  ")
        nb.add(self.tab_graph, text="  График распределения  ")
        nb.add(self.tab_hist,  text="  История расчётов  ")

        self._build_calc_tab()
        self._build_graph_tab()
        self._build_hist_tab()

    # ── TAB 1: Calculator ───────────────────
    def _build_calc_tab(self):
        f = self.tab_calc

        # Left – inputs
        left = ttk.LabelFrame(f, text="Введите параметры процесса", padding=12)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        labels = [
            ("Верхняя граница допуска (USL):", "usl"),
            ("Нижняя граница допуска (LSL):",  "lsl"),
            ("Среднее процесса (μ):",           "mu"),
            ("Стандартное отклонение (σ):",     "sigma"),
        ]
        self.entries = {}
        defaults = {"usl": "10.5", "lsl": "9.5", "mu": "10.2", "sigma": "0.1"}
        for i, (lbl, key) in enumerate(labels):
            ttk.Label(left, text=lbl).grid(row=i, column=0, sticky="w", pady=4)
            e = ttk.Entry(left, width=14)
            e.insert(0, defaults[key])
            e.grid(row=i, column=1, padx=8, pady=4)
            self.entries[key] = e

        # Buttons
        btn_frame = ttk.Frame(left)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="Рассчитать индексы качества",
                   command=self._calculate).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Сохранить в историю",
                   command=self._save_to_history).pack(side=tk.LEFT, padx=4)

        btn_frame2 = ttk.Frame(left)
        btn_frame2.grid(row=5, column=0, columnspan=2, pady=4)
        ttk.Button(btn_frame2, text="Экспорт в Excel",
                   command=self._export_current_excel).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame2, text="Экспорт в PDF",
                   command=self._export_pdf).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame2, text="Загрузить из Excel",
                   command=self._load_excel).pack(side=tk.LEFT, padx=4)

        # Right – results
        right = ttk.LabelFrame(f, text="Результаты анализа", padding=12)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.lbl_cp  = ttk.Label(right, text="Cp:  —", font=("Arial", 14, "bold"))
        self.lbl_cp.pack(anchor="w", pady=6)
        self.lbl_cpk = ttk.Label(right, text="Cpk: —", font=("Arial", 14, "bold"))
        self.lbl_cpk.pack(anchor="w", pady=6)
        self.lbl_status = tk.Label(right, text="Статус: —",
                                   font=("Arial", 12, "bold"), bg="#e8eaf6")
        self.lbl_status.pack(anchor="w", pady=6)

        sep = ttk.Separator(right, orient="horizontal")
        sep.pack(fill=tk.X, pady=8)

        interp_text = (
            "Интерпретация:\n"
            "Cp ≥ 1.33, Cpk ≥ 1.33 → Отлично\n"
            "Cp ≥ 1.0, Cpk ≥ 1.0 → Удовлетворительно\n"
            "Cp ≥ 0.67, Cpk ≥ 0.67 → Неудовлетворительно\n"
            "Cp < 0.67, Cpk < 0.67 → Критично"
        )
        ttk.Label(right, text=interp_text, justify=tk.LEFT,
                  font=("Arial", 9)).pack(anchor="w")

    # ── TAB 2: Graph ────────────────────────
    def _build_graph_tab(self):
        f = self.tab_graph
        ttk.Button(f, text="Обновить график", command=self._draw_graph).pack(pady=6)
        self.fig  = Figure(figsize=(8, 4.5), dpi=95)
        self.ax   = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=f)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    # ── TAB 3: History ──────────────────────
    def _build_hist_tab(self):
        f = self.tab_hist

        btn_bar = ttk.Frame(f)
        btn_bar.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(btn_bar, text="Обновить историю",
                   command=self._refresh_history).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="Очистить историю",
                   command=self._clear_history).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="Загрузить выделенное",
                   command=self._load_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="Экспорт истории в Excel",
                   command=self._export_history_excel).pack(side=tk.LEFT, padx=4)

        cols = ("Дата/время", "USL", "LSL", "Среднее", "Сигма", "Cp", "Cpk", "Статус")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        sb = ttk.Scrollbar(f, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=sb.set)
        sb.pack(fill=tk.X, padx=8)

    # ── Logic ───────────────────────────────
    def _get_params(self):
        try:
            usl   = float(self.entries["usl"].get())
            lsl   = float(self.entries["lsl"].get())
            mu    = float(self.entries["mu"].get())
            sigma = float(self.entries["sigma"].get())
            if sigma <= 0:
                raise ValueError("σ должно быть > 0")
            if usl <= lsl:
                raise ValueError("USL должно быть > LSL")
            return usl, lsl, mu, sigma
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return None

    def _calculate(self):
        p = self._get_params()
        if p is None:
            return
        usl, lsl, mu, sigma = p
        cp  = calc_cp(usl, lsl, sigma)
        cpk = calc_cpk(usl, lsl, mu, sigma)
        status_text, color = get_status(cpk)

        self.lbl_cp.config(text=f"Cp:  {cp:.3f}")
        self.lbl_cpk.config(text=f"Cpk: {cpk:.3f}")
        self.lbl_status.config(text=status_text, fg=color)

        self.current_result = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "USL": usl, "LSL": lsl, "Среднее": mu, "Сигма": sigma,
            "Cp": round(cp, 4), "Cpk": round(cpk, 4),
            "Статус": status_text.replace("Статус: ", "")
        }
        self._draw_graph()

    def _save_to_history(self):
        if self.current_result is None:
            messagebox.showinfo("Нет данных", "Сначала выполните расчёт.")
            return
        self.history.append(self.current_result.copy())
        self._refresh_history()
        messagebox.showinfo("Сохранено", "Результат добавлен в историю.")

    def _draw_graph(self):
        if self.current_result is None:
            messagebox.showinfo("Нет данных", "Сначала выполните расчёт.")
            return
        r = self.current_result
        usl, lsl, mu, sigma = r["USL"], r["LSL"], r["Среднее"], r["Сигма"]
        cp, cpk = r["Cp"], r["Cpk"]

        self.ax.clear()
        x_min = min(lsl, mu) - 4 * sigma
        x_max = max(usl, mu) + 4 * sigma
        x = np.linspace(x_min, x_max, 400)
        y = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

        # fill in tolerance
        mask_in  = (x >= lsl) & (x <= usl)
        mask_out_l = x < lsl
        mask_out_r = x > usl
        self.ax.fill_between(x, y, where=mask_in,  color="#90ee90", alpha=0.5, label="В допуске")
        self.ax.fill_between(x, y, where=mask_out_l, color="#ffaaaa", alpha=0.6, label="Вне допуска")
        self.ax.fill_between(x, y, where=mask_out_r, color="#ffaaaa", alpha=0.6)

        self.ax.plot(x, y, "b-", linewidth=2, label="Нормальное распределение")
        self.ax.axvline(lsl, color="red",   linestyle="--", label=f"LSL = {lsl}")
        self.ax.axvline(usl, color="red",   linestyle="--", label=f"USL = {usl}")
        self.ax.axvline(mu,  color="green", linestyle="-",  label=f"Среднее = {mu}")

        self.ax.set_title(f"Нормальное распределение процесса\nCp = {cp:.3f}, Cpk = {cpk:.3f}",
                          fontsize=11)
        self.ax.set_xlabel("Значение")
        self.ax.set_ylabel("Плотность вероятности")
        self.ax.legend(fontsize=8, loc="upper right")
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()

    def _refresh_history(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for h in self.history:
            self.tree.insert("", tk.END, values=(
                h["datetime"], h["USL"], h["LSL"],
                h["Среднее"], h["Сигма"], h["Cp"], h["Cpk"], h["Статус"]
            ))

    def _clear_history(self):
        if messagebox.askyesno("Очистить", "Очистить всю историю расчётов?"):
            self.history.clear()
            self._refresh_history()

    def _load_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Нет выбора", "Выберите строку в таблице.")
            return
        idx = self.tree.index(sel[0])
        h = self.history[idx]
        for key, entry_key in [("USL","usl"),("LSL","lsl"),("Среднее","mu"),("Сигма","sigma")]:
            self.entries[entry_key].delete(0, tk.END)
            self.entries[entry_key].insert(0, str(h[key]))
        self._calculate()

    # ── Export ──────────────────────────────
    def _export_current_excel(self):
        if self.current_result is None:
            messagebox.showinfo("Нет данных", "Сначала выполните расчёт.")
            return
        r = self.current_result
        data = {
            "Параметр": ["Верхняя граница допуска (USL)", "Нижняя граница допуска (LSL)",
                         "Среднее процесса (μ)", "Стандартное отклонение (σ)",
                         "Индекс Cp", "Индекс Cpk", "Статус", "Дата расчёта"],
            "Значение": [r["USL"], r["LSL"], r["Среднее"], r["Сигма"],
                         r["Cp"], r["Cpk"], r["Статус"], r["datetime"]]
        }
        df = pd.DataFrame(data)
        path = f"calc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(path, index=False)
        messagebox.showinfo("Экспорт", f"Сохранено: {path}")

    def _export_history_excel(self):
        if not self.history:
            messagebox.showinfo("Нет данных", "История пуста.")
            return
        df = pd.DataFrame(self.history)
        path = f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(path, index=False)
        messagebox.showinfo("Экспорт", f"Сохранено: {path}")

    def _export_pdf(self):
        if self.current_result is None:
            messagebox.showinfo("Нет данных", "Сначала выполните расчёт.")
            return
        if not PDF_AVAILABLE:
            messagebox.showerror("Ошибка", "Установите reportlab: pip install reportlab")
            return
        r = self.current_result
        path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("<b>ОТЧЁТ ПО АНАЛИЗУ КАЧЕСТВА ПРОЦЕССА</b>", styles["Title"]))
        elements.append(Spacer(1, 0.4*cm))
        elements.append(Paragraph(f"Дата отчёта: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", styles["Normal"]))
        elements.append(Spacer(1, 0.4*cm))

        elements.append(Paragraph("<b>1. Параметры процесса:</b>", styles["Heading2"]))
        param_data = [["Параметр", "Значение"],
                      ["Верхняя граница (USL)", r["USL"]],
                      ["Нижняя граница (LSL)",  r["LSL"]],
                      ["Среднее (μ)",            r["Среднее"]],
                      ["Ст. отклонение (σ)",     r["Сигма"]]]
        t = Table(param_data, colWidths=[9*cm, 7*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.4*cm))

        elements.append(Paragraph("<b>2. Результаты анализа:</b>", styles["Heading2"]))
        res_data = [["Показатель", "Значение"],
                    ["Индекс Cp",  r["Cp"]],
                    ["Индекс Cpk", r["Cpk"]],
                    ["Статус",     r["Статус"]]]
        t2 = Table(res_data, colWidths=[9*cm, 7*cm])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 0.4*cm))

        elements.append(Paragraph("<b>3. Интерпретация:</b>", styles["Heading2"]))
        interp = (
            "Cp ≥ 1.33, Cpk ≥ 1.33 — Отлично  |  "
            "Cp ≥ 1.0, Cpk ≥ 1.0 — Удовлетворительно  |  "
            "Cp ≥ 0.67, Cpk ≥ 0.67 — Неудовлетворительно  |  "
            "Cp < 0.67, Cpk < 0.67 — Критично"
        )
        elements.append(Paragraph(interp, styles["Normal"]))

        doc.build(elements)
        messagebox.showinfo("Экспорт", f"PDF сохранён: {path}")

    def _load_excel(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return
        try:
            df = pd.read_excel(path)
            # Expect columns: USL, LSL, Среднее/mu, Сигма/sigma
            col_map = {}
            for col in df.columns:
                cl = col.strip().lower()
                if "usl" in cl:         col_map["usl"]   = col
                elif "lsl" in cl:       col_map["lsl"]   = col
                elif "средн" in cl or "mu" in cl: col_map["mu"] = col
                elif "сигм" in cl or "sigma" in cl or "откл" in cl: col_map["sigma"] = col
            if len(col_map) < 4:
                messagebox.showerror("Ошибка", "Файл должен содержать столбцы: USL, LSL, Среднее, Сигма")
                return
            row = df.iloc[0]
            for key, col in col_map.items():
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, str(row[col]))
            self._calculate()
        except Exception as e:
            messagebox.showerror("Ошибка чтения", str(e))


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QualityApp()
    app.mainloop()
