import sys

DEMO_QA = {
    "hello": "Hello! I am Penguide, your Linux and Kernel teaching assistant. How can I help you learn today?",
    "hi": "Hi there! Ready to explore the Linux kernel?",
    "what is a kernel": (
        "The kernel is the core part of an operating system. It manages the system's resources "
        "and the communication between hardware and software. Think of it as the 'manager' "
        "of the computer that handles memory, processes, and device drivers."
    ),
    "what is kernal": (
        "The kernel is the core part of an operating system. It manages the system's resources "
        "and the communication between hardware and software. Think of it as the 'manager' "
        "of the computer that handles memory, processes, and device drivers."
    ),
    "how do i see running processes": (
        "You can see running processes using the `ps` command (Process Status). "
        "For a real-time view, `top` or `htop` are commonly used.\n\n"
        "RUN: ps aux"
    ),
    "what is linux": (
        "Linux is an open-source Unix-like operating system kernel first released by Linus Torvalds "
        "in 1991. It is the foundation for many operating system distributions (distros) like "
        "Ubuntu, Fedora, and Arch Linux."
    ),
    "how do i list files": (
        "You use the `ls` command to list files and directories in your current location.\n\n"
        "RUN: ls -F"
    ),
    "who am i": (
        "The `whoami` command prints the effective username of the current user.\n\n"
        "RUN: whoami"
    ),
    "where am i": (
        "The `pwd` command (Print Working Directory) shows the full path of your current directory.\n\n"
        "RUN: pwd"
    ),
    "how do i see disk space": (
        "The `df` command (disk free) displays the amount of available disk space on file systems.\n\n"
        "RUN: df -h"
    ),
    "how do i make a directory": (
        "You use the `mkdir` command to create a new folder (directory).\n\n"
        "RUN: mkdir my_new_folder"
    ),
    "how do i create a file": (
        "The `touch` command is the simplest way to create a new empty file.\n\n"
        "RUN: touch new_file.txt"
    ),
    "how do i delete a file": (
        "You use the `rm` command (remove) to delete a file. Be careful, as this is permanent!\n\n"
        "RUN: rm new_file.txt"
    ),
    "how do i copy a file": (
        "The `cp` command (copy) duplicates a file from one location to another.\n\n"
        "RUN: cp README.md README_backup.md"
    ),
    "how do i move a file": (
        "The `mv` command (move) shifts a file to a new location or renames it.\n\n"
        "RUN: mv README_backup.md old_readme.md"
    ),
    "how do i see the date": (
        "The `date` command shows the current system date and time.\n\n"
        "RUN: date"
    ),
    "what is my hostname": (
        "The `hostname` command shows the name assigned to your computer on the network.\n\n"
        "RUN: hostname"
    ),
    "who is logged in": (
        "The `who` command shows a list of users currently logged into the system.\n\n"
        "RUN: who"
    ),
    "what is my user id": (
        "The `id` command shows your current user ID (UID) and group IDs (GID).\n\n"
        "RUN: id"
    ),
    "how do i see system information": (
        "The `uname` command prints system information. Using `-a` gives you all details including the kernel version.\n\n"
        "RUN: uname -a"
    ),
    "how long has the system been running": (
        "The `uptime` command tells you how long the system has been active since the last boot.\n\n"
        "RUN: uptime"
    ),
    "how do i see memory usage": (
        "The `free` command displays the total amount of free and used physical memory and swap in the system.\n\n"
        "RUN: free -h"
    ),
    "how do i see file contents": (
        "The `cat` command (concatenate) is used to display the entire contents of a file in the terminal.\n\n"
        "RUN: cat requirements.txt"
    ),
    "how do i see the start of a file": (
        "The `head` command displays the first 10 lines of a file by default.\n\n"
        "RUN: head README.md"
    ),
    "how do i see the end of a file": (
        "The `tail` command displays the last 10 lines of a file. It's great for checking logs.\n\n"
        "RUN: tail README.md"
    ),
    "how do i search for text in a file": (
        "The `grep` command searches for a specific pattern of text within files.\n\n"
        "RUN: grep 'Penguide' README.md"
    ),
    "how do i find a file": (
        "The `find` command searches for files and directories in a directory hierarchy based on various criteria.\n\n"
        "RUN: find . -name 'settings.py'"
    ),
    "how do i see my ip address": (
        "The `ip addr` command shows all network interfaces and their assigned IP addresses.\n\n"
        "RUN: ip addr"
    ),
    "what is a shell": (
        "A shell is a command-line interpreter that provides a user interface for the Unix-like operating systems. "
        "It takes your commands and gives them to the kernel to execute. Common shells include Bash and Zsh."
    ),
    "what is sudo": (
        "Sudo (SuperUser DO) is a program that allows users to run programs with the security privileges of another user, "
        "typically the superuser (root)."
    ),
    "what is root": (
        "Root is the username or account that by default has access to all commands and files on a Linux system. "
        "It is also known as the superuser."
    ),
    "how do i clear the screen": (
        "The `clear` command wipes all previous output from your terminal screen, giving you a fresh prompt.\n\n"
        "RUN: clear"
    ),
    "what is a terminal": (
        "A terminal is a text-based interface used to interact with the computer. You type commands, "
        "and the terminal displays the output from the shell."
    ),
    "how do i see command history": (
        "The `history` command shows a list of commands you have previously typed in the current session.\n\n"
        "RUN: history"
    )
}

def _normalize(text: str) -> str:
    """Normalize text for better matching."""
    text = text.lower().strip()
    # Remove common punctuation
    for char in "?!.,":
        text = text.replace(char, "")
    # Remove common filler words
    for word in [" the ", " a ", " an "]:
        text = text.replace(word, " ")
    return " ".join(text.split())

def get_demo_answer(user_input: str) -> str | None:
    """
    Check if the user input matches any hardcoded demo questions.
    Returns the answer if found, otherwise None.
    """
    normalized_input = _normalize(user_input)
    
    # Check each key by normalizing it as well
    for key, answer in DEMO_QA.items():
        normalized_key = _normalize(key)
        if normalized_key == normalized_input:
            return answer
            
    # Fallback fuzzy match: check if normalized input is in normalized key or vice versa
    for key, answer in DEMO_QA.items():
        normalized_key = _normalize(key)
        if normalized_input in normalized_key or normalized_key in normalized_input:
            return answer
            
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        answer = get_demo_answer(query)
        if answer:
            print(answer)
        else:
            # If no demo match, we could just exit silently or show a generic help message
            # but for "real" behavior, we'd want the orchestrator to handle it.
            # Here we'll just print nothing or a standard reply.
            pass
    else:
        print("Usage: python3 core/demo.py \"your question\"")
