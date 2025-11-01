import os
import datetime

# Get the folder where this file is located 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create a path for progress.txt inside this folder
HISTORY_FILE = os.path.join(BASE_DIR, "progress.txt")

def ask_yes_no(prompt):
    """
    Ask user to enter Yes / No until valid input.
    Return: 1 means Yes, 0 means No
    """
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "yes"):
            return 1
        elif ans in ("n", "no"):
            return 0
        else:
            print("Please enter Yes or No (y/n).")

class HabitTracker:
    """
    A class to store user's daily habit data.
    """

    def __init__(self, name):
        """
        Set up a new tracker for one user.
        """
        self.name = name
        self.habits = ["Drink water", "Exercise", "Sleep 8 hours"]
        self.completions = {} # Store finish result for each habit
        self.score = 0 # Daily score
        self.total = len(self.habits) # Total number of habits


    def track_habits(self):
        """
        Ask user about each habit (Yes/No).
        """
        print('\nDid you finish these habits today? (Yes/No)')
        self.completions = {}
        self.score = 0
        for habit in self.habits:
            done = ask_yes_no(habit + ": ")
            self.completions[habit] = done # Store result
            self.score += done # Add score


    def reward_and_feedback(self):
        """
        Give points + feedback message to user.
        Extra point if all habits completed.
        """
        if self.total == 0:
            rate = 0
        else:
            rate = self.score * 1.0 / self.total # (score / total)
        points = self.score # Base points
        badge = None # If user gets perfect day

        # All habits completed and get Reward +1 point
        if self.score == self.total and self.total > 0:
            points += 1
            badge = 'All Clear!'

        # Provide feedback messages based on rate
        if rate >= 0.8:
            msg = 'Great job! Keep the momentum!'
        elif rate >= 0.5:
            msg = "Nice progress! You\'re getting there."
        else:
            msg = 'Small steps matter. Try one more tomorrow.'

        return points, badge, msg


# HISTORY_FILE = 'progress.txt'

def load_history(name, filename = HISTORY_FILE):
    """
    Load the score history for one user from the file.
    Parameters:
        name (str): The user's name. 
        filename (str): The file path, default is progress.txt. 
    Returns:
        history (list): A list of all point numbers for this user.
    """

    # Convert name to lowercase for case-insensitive matching
    target = name.strip().lower()

    # This list will store all the points found for the user
    history = []
    try:
        with open(filename, "r") as f:
            for line in f:
                s = line.strip()

                # Split the line by "|" into parts
                parts = s.split("|")

                # remove extra spaces for each part
                new_parts = []
                for p in parts:
                    new_parts.append(p.strip())
                parts = new_parts

                # Skip lines that don't have enough parts
                if len(parts) < 3:
                    continue

                # Get the name part from the line and make it lowercase
                name_in = parts[1].lower()

                # Skip if this line belongs to another user
                if name_in != target:
                    continue

                # Combine the rest of the parts (habit info + points)
                rest = ""
                for k in range(2, len(parts)):
                    if k > 2:
                        rest = rest + "|"
                    rest = rest + parts[k]

                # Check if there is a "Points=" pattern
                if "Points=" in rest:
                    try:
                        # Extract the number after "Points="
                        number_text = rest.split("Points=")[-1]
                        number_text = number_text.strip()
                        number_text = number_text.rstrip(",")
                        p = int(number_text)

                        # Save this score into list
                        history.append(p)
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass

    # Return the list of scores for this user
    return history

def save_today(name, points, completions):
    """
    Append or replace today's result for the user in progress.txt
    If user saves multiple times in one day, only keep the latest record.
    """
    today = str(datetime.date.today())

    # read old lines first
    lines = []
    try:
        with open(HISTORY_FILE, "r") as f:
            for line in f:
                line = line.strip()
                # skip empty lines
                if line == "":
                    continue
                # keep all lines that are not today's same user
                if today in line and name.lower() in line.lower():
                    continue
                lines.append(line)
    except FileNotFoundError:
        # if no file yet, just skip
        pass

    # now open file again to write (overwrite mode)
    with open(HISTORY_FILE, "w") as f:
        # write back all old lines first
        for l in lines:
            f.write(l + "\n")

        # then write today's latest record
        f.write(f"{today} | {name.strip()} | ")

        for habit in completions:
            if completions[habit] == 1:
                f.write(f"{habit}=Yes, ")
            else:
                f.write(f"{habit}=No, ")

        f.write(f"Points={points}\n")


def calc_streak(history):
    """
    Count how many consecutive non-zero days from the end of the list.

    Parameters:
        history (list[int]): points list for this user in date order (oldest to newest)

    Logic:
        - Go backward from the last item.
        - If > 0, increase streak and keep going.
        - If 0 or less, stop.

    Returns:
        streak (int): number of consecutive days with positive points
    """

    streak = 0

    # Walk the list backwards: newest to oldest
    for p in reversed(history):
        if p > 0:
            streak += 1
        else:
            break

    return streak



def weekly_average(name, filename=HISTORY_FILE):
    """
    Calculate the average of the most recent days (one per date).
    Each day only counts once (the last record if multiple exist).
    """
    day_scores = {}  # store date and score

    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()

                # skip empty lines
                if line == "":
                    continue

                # only handle this user's data
                if name.lower() not in line.lower():
                    continue

                # split into parts like ["2025-11-01", "Friend", "Drink water=Yes, ... Points=3"]
                parts = line.split("|")

                # skip bad lines
                if len(parts) < 3:
                    continue

                date_text = parts[0].strip()

                # find Points=
                if "Points=" not in line:
                    continue

                # try to get the number after Points=
                try:
                    split_text = line.split("Points=")
                    last_part = split_text[-1].strip()
                    p = int(last_part)
                except:
                    continue

                # record or replace this date's score
                day_scores[date_text] = p

    except FileNotFoundError:
        return 0

    # if no record at all
    if len(day_scores) == 0:
        return 0

    # get all the dates and sort
    all_dates = list(day_scores.keys())
    all_dates.sort()

    # only take last 7 days if there are more
    if len(all_dates) > 7:
        last_days = all_dates[-7:]
    else:
        last_days = all_dates

    total_points = 0
    for d in last_days:
        total_points = total_points + day_scores[d]

    avg = total_points / len(last_days)
    return round(avg, 1)

def load_totals_all(filename = HISTORY_FILE):
    """
    Load the total points of all users from the file.

    Parameters:
        filename (str): the file name (default: progress.txt)

    Returns:
        totals (dict): key = lowercase name, value = total points
        display (dict): key = lowercase name, value = original name (for printing)
    """
    
    totals = {}  # store total points for each user
    display = {}  # store display names for printing

    try:
        f = open(filename, "r")
        for line in f:
            # remove spaces and newlines
            s = line.strip()

            # split the line into parts by "|"
            parts = s.split("|")

            # remove extra spaces from each part
            new_parts = []
            for p in parts:
                new_parts.append(p.strip())
            parts = new_parts

            # skip lines that don't have enough sections
            if len(parts) < 3:
                continue

            # extract the user's name
            name_in = parts[1]

            # use lowercase to unify
            lower = name_in.lower()

            # join the remaining parts (habit info + points)
            rest = ""
            for k in range(2, len(parts)):
                if k > 2:
                    rest = rest + "|"
                rest = rest + parts[k]

            # check if this line contains "Points="
            if "Points=" in rest:
                try:
                    # extract the number after Points=
                    number_text = rest.split("Points=")[-1]
                    number_text = number_text.strip()
                    number_text = number_text.rstrip(",")
                    p = int(number_text)
                except ValueError:
                    continue

                # initialize totals and display if user appears first time
                if lower not in totals:
                    totals[lower] = 0
                    display[lower] = name_in

                # add this day's points to total
                totals[lower] = totals[lower] + p

        f.close()

    except FileNotFoundError:
        # if the file doesn't exist, just skip
        pass

    # return both dictionaries
    return totals, display

def get_user_rank(name):
    """
    Calculate the rank of a user based on total points.

    Steps:
      1. Read all users' total points from the file (using load_totals_all).
      2. Store the data in a list: [display_name, total_points, lowercase_name].
      3. Sort the list in descending order by total points.
         If two users have the same score, sort them alphabetically by name.
      4. Find the given user's position in the sorted list.
         If the user has no record, place them after the last one.

    Returns:
        (rank, user_total, total_users)
        rank: the user's rank (starting from 1)
        user_total: the user's total points
        total_users: number of users with records
    """

    # load total scores for all users
    totals, display = load_totals_all()
    target = name.strip().lower()

    # Build a list: [display_name, total_points, lower_key]
    order = []
    for k in totals:
        one_row = [display[k], totals[k], k]
        order.append(one_row)

    # Bubble sort: by score (desc), then by name (asc)
    for i in range(len(order)):
        for j in range(0, len(order) - 1 - i):
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

    # If no users have records yet
    if len(order) == 0:
        if target == "":
            target = "user"
        return (1, 0, 0)
    
    # Get user's total points (0 if no record yet)
    if target in totals:
        user_total = totals[target]
    else:
        user_total = 0

    # Find user's rank; if not found (no record), rank = last + 1
    rank = None
    for i in range(len(order)):
        if order[i][2] == target:
            rank = i + 1
            break

    if rank is None:
        rank = len(order) + 1

    return (rank, user_total, len(order))

def show_leaderboard(top_n = 5):
    """
    Print the top N users with the highest total points.

    Steps:
      1. Read all users' total points from the file (using load_totals_all).
      2. Store the data in a list: [display_name, total_points].
      3. Sort the list in descending order by score.
         If two users have the same score, sort them alphabetically by name.
      4. Print the top N users. If fewer than N users exist, print all.

    Example output:
      ===== Leaderboard =====
      1. harry  -  7 pts
      2. lily   -  5 pts
    """

    # get all users' total scores
    totals, display = load_totals_all()

    # Build a list: [display_name, total_points]
    order = []
    for key in totals:
        one_row = [display[key], totals[key]]
        order.append(one_row)

    # Bubble sort (score desc, name asc)
    for i in range(len(order)):
        for j in range(0, len(order) - 1 - i):
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

    print("\n===== Leaderboard =====")
    if len(order) == 0:
        print("No records yet.")
        return
    
    # Adjust top_n if there are fewer users
    if top_n > len(order):
        top_n = len(order)

    # Print the ranking
    for i in range(top_n):
        rank_number = i + 1
        name_text = order[i][0]
        score_text = order[i][1]
        print(f"{rank_number}. {name_text}  -  {score_text} pts")

def main():
    """
    Main menu loop for the Health Habit Tracker.
    """

    print('Welcome to the Health Habit Tracker!')

    # Ask for user name; if empty, use "Friend" as a default.
    name = input('Enter your name: ').strip()
    if name == '':
        name = 'Friend'
    
    # Create a tracker object for this user.
    tracker = HabitTracker(name)
    print("Welcome " + name + "! Let's build healthy habits together!")

    # Main loop: keep showing the menu until user types EXIT.
    while True:
        print("\n===== Menu =====")
        print("1) Track today ")
        print("2) My rank ")
        print("3) Leaderboard ")
        print("4) Switch user ")
        print("Type EXIT to quit")
        choice = input("Choose: ").strip().lower() # Read menu choice (case-insensitive).

        if choice == "1": # Option 1: Track today's habits for current user.
    
            tracker.track_habits()
            points, badge, feedback = tracker.reward_and_feedback()

            # Show today's result and feedback.
            print('\n===== Today =====')
            print('Points today: ' + str(points))
            if badge:
                print('Badge: ' + badge) # Show badge only if user got perfect day
            print('Feedback: ' + feedback)

            save_today(tracker.name, points, tracker.completions) # Save today's record to the shared file

            # Load history for this user only, then show streak and 7-day average.
            history = load_history(tracker.name)
            streak = calc_streak(history)
            avg_7 = weekly_average(name)
            print('\n===== Progress (' + tracker.name + ') =====')
            print('Streak: ' + str(streak) + ' day(s)')
            print('7-day average points: ' + str(avg_7))

        elif choice == "2": # Option 2: Show this user's rank among all users.
            
            rank, total, total_users = get_user_rank(tracker.name)
            print("\n===== My Rank =====")
            print("User: " + tracker.name)
            print("Total points: " + str(total))
            if total_users == 0 and total == 0:
                print("Rank: N/A (no records yet)") # No one has records yet
            else:
                print("Rank: " + str(rank) + " out of " + str(max(total_users, rank))) # If the user has no record, we show them after the last rank.

        elif choice == "3":  # Option 3: Print the top-5 leaderboard.
            
            show_leaderboard(top_n = 5)

        elif choice == "4": # Option 4: Switch to another user (start tracking for a new name).
            
            new_name = input("Enter new user name: ").strip()
            if new_name:
                tracker = HabitTracker(new_name)
                print("Switched to user: " + new_name)
            else:
                print("Name cannot be empty.") # Avoid empty name

        elif choice == "exit": # Exit the program.
            print("Bye! See you next time.")
            break

        else:
            print("Please choose 1/2/3/4 or type EXIT.") # Invalid input: ask user to choose again.

if __name__ == '__main__':
    main()