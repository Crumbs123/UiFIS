import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont


class Question:
    def __init__(self, text, options, correct_answer):
        self.text = text
        self.options = options
        self.correct_answer = correct_answer


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Угадай стандарт")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Center the window
        window_width = 420
        window_height = 380
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.questions = self._init_questions()
        self.current_index = 0
        self.correct_count = 0
        self.selected_answer = tk.StringVar()

        self._build_ui()
        self._load_question()

    def _init_questions(self):
        return [
            Question(
                "Какой стандарт определяет формат чисел с плавающей точкой?",
                ["ISO 9001", "IEEE 754", "ASCII", "USB 3.0"],
                "IEEE 754"
            ),
            Question(
                "Какой стандарт описывает базовый набор символов?",
                ["Unicode", "ASCII", "UTF-8", "ISO 8859-1"],
                "ASCII"
            ),
            Question(
                "Какой стандарт определяет требования к системе менеджмента качества?",
                ["ISO 9001", "IEEE 802.11", "GMP", "HACCP"],
                "ISO 9001"
            ),
            Question(
                "Какой стандарт описывает протоколы для Wi-Fi?",
                ["IEEE 802.3", "IEEE 802.11", "IEEE 1394", "Bluetooth"],
                "IEEE 802.11"
            ),
            Question(
                "Какой стандарт кодировки включает символы всех письменностей мира?",
                ["ASCII", "KOI-8", "Unicode", "Windows-1251"],
                "Unicode"
            ),
        ]

    def _build_ui(self):
        # Title label
        self.title_label = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0",
            fg="#1a1a1a",
            wraplength=380,
            justify="center"
        )
        self.title_label.pack(pady=(20, 5), padx=20)

        # Question text
        self.question_label = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            fg="#1a1a1a",
            wraplength=380,
            justify="center"
        )
        self.question_label.pack(pady=(0, 10), padx=20)

        # Options frame with border
        options_outer = tk.LabelFrame(
            self.root,
            text="Выберите правильный стандарт:",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="#333333",
            padx=10,
            pady=8
        )
        options_outer.pack(padx=20, fill="x")

        self.radio_buttons = []
        self.selected_answer = tk.StringVar()

        for i in range(4):
            rb = tk.Radiobutton(
                options_outer,
                text="",
                variable=self.selected_answer,
                value="",
                font=("Segoe UI", 10),
                bg="#f0f0f0",
                fg="#1a1a1a",
                activebackground="#f0f0f0",
                anchor="w"
            )
            rb.pack(fill="x", pady=2)
            self.radio_buttons.append(rb)

        # Result label
        self.result_label = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="#333333"
        )
        self.result_label.pack(pady=(8, 0))

        # Next button
        self.next_btn = tk.Button(
            self.root,
            text="Далее",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            fg="#1a1a1a",
            relief="raised",
            padx=20,
            pady=4,
            command=self._next_question
        )
        self.next_btn.pack(pady=8)

        # Progress label
        self.progress_label = tk.Label(
            self.root,
            text="Правильных ответов: 0 из 5",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="#555555"
        )
        self.progress_label.pack(pady=(0, 10))

    def _load_question(self):
        q = self.questions[self.current_index]
        self.title_label.config(
            text=f"Вопрос {self.current_index + 1} из {len(self.questions)}:"
        )
        self.question_label.config(text=q.text)
        self.selected_answer.set("")
        self.result_label.config(text="")

        for i, rb in enumerate(self.radio_buttons):
            rb.config(text=q.options[i], value=q.options[i])

        self._update_progress()

    def _next_question(self):
        answer = self.selected_answer.get()
        if not answer:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите ответ.")
            return

        q = self.questions[self.current_index]
        if answer == q.correct_answer:
            self.correct_count += 1
            self.result_label.config(text="✓ Верно!", fg="green")
        else:
            self.result_label.config(
                text=f"✗ Неверно. Правильный ответ: {q.correct_answer}", fg="red"
            )

        self._update_progress()
        self.current_index += 1

        if self.current_index < len(self.questions):
            self.root.after(800, self._load_question)
        else:
            self.root.after(800, self._show_result)

    def _update_progress(self):
        self.progress_label.config(
            text=f"Правильных ответов: {self.correct_count} из {len(self.questions)}"
        )

    def _show_result(self):
        percent = (self.correct_count / len(self.questions)) * 100
        msg = (
            f"Тест завершён!\n\n"
            f"Правильных ответов: {self.correct_count} из {len(self.questions)}\n"
            f"Процент: {percent:.1f}%\n\n"
            f"Хотите пройти тест заново?"
        )
        restart = messagebox.askyesno("Результат теста", msg)
        if restart:
            self.current_index = 0
            self.correct_count = 0
            self._load_question()
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
