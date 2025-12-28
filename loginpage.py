import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
import database

def connect_user_db():
    con = database.connect()
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(100)
        )
    """)
    con.commit()
    return con

def get_all_users():
    con = connect_user_db()
    cursor = con.cursor()
    cursor.execute("SELECT username FROM users")
    users = [user[0] for user in cursor.fetchall()]
    con.close()
    return users

def open_user_page():
    from tkinter import Tk
    root = Tk()
    root.mainloop()

class UserLoginPage:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("User Login")
        self.root.geometry("400x400")
        self.root.configure(bg="white")
        self.on_login_success = on_login_success

        tk.Label(root, text="Select or Create a User",
                 font=("Georgia", 16, "bold"), bg="white").pack(pady=10)

        self.user_listbox = tk.Listbox(root, font=("Georgia", 12), height=8,
                                       selectbackground="lightblue", selectforeground="black")
        self.user_listbox.pack(pady=10)

        tk.Button(root, text="Login with Selected User",
                  font=("Georgia", 10, "bold"), bg="darkgreen", fg="white",
                  command=self.login_user).pack(pady=10)

        tk.Button(root, text="Create New User",
                  font=("Georgia", 10, "bold"), bg="blue", fg="white",
                  command=self.create_user).pack(pady=5)
        
        tk.Button(root, text="Delete User",
          font=("Georgia", 10, "bold"),
          bg="darkred", fg="white",
          padx=10, pady=6,
          command=self.delete_user).pack(pady=5)


        self.refresh_users()

    def refresh_users(self):
        self.user_listbox.delete(0, tk.END)
        users = get_all_users()
        for user in users:
            self.user_listbox.insert(tk.END, user)

    def login_user(self):
        try:
            username = self.user_listbox.get(self.user_listbox.curselection())
        except:
            messagebox.showerror("No Selection", "Please select a user first.")
            return

        password = simpledialog.askstring("Password", f"Enter password for '{username}':", show='*')
        if not password:
            return

        con = connect_user_db()
        cursor = con.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        con.close()

        if result and result[0] == password:
            database.current_user = username
            self.root.destroy()
            self.on_login_success(username)
        else:
            messagebox.showerror("Error", "Incorrect password.")

    def create_user(self):
        username = simpledialog.askstring("New User", "Enter new username:")
        if not username:
            return
        password = simpledialog.askstring("Password", f"Set a password for '{username}':", show='*')
        if not password:
            return

        con = connect_user_db()
        cursor = con.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            con.commit()
            messagebox.showinfo("Success", f"User '{username}' created successfully.")
            self.refresh_users()
        except mysql.connector.Error:
            messagebox.showerror("Error", f"User '{username}' already exists.")
        finally:
            con.close()

    def delete_user(self):
        try:
            username = self.user_listbox.get(self.user_listbox.curselection())
        except:
            messagebox.showerror("No Selection", "Please select a user first.")
            return

        password = simpledialog.askstring("Delete User", f"Enter password for '{username}':", show="*")
        if not password:
            return

        if database.delete_user(username, password):
            messagebox.showinfo("Account Deleted", f"User '{username}' has been deleted successfully.")
            self.refresh_users() 
        else:
            messagebox.showerror("Error", "Incorrect password or failed to delete user.")

