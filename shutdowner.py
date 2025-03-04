import os
import tkinter as tk
from tkinter import messagebox
import time
from datetime import datetime, timedelta

shutdown_active = False
current_after_id = None

font_style = ("Arial", 12)

class TimePicker(tk.Canvas):
    def __init__(self, parent, values, width, height, command=None):
        super().__init__(parent, width=width, height=height, bg="white", highlightthickness=0)
        self.values = [f"{val:02}" for val in values]
        self.command = command
        self.current_index = 0
        self.text_items = []
        self.entry = None
        self.bind("<MouseWheel>", self.on_mousewheel)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Double-Button-1>", self.on_double_click)
        self.update_idletasks()
        self.draw_items()
        self.after(10, self.draw_items)

    def draw_items(self):
        self.delete("all")
        self.text_items.clear()
        mid_y = self.winfo_height() // 2
        font_size = 18
        offset = font_size * 2
        start_index = max(self.current_index - 3, 0)
        end_index = min(self.current_index + 3, len(self.values) - 1)
        for i in range(start_index, end_index + 1):
            y = mid_y + (i - self.current_index) * offset
            item = self.create_text(self.winfo_width() // 2, y,
                                    text=self.values[i],
                                    font=font_style,
                                    fill="black",
                                    anchor="center"),
            self.text_items.append(item)

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.current_index = max(0, self.current_index - 1)
        else:
            self.current_index = min(len(self.values) - 1, self.current_index + 1)
        self.draw_items()
        if self.command:
            self.command(self.get_value())

    def on_click(self, event):
        if self.entry:
            self.finish_edit(event)
        else:
            mid_y = self.winfo_height() // 2
            if event.y < mid_y:
                self.current_index = max(0, self.current_index - 1)
            elif event.y > mid_y:
                self.current_index = min(len(self.values) - 1, self.current_index + 1)
            self.draw_items()
            if self.command:
                self.command(self.get_value())

    def on_double_click(self, event):
        mid_y = self.winfo_height() // 2
        if abs(event.y - mid_y) <= 20:
            if self.entry:
                self.entry.destroy()
            self.entry = tk.Entry(self, font=font_style)
            self.entry.insert(0, self.values[self.current_index])
            self.entry.place(x=self.winfo_width()//2 - 20, y=mid_y - 15, width=40, height=30)
            self.entry.focus_set()
            self.entry.bind("<Return>", self.finish_edit)
            self.entry.bind("<FocusOut>", self.finish_edit)
            root.bind_all("<Button-1>", self.finish_edit_outside)

    def finish_edit(self, event):
        if self.entry:
            new_value = self.entry.get()
            try:
                int_val = int(new_value)
                if 0 <= int_val <= 99:
                    self.current_index = int_val
                    self.values[self.current_index] = f"{int_val:02}"
            except ValueError:
                pass
            self.entry.destroy()
            self.entry = None
            self.draw_items()
            if self.command:
                self.command(self.get_value())
            root.unbind_all("<Button-1>")

    def finish_edit_outside(self, event):
        if self.entry and not self.entry.winfo_containing(event.x_root, event.y_root):
            self.finish_edit(event)

    def get_value(self):
        return int(self.values[self.current_index])

    def update_value(self, new_value):
        self.current_index = new_value
        self.values[self.current_index] = f"{new_value:02}"
        self.draw_items()

def get_total_seconds():
    days = day_picker.get_value()
    hours = hour_picker.get_value()
    minutes = minute_picker.get_value()
    seconds = second_picker.get_value()
    return (days * 86400) + (hours * 3600) + (minutes * 60) + seconds

def countdown(seconds):
    global shutdown_active, current_after_id
    if seconds > 0 and shutdown_active:
        days, hh, mm, ss = seconds // 86400, (seconds % 86400) // 3600, (seconds % 3600) // 60, seconds % 60
        day_picker.update_value(days)
        hour_picker.update_value(hh)
        minute_picker.update_value(mm)
        second_picker.update_value(ss)
        current_after_id = root.after(1000, countdown, seconds - 1)
    elif shutdown_active:
        os.system("shutdown /s /f /t 0")

def start_shutdown():
    global shutdown_active, current_after_id
    seconds = get_total_seconds()
    if seconds > 0:
        shutdown_active = True
        start_button.config(state=tk.DISABLED)
        cancel_button.config(state=tk.NORMAL)
        countdown(seconds)
        shutdown_time = datetime.now() + timedelta(seconds=seconds)
        formatted_shutdown_time = shutdown_time.strftime("%H:%M:%S %a %b %d %Y ")
        
        shutdown_time_label.config(text="shutdown at", fg="#888888", bg="white")
        shutdown_time_actual_label.config(text=formatted_shutdown_time, fg="black", bg="white")

def cancel_shutdown():
    global shutdown_active, current_after_id
    shutdown_active = False
    if current_after_id:
        root.after_cancel(current_after_id)
    day_picker.update_value(0)
    hour_picker.update_value(0)
    minute_picker.update_value(0)
    second_picker.update_value(0)
    start_button.config(state=tk.NORMAL)
    cancel_button.config(state=tk.DISABLED)
    shutdown_time_label.config(text="", bg="white")
    shutdown_time_actual_label.config(text="", bg="white")

def update_clock():
    current_time = time.strftime("%H:%M:%S %a %b %d %Y")
    current_time_label.config(text=current_time)
    root.after(1000, update_clock)

root = tk.Tk()
root.title("shutdowner")
root.geometry("400x280")
root.iconbitmap("art/icon.ico")
root.config(bg="white")

time_frame = tk.Frame(root, bg="white")
time_frame.pack(pady=(10, 5))

right_now_label = tk.Label(time_frame, text="right now", font=font_style, fg="#888888", bg="white")
right_now_label.pack(side=tk.LEFT)

current_time_label = tk.Label(time_frame, text="", font=font_style, fg="black", bg="white")
current_time_label.pack(side=tk.LEFT)

update_clock()

frame = tk.Frame(root, bg="white")
frame.pack(pady=20)

day_picker = TimePicker(frame, list(range(100)), width=80, height=100, command=None)
hour_picker = TimePicker(frame, list(range(24)), width=80, height=100, command=None)
minute_picker = TimePicker(frame, list(range(60)), width=80, height=100, command=None)
second_picker = TimePicker(frame, list(range(60)), width=80, height=100, command=None)

day_picker.pack(side=tk.LEFT, padx=5)
tk.Label(frame, font=font_style, bg="white").pack(side=tk.LEFT)
hour_picker.pack(side=tk.LEFT, padx=5)
tk.Label(frame, font=font_style, bg="white").pack(side=tk.LEFT)
minute_picker.pack(side=tk.LEFT, padx=5)
tk.Label(frame, font=font_style, bg="white").pack(side=tk.LEFT)
second_picker.pack(side=tk.LEFT, padx=5)

button_frame = tk.Frame(root, bg="white")
button_frame.pack(pady=10)

cancel_button = tk.Button(button_frame, text="cancel", font=font_style, command=cancel_shutdown, bd=0, highlightthickness=0, relief="flat", bg="white", fg="black")
cancel_button.pack(side=tk.LEFT, padx=10)

start_button = tk.Button(button_frame, text="start", font=font_style, command=start_shutdown, bd=0, highlightthickness=0, relief="flat", bg="white", fg="black")
start_button.pack(side=tk.RIGHT, padx=10)

shutdown_time_frame = tk.Frame(root, bg="white")
shutdown_time_frame.pack(pady=10)

shutdown_time_label = tk.Label(shutdown_time_frame, text="", font=font_style, fg="#888888", bg="white")
shutdown_time_label.pack(side=tk.LEFT)

shutdown_time_actual_label = tk.Label(shutdown_time_frame, text="", font=font_style, fg="black", bg="white")
shutdown_time_actual_label.pack(side=tk.LEFT)

root.mainloop()
