# Linux Kernel Process Management

The process management in the Linux kernel is responsible for creating, managing, and terminating processes. 

## Key Concepts

- **Task Structure (`task_struct`)**: Every process in the system is represented by a `task_struct`. It contains information about the process state, stack, flags, and more.
- **Scheduling**: The kernel uses a scheduler to decide which process runs next. Modern Linux uses the Completely Fair Scheduler (CFS).
- **System Calls**: Processes interact with the kernel through system calls (e.g., `fork`, `exec`, `exit`).

---
*Reference: Derived from Linux Kernel Documentation.*
