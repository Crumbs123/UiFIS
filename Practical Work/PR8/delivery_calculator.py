import tkinter as tk
from tkinter import ttk, messagebox
import math
import datetime
import json
import urllib.request
import urllib.parse


# ─── Геокодирование через Nominatim (OpenStreetMap) ───────────────────────────

def geocode(address: str):
    """Возвращает (lat, lon) или None."""
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": address,
        "format": "json",
        "limit": 1
    })
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DeliveryCalculator/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def haversine(lat1, lon1, lat2, lon2):
    """Расстояние между двумя точками на земле в километрах."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# ─── Типы транспорта ──────────────────────────────────────────────────────────

TRANSPORT = {
    "Автомобиль (40 руб./км)":  {"rate": 40,  "speed": 80,  "short": "Авто"},
    "Грузовик (60 руб./км)":    {"rate": 60,  "speed": 60,  "short": "Груз"},
    "Мотоцикл (25 руб./км)":   {"rate": 25,  "speed": 90,  "short": "Мото"},
    "Велосипед (10 руб./км)":  {"rate": 10,  "speed": 20,  "short": "Вело"},
}


# ─── Главное окно ─────────────────────────────────────────────────────────────

class DeliveryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор доставки")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        self._build_ui()
        self._set_status("Готов", "green")

    # ── Построение интерфейса ─────────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # ── Параметры доставки ────────────────────────────────────────────────
        frame_params = ttk.LabelFrame(self, text="Параметры доставки")
        frame_params.grid(row=0, column=0, sticky="ew", **pad)

        ttk.Label(frame_params, text="Пункт отправления:").grid(row=0, column=0, sticky="w", padx=6, pady=3)
        self.entry_from = ttk.Entry(frame_params, width=45)
        self.entry_from.grid(row=0, column=1, padx=4, pady=3)
        self.entry_from.insert(0, "Москва, Красная площадь")

        btn_swap = ttk.Button(frame_params, text="⇌", width=3, command=self._swap_points)
        btn_swap.grid(row=0, column=2, rowspan=2, padx=4)

        ttk.Label(frame_params, text="Пункт назначения:").grid(row=1, column=0, sticky="w", padx=6, pady=3)
        self.entry_to = ttk.Entry(frame_params, width=45)
        self.entry_to.grid(row=1, column=1, padx=4, pady=3)
        self.entry_to.insert(0, "Санкт-Петербург, Невский проспект")

        ttk.Label(frame_params, text="Тип транспорта:").grid(row=2, column=0, sticky="w", padx=6, pady=3)
        self.combo_transport = ttk.Combobox(
            frame_params, values=list(TRANSPORT.keys()), state="readonly", width=28
        )
        self.combo_transport.grid(row=2, column=1, sticky="w", padx=4, pady=3)
        self.combo_transport.current(0)

        btn_calc = ttk.Button(frame_params, text="Рассчитать", command=self._calculate)
        btn_calc.grid(row=2, column=1, sticky="e", padx=4)

        btn_clear = ttk.Button(frame_params, text="Очистить", command=self._clear)
        btn_clear.grid(row=2, column=2, padx=4)

        # ── Строка статуса ────────────────────────────────────────────────────
        self.lbl_status = tk.Label(self, text="", bg="#f0f0f0", fg="green", font=("Segoe UI", 9, "bold"))
        self.lbl_status.grid(row=1, column=0, sticky="w", padx=14)

        # ── Результат ─────────────────────────────────────────────────────────
        frame_result = ttk.LabelFrame(self, text="Результат расчёта")
        frame_result.grid(row=2, column=0, sticky="ew", **pad)

        self.txt_result = tk.Text(frame_result, width=62, height=8, state="disabled",
                                   font=("Consolas", 9), bg="#ffffff")
        sb1 = ttk.Scrollbar(frame_result, command=self.txt_result.yview)
        self.txt_result.configure(yscrollcommand=sb1.set)
        self.txt_result.grid(row=0, column=0, padx=4, pady=4)
        sb1.grid(row=0, column=1, sticky="ns")

        # ── История ───────────────────────────────────────────────────────────
        frame_hist = ttk.LabelFrame(self, text="История расчётов")
        frame_hist.grid(row=3, column=0, sticky="ew", **pad)

        cols = ("Time", "From", "To", "Vehicle", "Cost")
        self.tree = ttk.Treeview(frame_hist, columns=cols, show="headings", height=5)
        for col, w in zip(cols, (65, 160, 160, 70, 90)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        sb2 = ttk.Scrollbar(frame_hist, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb2.set)
        self.tree.grid(row=0, column=0, padx=4, pady=4)
        sb2.grid(row=0, column=1, sticky="ns")

    # ── Логика ────────────────────────────────────────────────────────────────

    def _set_status(self, text, color="green"):
        self.lbl_status.configure(text=text, fg=color)

    def _swap_points(self):
        a, b = self.entry_from.get(), self.entry_to.get()
        self.entry_from.delete(0, tk.END); self.entry_from.insert(0, b)
        self.entry_to.delete(0, tk.END);   self.entry_to.insert(0, a)

    def _clear(self):
        self.entry_from.delete(0, tk.END)
        self.entry_to.delete(0, tk.END)
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert("1.0", "Результат расчёта")
        self.txt_result.configure(state="disabled")
        self._set_status("Готов", "green")

    def _calculate(self):
        addr_from = self.entry_from.get().strip()
        addr_to   = self.entry_to.get().strip()

        if not addr_from or not addr_to:
            messagebox.showerror("Ошибка", "Заполните оба пункта!")
            return

        self._set_status("Геокодирование...", "orange")
        self.update_idletasks()

        coords_from = geocode(addr_from)
        coords_to   = geocode(addr_to)

        if coords_from is None:
            messagebox.showerror("Ошибка", f"Не удалось найти адрес:\n{addr_from}")
            self._set_status("Ошибка геокодирования", "red")
            return
        if coords_to is None:
            messagebox.showerror("Ошибка", f"Не удалось найти адрес:\n{addr_to}")
            self._set_status("Ошибка геокодирования", "red")
            return

        transport_key = self.combo_transport.get()
        t = TRANSPORT[transport_key]
        distance = haversine(*coords_from, *coords_to)
        cost = distance * t["rate"]
        hours = distance / t["speed"]
        h = int(hours)
        m = int((hours - h) * 60)

        now = datetime.datetime.now()
        result = (
            f"Откуда: {addr_from}\n"
            f"Куда: {addr_to}\n"
            f"Транспорт: {transport_key.split('(')[0].strip()}\n"
            f"Расстояние: {distance:.1f} км\n"
            f"Время: {h} ч {m:02d} мин\n"
            f"Стоимость: {cost:.2f} руб.\n"
            f"Рассчитано: {now.strftime('%d.%m.%Y %H:%M:%S')}"
        )

        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert("1.0", result)
        self.txt_result.configure(state="disabled")
        self._set_status("Расчёт выполнен успешно", "green")

        # история
        self.tree.insert(
            "", 0,
            values=(
                now.strftime("%H:%M:%S"),
                addr_from[:20] + ("…" if len(addr_from) > 20 else ""),
                addr_to[:20]   + ("…" if len(addr_to)   > 20 else ""),
                t["short"],
                f"{cost:.0f} руб."
            )
        )
        # выделить последнюю запись
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.see(children[0])


if __name__ == "__main__":
    app = DeliveryApp()
    app.mainloop()
