#!/usr/bin/bpftrace

tracepoint:sched:sched_process_fork
/comm == "python" || comm == "python3"/
{
    printf("[%s] New process: %s (PID:%d, PPID:%d)\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, child_pid, pid);
}

tracepoint:sched:sched_process_exit
/comm == "python" || comm == "python3"/
{
    printf("[%s] Process exited: %s (PID:%d)\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, pid);
}

tracepoint:raw_syscalls:sys_enter
/pid != 0 && (comm == "python" || comm == "python3")/
{
    @total_syscalls[comm] = count();
}

END
{
    printf("\n=== Process Activity Summary ===\n");
    print(@total_syscalls);
}
