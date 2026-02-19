# Code for menu taken from https://gist.github.com/lurch/2494781 and modified for my needs

from .reading_statistics import *
import curses
import json
import os


def clear_terminal():
    """Close the curses menu and clear the terminal
    """
    curses.endwin()
    os.system("cls" if os.name == "nt" else "clear")


def press_enter():
    """Press Enter to continue execution
    """
    input("\nPress Enter to continue...")


with open(f"{__package__}/menu.json", "r") as file:
    menu_data = json.load(file)


screen = curses.initscr()  # initializes a new window for capturing key presses
curses.noecho()  # Disables automatic echoing of key presses (prevents program from input each key twice)
curses.cbreak()  # Disables line buffering (runs each key as it is pressed rather than waiting for the return key to pressed)
curses.start_color()  # Lets you use colors when highlighting selected menu option
screen.keypad(1)  # Capture input from keypad

# Change this to use different colors when highlighting
# Sets up color pair #1, it does black text with white background
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
h = curses.color_pair(1)  # h is the coloring for a highlighted menu option
n = curses.A_NORMAL  # n is the coloring for a non highlighted menu option

# This function displays the appropriate menu and returns the option selected


def runmenu(menu, parent):

    # work out what text to display as the last menu option
    if parent is None:
        lastoption = "Exit"
    else:
        lastoption = "Return to %s menu" % parent["title"]

    optioncount = len(menu["options"])  # how many options in this menu

    pos = 0  # pos is the zero-based index of the hightlighted menu option.  Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what option has been selected
    oldpos = None  # used to prevent the screen being redrawn every time
    x = None  # control for while loop, let's you scroll through options until return key is pressed then returns pos to program

    # Loop until return key is pressed
    while x != ord("\n"):
        if pos != oldpos:
            oldpos = pos
            screen.clear()  # clears previous screen on key press and updates display based on pos
            screen.border(0)
            # Title for this menu
            screen.addstr(2, 2, menu["title"], curses.A_STANDOUT)
            # Subtitle for this menu
            screen.addstr(4, 2, menu["subtitle"], curses.A_BOLD)

            # Display all the menu items, showing the "pos" item highlighted
            for index in range(optioncount):
                textstyle = n
                if pos == index:
                    textstyle = h
                screen.addstr(5+index, 4, "%d - %s" %
                              (index+1, menu["options"][index]["title"]), textstyle)
            # Now display Exit/Return at bottom of menu
            textstyle = n
            if pos == optioncount:
                textstyle = h
            screen.addstr(5+optioncount, 4, "%d - %s" %
                          (optioncount+1, lastoption), textstyle)
            screen.refresh()
            # finished updating screen

        x = screen.getch()  # Gets user input

        # What is user input?
        if x >= ord("1") and x <= ord(str(optioncount+1)):
            # convert keypress back to a number, then subtract 1 to get index
            pos = x - ord("0") - 1
        elif x == 258:  # down arrow
            if pos < optioncount:
                pos += 1
            else:
                pos = 0
        elif x == 259:  # up arrow
            if pos > 0:
                pos += -1
            else:
                pos = optioncount
        elif x != ord("\n"):
            curses.flash()

    # return index of the selected item
    return pos

# This function calls showmenu and then acts on the selected item


def processmenu(menu, parent=None):
    optioncount = len(menu["options"])
    exitmenu = False
    while not exitmenu:  # Loop until the user exits the menu
        getin = runmenu(menu, parent)
        if getin == optioncount:
            exitmenu = True
        elif menu["options"][getin]["type"] == "command":
            for i in menu["options"][getin]["command"]:  # run the command
                exec(i)
        elif menu["options"][getin]["type"] == "menu":
            processmenu(menu["options"][getin], menu)  # display the submenu


# Main program
processmenu(menu_data)
# VITAL!  This closes out the menu system and returns you to the bash prompt.
curses.endwin()
db.close()
os.system("cls" if os.name == "nt" else "clear")
