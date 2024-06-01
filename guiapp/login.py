import tkinter as tk
from tkinter import messagebox
import MySQLdb
from datetime import datetime, timedelta
import time
from tkinter import PhotoImage
import os
from PIL import Image, ImageTk

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Login System")
        
        # Fullscreen for login
        self.root.attributes('-fullscreen', True)
        
        self.logged_in_student = None
        self.login_time = None
        self.elapsed_time = timedelta(0)
        
        # Create login screen
        self.create_login_screen()

        # Connect to MySQL
        self.conn = MySQLdb.connect(user='root', password='mysqlpass', 
                                    host='localhost', database='lic')
        self.cursor = self.conn.cursor()
        
        # Timer label
        self.timer_label = tk.Label(self.root, text="", font=("Helvetica", 16))
        
    def create_login_screen(self):
        self.clear_screen()
        # Disable switching tabs
        self.root.wm_attributes("-topmost", 1)

         # Disable closing application
        #self.root.protocol("WM_DELETE_WINDOW", lambda: messagebox.showinfo("Information", "Request denied"))
        container = tk.Frame(self.root)
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        login_frame = tk.Frame(container)
        login_frame.grid(row=0, column=0)

        # Load and display the image
        image_path = r"C:/Users/JohnO/OneDrive/Documents/GITHUB/Capstone/LIC_System/LIC_Connect/static/images/gui_logo.png"
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((100, 100))
            image = ImageTk.PhotoImage(img)
            image_label = tk.Label(login_frame, image=image)
            image_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')  # Place the image label in the leftmost column and spanning 4 rows
            image_label.image = image  # Keep a reference to avoid garbage collection

         # Add additional text
        self.additional_text = tk.Label(login_frame, text="LIC CONNECT", fg="maroon", font=("Helvetica", 25, "bold"), justify='center')
        self.additional_text.grid(row=0, column=1, columnspan=2, pady=10)

        self.label1 = tk.Label(login_frame, text="Student ID")
        self.label1.grid(row=1, column=0, padx=10, pady=10, sticky='e')  # Align label to the right
        
        self.entry1 = tk.Entry(login_frame)
        self.entry1.grid(row=1, column=1, padx=10, pady=10)
        
        self.label2 = tk.Label(login_frame, text="Password")
        self.label2.grid(row=2, column=0, padx=10, pady=10, sticky='e')  # Align label to the right
        
        self.entry2 = tk.Entry(login_frame, show="*")
        self.entry2.grid(row=2, column=1, padx=10, pady=10)
        
        self.login_button = tk.Button(login_frame, text="Login", command=self.login)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # # Add an image
        # image = PhotoImage(file="path_to_your_image.png")  # Change "path_to_your_image.png" to the actual path
        # image_label = tk.Label(login_frame, image=image)
        # image_label.grid(row=3, column=0, columnspan=2, pady=10)
        # image_label.image = image  # Keep a reference to avoid garbage collection
    def on_menu_screen_close(self):
        self.logout()
    def create_menu_screen(self):
        self.clear_screen()

        self.root.attributes('-fullscreen', False)
        self.root.geometry('300x200')
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_menu_screen_close)
        
        self.elapsed_time = timedelta(0)
        self.login_time = datetime.now()
        
        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky='nsew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        menu_frame = tk.Frame(container)
        menu_frame.grid(row=0, column=0)

        self.check_history_button = tk.Button(menu_frame, text="Check History", command=self.check_history)
        self.check_history_button.grid(row=0, column=0, padx=10, pady=10)
        
        self.logout_button = tk.Button(menu_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=1, column=0, padx=10, pady=10)
        
        self.timer_label = tk.Label(menu_frame, text="Time Elapsed: 00:00:00", font=("Helvetica", 16))
        self.timer_label.grid(row=2, column=0, padx=10, pady=10)
        
        self.update_timer()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
    def login(self):
        student_id = self.entry1.get()
        password = self.entry2.get()

        
        try:
            # Query to select all columns from the webapp_student table for the given studentID and password
            self.cursor.execute("SELECT * FROM webapp_student WHERE studentID = %s AND password = %s", 
                                (student_id, password))
            student = self.cursor.fetchone()
            
            if student:
                time_left_minutes = student[4]  # time_left is the fifth column
                
                # Prevent login if time_left is 0
                if time_left_minutes == 0:
                    messagebox.showerror("Error", "No time left. Login not allowed.")
                    return
                
                self.logged_in_student = student_id
                self.time_left = timedelta(minutes=time_left_minutes)
                self.login_time = datetime.now()
                
                # Insert a new session record
                session_date = self.login_time.date()
                session_time = self.login_time.time()
                
                self.cursor.execute(
                    "INSERT INTO webapp_session (date, loginTime, parent_id, course) VALUES (%s, %s, %s, %s)",
                    (session_date, session_time, student_id, student[2])  # course is the third column
                )
                self.conn.commit()
                
                # messagebox.showinfo("Login", "Login Successful!")
                self.create_menu_screen()
                self.start_timer()
            else:
                messagebox.showerror("Error", "Invalid StudentID or Password")
        except MySQLdb.ProgrammingError as e:
            print("MySQL Programming Error:", e)
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        except IndexError as e:
            print("Index Error:", e)
            messagebox.showerror("Index Error", f"An error occurred: {e}")


    def logout(self):
        if self.logged_in_student and self.login_time:
            logout_time = datetime.now()

            # Time consumed converted to minutes
            time_logged_in = (logout_time - self.login_time).total_seconds() // 60

            print(time_logged_in)

            # Fetch current time left of student
            self.cursor.execute("SELECT time_left FROM webapp_student WHERE studentID = %s", 
                                (self.logged_in_student,))
            current_time_left = self.cursor.fetchone()[0]

            new_time_left = current_time_left - time_logged_in
            
            # Placing logout time
            self.cursor.execute("UPDATE webapp_session SET logoutTime = %s WHERE parent_id = %s AND logoutTime IS NULL",
                    (logout_time, self.logged_in_student))
            
            # Placing time_consumed
            self.cursor.execute("UPDATE webapp_session SET consumedTime = %s WHERE parent_id = %s AND consumedTime IS NULL",
                    (time_logged_in, self.logged_in_student))
            
            # Updating time left
            self.cursor.execute("UPDATE webapp_student SET time_left = %s WHERE studentID = %s", 
                                (new_time_left, self.logged_in_student))
            self.conn.commit()
            
            self.logged_in_student = None
            self.login_time = None
            self.elapsed_time = timedelta(0)
            # messagebox.showinfo("Logout", "Logout Successful!")
            
            # Return to fullscreen login screen
            self.root.attributes('-fullscreen', True)
            self.create_login_screen()
        else:
            messagebox.showerror("Error", "No student is logged in")

    def check_history(self):
        if self.logged_in_student:
            self.cursor.execute("SELECT * FROM webapp_session WHERE parent_id = %s", 
                                (self.logged_in_student,))
            sessions = self.cursor.fetchall()
            
            if sessions:
                history_window = tk.Toplevel(self.root)
                history_window.title("Session History")
                history_window.geometry("400x300")

                text_widget = tk.Text(history_window)
                text_widget.pack(expand=True, fill='both')

                for i, session in enumerate(sessions, start=1):
                    logintime = session[2]
                    logouttime = session[3]
                    timeconsumed = session[6]
                    text_widget.insert(tk.END, f"Session {i}:\n")
                    text_widget.insert(tk.END, f"Login Time: {logintime}\n")
                    text_widget.insert(tk.END, f"Logout Time: {logouttime}\n")
                    text_widget.insert(tk.END, f"Time Consumed: {timeconsumed} minutes\n\n")
            else:
                messagebox.showerror("Error", "No session history found for this student")
        else:
            messagebox.showerror("Error", "No student is logged in")

    def start_timer(self):
        self.update_timer()

    def update_timer(self):
        now = datetime.now()
        elapsed = now - self.login_time
        remaining_time = self.time_left - elapsed
        
        if remaining_time <= timedelta(seconds=0):
            self.timer_label.config(text="Time Left: 00:00:00")
            messagebox.showwarning("Time Up", "Your time has expired.")
            self.logout()
            return
        
        remaining_seconds = int(remaining_time.total_seconds())
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(remaining_seconds))
        self.timer_label.config(text=f"Time Left: {formatted_time}")
        
        # Show warning messages at specific time intervals
        if remaining_seconds == 600:  # 10 minutes
            messagebox.showwarning("Warning", "Only 10 minutes left!")
        elif remaining_seconds == 300:  # 5 minutes
            messagebox.showwarning("Warning", "Only 5 minutes left!")
        elif remaining_seconds == 60:  # 1 minute
            messagebox.showwarning("Warning", "Only 1 minute left!")
        
        # Update every second
        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
