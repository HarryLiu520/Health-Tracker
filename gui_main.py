"""
Health Habit Tracker Program
----------------------------
This is a simple Python program that helps users build healthy daily habits.

You can record if you finished habits like drinking water, exercising, or sleeping well.
The program gives you points, keeps track of your streak, and shows your ranking compared to others.

How to run:
1. Make sure you have Python installed.
2. Run this file gui_main.py directly, e.g. python gui_main.py
3. A small window will open. Enter your name, tick your habits, and click ”Save Today“.

You can also check your total score, rank, and the top users in the scoreboard.

Note:
The Graphical User Interface design of this program was created with the help of GPT guidance.
"""

import os
import datetime
import tkinter as tk
from tkinter import ttk
from datetime import date

# get the folder where this file is located, then set up the path for progress.txt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "progress.txt")


def save_today(name, points, completions):
    # save today's data into progress.txt
    today = str(datetime.date.today())

    with open(HISTORY_FILE, "a") as f:
        f.write(today)
        f.write(" | ")
        f.write(name.strip())
        f.write(" | ")

        # write each habit and result separately
        for habit in completions:
            if completions[habit] == 1:
                f.write(habit)
                f.write("=Yes, ")
            else:
                f.write(habit)
                f.write("=No, ")

        # finally write total points
        f.write("Points=")
        f.write(str(points))
        f.write("\n")


def load_history(name, filename=HISTORY_FILE):
    # load one user's history of scores from the text file
    target = name.strip().lower()
    history = []
    try:
        with open(filename, "r") as f:
            for line in f:
                s = line.strip()
                
                # split and clean manually
                items = s.split("|")
                parts = []
                for p in items:
                    parts.append(p.strip())

                # skip short lines
                if len(parts) < 3:
                    continue

                name_in = parts[1].lower()
                if name_in != target:
                    continue

                # join the rest manually
                rest = ""
                for i in range(2, len(parts)):
                    rest = rest + parts[i]
                    if i < len(parts) - 1:
                        rest = rest + "|"

                # look for "Points=" in the rest text
                if "Points=" in rest:
                    # extract the number part step by step
                    pieces = rest.split("Points=")
                    last_piece = pieces[-1]
                    last_piece = last_piece.strip()
                    last_piece = last_piece.rstrip(",")

                    try:
                        p = int(last_piece)
                        history.append(p)
                    except ValueError:
                        pass

    except FileNotFoundError:
        # if no file yet, just return an empty list
        pass

    return history


def calc_streak(history):
    # count continuous days with points > 0
    streak = 0
    for p in reversed(history):
        if p > 0:
            streak += 1
        else:
            break
    return streak


def weekly_average(history, days=7):
    # calculate the average points in the last 7 days
    if not history:
        return 0
    last = history[-days:]
    avg = sum(last) / len(last)
    return round(avg, 1)


def load_totals_all(filename=HISTORY_FILE):
    # load total points for all users from the text file
    totals = {}     # store total points for each user by lowercase name
    display = {}    # store original names for showing

    try:
        with open(filename, "r") as f:
            for line in f:
                s = line.strip()

                # split the line by "|" and clean each part
                items = s.split("|")
                parts = []
                for p in items:
                    parts.append(p.strip())

                # skip lines that don't have enough parts
                if len(parts) < 3:
                    continue

                # get the username and lowercase for matching
                name_in = parts[1]
                lower = name_in.lower()

                # manually combine the rest (no join)
                rest = ""
                for i in range(2, len(parts)):
                    rest = rest + parts[i]
                    if i < len(parts) - 1:
                        rest = rest + "|"

                # check if the line contains "Points="
                if "Points=" in rest:
                    pieces = rest.split("Points=")
                    last_piece = pieces[-1]
                    last_piece = last_piece.strip()
                    last_piece = last_piece.rstrip(",")

                    # try to turn the points text into a number
                    try:
                        p = int(last_piece)
                    except ValueError:
                        # if it fails, skip this line
                        continue

                    # first time we see this user and make new record
                    if lower not in totals:
                        totals[lower] = 0
                        display[lower] = name_in

                    # add the points to the user's total
                    totals[lower] = totals[lower] + p

    except FileNotFoundError:
        # if the file doesn't exist, just return empty results
        pass

    return totals, display


def get_user_rank(name):
    # calculate user's ranking based on their total points
    totals, display = load_totals_all()
    target = name.strip().lower()

    # build a list like: display_name, total_points, lowercase_key
    order = []
    for k in totals:
        row = [display[k], totals[k], k]
        order.append(row)

    # bubble sort: higher score first; if tie, sort alphabetically
    n = len(order)
    for i in range(n):
        for j in range(0, n - 1 - i):
            a_name = order[j][0].lower()
            a_score = order[j][1]
            b_name = order[j + 1][0].lower()
            b_score = order[j + 1][1]

            need_swap = False

            if a_score < b_score:
                need_swap = True
            elif a_score == b_score:
                if a_name > b_name:
                    need_swap = True

            if need_swap:
                temp = order[j]
                order[j] = order[j + 1]
                order[j + 1] = temp

    # if no user yet
    if n == 0:
        return (1, 0, 0)

    # get user's total points
    if target in totals:
        user_total = totals[target]
    else:
        user_total = 0

    # find rank
    rank = 0
    found = False
    for i in range(n):
        if order[i][2] == target:
            rank = i + 1
            found = True
            break

    if not found:
        rank = n + 1

    # print for checking (optional for debugging)
    print(f"User: {name}")
    print(f"Total Points: {user_total}")
    print(f"Rank: {rank} out of {n}")

    return (rank, user_total, n)

# GUI section
class HabitGUI:
    def __init__(self, root):
        # basic window setup
        self.root = root
        self.root.title("💪 Health Habit Tracker")
        self.current_user = "Friend"

        # use a better looking theme
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except:
            pass

        # define some styles
        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        self.style.configure("Card.TLabelframe", padding=12)
        self.style.configure("Card.TLabelframe.Label", font=("Helvetica", 12, "bold"))
        self.style.configure("Primary.TButton", padding=8)
        self.style.configure("Body.TLabel", font=("Helvetica", 11))
        self.style.configure("TCheckbutton", padding=4)

        # --- Header ---
        self.header = ttk.Label(root, text="Health Habit Tracker", style="Title.TLabel")
        self.header.grid(row=0, column=0, columnspan=3, padx=12, pady=(12, 4), sticky="w")
        
        sub = ttk.Label(root, text="Track daily habits, earn points, and stay motivated.", style="Body.TLabel")
        sub.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 10), sticky="w")

        # Name input row
        ttk.Label(root, text="Name:", style="Body.TLabel").grid(row=2, column=0, padx=(12,4), pady=6, sticky="e")
        self.name_var = tk.StringVar(value="Friend")
        ttk.Entry(root, textvariable=self.name_var, width=18).grid(row=2, column=1, padx=4, pady=6, sticky="w")
        ttk.Button(root, text="Confirm", style="Primary.TButton", command=self.use_name)\
            .grid(row=2, column=2, padx=(4,12), pady=6, sticky="w")

        # Habits section
        habits_card = ttk.Labelframe(root, text="Today's Habits", style="Card.TLabelframe")
        habits_card.grid(row=3, column=0, columnspan=3, padx=12, pady=8, sticky="ew")

        self.habits = ["Drink water", "Exercise", "Sleep 8 hours"]
        self.check_vars = {}
        for i, h in enumerate(self.habits):
            var = tk.IntVar()
            self.check_vars[h] = var
            ttk.Checkbutton(habits_card, text=h, variable=var).grid(row=i, column=0, sticky="w", pady=2)

        # Progress bar
        self.pbar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=280)
        self.pbar.grid(row=4, column=0, columnspan=2, padx=12, pady=6, sticky="w")
        self.progress_label = ttk.Label(root, text="Progress: 0%", style="Body.TLabel")
        self.progress_label.grid(row=4, column=2, padx=(0,12), pady=6, sticky="w")

        # Buttons row
        btn_row = ttk.Frame(root)
        btn_row.grid(row=5, column=0, columnspan=3, padx=12, pady=8, sticky="w")

        ttk.Button(btn_row, text="Save Today", style="Primary.TButton", command=self.save_today_gui)\
            .grid(row=0, column=0, padx=(0,8))
        ttk.Button(btn_row, text="My Rank", command=self.show_rank)\
            .grid(row=0, column=1, padx=8)
        ttk.Button(btn_row, text="Ranking List", command=self.show_rankinglist)\
            .grid(row=0, column=2, padx=8)

        # Output box 
        self.output = tk.Text(root, height=12, width=60)
        self.output.grid(row=6, column=0, columnspan=3, padx=12, pady=(4,12), sticky="nsew")
        self.output.insert(tk.END, "Welcome! Enter your name and check your habits.\n")

        # make text box stretch when window is resized
        root.grid_rowconfigure(6, weight=1)
        root.grid_columnconfigure(1, weight=1)

    def use_name(self):
        # handle the name input and switch user
        name = self.name_var.get().strip()
        if name == "":
            name = "Friend"
            self.name_var.set(name)
        self.current_user = name
        self.output.insert(tk.END, "\nSwitched to user: " + name + "\n")

    def save_today_gui(self):
        # save today’s habit results from checkboxes
        completions = {}
        score = 0
        for h in self.habits:
            completions[h] = self.check_vars[h].get()
            score += completions[h]

        total = len(self.habits)
        rate = (score / total) if total else 0.0
        points = score
        badge = None

        # give bonus if all habits are done
        if score == total and total > 0:
            points += 1
            badge = "All Clear!"
        
        # feedback messages based on completion rate
        if rate >= 0.8:
            msg = "Great job! Keep the momentum!"
        elif rate >= 0.5:
            msg = "Nice progress! You're getting there."
        else:
            msg = "Small steps matter. Try one more tomorrow."

        # dynamic title based on performance
        if total > 0 and score == total:
            self.header.config(text="🔥 Perfect day! Health Habit Tracker")
        elif rate >= 0.8:
            self.header.config(text="💪 Great streak! Health Habit Tracker")
        elif rate > 0:
            self.header.config(text="➡️ Keep going! Health Habit Tracker")
        else:
            self.header.config(text="Health Habit Tracker")

        # update progress bar
        self.pbar["value"] = int(rate * 100)
        self.progress_label.config(text="Progress: " + str(int(rate * 100)) + "%")

        # save result and show feedback
        save_today(self.current_user, points, completions)
        hist = load_history(self.current_user)
        streak = calc_streak(hist)
        avg = weekly_average(hist)

        self.output.insert(tk.END, "\n==== Today (" + self.current_user + ") ====\n")
        self.output.insert(tk.END, "Points: " + str(points) + "\n")
        if badge:
            self.output.insert(tk.END, "Badge: " + badge + "\n")
        self.output.insert(tk.END, msg + "\n")
        self.output.insert(tk.END, "Streak: " + str(streak) + " days\n")
        self.output.insert(tk.END, "7-day avg: " + str(avg) + "\n")

        # clear all checkboxes after saving
        self.clear_checks()

    def show_rank(self):
        # show the current user's ranking information
        rank, total, total_users = get_user_rank(self.current_user)

        # start writing into the text box
        self.output.insert(tk.END, "\n==== My Rank ====\n")
        self.output.insert(tk.END, f"User: {self.current_user}\n")
        self.output.insert(tk.END, f"Total Points: {total}\n")

        # if there are no users yet
        if total_users == 0:
            self.output.insert(tk.END, "Rank: N/A (no records yet)\n")
        else:
            self.output.insert(tk.END, f"Rank: {rank} out of {total_users}\n")

    def show_rankinglist(self):
    # show top users ranking list from progress.txt

    # load all users' total points from the file
        totals, display = load_totals_all()

    # build a list that stores name, total_points
        order = []
        for key in totals:
            name_text = display[key]
            total_points = totals[key]
            one_row = [name_text, total_points]
            order.append(one_row)

    # sort the list by score (high to low) using bubble sort
    # if two users have same score, sort alphabetically by name
        i = 0
        while i < len(order):
            j = 0
            while j < len(order) - 1 - i:
                a_name = order[j][0].lower()
                a_score = order[j][1]
                b_name = order[j + 1][0].lower()
                b_score = order[j + 1][1]

                need_swap = False
                if a_score < b_score:
                    need_swap = True
                elif a_score == b_score and a_name > b_name:
                    need_swap = True

                if need_swap:
                    temp = order[j]
                    order[j] = order[j + 1]
                    order[j + 1] = temp

                j = j + 1
            i = i + 1

        # get today's date and number of users
        today_str = str(date.today())
        user_count = len(order)

        # print leaderboard title and summary into text box
        self.output.insert(tk.END, "\n===== Ranking List =====\n")
        self.output.insert(tk.END, f"Date: {today_str} | Users: {user_count}\n")

        # if there are no users yet, show a message and return
        if len(order) == 0:
            self.output.insert(tk.END, "No records yet.\n")
            return

        # decide how many users to display (top 5 only)
        if len(order) < 5:
            top_n = len(order)
        else:
            top_n = 5

        # print the top users one by one
        index = 0
        while index < top_n:
            rank_number = index + 1
            name = order[index][0]
            points = order[index][1]
            self.output.insert(tk.END, f"{rank_number}. {name} - {points} pts\n")
            index = index + 1

    def clear_checks(self):
        # uncheck all boxes after saving, so user can start fresh
        for h in self.check_vars:
            self.check_vars[h].set(0)


# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = HabitGUI(root)
    root.mainloop()
