import tkinter as tk
from tkinter import messagebox, simpledialog
import database
from loginpage import UserLoginPage

class LaunchPage:
    def __init__(self, root, username, on_launch_complete):
        self.root = root
        self.username = username
        self.on_launch_complete = on_launch_complete

        self.root.title("Table Selection")
        self.root.geometry("420x750")
        self.root.configure(bg="white")

        tk.Label(root, text="Choose or Create a Table",
                 font=("Georgia", 16, "bold"),
                 bg="white", fg="darkblue").pack(pady=15)

        self.table_listbox = tk.Listbox(root, font=("Georgia", 12), height=8)
        self.table_listbox.pack(pady=10, fill="x", padx=20)
        self.table_listbox.bind("<<ListboxSelect>>", self.show_table_info)
        self.load_tables()

        self.info_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
        self.info_frame.pack(fill="x", padx=20, pady=10)
        self.table_info_label = tk.Label(self.info_frame, text="Select a table to view details",
                                         font=("Georgia", 10),
                                         bg="white", justify="left", anchor="w")
        self.table_info_label.pack(padx=5, pady=5, fill="x")

        tk.Button(root, text="Use Selected Table",
                  font=("Georgia", 10, "bold"),
                  bg="darkblue", fg="white",
                  padx=10, pady=6,
                  command=self.use_selected_table).pack(pady=10)

        tk.Button(root, text="Create New Table",
                  font=("Georgia", 10, "bold"),
                  bg="green", fg="white",
                  padx=10, pady=6,
                  command=self.create_table).pack(pady=10)

        tk.Button(root, text="Delete Selected Table",
                  font=("Georgia", 10, "bold"),
                  bg="red", fg="white",
                  padx=10, pady=6,
                  command=self.delete_selected_table).pack(pady=5)

        tk.Button(root, text="Rename Selected Table",
                  font=("Georgia", 10, "bold"),
                  bg="orange", fg="white",
                  padx=10, pady=6,
                  command=self.rename_selected_table).pack(pady=5)

        tk.Button(root, text="Duplicate Selected Table",
                  font=("Georgia", 10, "bold"),
                  bg="purple", fg="white",
                  padx=10, pady=6,
                  command=self.duplicate_selected_table).pack(pady=5)

        tk.Button(root, text="Logout",
                  font=("Georgia", 10, "bold"),
                  bg="gray", fg="white",
                  padx=10, pady=6,
                  command=self.logout).pack(pady=10)

    def _display_to_full(self, display_name: str) -> str:
        return f"{self.username}_{display_name}"

    def load_tables(self):
        self.table_listbox.delete(0, tk.END)
        tables = database.get_user_tables()
        prefix = f"{self.username}_"
        for table in tables:
            if table.startswith(prefix):
                self.table_listbox.insert(tk.END, table[len(prefix):])

    def show_table_info(self, event=None):
        selected = self.table_listbox.curselection()
        if not selected:
            self.table_info_label.config(text="Select a table to view details")
            return

        display_name = self.table_listbox.get(selected[0])
        full_name = self._display_to_full(display_name)
        try:
            columns = database.get_table_info(full_name)
            entry_count = database.get_table_count(full_name)
            if not columns:
                self.table_info_label.config(text=f"No column info found for {display_name}.")
                return
            info_text = f"Table: {display_name}\n"
            info_text += f"Number of entries: {entry_count}\n"
            info_text += "Columns:\n"
            for col_name, col_type in columns:
                info_text += f"• {col_name} ({col_type})\n"
            self.table_info_label.config(text=info_text.strip())
        except Exception as e:
            self.table_info_label.config(text=f"Error: {e}")

    def use_selected_table(self):
        selected = self.table_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a table.")
            return
        display_name = self.table_listbox.get(selected[0])
        full_name = self._display_to_full(display_name)
        if full_name not in database.get_user_tables():
            messagebox.showerror("Invalid Table", "Selected table does not exist or was not created by this user.")
            return
        database.set_table(full_name)
        self.root.withdraw()
        self.on_launch_complete(self.username, self.root)

    def create_table(self):
        new_table_name = simpledialog.askstring("New Table", "Enter new table name:")
        if not new_table_name:
            return
        new_table_name = new_table_name.strip()
        if not new_table_name:
            return
        if database.create_table(new_table_name):
            messagebox.showinfo("Success", f"Table '{new_table_name}' created.")
            self.load_tables()
        else:
            messagebox.showerror("Error", "Failed to create table.")

    def delete_selected_table(self):
        selected = self.table_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a table to delete.")
            return
        display_name = self.table_listbox.get(selected[0])
        full_name = self._display_to_full(display_name)
        confirm = messagebox.askyesno("Confirm Delete", f"Delete '{display_name}'?")
        if not confirm:
            return
        if database.delete_table(full_name):
            messagebox.showinfo("Deleted", f"Table '{display_name}' deleted.")
            self.load_tables()
        else:
            messagebox.showerror("Error", f"Failed to delete table '{display_name}'.")

    def rename_selected_table(self):
        selected = self.table_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a table to rename.")
            return
        old_display = self.table_listbox.get(selected[0])
        new_name = simpledialog.askstring("Rename Table", f"Enter new name for '{old_display}':")
        if not new_name or not new_name.strip():
            return
        new_name = new_name.strip()
        old_full = self._display_to_full(old_display)
        try:
            from database import rename_table
        except ImportError:
            messagebox.showerror("Error", "rename_table function not found in database.py")
            return
        if rename_table(self.username, old_display, new_name):
            messagebox.showinfo("Success", f"Table renamed to '{new_name}'.")
            self.load_tables()
        else:
            messagebox.showerror("Error", "Failed to rename table. Table may already exist.")

    def duplicate_selected_table(self):
        selected = self.table_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a table to duplicate.")
            return
        source_display = self.table_listbox.get(selected[0])
        new_display = simpledialog.askstring("Duplicate Table", f"Enter new name for '{source_display}':")
        if not new_display or not new_display.strip():
            return
        new_display = new_display.strip()
        if database.duplicate_table(self.username, source_display, new_display):
            messagebox.showinfo("Duplicated", f"Table '{source_display}' duplicated as '{new_display}'.")
            self.load_tables()
        else:
            messagebox.showerror("Error", "Failed to duplicate table.")

    def logout(self):
        self.root.withdraw()
        login_root = tk.Toplevel(self.root)
        def after_login(username):
            login_root.destroy()
            self.root.deiconify()
            for w in self.root.winfo_children():
                w.destroy()
            self.username = username
            self.__init__(self.root, username, self.on_launch_complete)
        UserLoginPage(login_root, on_login_success=after_login)
