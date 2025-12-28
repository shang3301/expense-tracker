import tkinter as tk
from tkinter import messagebox
from expensepage import Expense
from summarypage import Summary
from analysispage import Analysis
from launchpage import LaunchPage
from loginpage import UserLoginPage
import database


def run_main_app(username, launch_window):
    try:
        if not database.get_table():
            messagebox.showerror("Error", "No table selected. Please select a table first.")
            return

        user_tables = database.get_user_tables()
        if database.get_table() not in user_tables:
            messagebox.showerror("Invalid Table", "Selected table does not exist or wasn't created by this user.")
            return

        launch_window.withdraw()
        exp_win = tk.Toplevel(launch_window)
        exp_win.title(f"Expenses - {database.get_table()}")
        Expense(exp_win)

        def back_to_launch():
            exp_win.destroy()
            launch_window.deiconify()

        def open_summary():
            exp_win.withdraw()
            summary_window = tk.Toplevel(exp_win)
            summary_window.title("Summary")
            Summary(summary_window, on_back=lambda: _close_child_and_return(summary_window, exp_win))

        def open_analysis():
            exp_win.withdraw()
            analysis_window = tk.Toplevel(exp_win)
            analysis_window.title("Analysis")
            Analysis(analysis_window, on_back=lambda: _close_child_and_return(analysis_window, exp_win))

        def _close_child_and_return(child, parent_to_show):
            child.destroy()
            parent_to_show.deiconify()

        summary_btn = tk.Button(
            exp_win, text="View Total",
            font=("Georgia", 12, "bold"), bg="blue", fg="white",
            activebackground="blue", padx=15, pady=6,
            relief=tk.RAISED,
            command=open_summary
        )
        summary_btn.grid(row=4, column=6, padx=10, pady=10, sticky="e")

        analysis_btn = tk.Button(
            exp_win, text="Analysis",
            font=("Georgia", 12, "bold"), bg="purple", fg="white",
            activebackground="purple", padx=15, pady=6,
            relief=tk.RAISED,
            command=open_analysis
        )
        analysis_btn.grid(row=4, column=7, padx=10, pady=10, sticky="e")

        back_button = tk.Button(
            exp_win, text="Back",
            font=("Georgia", 10, "bold"),
            bg="gray", fg="white",
            padx=10, pady=5,
            command=back_to_launch
        )
        back_button.grid(row=5, column=7, padx=10, pady=20, sticky="e")

    except Exception as e:
        messagebox.showerror("Unexpected Error", str(e))


class IntroPage:
    def __init__(self, root):
        self.root = root
        self.root.title("!Welcome!")
        self.root.geometry("420x300")
        self.root.configure(bg="white")

        tk.Label(root, text="Expense Tracker",
                 font=("Georgia", 20, "bold"),
                 bg="white", fg="darkgreen").pack(pady=(40, 10))
        tk.Label(root, text="Made by Satish Garg & Joydeep Patra",
                 font=("Georgia", 15, "bold"),
                 bg="white", fg="black").pack(pady=(0, 20))
        tk.Button(root, text="Launch App",
                  font=("Georgia", 10, "bold"),
                  bg="darkgreen", fg="white",
                  activebackground="green", padx=20, pady=8,
                  command=self.open_login_page).pack(pady=10)

    def open_login_page(self):
        def after_login(username):
            self.root.withdraw()
            launch_win = tk.Toplevel(self.root)
            LaunchPage(launch_win, username,
                       on_launch_complete=lambda u, lw=launch_win: run_main_app(u, lw))

        login_root = tk.Toplevel(self.root)
        UserLoginPage(login_root, on_login_success=after_login)


def main():
    root = tk.Tk()
    IntroPage(root)
    root.mainloop()


if __name__ == "__main__":
    main()
