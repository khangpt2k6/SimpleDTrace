#!/usr/bin/bpftrace

tracepoint:raw_syscalls:sys_enter
/comm == "python" || comm == "python3"/
{
    @calls[comm, syscall] = count();
}

tracepoint:raw_syscalls:sys_exit
/comm == "python" || comm == "python3"/
{
    @times[comm, syscall] = count();
}

END
{
    printf("\n=== System Calls Summary ===\n");
    print(@calls);
    
    printf("\n=== System Call Frequency ===\n");
    print(@times);
}
