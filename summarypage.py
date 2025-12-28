import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import get_total_expenses

class Summary:
    def __init__(self, root, on_back):
        self.root = root
        self.on_back = on_back
        self.root.title("Expense Summary")
        self.root.geometry("500x500")
        self.root.configure(bg="white")
        self.create_widgets()

    def create_widgets(self):
        style_font = ("Georgia", 12, "bold")
        label_style = {"bg": "white", "fg": "darkgreen", "font": ("Georgia", 12, "bold")}
        entry_style = {"font": style_font, "background": "white"}

        tk.Label(self.root, text="Select Category:", **label_style).pack(pady=(20, 5))
        self.category_cb = ttk.Combobox(self.root, values=[
            "Food", "Transportation", "Rent", "Shopping", "Entertainment", "Bills", "Other"
        ], font=style_font, state="readonly")
        self.category_cb.current(0)
        self.category_cb.pack(pady=5, ipady=4)

        tk.Label(self.root, text="Start Date:", **label_style).pack(pady=(15, 5))
        self.start_date = DateEntry(self.root, date_pattern="yyyy-mm-dd", font=style_font, background="white")
        self.start_date.pack(pady=5, ipady=3)

        tk.Label(self.root, text="End Date:", **label_style).pack(pady=(15, 5))
        self.end_date = DateEntry(self.root, date_pattern="yyyy-mm-dd", font=style_font, background="white")
        self.end_date.pack(pady=5, ipady=3)

        self.check_btn = tk.Button(self.root, text="Check Total",
            font=("Georgia", 12, "bold"), bg="green", fg="white",
            activebackground="darkgreen", relief=tk.RAISED,
            bd=2, padx=20, pady=6, command=self.check_total)
        self.check_btn.pack(pady=(25, 10))

        self.result_label = tk.Label(self.root, text="",
            font=("Georgia", 12, "bold"), bg="white", fg="darkblue",
            wraplength=360, justify="center", relief=tk.GROOVE,
            bd=2, padx=10, pady=10)
        self.result_label.pack(pady=10, fill="x", padx=20)

        self.back_btn = tk.Button(self.root, text="Back to Main App",
            font=("Georgia", 12, "bold"), bg="red", fg="white",
            activebackground="darkred", relief=tk.RAISED,
            bd=2, padx=10, pady=4, command=self.on_back)
        self.back_btn.pack(pady=(10, 20))

    def check_total(self):
        category = self.category_cb.get()
        start = self.start_date.get_date().strftime("%Y-%m-%d")
        end = self.end_date.get_date().strftime("%Y-%m-%d")

        total = get_total_expenses(category, start, end)
        self.result_label.config(text=f"Total in '{category}' from {start} to {end}:\n₹ {total:.2f}")
