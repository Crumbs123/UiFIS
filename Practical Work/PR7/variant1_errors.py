import tkinter as tk
from tkinter import ttk, messagebox

# ─────────────────────────────────────────────
#  Формулы:
#  P_ош  = N_ош / N_общ
#  K_испр = N_испр / N_ош
# ─────────────────────────────────────────────

def calculate():
    try:
        n_total   = float(entry_total.get())
        n_errors  = float(entry_errors.get())
        n_fixed   = float(entry_fixed.get())
        n_corrupt = float(entry_corrupt.get())
    except ValueError:
        messagebox.showerror("Ошибка ввода", "Пожалуйста, введите числовые значения во все поля.")
        return

    if n_total <= 0:
        messagebox.showerror("Ошибка", "Общее число записей должно быть больше 0.")
        return
    if n_errors <= 0:
        messagebox.showerror("Ошибка", "Число ошибок должно быть больше 0.")
        return

    p_error = n_errors / n_total
    k_fix   = n_fixed / n_errors

    # n_detected = n_errors - n_fixed - n_corrupt  (только обнаружены, не исправлены)
    n_detected = n_errors - n_fixed - n_corrupt

    result_text = (
        f"──────────────────────────────\n"
        f"  Результаты расчёта:\n"
        f"──────────────────────────────\n"
        f"  Вероятность ошибки\n"
        f"  P_ош = {n_errors:.0f} / {n_total:.0f} = {p_error:.6f}\n\n"
        f"  Коэффициент исправления\n"
        f"  K_испр = {n_fixed:.0f} / {n_errors:.0f} = {k_fix:.4f}\n"
        f"──────────────────────────────\n"
        f"  Дополнительно:\n"
        f"  • Исправлено:           {n_fixed:.0f}\n"
        f"  • Искажено (не верно):  {n_corrupt:.0f}\n"
        f"  • Только обнаружено:    {n_detected:.0f}\n"
        f"──────────────────────────────"
    )
    result_var.set(result_text)


def fill_variant1():
    """Заполняет поля данными из Варианта 1."""
    entry_total.delete(0, tk.END);   entry_total.insert(0, "120000")
    entry_errors.delete(0, tk.END);  entry_errors.insert(0, "240")
    entry_fixed.delete(0, tk.END);   entry_fixed.insert(0, "180")
    entry_corrupt.delete(0, tk.END); entry_corrupt.insert(0, "12")


def clear_all():
    for e in (entry_total, entry_errors, entry_fixed, entry_corrupt):
        e.delete(0, tk.END)
    result_var.set("")


# ─── GUI ────────────────────────────────────
root = tk.Tk()
root.title("Анализ ошибок в информационной системе")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

PAD = {"padx": 10, "pady": 5}

# Заголовок
title_lbl = tk.Label(root, text="Контроль ошибок в ИС", font=("Arial", 14, "bold"),
                     fg="#2c3e50")
title_lbl.grid(row=0, column=0, columnspan=2, pady=(14, 4))

subtitle = tk.Label(root, text="Вариант 1", font=("Arial", 10, "italic"), fg="#7f8c8d")
subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 10))

# Поля ввода
fields = [
    ("Общее число записей (N):",         "entry_total"),
    ("Число обнаруженных ошибок (N_ош):", "entry_errors"),
    ("Исправлено правильно (N_испр):",    "entry_fixed"),
    ("Искажено (неверно исправлено):",    "entry_corrupt"),
]

entries = {}
for i, (label_text, name) in enumerate(fields, start=2):
    tk.Label(root, text=label_text, anchor="w", font=("Arial", 10)).grid(
        row=i, column=0, sticky="w", **PAD)
    e = ttk.Entry(root, width=18, font=("Arial", 10))
    e.grid(row=i, column=1, **PAD)
    entries[name] = e

entry_total   = entries["entry_total"]
entry_errors  = entries["entry_errors"]
entry_fixed   = entries["entry_fixed"]
entry_corrupt = entries["entry_corrupt"]

# Кнопки
btn_frame = tk.Frame(root)
btn_frame.grid(row=6, column=0, columnspan=2, pady=6)

ttk.Button(btn_frame, text="▶  Рассчитать",     command=calculate,    width=16).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Вариант 1",          command=fill_variant1, width=14).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="Очистить",           command=clear_all,    width=10).grid(row=0, column=2, padx=5)

# Результаты
result_var = tk.StringVar()
result_lbl = tk.Label(root, textvariable=result_var, font=("Courier", 10),
                      justify="left", bg="#ecf0f1", relief="sunken",
                      anchor="nw", padx=10, pady=8, width=46)
result_lbl.grid(row=7, column=0, columnspan=2, padx=10, pady=(4, 14), sticky="we")

# Подсказка
hint = tk.Label(root, text='Нажмите "Вариант 1" для автозаполнения',
                font=("Arial", 8), fg="#95a5a6")
hint.grid(row=8, column=0, columnspan=2, pady=(0, 8))

root.mainloop()
