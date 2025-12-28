import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import csv
from database import fetch_expenses, add_expense, delete_expense


class Expense:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1500x550")
        self.root.configure(bg="white")

        self.sort_by = tk.StringVar(value="None")
        self.order_by = tk.StringVar(value="Ascending")

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        label_font = ("Georgia", 15, "bold")
        input_font = ("Georgia", 12, "bold")

        tk.Label(
            self.root, text="Date:",
            bg="white", fg="darkgreen", font=label_font
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.date_entry = DateEntry(
            self.root, date_pattern="yyyy-mm-dd", font=input_font
        )
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(
            self.root, text="Category:",
            bg="white", fg="darkgreen", font=label_font
        ).grid(row=0, column=2, padx=10, sticky="w")

        self.dropdown = ttk.Combobox(
            self.root, font=input_font,
            state="readonly", width=18
        )
        self.dropdown["values"] = [
            "Food", "Transportation", "Rent",
            "Shopping", "Entertainment", "Bills", "Other"
        ]
        self.dropdown.current(0)
        self.dropdown.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(
            self.root, text="Amount:",
            bg="white", fg="darkgreen", font=label_font
        ).grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.amount = tk.Entry(
            self.root, font=input_font,
            bg="white", relief=tk.GROOVE, bd=2
        )
        self.amount.grid(row=1, column=1, padx=10)

        tk.Label(
            self.root, text="Description:",
            bg="white", fg="darkgreen", font=label_font
        ).grid(row=1, column=2, padx=10, sticky="w")

        self.description = tk.Entry(
            self.root, font=input_font,
            bg="white", relief=tk.GROOVE, bd=2
        )
        self.description.grid(row=1, column=3, padx=10)

        tk.Button(
            self.root, text="Add Expense",
            font=input_font, bg="green", fg="white",
            padx=15, pady=6, command=self.add_expense
        ).grid(row=2, column=0, padx=10, pady=10)

        tk.Button(
            self.root, text="Delete Selected",
            font=input_font, bg="red", fg="white",
            padx=15, pady=6, command=self.delete_expense
        ).grid(row=2, column=1, padx=10, pady=10)

        tk.Button(
            self.root, text="Export to CSV",
            font=input_font, bg="darkblue", fg="white",
            padx=15, pady=6, command=self.export_to_csv
        ).grid(row=2, column=2, padx=10, pady=10)

        tk.Label(
            self.root, text="Sort By:",
            bg="white", fg="black", font=("Georgia", 12, "bold")
        ).grid(row=2, column=3, sticky="e", padx=5)

        sort_options = ["None", "Amount", "Category", "Date"]
        ttk.Combobox(
            self.root, textvariable=self.sort_by,
            values=sort_options, font=("Georgia", 11),
            width=12, state="readonly"
        ).grid(row=2, column=4, padx=5)

        tk.Label(
            self.root, text="Order:",
            bg="white", fg="black", font=("Georgia", 12, "bold")
        ).grid(row=2, column=5, sticky="e", padx=5)

        order_options = ["Ascending", "Descending"]
        ttk.Combobox(
            self.root, textvariable=self.order_by,
            values=order_options, font=("Georgia", 11),
            width=12, state="readonly"
        ).grid(row=2, column=6, padx=5)

        tk.Button(
            self.root, text="Apply Filter",
            font=("Georgia", 11, "bold"),
            bg="purple", fg="white",
            command=self.load_data
        ).grid(row=2, column=7, padx=10)

        style = ttk.Style()
        style.configure("Treeview", font=("Georgia", 10, "bold"), rowheight=28)
        style.configure("Treeview.Heading", font=("Georgia", 12, "bold"))

        self.table = ttk.Treeview(
            self.root,
            columns=("id", "date", "category", "amount", "description"),
            show="headings"
        )
        columns = [
            ("id", "ID", 80), ("date", "Date", 150),
            ("category", "Category", 150),
            ("amount", "Amount", 150),
            ("description", "Description", 250)
        ]
        for col, title, width in columns:
            self.table.heading(col, text=title)
            self.table.column(col, width=width, anchor="center")

        self.table.grid(
            row=3, column=0, columnspan=8,
            padx=20, pady=10, sticky="nsew"
        )

        scrollbar = ttk.Scrollbar(
            self.root, orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=3, column=8, sticky="ns")

        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)

    def load_data(self):
        data = fetch_expenses()
        sort = self.sort_by.get()
        order = self.order_by.get()

        if sort != "None":
            index_map = {"Amount": 3, "Category": 2, "Date": 1}
            index = index_map.get(sort, 0)
            reverse = (order == "Descending")
            data = sorted(data, key=lambda x: x[index], reverse=reverse)

        self.table.delete(*self.table.get_children())
        for row in data:
            self.table.insert("", "end", values=row)

    def add_expense(self):
        date = self.date_entry.get_date().strftime("%Y-%m-%d")
        category = self.dropdown.get()
        amount_text = self.amount.get().strip()
        desc = self.description.get().strip()

        if not desc:
            messagebox.showwarning("Warning", "Please enter a description.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        if add_expense(date, category, amount, desc):
            self.load_data()
            self.amount.delete(0, tk.END)
            self.description.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Failed to add expense.")

    def delete_expense(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an expense to delete.")
            return

        item = self.table.item(selected[0])
        expense_id = item["values"][0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            if delete_expense(expense_id):
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete expense.")

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["ID", "Date", "Category", "Amount", "Description"]
                )
                for row in self.table.get_children():
                    writer.writerow(self.table.item(row)["values"])
            messagebox.showinfo(
                "Export Successful",
                f"Expenses saved to:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{e}")
