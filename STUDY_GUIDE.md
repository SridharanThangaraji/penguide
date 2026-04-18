# Penguide - Project Study Guide

This guide contains the common questions and answers used for the Penguide project demo. Project members can use this to study the core concepts and the agent's expected behavior.

---

## Core Concepts

### Q: What is a kernel?
**A:** The kernel is the core part of an operating system. It manages the system's resources and the communication between hardware and software. Think of it as the 'manager' of the computer that handles memory, processes, and device drivers.

### Q: What is Linux?
**A:** Linux is an open-source Unix-like operating system kernel first released by Linus Torvalds in 1991. It is the foundation for many operating system distributions (distros) like Ubuntu, Fedora, and Arch Linux.

### Q: What is a shell?
**A:** A shell is a command-line interpreter that provides a user interface for the Unix-like operating systems. It takes your commands and gives them to the kernel to execute. Common shells include Bash and Zsh.

### Q: What is a terminal?
**A:** A terminal is a text-based interface used to interact with the computer. You type commands, and the terminal displays the output from the shell.

### Q: What is sudo?
**A:** Sudo (SuperUser DO) is a program that allows users to run programs with the security privileges of another user, typically the superuser (root).

### Q: What is root?
**A:** Root is the username or account that by default has access to all commands and files on a Linux system. It is also known as the superuser.

---

## File & Directory Operations

### Q: How do I list files?
**Command:** `ls -F`
**Explanation:** You use the `ls` command to list files and directories in your current location.

### Q: How do I make a directory?
**Command:** `mkdir folder_name`
**Explanation:** You use the `mkdir` command to create a new folder (directory).

### Q: How do I create a file?
**Command:** `touch file_name`
**Explanation:** The `touch` command is the simplest way to create a new empty file.

### Q: How do I delete a file?
**Command:** `rm file_name`
**Explanation:** You use the `rm` command (remove) to delete a file. Be careful, as this is permanent!

### Q: How do I copy a file?
**Command:** `cp source destination`
**Explanation:** The `cp` command (copy) duplicates a file from one location to another.

### Q: How do I move or rename a file?
**Command:** `mv source destination`
**Explanation:** The `mv` command (move) shifts a file to a new location or renames it.

---

## System Information

### Q: How do I see system information?
**Command:** `uname -a`
**Explanation:** The `uname` command prints system information. Using `-a` gives you all details including the kernel version.

### Q: How do I see the date?
**Command:** `date`
**Explanation:** The `date` command shows the current system date and time.

### Q: What is my hostname?
**Command:** `hostname`
**Explanation:** The `hostname` command shows the name assigned to your computer on the network.

### Q: Who is logged in?
**Command:** `who`
**Explanation:** The `who` command shows a list of users currently logged into the system.

### Q: What is my user ID?
**Command:** `id`
**Explanation:** The `id` command shows your current user ID (UID) and group IDs (GID).

### Q: How long has the system been running?
**Command:** `uptime`
**Explanation:** The `uptime` command tells you how long the system has been active since the last boot.

### Q: How do I see memory usage?
**Command:** `free -h`
**Explanation:** The `free` command displays the total amount of free and used physical memory and swap in the system.

### Q: How do I see disk space?
**Command:** `df -h`
**Explanation:** The `df` command (disk free) displays the amount of available disk space on file systems.

---

## Content Viewing & Searching

### Q: How do I see file contents?
**Command:** `cat file_name`
**Explanation:** The `cat` command (concatenate) is used to display the entire contents of a file in the terminal.

### Q: How do I see the start of a file?
**Command:** `head file_name`
**Explanation:** The `head` command displays the first 10 lines of a file by default.

### Q: How do I see the end of a file?
**Command:** `tail file_name`
**Explanation:** The `tail` command displays the last 10 lines of a file. It's great for checking logs.

### Q: How do I search for text in a file?
**Command:** `grep 'pattern' file_name`
**Explanation:** The `grep` command searches for a specific pattern of text within files.

### Q: How do I find a file?
**Command:** `find . -name 'filename'`
**Explanation:** The `find` command searches for files and directories based on various criteria.

---

## Networking & Miscellaneous

### Q: How do I see my IP address?
**Command:** `ip addr`
**Explanation:** The `ip addr` command shows all network interfaces and their assigned IP addresses.

### Q: How do I clear the screen?
**Command:** `clear`
**Explanation:** The `clear` command wipes all previous output from your terminal screen.

### Q: How do I see command history?
**Command:** `history`
**Explanation:** The `history` command shows a list of commands you have previously typed.
