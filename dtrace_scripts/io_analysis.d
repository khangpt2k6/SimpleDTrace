#!/usr/bin/bpftrace

tracepoint:syscalls:sys_enter_read,
tracepoint:syscalls:sys_enter_write,
tracepoint:syscalls:sys_enter_open,
tracepoint:syscalls:sys_enter_close,
tracepoint:syscalls:sys_enter_openat
/comm == "python" || comm == "python3"/
{
    printf("[%s] %s (PID:%d) -> %s\n", strftime("%H:%M:%S", nsecs / 1e9), comm, pid, probe);
}

tracepoint:syscalls:sys_exit_read,
tracepoint:syscalls:sys_exit_write
/comm == "python" || comm == "python3"/
{
    printf("       Result: %ld\n", retval);
    @io[comm, probe] = count();
}

END
{
    printf("\n=== I/O Operations Summary ===\n");
    print(@io);
}
