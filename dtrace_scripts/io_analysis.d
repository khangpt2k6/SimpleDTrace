#!/usr/bin/dtrace -s
/*
 * io_analysis.d - Monitor I/O operations and file access
 * 
 * Usage:
 *   dtrace -s io_analysis.d 2>/dev/null
 * 
 * Shows: File I/O patterns, read/write operations
 */

probe syscall.read.entry,
      syscall.write.entry,
      syscall.open.entry,
      syscall.close.entry,
      syscall.openat.entry
{
    if (execname() == "python" || execname() == "python3") {
        printf("[%s] %s (PID:%d) -> %s()\n",
               ctime(gettimeofday_s()), execname(), pid(), probefunc());
    }
}

probe syscall.read.return,
      syscall.write.return
{
    if (execname() == "python" || execname() == "python3") {
        printf("       Result: %d bytes\n", retval);
        @io[execname(), probefunc()] <<< 1;
    }
}

END
{
    printf("\n=== I/O Operations Summary ===\n");
    printa(@io);
}