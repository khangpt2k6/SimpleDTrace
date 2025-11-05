#!/usr/bin/dtrace -s
/*
 * syscalls.d - Track system calls from both Flask and Noise Generator processes
 * 
 * Usage:
 *   dtrace -s syscalls.d 2>/dev/null | head -100
 * 
 * Shows: Syscall name, process name, execution time
 */

probe syscall.*.entry
{
    if (execname() == "python" || execname() == "python3") {
        @calls[execname(), probefunc()] <<< 1;
    }
}

probe syscall.*.return
{
    if (execname() == "python" || execname() == "python3") {
        @times[execname(), probefunc()] <<< 1;
    }
}

END
{
    printf("\n=== System Calls Summary ===\n");
    printf("Process: Function Count\n");
    printa(@calls);
    
    printf("\n=== Average Execution Time (ns) ===\n");
    printa(@times);
}