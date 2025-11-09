#!/usr/bin/bpftrace

tracepoint:sched:sched_switch
/args->next_comm == "python" || args->next_comm == "python3"/
{
    printf("[%s] %s (PID:%d) on CPU\n",
           strftime("%H:%M:%S", nsecs / 1e9), args->next_comm, args->next_pid);
}

tracepoint:sched:sched_switch
/args->prev_comm == "python" || args->prev_comm == "python3"/
{
    printf("[%s] %s (PID:%d) off CPU\n",
           strftime("%H:%M:%S", nsecs / 1e9), args->prev_comm, args->prev_pid);
}

tracepoint:sched:sched_wakeup
/args->comm == "python" || args->comm == "python3"/
{
    printf("[%s] %s (PID:%d) woken up\n",
           strftime("%H:%M:%S", nsecs / 1e9), args->comm, args->pid);
}

END
{
    printf("\n=== CPU Scheduling Summary ===\n");
    printf("Analysis complete. Check events above for scheduling patterns.\n");
}
