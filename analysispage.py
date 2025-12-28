import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from database import fetch_expenses


class Analysis:
    def __init__(self, root, on_back):
        self.root = root
        self.on_back = on_back
        self.root.title("Expense Analysis")
        self.root.geometry("800x800")
        self.root.configure(bg="white")

        tk.Label(
            self.root, text="Expense Analysis",
            font=("Georgia", 18, "bold"),
            fg="green", bg="white"
        ).pack(pady=20)

        self.graph_type = tk.StringVar(value="Bar Chart")
        graph_options = ["Bar Chart", "Pie Chart", "Line Chart"]

        ttk.Label(
            self.root, text="Select Graph Type:",
            font=("Georgia", 12), background="white"
        ).pack()

        ttk.Combobox(
            self.root, textvariable=self.graph_type,
            values=graph_options, state="readonly",
            font=("Georgia", 11)
        ).pack(pady=5)

        tk.Button(
            self.root, text="Generate Graph",
            command=self.draw_graph,
            font=("Georgia", 12, "bold"),
            bg="blue", fg="white", padx=10, pady=4
        ).pack(pady=10)

        self.canvas_frame = tk.Frame(self.root, bg="white")
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)

        tk.Button(
            self.root, text="Back",
            command=self.back_to_main,
            font=("Georgia", 12, "bold"),
            bg="gray", fg="white", padx=10, pady=4
        ).pack(pady=10)

    def draw_graph(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        data = fetch_expenses()
        if not data:
            tk.Label(
                self.canvas_frame, text="No expense data found.",
                font=("Georgia", 12), bg="white"
            ).pack()
            return

        category_totals = {}
        for row in data:
            category_totals[row[2]] = category_totals.get(row[2], 0) + row[3]

        categories = list(category_totals.keys())
        totals = list(category_totals.values())

        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        graph_type = self.graph_type.get()

        if graph_type == "Bar Chart":
            ax.bar(categories, totals, color="skyblue")
            ax.set_title("Expenses by Category")
            ax.set_ylabel("Amount Spent")
            ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('₹{x:,.0f}'))

        elif graph_type == "Pie Chart":
            ax.pie(totals, labels=categories, autopct='%1.1f%%', startangle=140)
            ax.set_title("Expense Distribution")

        elif graph_type == "Line Chart":
            ax.plot(categories, totals, marker='o', linestyle='-', color="green")
            ax.set_title("Expenses by Category (Line)")
            ax.set_ylabel("Amount")
            ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('₹{x:,.0f}'))

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def back_to_main(self):
        self.root.destroy()
        self.on_back()

