import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import time
import mysql.connector
from PIL import ImageTk, Image

# Initialize mysql
def connect_to_mysql():
    try:
        # Replace these with your MySQL server details
        connection = mysql.connector.connect(
            host="172.16.97.22",
            user="root",
            password=" ",
            database="records"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
        return None

def on_closing():
    messagebox.showinfo("Warning", "Cannot close the application this way.")

def authenticate_user(student_id, password):
    connection = connect_to_mysql()
    if not connection:
        return False
    
    cursor = connection.cursor()

    query = "SELECT * FROM students WHERE studentid = %s AND password = %s"
    cursor.execute(query, (student_id, password))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result 

def login():
    student_id = student_id_entry.get()
    password = password_entry.get()

    global current_session
    if authenticate_user(student_id, password):
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()

            # Retrieve time_left for the student
            select_query = "SELECT time_left FROM students WHERE studentid = %s"
            cursor.execute(select_query, (student_id,))
            result = cursor.fetchone()

            if result and result[0] > 0:  # Assuming result[0] is the time_left column
                login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert_query = "INSERT INTO login_sessions (studentid, login_time) VALUES (%s, %s)"

                try:
                    cursor.execute(insert_query, (student_id, login_time))
                    connection.commit()
                    print("Login session successful")
                except mysql.connector.Error as insert_err:
                    print(f"Error inserting login session: {insert_err}")

                

                # Store current session information
                current_session = {"student_id": student_id, "login_time": login_time}

                login_window.withdraw()
                main_window(student_id, login_time)
            elif result and result[0] <= 0:
                error_label.config(text="You've already consumed your 10 hours this semester.", fg="red")
            else:
                error_label.config(text="Invalid credentials", fg="red")

            connection.close()  # Close the connection after using it

def on_logout(window, student_id, login_time):
    logout_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    connection = connect_to_mysql()
    if connection:
        cursor = connection.cursor()

        update_query = "UPDATE login_sessions SET logout_time = %s WHERE studentid = %s AND login_time = %s"
        cursor.execute(update_query, (logout_time, student_id, login_time))

        update_time = "UPDATE login_sessions SET consumed_time = TIMESTAMPDIFF(MINUTE, login_time, logout_time) WHERE studentid = %s AND login_time = %s"
        cursor.execute(update_time, (student_id, login_time))
     
        update_timeleft = "UPDATE students SET time_left = time_left - (SELECT consumed_time FROM login_sessions WHERE students.studentid = login_sessions.studentid AND students.studentid = %s ORDER BY login_time DESC LIMIT 1) WHERE students.studentid = %s;"
        cursor.execute(update_timeleft, (student_id, student_id))


        connection.commit()
        cursor.close()
        connection.close()

        window.destroy()  # Corrected to use main_window window object 
        student_id_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
        login_window.deiconify()
        

def main_window(student_id, login_time):
    global start_time
    start_time = time.time()

    window = tk.Tk()  # Changed variable name to window
    window.title("Logged In")
    window.geometry("300x150")

    # Display current time at login
    current_time = datetime.now().strftime("%H:%M:%S %p")
    logged_in_label = tk.Label(window, text=f"Logged In: {current_time}")
    logged_in_label.pack()

    time_label = tk.Label(window, text="Running Time: 00:00:00")
    time_label.pack()

    def update_time():
        elapsed_time = time.time() - start_time
        running_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        time_label.config(text=f"Running Time: {running_time}")
        window.after(1000, update_time)  # Update every second

    update_time()

    logout_button = tk.Button(window, text="Logout", command=lambda: on_logout(window, student_id, login_time))
    logout_button.pack()

    window.mainloop()

# Login window
global login_window
login_window = tk.Tk()
login_window.attributes("-fullscreen", True)

# Disable Alt+Tab
login_window.attributes('-toolwindow', 1)
login_window.attributes('-topmost', 1)

# Intercept the window close event
login_window.protocol("WM_DELETE_WINDOW", on_closing)

# Open the image file
image_path = "logo.png" 
original_image = Image.open(image_path)
resized_image = original_image.resize((100, 100)) 
 
# Create a Tkinter-compatible photo image
photo = ImageTk.PhotoImage(resized_image)

#Create a frame to hold the image and text
frame = tk.Frame(login_window)
frame.pack(pady=(100, 10))

label_image = tk.Label(frame, image=photo)
label_image.pack(side=tk.LEFT)

# Add the text "LIC Gateway" beside the image
font_style = ("Arial", 30, "bold")
label_text = tk.Label(frame, text="LIC Gateway", font=font_style)
label_text.pack(side=tk.LEFT, padx=10)

# Create a label for displaying the image
# label = tk.Label(login_window, image=photo)
# label.pack(pady=10)

#frame for student ID label and entry
frame_student_id = tk.Frame(login_window)
frame_student_id.pack(side=tk.TOP, pady=5)

student_id_label = tk.Label(frame_student_id, text="Student ID:")
student_id_label.pack(side=tk.LEFT)

student_id_entry = tk.Entry(frame_student_id)
student_id_entry.pack(side=tk.LEFT, padx=5)

#frame for student PASSWORD label and entry
frame_password = tk.Frame(login_window)
frame_password.pack(side=tk.TOP, pady=5)

password_label = tk.Label(frame_password, text="Password:")
password_label.pack(side=tk.LEFT)

password_entry = tk.Entry(frame_password, show="*")
password_entry.pack(side=tk.LEFT, padx=5)

login_button = tk.Button(login_window, text="Login", command=login)
login_button.pack(side=tk.TOP, pady=20)

error_label = tk.Label(login_window, text="")
error_label.pack(side=tk.TOP, pady=10)

# Center the widgets in the window
for widget in login_window.winfo_children():
    widget.pack_configure(anchor='n')

# WIDGETS ^^
login_window.mainloop()

