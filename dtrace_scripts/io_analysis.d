#!/usr/bin/bpftrace

// Comprehensive I/O Analysis for Cloud/Server Computing Research
// Tracks file operations, performance metrics, and access patterns

// File Open Operations - Track all processes
tracepoint:syscalls:sys_enter_open,
tracepoint:syscalls:sys_enter_openat
{
    @open_count[comm] = count();
    @open_files[comm, str(args->filename)] = count();

    // Track file access patterns
    if (str(args->filename) != "") {
        @file_access_patterns[str(args->filename)] = count();
    }

    printf("[%s] OPEN: %s (PID:%d) -> %s\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, pid, str(args->filename));
}

// File Read Operations
tracepoint:syscalls:sys_enter_read
{
    @read_count[comm] = count();
    @read_sizes[comm] = hist(args->count);
    @total_read_bytes[comm] = sum(args->count);

    // Track read start time for latency
    @read_start[pid, args->fd] = nsecs;

    printf("[%s] READ: %s (PID:%d, FD:%d) size=%lu\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, pid, args->fd, args->count);
}

tracepoint:syscalls:sys_exit_read
{
    $start_time = @read_start[pid, args->fd];
    if ($start_time) {
        $latency = nsecs - $start_time;
        @read_latency[comm] = avg($latency);
        @read_latency_hist[comm] = hist($latency / 1000000); // ms
        delete(@read_start[pid, args->fd]);
    }

    if (retval > 0) {
        @read_success[comm] = count();
        @actual_read_bytes[comm] = sum(retval);
    } else if (retval < 0) {
        @read_errors[comm] = count();
    }
}

// File Write Operations
tracepoint:syscalls:sys_enter_write
{
    @write_count[comm] = count();
    @write_sizes[comm] = hist(args->count);
    @total_write_bytes[comm] = sum(args->count);

    // Track write start time for latency
    @write_start[pid, args->fd] = nsecs;

    printf("[%s] WRITE: %s (PID:%d, FD:%d) size=%lu\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, pid, args->fd, args->count);
}

tracepoint:syscalls:sys_exit_write
{
    $start_time = @write_start[pid, args->fd];
    if ($start_time) {
        $latency = nsecs - $start_time;
        @write_latency[comm] = avg($latency);
        @write_latency_hist[comm] = hist($latency / 1000000); // ms
        delete(@write_start[pid, args->fd]);
    }

    if (retval > 0) {
        @write_success[comm] = count();
        @actual_write_bytes[comm] = sum(retval);
    } else if (retval < 0) {
        @write_errors[comm] = count();
    }
}

// File Close Operations
tracepoint:syscalls:sys_enter_close
{
    @close_count[comm] = count();
    printf("[%s] CLOSE: %s (PID:%d, FD:%d)\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, pid, args->fd);
}

// Directory Operations
tracepoint:syscalls:sys_enter_getdents,
tracepoint:syscalls:sys_enter_getdents64
{
    @dir_read_count[comm] = count();
    printf("[%s] DIR_READ: %s (PID:%d, FD:%d)\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, pid, args->fd);
}

// File System Operations
tracepoint:syscalls:sys_enter_stat,
tracepoint:syscalls:sys_enter_lstat,
tracepoint:syscalls:sys_enter_fstat
{
    @stat_count[comm] = count();
    printf("[%s] STAT: %s (PID:%d) -> %s\n",
           strftime("%H:%M:%S", nsecs / 1e9), comm, pid, str(args->filename));
}

// Periodic I/O Performance Snapshot
interval:s:30
{
    time("%H:%M:%S");
    printf("=== 30-Second I/O Performance Snapshot ===\n");

    if (@read_count) {
        printf("Read Operations by Process:\n");
        print(@read_count, 5);
        printf("Read Throughput (bytes/sec): ");
        print(@total_read_bytes, 5);
    }

    if (@write_count) {
        printf("Write Operations by Process:\n");
        print(@write_count, 5);
        printf("Write Throughput (bytes/sec): ");
        print(@total_write_bytes, 5);
    }

    if (@read_latency) {
        printf("Read Latency (avg ms): ");
        print(@read_latency, 5);
    }

    // Clear counters for next interval
    clear(@read_count);
    clear(@write_count);
    clear(@total_read_bytes);
    clear(@total_write_bytes);
    clear(@open_count);
    clear(@close_count);
    clear(@stat_count);
}

// File Access Pattern Analysis
tracepoint:syscalls:sys_enter_openat
/str(args->filename) != ""/
{
    // Categorize files by type
    $filename = str(args->filename);
    if ($filename ~ /\.log$/) {
        @file_types["log"] = count();
    } else if ($filename ~ /\.(txt|md|conf|ini|cfg|yaml|yml|json|xml)$/) {
        @file_types["config"] = count();
    } else if ($filename ~ /\.(so|dll|dylib)$/) {
        @file_types["library"] = count();
    } else if ($filename ~ /\.(db|sqlite|sql)$/) {
        @file_types["database"] = count();
    } else {
        @file_types["other"] = count();
    }
}

END
{
    printf("\n=== Comprehensive I/O Analysis Summary ===\n");

    printf("File Operations:\n");
    printf("- Open operations: ");
    print(@open_count);
    printf("- Close operations: ");
    print(@close_count);
    printf("- Stat operations: ");
    print(@stat_count);
    printf("- Directory reads: ");
    print(@dir_read_count);

    printf("\nRead Operations:\n");
    printf("- Read calls: ");
    print(@read_count);
    printf("- Successful reads: ");
    print(@read_success);
    printf("- Read errors: ");
    print(@read_errors);
    printf("- Total bytes read: ");
    print(@total_read_bytes);
    printf("- Actual bytes read: ");
    print(@actual_read_bytes);
    printf("- Read size distribution: ");
    print(@read_sizes);
    printf("- Read latency (avg ns): ");
    print(@read_latency);
    printf("- Read latency histogram (ms): ");
    print(@read_latency_hist);

    printf("\nWrite Operations:\n");
    printf("- Write calls: ");
    print(@write_count);
    printf("- Successful writes: ");
    print(@write_success);
    printf("- Write errors: ");
    print(@write_errors);
    printf("- Total bytes written: ");
    print(@total_write_bytes);
    printf("- Actual bytes written: ");
    print(@actual_write_bytes);
    printf("- Write size distribution: ");
    print(@write_sizes);
    printf("- Write latency (avg ns): ");
    print(@write_latency);
    printf("- Write latency histogram (ms): ");
    print(@write_latency_hist);

    printf("\nFile Access Patterns:\n");
    printf("- Files by type: ");
    print(@file_types);
    printf("- Most accessed files: ");
    print(@file_access_patterns, 10);
    printf("- Files opened by process: ");
    print(@open_files, 5);

    // JSON Export for Research Analysis
    printf("\n=== JSON Export for Data Analysis ===\n");
    printf("{\n");
    printf("  \"timestamp\": \"%s\",\n", strftime("%Y-%m-%d %H:%M:%S", nsecs / 1e9));
    printf("  \"file_operations\": {\n");
    printf("    \"opens\": ");
    print(@open_count, 0, 1);
    printf(",\n    \"closes\": ");
    print(@close_count, 0, 1);
    printf(",\n    \"stats\": ");
    print(@stat_count, 0, 1);
    printf(",\n    \"dir_reads\": ");
    print(@dir_read_count, 0, 1);
    printf("\n  },\n");
    printf("  \"read_operations\": {\n");
    printf("    \"calls\": ");
    print(@read_count, 0, 1);
    printf(",\n    \"success\": ");
    print(@read_success, 0, 1);
    printf(",\n    \"errors\": ");
    print(@read_errors, 0, 1);
    printf(",\n    \"total_bytes\": ");
    print(@total_read_bytes, 0, 1);
    printf(",\n    \"actual_bytes\": ");
    print(@actual_read_bytes, 0, 1);
    printf(",\n    \"size_distribution\": ");
    print(@read_sizes, 0, 1);
    printf(",\n    \"latency_avg_ns\": ");
    print(@read_latency, 0, 1);
    printf("\n  },\n");
    printf("  \"write_operations\": {\n");
    printf("    \"calls\": ");
    print(@write_count, 0, 1);
    printf(",\n    \"success\": ");
    print(@write_success, 0, 1);
    printf(",\n    \"errors\": ");
    print(@write_errors, 0, 1);
    printf(",\n    \"total_bytes\": ");
    print(@total_write_bytes, 0, 1);
    printf(",\n    \"actual_bytes\": ");
    print(@actual_write_bytes, 0, 1);
    printf(",\n    \"size_distribution\": ");
    print(@write_sizes, 0, 1);
    printf(",\n    \"latency_avg_ns\": ");
    print(@write_latency, 0, 1);
    printf("\n  },\n");
    printf("  \"file_analysis\": {\n");
    printf("    \"file_types\": ");
    print(@file_types, 0, 1);
    printf(",\n    \"access_patterns\": ");
    print(@file_access_patterns, 0, 1);
    printf("\n  }\n");
    printf("}\n");
}
