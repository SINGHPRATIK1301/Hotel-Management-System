import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import qrcode
from PIL import Image, ImageTk
import os

# Constants for billing
TAX_RATE = 0.10  # 10% tax
QR_CODE_PATH = "payment_qr.png"  # Path to save QR code image

# Room Class
class Room:
    ROOM_TYPES = [
        ('SINGLE', 'Single Room'),
        ('DOUBLE', 'Double Room'), 
        ('DELUXE', 'Deluxe Room'),
        ('SUITE', 'Suite')
    ]
    
    def __init__(self, room_number, room_type, rate, is_available=True, description=""):
        self.room_number = room_number
        self.room_type = room_type
        self.rate = rate
        self.is_available = is_available
        self.description = description
        self.last_updated = datetime.now()

# Main Application Class
class HotelManagementSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hotel Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize Database
        self.init_database()
        
        # Create Main UI Components
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        
    def init_database(self):
        self.conn = sqlite3.connect('hotel.db')
        self.cursor = self.conn.cursor()
        
        # Create rooms table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY,
                room_number TEXT UNIQUE,
                room_type TEXT,
                rate REAL,
                is_available INTEGER,
                description TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        # Create bookings table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                room_number TEXT,
                customer_name TEXT,
                customer_phone TEXT,
                check_in_date TEXT,
                check_out_date TEXT,
                total_amount REAL,
                booking_date TIMESTAMP,
                FOREIGN KEY (room_number) REFERENCES rooms (room_number)
            )
        ''')

        # Create bills table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY,
                booking_id INTEGER,
                subtotal REAL,
                tax_amount REAL,
                discount_amount REAL,
                total_amount REAL,
                payment_status TEXT,
                payment_method TEXT,
                bill_date TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
        ''')

        # Create services table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY,
                service_name TEXT,
                description TEXT,
                price REAL,
                category TEXT,
                is_active INTEGER
            )
        ''')

        # Create service_requests table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_requests (
                id INTEGER PRIMARY KEY,
                booking_id INTEGER,
                service_id INTEGER,
                quantity INTEGER,
                total_amount REAL,
                request_date TIMESTAMP,
                status TEXT,
                notes TEXT,
                FOREIGN KEY (booking_id) REFERENCES bookings (id),
                FOREIGN KEY (service_id) REFERENCES services (id)
            )
        ''')

        # Create analytics table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY,
                date TEXT,
                total_bookings INTEGER,
                total_revenue REAL,
                average_booking_value REAL,
                occupancy_rate REAL,
                room_type_distribution TEXT,
                payment_method_distribution TEXT
            )
        ''')

        # Create staff table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY,
                employee_id TEXT UNIQUE,
                name TEXT,
                position TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                join_date TEXT,
                base_salary REAL,
                status TEXT
            )
        ''')

        # Create salary_payments table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS salary_payments (
                id INTEGER PRIMARY KEY,
                employee_id TEXT,
                payment_date TEXT,
                base_salary REAL,
                bonus REAL,
                deductions REAL,
                net_salary REAL,
                payment_method TEXT,
                remarks TEXT,
                FOREIGN KEY (employee_id) REFERENCES staff (employee_id)
            )
        ''')

        # Insert default services if not exists
        self.cursor.execute('SELECT COUNT(*) FROM services')
        if self.cursor.fetchone()[0] == 0:
            default_services = [
                ('Room Service', 'Daily room cleaning and maintenance', 25.00, 'Cleaning', 1),
                ('Laundry Service', 'Wash, dry, and fold service', 15.00, 'Laundry', 1),
                ('Mini Bar Refill', 'Refill of room mini bar items', 50.00, 'Food', 1),
                ('Food Delivery', 'Delivery of food and snacks to room', 10.00, 'Food', 1),
                ('Extra Towels', 'Additional towels and linens', 5.00, 'Cleaning', 1),
                ('Late Checkout', 'Extended stay beyond standard checkout time', 30.00, 'Other', 1)
            ]
            self.cursor.executemany('''
                INSERT INTO services (service_name, description, price, category, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', default_services)
            self.conn.commit()

        self.conn.commit()
        
    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=70)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame, 
            text="Hotel Management System",
            font=("Helvetica", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
    def create_sidebar(self):
        sidebar_frame = tk.Frame(self.root, bg="#34495e", width=200)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Sidebar Buttons
        buttons = [
            ("Room Management", self.show_room_management),
            ("Booking History", self.show_booking_history),
            ("Billing System", self.show_billing_system),
            ("Staff Management", self.show_staff_management),
            ("Services", self.show_services),
            ("Reports & Analytics", self.show_reports_analytics)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                sidebar_frame,
                text=text,
                command=command,
                width=20,
                font=("Helvetica", 10),
                bg="#2c3e50",
                fg="white",
                relief=tk.FLAT
            )
            btn.pack(pady=5, padx=10)
            
    def create_main_content(self):
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create welcome message
        welcome_label = tk.Label(
            self.main_frame,
            text="Welcome to Hotel Management System\nClick 'Room Management' to start",
            font=("Helvetica", 16),
            bg="white",
            fg="#2c3e50"
        )
        welcome_label.pack(expand=True)
        
    def show_room_management(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create top frame for navigation
        top_frame = tk.Frame(self.main_frame, bg="white")
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=self.show_welcome_screen,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Create Room List
        columns = ('Room Number', 'Type', 'Rate', 'Status', 'Last Updated')
        self.room_tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')
        
        for col in columns:
            self.room_tree.heading(col, text=col)
            self.room_tree.column(col, width=150)
        
        # Create buttons frame
        buttons_frame = tk.Frame(self.main_frame, bg="white")
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add operation buttons
        add_btn = tk.Button(
            buttons_frame,
            text="Add Room",
            command=self.show_add_room,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(
            buttons_frame,
            text="Update Room",
            command=lambda: self.show_update_room(self.room_tree.selection()),
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = tk.Button(
            buttons_frame,
            text="Remove Room",
            command=lambda: self.show_remove_room(self.room_tree.selection()),
            bg="#e74c3c",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        remove_btn.pack(side=tk.LEFT, padx=5)

        # Add Book Room button
        book_btn = tk.Button(
            buttons_frame,
            text="Book Room",
            command=lambda: self.show_book_room(self.room_tree.selection()),
            bg="#9b59b6",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        book_btn.pack(side=tk.LEFT, padx=5)
            
        self.room_tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Load rooms from database
        self.load_rooms()
        
    def load_rooms(self):
        self.cursor.execute("SELECT * FROM rooms")
        rooms = self.cursor.fetchall()
        
        for room in rooms:
            status = "Available" if room[4] else "Occupied"
            self.room_tree.insert('', tk.END, values=(
                room[1], room[2], f"${room[3]}", status, room[6]
            ))
            
    def show_welcome_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create welcome message
        welcome_label = tk.Label(
            self.main_frame,
            text="Welcome to Hotel Management System\nClick 'Room Management' to start",
            font=("Helvetica", 16),
            bg="white",
            fg="#2c3e50"
        )
        welcome_label.pack(expand=True)
        
    def show_add_room(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Room")
        add_window.geometry("400x500")
        
        # Create top frame for navigation
        top_frame = tk.Frame(add_window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=add_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Form Fields
        tk.Label(add_window, text="Room Number:").pack(pady=5)
        room_number = tk.Entry(add_window)
        room_number.pack()
        
        tk.Label(add_window, text="Room Type:").pack(pady=5)
        room_type = ttk.Combobox(add_window, values=['SINGLE', 'DOUBLE', 'DELUXE', 'SUITE'])
        room_type.pack()
        
        tk.Label(add_window, text="Rate:").pack(pady=5)
        rate = tk.Entry(add_window)
        rate.pack()
        
        tk.Label(add_window, text="Description:").pack(pady=5)
        description = tk.Text(add_window, height=4)
        description.pack()
        
        def save_room():
            try:
                self.cursor.execute('''
                    INSERT INTO rooms (room_number, room_type, rate, is_available, description, last_updated)
                    VALUES (?, ?, ?, 1, ?, ?)
                ''', (
                    room_number.get(),
                    room_type.get(),
                    float(rate.get()),
                    description.get("1.0", tk.END),
                    datetime.now()
                ))
                self.conn.commit()
                messagebox.showinfo("Success", "Room added successfully!")
                add_window.destroy()
                self.show_room_management()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Room number already exists!")
            except ValueError:
                messagebox.showerror("Error", "Invalid rate value!")
                
        tk.Button(
            add_window,
            text="Save Room",
            command=save_room,
            bg="#2c3e50",
            fg="white"
        ).pack(pady=20)
        
    def show_update_room(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a room to update")
            return
            
        selected_item = selection[0]
        room_data = self.room_tree.item(selected_item)['values']
        
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Room")
        update_window.geometry("400x500")
        
        # Create top frame for navigation
        top_frame = tk.Frame(update_window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=update_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Form Fields
        tk.Label(update_window, text="Room Number:").pack(pady=5)
        room_number = tk.Entry(update_window)
        room_number.insert(0, room_data[0])
        room_number.config(state='readonly')  # Can't change room number
        room_number.pack()
        
        tk.Label(update_window, text="Room Type:").pack(pady=5)
        room_type = ttk.Combobox(update_window, values=['SINGLE', 'DOUBLE', 'DELUXE', 'SUITE'])
        room_type.set(room_data[1])
        room_type.pack()
        
        tk.Label(update_window, text="Rate:").pack(pady=5)
        rate = tk.Entry(update_window)
        rate.insert(0, str(room_data[2]).replace('$', ''))
        rate.pack()
        
        tk.Label(update_window, text="Description:").pack(pady=5)
        description = tk.Text(update_window, height=4)
        
        # Get description from database
        self.cursor.execute("SELECT description FROM rooms WHERE room_number = ?", (room_data[0],))
        desc_data = self.cursor.fetchone()
        if desc_data:
            description.insert("1.0", desc_data[0])
        description.pack()
        
        def save_updates():
            try:
                self.cursor.execute('''
                    UPDATE rooms 
                    SET room_type = ?, rate = ?, description = ?, last_updated = ?
                    WHERE room_number = ?
                ''', (
                    room_type.get(),
                    float(rate.get()),
                    description.get("1.0", tk.END),
                    datetime.now(),
                    room_data[0]
                ))
                self.conn.commit()
                messagebox.showinfo("Success", "Room updated successfully!")
                update_window.destroy()
                self.show_room_management()
            except ValueError:
                messagebox.showerror("Error", "Invalid rate value!")
                
        tk.Button(
            update_window,
            text="Save Updates",
            command=save_updates,
            bg="#2c3e50",
            fg="white"
        ).pack(pady=20)

    def show_remove_room(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a room to remove")
            return
            
        selected_item = selection[0]
        room_number = self.room_tree.item(selected_item)['values'][0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this room?"):
            self.cursor.execute("DELETE FROM rooms WHERE room_number = ?", (room_number,))
            self.conn.commit()
            
            self.show_room_management()
            messagebox.showinfo("Success", "Room removed successfully!")

    def show_billing_system(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create top frame for navigation
        top_frame = tk.Frame(self.main_frame, bg="white")
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=self.show_welcome_screen,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Add title
        title_label = tk.Label(
            top_frame,
            text="Billing System",
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Create main content frame
        content_frame = tk.Frame(self.main_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - Booking selection and billing details
        left_frame = tk.Frame(content_frame, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Booking selection
        tk.Label(left_frame, text="Select Booking:", bg="white", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        
        # Create Booking List
        columns = ('Booking ID', 'Room', 'Customer', 'Check In', 'Check Out', 'Amount')
        self.billing_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.billing_tree.heading(col, text=col)
            self.billing_tree.column(col, width=100)
            
        self.billing_tree.pack(fill=tk.X, pady=10)
        
        # Load unbilled bookings
        self.load_unbilled_bookings()
        
        # Billing details frame
        billing_frame = tk.Frame(left_frame, bg="white", relief=tk.GROOVE, borderwidth=1)
        billing_frame.pack(fill=tk.X, pady=10)
        
        # Billing details
        tk.Label(billing_frame, text="Billing Details", bg="white", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        details_frame = tk.Frame(billing_frame, bg="white")
        details_frame.pack(fill=tk.X, padx=10)
        
        # Variables for billing
        self.subtotal_var = tk.StringVar(value="$0.00")
        self.tax_var = tk.StringVar(value="$0.00")
        self.discount_var = tk.StringVar(value="$0.00")
        self.total_var = tk.StringVar(value="$0.00")
        
        # Labels and entries
        tk.Label(details_frame, text="Subtotal:", bg="white").grid(row=0, column=0, sticky=tk.W, pady=2)
        tk.Label(details_frame, textvariable=self.subtotal_var, bg="white").grid(row=0, column=1, sticky=tk.W, pady=2)
        
        tk.Label(details_frame, text="Tax (10%):", bg="white").grid(row=1, column=0, sticky=tk.W, pady=2)
        tk.Label(details_frame, textvariable=self.tax_var, bg="white").grid(row=1, column=1, sticky=tk.W, pady=2)
        
        tk.Label(details_frame, text="Discount:", bg="white").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.discount_entry = tk.Entry(details_frame, width=10)
        self.discount_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.discount_entry.insert(0, "0")
        
        tk.Label(details_frame, text="Total:", bg="white", font=("Helvetica", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=2)
        tk.Label(details_frame, textvariable=self.total_var, bg="white", font=("Helvetica", 10, "bold")).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Calculate button
        tk.Button(
            billing_frame,
            text="Calculate Total",
            command=self.calculate_bill,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10)
        ).pack(pady=10)
        
        # Right side - Payment and QR code
        right_frame = tk.Frame(content_frame, bg="white", relief=tk.GROOVE, borderwidth=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        # Payment method
        tk.Label(right_frame, text="Payment Method:", bg="white", font=("Helvetica", 10, "bold")).pack(pady=5)
        self.payment_method = ttk.Combobox(right_frame, values=['Cash', 'Credit Card', 'QR Code'])
        self.payment_method.pack(pady=5)
        self.payment_method.set('Cash')
        
        # QR Code frame
        qr_frame = tk.Frame(right_frame, bg="white")
        qr_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # QR Code display
        self.qr_label = tk.Label(qr_frame, bg="white")
        self.qr_label.pack(expand=True)
        
        def update_qr():
            if self.payment_method.get() == 'QR Code':
                self.generate_payment_qr()
        
        self.payment_method.bind('<<ComboboxSelected>>', lambda e: update_qr())
        
        # Generate Invoice and Process Payment buttons
        button_frame = tk.Frame(right_frame, bg="white")
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            button_frame,
            text="Generate Invoice",
            command=self.generate_invoice,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Process Payment",
            command=self.process_payment,
            bg="#9b59b6",
            fg="white",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=5)

    def show_booking_history(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create top frame for navigation
        top_frame = tk.Frame(self.main_frame, bg="white")
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=self.show_welcome_screen,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Add title
        title_label = tk.Label(
            top_frame,
            text="Booking History",
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Create Booking List
        columns = ('Room Number', 'Customer Name', 'Phone', 'Check In', 'Check Out', 'Amount', 'Booking Date')
        self.booking_tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')
        
        # Set column headings and widths
        for col in columns:
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=140)
            
        self.booking_tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Add search frame
        search_frame = tk.Frame(self.main_frame, bg="white")
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(search_frame, text="Search by Customer Name:", bg="white").pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        def search_bookings():
            # Clear current items
            for item in self.booking_tree.get_children():
                self.booking_tree.delete(item)
                
            search_term = f"%{search_entry.get()}%"
            self.cursor.execute('''
                SELECT * FROM bookings 
                WHERE customer_name LIKE ? 
                ORDER BY booking_date DESC
            ''', (search_term,))
            
            self.load_booking_data()
        
        tk.Button(
            search_frame,
            text="Search",
            command=search_bookings,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="Show All",
            command=self.load_booking_data,
            bg="#2c3e50",
            fg="white",
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        # Load initial booking data
        self.load_booking_data()
        
    def load_booking_data(self):
        # Clear current items
        for item in self.booking_tree.get_children():
            self.booking_tree.delete(item)
            
        self.cursor.execute('''
            SELECT * FROM bookings 
            ORDER BY booking_date DESC
        ''')
        bookings = self.cursor.fetchall()
        
        for booking in bookings:
            self.booking_tree.insert('', tk.END, values=(
                booking[1],  # room_number
                booking[2],  # customer_name
                booking[3],  # customer_phone
                booking[4],  # check_in_date
                booking[5],  # check_out_date
                f"${booking[6]:.2f}",  # total_amount
                booking[7]   # booking_date
            ))

    def show_book_room(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a room to book")
            return
            
        selected_item = selection[0]
        room_data = self.room_tree.item(selected_item)['values']
        
        # Check if room is available
        if room_data[3] != "Available":
            messagebox.showerror("Error", "This room is not available for booking")
            return
        
        book_window = tk.Toplevel(self.root)
        book_window.title(f"Book Room {room_data[0]}")
        book_window.geometry("400x600")
        
        # Create top frame for navigation
        top_frame = tk.Frame(book_window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=book_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Room Info
        info_frame = tk.Frame(book_window, relief=tk.GROOVE, borderwidth=1)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(info_frame, text=f"Room: {room_data[0]}", font=("Helvetica", 12, "bold")).pack(pady=5)
        tk.Label(info_frame, text=f"Type: {room_data[1]}").pack()
        tk.Label(info_frame, text=f"Rate: {room_data[2]} per night").pack()
        
        # Booking Form
        form_frame = tk.Frame(book_window)
        form_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        tk.Label(form_frame, text="Customer Name:").pack(pady=5)
        customer_name = tk.Entry(form_frame)
        customer_name.pack(fill=tk.X)
        
        tk.Label(form_frame, text="Phone Number:").pack(pady=5)
        phone = tk.Entry(form_frame)
        phone.pack(fill=tk.X)
        
        tk.Label(form_frame, text="Check-in Date (YYYY-MM-DD):").pack(pady=5)
        check_in = tk.Entry(form_frame)
        check_in.pack(fill=tk.X)
        
        tk.Label(form_frame, text="Check-out Date (YYYY-MM-DD):").pack(pady=5)
        check_out = tk.Entry(form_frame)
        check_out.pack(fill=tk.X)
        
        def save_booking():
            try:
                # Validate dates
                check_in_date = datetime.strptime(check_in.get(), "%Y-%m-%d")
                check_out_date = datetime.strptime(check_out.get(), "%Y-%m-%d")
                
                if check_in_date >= check_out_date:
                    messagebox.showerror("Error", "Check-out date must be after check-in date")
                    return
                
                if check_in_date < datetime.now():
                    messagebox.showerror("Error", "Check-in date cannot be in the past")
                    return
                
                # Calculate total amount
                days = (check_out_date - check_in_date).days
                rate = float(room_data[2].replace('$', ''))
                total_amount = days * rate
                
                # Save booking
                self.cursor.execute('''
                    INSERT INTO bookings (
                        room_number, customer_name, customer_phone,
                        check_in_date, check_out_date, total_amount, booking_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    room_data[0],
                    customer_name.get(),
                    phone.get(),
                    check_in.get(),
                    check_out.get(),
                    total_amount,
                    datetime.now()
                ))
                
                # Update room availability
                self.cursor.execute('''
                    UPDATE rooms 
                    SET is_available = 0, last_updated = ?
                    WHERE room_number = ?
                ''', (datetime.now(), room_data[0]))
                
                self.conn.commit()
                messagebox.showinfo("Success", f"Room booked successfully!\nTotal Amount: ${total_amount:.2f}")
                book_window.destroy()
                self.show_room_management()
                
            except ValueError as e:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                
        tk.Button(
            form_frame,
            text="Book Room",
            command=save_booking,
            bg="#9b59b6",
            fg="white",
            font=("Helvetica", 12)
        ).pack(pady=20)

    def load_unbilled_bookings(self):
        # Clear current items
        for item in self.billing_tree.get_children():
            self.billing_tree.delete(item)
            
        self.cursor.execute('''
            SELECT b.id, b.room_number, b.customer_name, b.check_in_date, 
                   b.check_out_date, b.total_amount
            FROM bookings b
            LEFT JOIN bills bi ON b.id = bi.booking_id
            WHERE bi.id IS NULL
            ORDER BY b.booking_date DESC
        ''')
        bookings = self.cursor.fetchall()
        
        for booking in bookings:
            self.billing_tree.insert('', tk.END, values=(
                booking[0],  # booking_id
                booking[1],  # room_number
                booking[2],  # customer_name
                booking[3],  # check_in_date
                booking[4],  # check_out_date
                f"${booking[5]:.2f}"  # total_amount
            ))

    def calculate_bill(self):
        selection = self.billing_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a booking to calculate bill")
            return
            
        selected_item = selection[0]
        booking_data = self.billing_tree.item(selected_item)['values']
        
        # Get subtotal from booking
        subtotal = float(booking_data[5].replace('$', ''))
        
        # Calculate tax
        tax = subtotal * TAX_RATE
        
        # Get discount
        try:
            discount = float(self.discount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid discount amount")
            return
        
        # Calculate total
        total = subtotal + tax - discount
        
        # Update display
        self.subtotal_var.set(f"${subtotal:.2f}")
        self.tax_var.set(f"${tax:.2f}")
        self.discount_var.set(f"${discount:.2f}")
        self.total_var.set(f"${total:.2f}")

    def generate_payment_qr(self):
        total = self.total_var.get().replace('$', '')
        if total == "0.00":
            messagebox.showwarning("Warning", "Please calculate the bill first")
            return
            
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"Amount: {total}")
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image = qr_image.resize((200, 200))
        
        # Save QR code
        qr_image.save(QR_CODE_PATH)
        
        # Display QR code
        qr_photo = ImageTk.PhotoImage(Image.open(QR_CODE_PATH))
        self.qr_label.configure(image=qr_photo)
        self.qr_label.image = qr_photo

    def generate_invoice(self):
        selection = self.billing_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a booking to generate invoice")
            return
            
        if self.total_var.get() == "$0.00":
            messagebox.showwarning("Warning", "Please calculate the bill first")
            return
            
        selected_item = selection[0]
        booking_data = self.billing_tree.item(selected_item)['values']
        
        # Create invoice content
        invoice_content = f"""
        HOTEL MANAGEMENT SYSTEM
        =====================
        Invoice Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Booking Details:
        ---------------
        Booking ID: {booking_data[0]}
        Room Number: {booking_data[1]}
        Customer Name: {booking_data[2]}
        Check-in Date: {booking_data[3]}
        Check-out Date: {booking_data[4]}
        
        Billing Details:
        ---------------
        Subtotal: {self.subtotal_var.get()}
        Tax (10%): {self.tax_var.get()}
        Discount: {self.discount_var.get()}
        
        Total Amount: {self.total_var.get()}
        
        Payment Method: {self.payment_method.get()}
        
        Thank you for your business!
        """
        
        # Save invoice to file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"invoice_{booking_data[0]}.txt"
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(invoice_content)
            messagebox.showinfo("Success", "Invoice generated successfully!")

    def process_payment(self):
        selection = self.billing_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a booking to process payment")
            return
            
        if self.total_var.get() == "$0.00":
            messagebox.showwarning("Warning", "Please calculate the bill first")
            return
            
        selected_item = selection[0]
        booking_data = self.billing_tree.item(selected_item)['values']
        
        try:
            # Save bill to database
            self.cursor.execute('''
                INSERT INTO bills (
                    booking_id, subtotal, tax_amount, discount_amount,
                    total_amount, payment_status, payment_method, bill_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                booking_data[0],  # booking_id
                float(self.subtotal_var.get().replace('$', '')),
                float(self.tax_var.get().replace('$', '')),
                float(self.discount_var.get().replace('$', '')),
                float(self.total_var.get().replace('$', '')),
                'Paid',
                self.payment_method.get(),
                datetime.now()
            ))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Payment processed successfully!")
            
            # Refresh the billing list
            self.load_unbilled_bookings()
            
            # Clear the current calculation
            self.subtotal_var.set("$0.00")
            self.tax_var.set("$0.00")
            self.discount_var.set("$0.00")
            self.total_var.set("$0.00")
            self.discount_entry.delete(0, tk.END)
            self.discount_entry.insert(0, "0")
            
            # Clear QR code if displayed
            self.qr_label.configure(image='')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process payment: {str(e)}")

    def show_staff_management(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create top frame for navigation
        top_frame = tk.Frame(self.main_frame, bg="white")
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=self.show_welcome_screen,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Add title
        title_label = tk.Label(
            top_frame,
            text="Staff Management",
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Create buttons frame
        buttons_frame = tk.Frame(self.main_frame, bg="white")
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add operation buttons
        add_btn = tk.Button(
            buttons_frame,
            text="Add Staff",
            command=self.show_add_staff,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        salary_btn = tk.Button(
            buttons_frame,
            text="Process Salary",
            command=lambda: self.show_process_salary(self.staff_tree.selection()),
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        salary_btn.pack(side=tk.LEFT, padx=5)
        
        history_btn = tk.Button(
            buttons_frame,
            text="Salary History",
            command=lambda: self.show_salary_history(self.staff_tree.selection()),
            bg="#9b59b6",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        history_btn.pack(side=tk.LEFT, padx=5)
        
        # Create Staff List
        columns = ('ID', 'Name', 'Position', 'Phone', 'Email', 'Join Date', 'Base Salary', 'Status')
        self.staff_tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')
        
        for col in columns:
            self.staff_tree.heading(col, text=col)
            self.staff_tree.column(col, width=120)
            
        self.staff_tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Load staff data
        self.load_staff_data()

    def load_staff_data(self):
        # Clear current items
        for item in self.staff_tree.get_children():
            self.staff_tree.delete(item)
            
        self.cursor.execute('SELECT * FROM staff ORDER BY name')
        staff = self.cursor.fetchall()
        
        for employee in staff:
            self.staff_tree.insert('', tk.END, values=(
                employee[1],  # employee_id
                employee[2],  # name
                employee[3],  # position
                employee[4],  # phone
                employee[5],  # email
                employee[7],  # join_date
                f"${employee[8]:.2f}",  # base_salary
                employee[9]   # status
            ))

    def show_add_staff(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Staff")
        add_window.geometry("500x700")
        
        # Create top frame for navigation
        top_frame = tk.Frame(add_window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=add_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Form frame
        form_frame = tk.Frame(add_window)
        form_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        # Form fields
        fields = [
            ("Employee ID:", "entry"),
            ("Name:", "entry"),
            ("Position:", "combobox", ["Manager", "Receptionist", "Housekeeper", "Maintenance", "Security"]),
            ("Phone:", "entry"),
            ("Email:", "entry"),
            ("Address:", "text"),
            ("Join Date (YYYY-MM-DD):", "entry"),
            ("Base Salary:", "entry"),
            ("Status:", "combobox", ["Active", "On Leave", "Terminated"])
        ]
        
        # Store widgets references
        self.staff_entries = {}
        
        for i, (label_text, field_type, *args) in enumerate(fields):
            tk.Label(form_frame, text=label_text).grid(row=i, column=0, pady=5, sticky=tk.W)
            
            if field_type == "entry":
                widget = tk.Entry(form_frame, width=30)
                widget.grid(row=i, column=1, pady=5, padx=5, sticky=tk.W)
                self.staff_entries[label_text] = widget
            elif field_type == "text":
                widget = tk.Text(form_frame, height=4, width=30)
                widget.grid(row=i, column=1, pady=5, padx=5, sticky=tk.W)
                self.staff_entries[label_text] = widget
            elif field_type == "combobox":
                widget = ttk.Combobox(form_frame, values=args[0], width=27)
                widget.grid(row=i, column=1, pady=5, padx=5, sticky=tk.W)
                self.staff_entries[label_text] = widget
        
        def save_staff():
            try:
                # Validate join date
                join_date = datetime.strptime(
                    self.staff_entries["Join Date (YYYY-MM-DD):"].get(),
                    "%Y-%m-%d"
                )
                
                # Validate salary
                base_salary = float(self.staff_entries["Base Salary:"].get())
                
                # Insert into database
                self.cursor.execute('''
                    INSERT INTO staff (
                        employee_id, name, position, phone, email,
                        address, join_date, base_salary, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.staff_entries["Employee ID:"].get(),
                    self.staff_entries["Name:"].get(),
                    self.staff_entries["Position:"].get(),
                    self.staff_entries["Phone:"].get(),
                    self.staff_entries["Email:"].get(),
                    self.staff_entries["Address:"].get("1.0", tk.END),
                    self.staff_entries["Join Date (YYYY-MM-DD):"].get(),
                    base_salary,
                    self.staff_entries["Status:"].get()
                ))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Staff member added successfully!")
                add_window.destroy()
                self.load_staff_data()
                
            except ValueError:
                messagebox.showerror("Error", "Invalid date format or salary value")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Employee ID already exists")
        
        # Save button
        tk.Button(
            form_frame,
            text="Save Staff",
            command=save_staff,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 12)
        ).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def show_process_salary(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a staff member")
            return
            
        selected_item = selection[0]
        staff_data = self.staff_tree.item(selected_item)['values']
        
        salary_window = tk.Toplevel(self.root)
        salary_window.title(f"Process Salary - {staff_data[1]}")
        salary_window.geometry("400x600")
        
        # Create top frame for navigation
        top_frame = tk.Frame(salary_window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=salary_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Main content
        content_frame = tk.Frame(salary_window)
        content_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        # Staff info
        info_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=1)
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(info_frame, text=f"Employee: {staff_data[1]}", font=("Helvetica", 12, "bold")).pack(pady=5)
        tk.Label(info_frame, text=f"Position: {staff_data[2]}").pack()
        tk.Label(info_frame, text=f"Base Salary: {staff_data[6]}").pack()
        
        # Salary details
        details_frame = tk.Frame(content_frame)
        details_frame.pack(fill=tk.X, pady=10)
        
        # Base salary (readonly)
        tk.Label(details_frame, text="Base Salary:").grid(row=0, column=0, pady=5, sticky=tk.W)
        base_salary = tk.Entry(details_frame)
        base_salary.insert(0, staff_data[6].replace('$', ''))
        base_salary.config(state='readonly')
        base_salary.grid(row=0, column=1, pady=5, padx=5)
        
        # Bonus
        tk.Label(details_frame, text="Bonus:").grid(row=1, column=0, pady=5, sticky=tk.W)
        bonus_entry = tk.Entry(details_frame)
        bonus_entry.insert(0, "0")
        bonus_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Deductions
        tk.Label(details_frame, text="Deductions:").grid(row=2, column=0, pady=5, sticky=tk.W)
        deductions_entry = tk.Entry(details_frame)
        deductions_entry.insert(0, "0")
        deductions_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Payment method
        tk.Label(details_frame, text="Payment Method:").grid(row=3, column=0, pady=5, sticky=tk.W)
        payment_method = ttk.Combobox(details_frame, values=['Bank Transfer', 'Cash', 'Check'])
        payment_method.set('Bank Transfer')
        payment_method.grid(row=3, column=1, pady=5, padx=5)
        
        # Remarks
        tk.Label(details_frame, text="Remarks:").grid(row=4, column=0, pady=5, sticky=tk.W)
        remarks = tk.Text(details_frame, height=4, width=20)
        remarks.grid(row=4, column=1, pady=5, padx=5)
        
        def calculate_salary():
            try:
                base = float(base_salary.get())
                bonus = float(bonus_entry.get())
                deductions = float(deductions_entry.get())
                net_salary = base + bonus - deductions
                
                result_label.config(text=f"Net Salary: ${net_salary:.2f}")
                return net_salary
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric values")
                return None
        
        def save_salary():
            net_salary = calculate_salary()
            if net_salary is None:
                return
                
            try:
                self.cursor.execute('''
                    INSERT INTO salary_payments (
                        employee_id, payment_date, base_salary, bonus,
                        deductions, net_salary, payment_method, remarks
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    staff_data[0],  # employee_id
                    datetime.now().strftime('%Y-%m-%d'),
                    float(base_salary.get()),
                    float(bonus_entry.get()),
                    float(deductions_entry.get()),
                    net_salary,
                    payment_method.get(),
                    remarks.get("1.0", tk.END)
                ))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Salary processed successfully!")
                salary_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process salary: {str(e)}")
        
        # Calculate button
        tk.Button(
            content_frame,
            text="Calculate",
            command=calculate_salary,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10)
        ).pack(pady=10)
        
        # Result label
        result_label = tk.Label(content_frame, text="Net Salary: $0.00", font=("Helvetica", 12, "bold"))
        result_label.pack(pady=10)
        
        # Process button
        tk.Button(
            content_frame,
            text="Process Salary",
            command=save_salary,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 12)
        ).pack(pady=20)

    def show_salary_history(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a staff member")
            return
            
        selected_item = selection[0]
        staff_data = self.staff_tree.item(selected_item)['values']
        
        history_window = tk.Toplevel(self.root)
        history_window.title(f"Salary History - {staff_data[1]}")
        history_window.geometry("800x600")
        
        # Create top frame for navigation
        top_frame = tk.Frame(history_window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=history_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Staff info
        tk.Label(
            history_window,
            text=f"Salary History for {staff_data[1]} ({staff_data[2]})",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)
        
        # Create salary history list
        columns = ('Payment Date', 'Base Salary', 'Bonus', 'Deductions', 'Net Salary', 'Payment Method', 'Remarks')
        history_tree = ttk.Treeview(history_window, columns=columns, show='headings')
        
        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=100)
            
        history_tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Load salary history
        self.cursor.execute('''
            SELECT payment_date, base_salary, bonus, deductions,
                   net_salary, payment_method, remarks
            FROM salary_payments
            WHERE employee_id = ?
            ORDER BY payment_date DESC
        ''', (staff_data[0],))
        
        payments = self.cursor.fetchall()
        
        for payment in payments:
            history_tree.insert('', tk.END, values=(
                payment[0],
                f"${payment[1]:.2f}",
                f"${payment[2]:.2f}",
                f"${payment[3]:.2f}",
                f"${payment[4]:.2f}",
                payment[5],
                payment[6]
            ))

    def show_reports_analytics(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create top frame for navigation
        top_frame = tk.Frame(self.main_frame, bg="white")
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=self.show_welcome_screen,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Add title
        title_label = tk.Label(
            top_frame,
            text="Reports & Analytics",
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Create buttons frame
        buttons_frame = tk.Frame(self.main_frame, bg="white")
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add operation buttons
        weekly_btn = tk.Button(
            buttons_frame,
            text="Weekly Analytics",
            command=self.show_weekly_analytics,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        weekly_btn.pack(side=tk.LEFT, padx=5)
        
        monthly_btn = tk.Button(
            buttons_frame,
            text="Monthly Analytics",
            command=self.show_monthly_analytics,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        monthly_btn.pack(side=tk.LEFT, padx=5)
        
        trends_btn = tk.Button(
            buttons_frame,
            text="Booking Trends",
            command=self.show_booking_trends,
            bg="#9b59b6",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        trends_btn.pack(side=tk.LEFT, padx=5)
        
        revenue_btn = tk.Button(
            buttons_frame,
            text="Revenue Analysis",
            command=self.show_revenue_analysis,
            bg="#e67e22",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        revenue_btn.pack(side=tk.LEFT, padx=5)
        
        # Create main content frame
        self.analytics_frame = tk.Frame(self.main_frame, bg="white")
        self.analytics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Show welcome message
        welcome_label = tk.Label(
            self.analytics_frame,
            text="Select an analytics option from above to view reports",
            font=("Helvetica", 14),
            bg="white",
            fg="#2c3e50"
        )
        welcome_label.pack(expand=True)

    def show_weekly_analytics(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()
            
        # Get current week's data
        current_date = datetime.now()
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Create analytics display
        analytics_frame = tk.Frame(self.analytics_frame, bg="white")
        analytics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        tk.Label(
            analytics_frame,
            text=f"Weekly Analytics ({week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')})",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Get analytics data
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total_bookings,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as average_booking_value,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM rooms) as occupancy_rate
            FROM bookings
            WHERE booking_date BETWEEN ? AND ?
        ''', (week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))
        
        analytics = self.cursor.fetchone()
        
        # Display analytics
        metrics_frame = tk.Frame(analytics_frame, bg="white")
        metrics_frame.pack(fill=tk.X, pady=10)
        
        metrics = [
            ("Total Bookings", analytics[0] or 0),
            ("Total Revenue", f"${analytics[1] or 0:.2f}"),
            ("Average Booking Value", f"${analytics[2] or 0:.2f}"),
            ("Occupancy Rate", f"{analytics[3] or 0:.1f}%")
        ]
        
        for i, (label, value) in enumerate(metrics):
            metric_frame = tk.Frame(metrics_frame, bg="white", relief=tk.GROOVE, borderwidth=1)
            metric_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            tk.Label(
                metric_frame,
                text=label,
                font=("Helvetica", 10),
                bg="white",
                fg="#2c3e50"
            ).pack(pady=5)
            
            tk.Label(
                metric_frame,
                text=value,
                font=("Helvetica", 12, "bold"),
                bg="white",
                fg="#2c3e50"
            ).pack(pady=5)

    def show_monthly_analytics(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()
            
        # Get current month's data
        current_date = datetime.now()
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        # Create analytics display
        analytics_frame = tk.Frame(self.analytics_frame, bg="white")
        analytics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        tk.Label(
            analytics_frame,
            text=f"Monthly Analytics ({month_start.strftime('%Y-%m')})",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Get analytics data
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total_bookings,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as average_booking_value,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM rooms) as occupancy_rate
            FROM bookings
            WHERE booking_date BETWEEN ? AND ?
        ''', (month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')))
        
        analytics = self.cursor.fetchone()
        
        # Display analytics
        metrics_frame = tk.Frame(analytics_frame, bg="white")
        metrics_frame.pack(fill=tk.X, pady=10)
        
        metrics = [
            ("Total Bookings", analytics[0] or 0),
            ("Total Revenue", f"${analytics[1] or 0:.2f}"),
            ("Average Booking Value", f"${analytics[2] or 0:.2f}"),
            ("Occupancy Rate", f"{analytics[3] or 0:.1f}%")
        ]
        
        for i, (label, value) in enumerate(metrics):
            metric_frame = tk.Frame(metrics_frame, bg="white", relief=tk.GROOVE, borderwidth=1)
            metric_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            tk.Label(
                metric_frame,
                text=label,
                font=("Helvetica", 10),
                bg="white",
                fg="#2c3e50"
            ).pack(pady=5)
            
            tk.Label(
                metric_frame,
                text=value,
                font=("Helvetica", 12, "bold"),
                bg="white",
                fg="#2c3e50"
            ).pack(pady=5)

    def show_booking_trends(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()
            
        # Create analytics display
        analytics_frame = tk.Frame(self.analytics_frame, bg="white")
        analytics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        tk.Label(
            analytics_frame,
            text="Booking Trends (Last 6 Months)",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Get monthly booking trends
        self.cursor.execute('''
            SELECT 
                strftime('%Y-%m', booking_date) as month,
                COUNT(*) as total_bookings,
                SUM(total_amount) as total_revenue
            FROM bookings
            WHERE booking_date >= date('now', '-6 months')
            GROUP BY month
            ORDER BY month
        ''')
        
        trends = self.cursor.fetchall()
        
        # Create trends display
        trends_frame = tk.Frame(analytics_frame, bg="white")
        trends_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create Treeview for trends
        columns = ('Month', 'Total Bookings', 'Total Revenue')
        trends_tree = ttk.Treeview(trends_frame, columns=columns, show='headings')
        
        for col in columns:
            trends_tree.heading(col, text=col)
            trends_tree.column(col, width=150)
            
        trends_tree.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Add data to Treeview
        for month, bookings, revenue in trends:
            trends_tree.insert('', tk.END, values=(
                month,
                bookings,
                f"${revenue:.2f}"
            ))
        
        # Calculate growth rates
        if len(trends) >= 2:
            current_month = trends[-1]
            previous_month = trends[-2]
            
            booking_growth = ((current_month[1] - previous_month[1]) / previous_month[1]) * 100
            revenue_growth = ((current_month[2] - previous_month[2]) / previous_month[2]) * 100
            
            growth_frame = tk.Frame(analytics_frame, bg="white")
            growth_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(
                growth_frame,
                text=f"Booking Growth: {booking_growth:.1f}%",
                font=("Helvetica", 10),
                bg="white",
                fg="#2c3e50"
            ).pack(side=tk.LEFT, padx=10)
            
            tk.Label(
                growth_frame,
                text=f"Revenue Growth: {revenue_growth:.1f}%",
                font=("Helvetica", 10),
                bg="white",
                fg="#2c3e50"
            ).pack(side=tk.LEFT, padx=10)

    def show_revenue_analysis(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()
            
        # Create analytics display
        analytics_frame = tk.Frame(self.analytics_frame, bg="white")
        analytics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        tk.Label(
            analytics_frame,
            text="Revenue Analysis",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Get revenue data
        self.cursor.execute('''
            SELECT 
                strftime('%Y-%m', b.bill_date) as month,
                SUM(b.total_amount) as total_revenue,
                SUM(b.tax_amount) as total_tax,
                SUM(b.discount_amount) as total_discounts
            FROM bills b
            WHERE b.bill_date >= date('now', '-12 months')
            GROUP BY month
            ORDER BY month
        ''')
        
        revenue_data = self.cursor.fetchall()
        
        # Create revenue display
        revenue_frame = tk.Frame(analytics_frame, bg="white")
        revenue_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create Treeview for revenue
        columns = ('Month', 'Total Revenue', 'Tax', 'Discounts', 'Net Revenue')
        revenue_tree = ttk.Treeview(revenue_frame, columns=columns, show='headings')
        
        for col in columns:
            revenue_tree.heading(col, text=col)
            revenue_tree.column(col, width=120)
            
        revenue_tree.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Add data to Treeview
        for month, revenue, tax, discounts in revenue_data:
            net_revenue = revenue - tax - discounts
            revenue_tree.insert('', tk.END, values=(
                month,
                f"${revenue:.2f}",
                f"${tax:.2f}",
                f"${discounts:.2f}",
                f"${net_revenue:.2f}"
            ))
        
        # Calculate summary statistics
        if revenue_data:
            total_revenue = sum(row[1] for row in revenue_data)
            total_tax = sum(row[2] for row in revenue_data)
            total_discounts = sum(row[3] for row in revenue_data)
            net_revenue = total_revenue - total_tax - total_discounts
            
            summary_frame = tk.Frame(analytics_frame, bg="white")
            summary_frame.pack(fill=tk.X, pady=10)
            
            metrics = [
                ("Total Revenue", f"${total_revenue:.2f}"),
                ("Total Tax", f"${total_tax:.2f}"),
                ("Total Discounts", f"${total_discounts:.2f}"),
                ("Net Revenue", f"${net_revenue:.2f}")
            ]
            
            for label, value in metrics:
                metric_frame = tk.Frame(summary_frame, bg="white", relief=tk.GROOVE, borderwidth=1)
                metric_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                tk.Label(
                    metric_frame,
                    text=label,
                    font=("Helvetica", 10),
                    bg="white",
                    fg="#2c3e50"
                ).pack(pady=5)
                
                tk.Label(
                    metric_frame,
                    text=value,
                    font=("Helvetica", 12, "bold"),
                    bg="white",
                    fg="#2c3e50"
                ).pack(pady=5)

    def show_services(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create top frame for navigation
        top_frame = tk.Frame(self.main_frame, bg="white")
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=self.show_welcome_screen,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Add title
        title_label = tk.Label(
            top_frame,
            text="Hotel Services",
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Create buttons frame
        buttons_frame = tk.Frame(self.main_frame, bg="white")
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add operation buttons
        request_btn = tk.Button(
            buttons_frame,
            text="Request Service",
            command=self.show_request_service,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        request_btn.pack(side=tk.LEFT, padx=5)
        
        manage_btn = tk.Button(
            buttons_frame,
            text="Manage Services",
            command=self.show_manage_services,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        manage_btn.pack(side=tk.LEFT, padx=5)
        
        history_btn = tk.Button(
            buttons_frame,
            text="Service History",
            command=self.show_service_history,
            bg="#9b59b6",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        history_btn.pack(side=tk.LEFT, padx=5)
        
        # Create main content frame
        self.services_frame = tk.Frame(self.main_frame, bg="white")
        self.services_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Show welcome message
        welcome_label = tk.Label(
            self.services_frame,
            text="Select an option from above to manage hotel services",
            font=("Helvetica", 14),
            bg="white",
            fg="#2c3e50"
        )
        welcome_label.pack(expand=True)

    def show_request_service(self):
        for widget in self.services_frame.winfo_children():
            widget.destroy()
            
        # Create request service interface
        request_frame = tk.Frame(self.services_frame, bg="white")
        request_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        tk.Label(
            request_frame,
            text="Request Hotel Service",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Booking selection
        booking_frame = tk.Frame(request_frame, bg="white")
        booking_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            booking_frame,
            text="Select Booking:",
            bg="white",
            font=("Helvetica", 10, "bold")
        ).pack(anchor=tk.W)
        
        # Create Booking List
        columns = ('Booking ID', 'Room', 'Customer', 'Check In', 'Check Out')
        self.service_booking_tree = ttk.Treeview(booking_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            self.service_booking_tree.heading(col, text=col)
            self.service_booking_tree.column(col, width=120)
            
        self.service_booking_tree.pack(fill=tk.X, pady=5)
        
        # Load active bookings
        self.load_active_bookings()
        
        # Service selection
        service_frame = tk.Frame(request_frame, bg="white")
        service_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            service_frame,
            text="Select Service:",
            bg="white",
            font=("Helvetica", 10, "bold")
        ).pack(anchor=tk.W)
        
        # Create Service List
        columns = ('Service', 'Category', 'Price', 'Description')
        self.service_tree = ttk.Treeview(service_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            self.service_tree.heading(col, text=col)
            self.service_tree.column(col, width=150)
            
        self.service_tree.pack(fill=tk.X, pady=5)
        
        # Load available services
        self.load_available_services()
        
        # Quantity and notes
        details_frame = tk.Frame(request_frame, bg="white")
        details_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(details_frame, text="Quantity:").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.quantity_entry = tk.Entry(details_frame, width=10)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        tk.Label(details_frame, text="Notes:").grid(row=1, column=0, pady=5, sticky=tk.W)
        self.notes_text = tk.Text(details_frame, height=3, width=30)
        self.notes_text.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Total amount
        self.total_var = tk.StringVar(value="$0.00")
        tk.Label(
            details_frame,
            textvariable=self.total_var,
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg="#2c3e50"
        ).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Calculate button
        tk.Button(
            details_frame,
            text="Calculate Total",
            command=self.calculate_service_total,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10)
        ).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Submit button
        tk.Button(
            request_frame,
            text="Submit Request",
            command=self.submit_service_request,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 12)
        ).pack(pady=20)

    def load_active_bookings(self):
        # Clear current items
        for item in self.service_booking_tree.get_children():
            self.service_booking_tree.delete(item)
            
        # Get active bookings
        self.cursor.execute('''
            SELECT id, room_number, customer_name, check_in_date, check_out_date
            FROM bookings
            WHERE check_out_date >= date('now')
            ORDER BY check_in_date DESC
        ''')
        
        bookings = self.cursor.fetchall()
        
        for booking in bookings:
            self.service_booking_tree.insert('', tk.END, values=(
                booking[0],  # booking_id
                booking[1],  # room_number
                booking[2],  # customer_name
                booking[3],  # check_in_date
                booking[4]   # check_out_date
            ))

    def load_available_services(self):
        # Clear current items
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
            
        # Get active services
        self.cursor.execute('''
            SELECT id, service_name, category, price, description
            FROM services
            WHERE is_active = 1
            ORDER BY category, service_name
        ''')
        
        services = self.cursor.fetchall()
        
        for service in services:
            self.service_tree.insert('', tk.END, values=(
                service[1],  # service_name
                service[2],  # category
                f"${service[3]:.2f}",  # price
                service[4]   # description
            ))

    def calculate_service_total(self):
        selection = self.service_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a service")
            return
            
        try:
            quantity = int(self.quantity_entry.get())
            if quantity < 1:
                raise ValueError("Quantity must be at least 1")
                
            selected_item = selection[0]
            service_data = self.service_tree.item(selected_item)['values']
            price = float(service_data[2].replace('$', ''))
            
            total = price * quantity
            self.total_var.set(f"${total:.2f}")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def submit_service_request(self):
        booking_selection = self.service_booking_tree.selection()
        service_selection = self.service_tree.selection()
        
        if not booking_selection or not service_selection:
            messagebox.showwarning("Warning", "Please select both booking and service")
            return
            
        try:
            quantity = int(self.quantity_entry.get())
            if quantity < 1:
                raise ValueError("Quantity must be at least 1")
                
            booking_data = self.service_booking_tree.item(booking_selection[0])['values']
            service_data = self.service_tree.item(service_selection[0])['values']
            price = float(service_data[2].replace('$', ''))
            total = price * quantity
            
            # Get service ID
            self.cursor.execute('SELECT id FROM services WHERE service_name = ?', (service_data[0],))
            service_id = self.cursor.fetchone()[0]
            
            # Save service request
            self.cursor.execute('''
                INSERT INTO service_requests (
                    booking_id, service_id, quantity, total_amount,
                    request_date, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                booking_data[0],  # booking_id
                service_id,
                quantity,
                total,
                datetime.now(),
                'Pending',
                self.notes_text.get("1.0", tk.END)
            ))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Service request submitted successfully!")
            
            # Clear form
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, "1")
            self.notes_text.delete("1.0", tk.END)
            self.total_var.set("$0.00")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_manage_services(self):
        for widget in self.services_frame.winfo_children():
            widget.destroy()
            
        # Create manage services interface
        manage_frame = tk.Frame(self.services_frame, bg="white")
        manage_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        tk.Label(
            manage_frame,
            text="Manage Hotel Services",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Create buttons frame
        buttons_frame = tk.Frame(manage_frame, bg="white")
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Add operation buttons
        add_btn = tk.Button(
            buttons_frame,
            text="Add Service",
            command=self.show_add_service,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(
            buttons_frame,
            text="Update Service",
            command=lambda: self.show_update_service(self.service_manage_tree.selection()),
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        toggle_btn = tk.Button(
            buttons_frame,
            text="Toggle Service",
            command=lambda: self.toggle_service(self.service_manage_tree.selection()),
            bg="#9b59b6",
            fg="white",
            font=("Helvetica", 10),
            width=15
        )
        toggle_btn.pack(side=tk.LEFT, padx=5)
        
        # Create Service List
        columns = ('ID', 'Service', 'Category', 'Price', 'Description', 'Status')
        self.service_manage_tree = ttk.Treeview(manage_frame, columns=columns, show='headings')
        
        for col in columns:
            self.service_manage_tree.heading(col, text=col)
            self.service_manage_tree.column(col, width=120)
            
        self.service_manage_tree.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Load all services
        self.load_all_services()

    def load_all_services(self):
        # Clear current items
        for item in self.service_manage_tree.get_children():
            self.service_manage_tree.delete(item)
            
        # Get all services
        self.cursor.execute('''
            SELECT id, service_name, category, price, description, is_active
            FROM services
            ORDER BY category, service_name
        ''')
        
        services = self.cursor.fetchall()
        
        for service in services:
            self.service_manage_tree.insert('', tk.END, values=(
                service[0],  # id
                service[1],  # service_name
                service[2],  # category
                f"${service[3]:.2f}",  # price
                service[4],  # description
                "Active" if service[5] else "Inactive"  # status
            ))

    def show_add_service(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Service")
        add_window.geometry("400x500")
        
        # Create top frame for navigation
        top_frame = tk.Frame(add_window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=add_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Form Fields
        tk.Label(add_window, text="Service Name:").pack(pady=5)
        service_name = tk.Entry(add_window)
        service_name.pack()
        
        tk.Label(add_window, text="Category:").pack(pady=5)
        category = ttk.Combobox(add_window, values=['Cleaning', 'Laundry', 'Food', 'Other'])
        category.pack()
        
        tk.Label(add_window, text="Price:").pack(pady=5)
        price = tk.Entry(add_window)
        price.pack()
        
        tk.Label(add_window, text="Description:").pack(pady=5)
        description = tk.Text(add_window, height=4)
        description.pack()
        
        def save_service():
            try:
                self.cursor.execute('''
                    INSERT INTO services (service_name, category, price, description, is_active)
                    VALUES (?, ?, ?, ?, 1)
                ''', (
                    service_name.get(),
                    category.get(),
                    float(price.get()),
                    description.get("1.0", tk.END)
                ))
                self.conn.commit()
                messagebox.showinfo("Success", "Service added successfully!")
                add_window.destroy()
                self.load_all_services()
            except ValueError:
                messagebox.showerror("Error", "Invalid price value!")
                
        tk.Button(
            add_window,
            text="Save Service",
            command=save_service,
            bg="#2c3e50",
            fg="white"
        ).pack(pady=20)

    def show_update_service(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a service to update")
            return
            
        selected_item = selection[0]
        service_data = self.service_manage_tree.item(selected_item)['values']
        
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Service")
        update_window.geometry("400x500")
        
        # Create top frame for navigation
        top_frame = tk.Frame(update_window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = tk.Button(
            top_frame,
            text="← Back",
            command=update_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Helvetica", 10),
            width=10
        )
        back_btn.pack(side=tk.LEFT)
        
        # Form Fields
        tk.Label(update_window, text="Service Name:").pack(pady=5)
        service_name = tk.Entry(update_window)
        service_name.insert(0, service_data[1])
        service_name.pack()
        
        tk.Label(update_window, text="Category:").pack(pady=5)
        category = ttk.Combobox(update_window, values=['Cleaning', 'Laundry', 'Food', 'Other'])
        category.set(service_data[2])
        category.pack()
        
        tk.Label(update_window, text="Price:").pack(pady=5)
        price = tk.Entry(update_window)
        price.insert(0, str(service_data[3]).replace('$', ''))
        price.pack()
        
        tk.Label(update_window, text="Description:").pack(pady=5)
        description = tk.Text(update_window, height=4)
        description.insert("1.0", service_data[4])
        description.pack()
        
        def save_updates():
            try:
                self.cursor.execute('''
                    UPDATE services 
                    SET service_name = ?, category = ?, price = ?, description = ?
                    WHERE id = ?
                ''', (
                    service_name.get(),
                    category.get(),
                    float(price.get()),
                    description.get("1.0", tk.END),
                    service_data[0]
                ))
                self.conn.commit()
                messagebox.showinfo("Success", "Service updated successfully!")
                update_window.destroy()
                self.load_all_services()
            except ValueError:
                messagebox.showerror("Error", "Invalid price value!")
                
        tk.Button(
            update_window,
            text="Save Updates",
            command=save_updates,
            bg="#2c3e50",
            fg="white"
        ).pack(pady=20)

    def toggle_service(self, selection):
        if not selection:
            messagebox.showwarning("Warning", "Please select a service to toggle")
            return
            
        selected_item = selection[0]
        service_data = self.service_manage_tree.item(selected_item)['values']
        
        current_status = service_data[5]
        new_status = 0 if current_status == "Active" else 1
        
        self.cursor.execute('''
            UPDATE services 
            SET is_active = ?
            WHERE id = ?
        ''', (new_status, service_data[0]))
        
        self.conn.commit()
        self.load_all_services()
        messagebox.showinfo("Success", f"Service status updated to {'Active' if new_status else 'Inactive'}")

    def show_service_history(self):
        for widget in self.services_frame.winfo_children():
            widget.destroy()
            
        # Create service history interface
        history_frame = tk.Frame(self.services_frame, bg="white")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        tk.Label(
            history_frame,
            text="Service Request History",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Create Service History List
        columns = ('Date', 'Room', 'Customer', 'Service', 'Quantity', 'Amount', 'Status', 'Notes')
        history_tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=120)
            
        history_tree.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Load service history
        self.cursor.execute('''
            SELECT 
                sr.request_date,
                b.room_number,
                b.customer_name,
                s.service_name,
                sr.quantity,
                sr.total_amount,
                sr.status,
                sr.notes
            FROM service_requests sr
            JOIN bookings b ON sr.booking_id = b.id
            JOIN services s ON sr.service_id = s.id
            ORDER BY sr.request_date DESC
        ''')
        
        requests = self.cursor.fetchall()
        
        for request in requests:
            history_tree.insert('', tk.END, values=(
                request[0],  # request_date
                request[1],  # room_number
                request[2],  # customer_name
                request[3],  # service_name
                request[4],  # quantity
                f"${request[5]:.2f}",  # total_amount
                request[6],  # status
                request[7]   # notes
            ))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HotelManagementSystem()
    app.run()
