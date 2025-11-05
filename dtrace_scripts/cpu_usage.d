#!/usr/bin/bpftrace

tracepoint:sched:sched_switch
/next_comm == "python" || next_comm == "python3"/
{
    printf("[%s] %s (PID:%d) on CPU\n",
           strftime("%H:%M:%S", nsecs / 1e9), next_comm, next_pid);
}

tracepoint:sched:sched_switch
/prev_comm == "python" || prev_comm == "python3"/
{
    printf("[%s] %s (PID:%d) off CPU\n",
           strftime("%H:%M:%S", nsecs / 1e9), prev_comm, prev_pid);
}

tracepoint:sched:sched_wakeup
/comm == "python" || comm == "python3"/
{
    printf("[%s] %s (PID:%d) woken up\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, pid);
}

END
{
    printf("\n=== CPU Scheduling Summary ===\n");
    printf("Analysis complete. Check events above for scheduling patterns.\n");
}
