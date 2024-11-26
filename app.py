import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from ttkthemes import ThemedTk
import calendar

class EmployeeTimekeeper:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Employee Timekeeper")
        self.root.geometry("1200x800")
        self.root.configure(bg='#ffffff')
        
        self.setup_database()
        self.create_styles()
        self.create_gui()
        self.load_employees()

    def setup_database(self):
        self.conn = sqlite3.connect("timekeeper.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def create_styles(self):
        style = ttk.Style()
        style.configure('.', background='#ffffff', foreground='#202124')
        style.configure('Header.TLabel', font=('Google Sans', 28, 'bold'), padding=20, background='#ffffff', foreground='#202124')
        style.configure('Material.TButton', font=('Google Sans', 11), padding=(10, 5), background='white', foreground='black')
        style.configure('MaterialOutline.TButton', font=('Google Sans', 11), padding=(10, 5), background='white', foreground='black')
        style.configure('Material.TEntry', padding=10, fieldbackground='#f1f3f4', borderwidth=0)
        style.configure('Material.TFrame', background='white')
        style.configure('Card.TFrame', background='white', relief='flat', borderwidth=1)
        style.configure('Material.TLabelframe', background='white', foreground='#5f6368', font=('Google Sans', 12))
        style.configure('Material.TLabelframe.Label', background='white', foreground='#5f6368', font=('Google Sans', 12))
        style.configure('Treeview', background='white', fieldbackground='white', foreground='#202124', font=('Google Sans', 11), rowheight=40)
        style.configure('Treeview.Heading', background='#f1f3f4', font=('Google Sans', 11, 'bold'), padding=10)

    def create_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.add_tab = ttk.Frame(notebook)
        notebook.add(self.add_tab, text="Add Employee")
        
        self.view_tab = ttk.Frame(notebook)
        notebook.add(self.view_tab, text="Employee List")
        
        self.stats_tab = ttk.Frame(notebook)
        notebook.add(self.stats_tab, text="Statistics")

        self.create_add_tab()
        self.create_view_tab()
        self.create_stats_tab()

    def create_add_tab(self):
        header = ttk.Label(self.add_tab, text="Add Employee", style='Header.TLabel')
        header.pack(pady=(0, 30))

        input_frame = ttk.LabelFrame(self.add_tab, text="New Entry", style='Material.TLabelframe', padding=20)
        input_frame.pack(fill=tk.X, pady=(0, 20))

        self.name_var = tk.StringVar()
        self.start_time_var = tk.StringVar()
        self.end_time_var = tk.StringVar()

        ttk.Label(input_frame, text="Employee Name:").pack(anchor='w')
        ttk.Entry(input_frame, textvariable=self.name_var, style='Material.TEntry').pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Start Time (HH:MM):").pack(anchor='w')
        ttk.Entry(input_frame, textvariable=self.start_time_var, style='Material.TEntry').pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="End Time (HH:MM):").pack(anchor='w')
        ttk.Entry(input_frame, textvariable=self.end_time_var, style='Material.TEntry').pack(fill=tk.X, pady=5)

        ttk.Button(input_frame, text="Add Entry", style='Material.TButton', command=self.add_employee).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(input_frame, text="Clear", style='MaterialOutline.TButton', command=self.clear_fields).pack(side=tk.LEFT, padx=10, pady=10)

    def create_view_tab(self):
        header = ttk.Label(self.view_tab, text="Employee List", style='Header.TLabel')
        header.pack(pady=(0, 30))

        search_frame = ttk.Frame(self.view_tab)
        search_frame.pack(fill=tk.X, pady=(0, 20))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, style='Material.TEntry')
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", style='Material.TButton', command=self.search_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Show All", style='MaterialOutline.TButton', command=self.load_employees).pack(side=tk.LEFT, padx=5)

        records_frame = ttk.Frame(self.view_tab)
        records_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('ID', 'Name', 'Start Time', 'End Time', 'Date', 'Work Hours')
        self.tree = ttk.Treeview(records_frame, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def create_stats_tab(self):
        header = ttk.Label(self.stats_tab, text="Statistics", style='Header.TLabel')
        header.pack(pady=(0, 30))

        stats_frame = ttk.Frame(self.stats_tab)
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        self.total_hours_var = tk.StringVar(value="Total Hours: 0")
        ttk.Label(stats_frame, textvariable=self.total_hours_var, font=('Google Sans', 14)).pack(pady=5)

        self.month_var = tk.StringVar(value=datetime.now().strftime("%B"))
        month_menu = ttk.OptionMenu(stats_frame, self.month_var, datetime.now().strftime("%B"), *calendar.month_name[1:], command=self.update_monthly_stats)
        month_menu.pack(pady=5)

        self.monthly_hours_var = tk.StringVar(value="Monthly Hours: 0")
        ttk.Label(stats_frame, textvariable=self.monthly_hours_var, font=('Google Sans', 14)).pack(pady=5)

    def add_employee(self):
        name = self.name_var.get().strip()
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        
        if not all([name, start_time, end_time]):
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            self.cursor.execute("""
                INSERT INTO employees (name, start_time, end_time, date)
                VALUES (?, ?, ?, ?)
            """, (name, start_time, end_time, current_date))
            self.conn.commit()
            
            self.clear_fields()
            self.load_employees()
            messagebox.showinfo("Success", "Entry added successfully")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM format")

    def load_employees(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cursor.execute("""
            SELECT id, name, start_time, end_time, date FROM employees
            ORDER BY date DESC, start_time DESC
        """)
        
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def search_employee(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_employees()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cursor.execute("""
            SELECT id, name, start_time, end_time, date FROM employees
            WHERE name LIKE ?
        """, (f"%{search_term}%",))

        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def update_monthly_stats(self, *args):
        selected_month = self.month_var.get()
        month_num = list(calendar.month_name).index(selected_month)
        
        self.cursor.execute("""
            SELECT start_time, end_time FROM employees
            WHERE strftime('%m', date) = ?
        """, (f"{month_num:02d}",))
        
        total_hours = sum(self.calculate_hours(start, end) for start, end in self.cursor.fetchall())
        self.monthly_hours_var.set(f"Monthly Hours: {total_hours:.2f}")

    def calculate_hours(self, start_time, end_time):
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        diff = end - start
        return diff.seconds / 3600

    def clear_fields(self):
        self.name_var.set("")
        self.start_time_var.set("")
        self.end_time_var.set("")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = EmployeeTimekeeper()
    app.run()
