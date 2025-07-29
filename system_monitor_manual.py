import psutil
import time
import os
import platform

# For CPU usage calculation (manual)
_last_cpu_times = None
_last_cpu_time_stamp = None

# For network IO rate calculation (manual)
_last_net_io = None
_last_net_time_stamp = None

# For process CPU usage (manual)
_last_process_cpu_times = {}
_last_process_time_stamp = None

#give CPU time
def _get_raw_cpu_jiffies():
    cpu_times = psutil.cpu_times()
    # Use getattr for cross-platform compatibility
    return {
        'user': getattr(cpu_times, 'user', 0),
        'nice': getattr(cpu_times, 'nice', 0),  # may not exist on Windows
        'system': getattr(cpu_times, 'system', 0),
        'idle': getattr(cpu_times, 'idle', 0),
        'iowait': getattr(cpu_times, 'iowait', 0),   # mostly Linux
        'irq': getattr(cpu_times, 'irq', 0),         # mostly Linux
        'softirq': getattr(cpu_times, 'softirq', 0), # mostly Linux
        'steal': getattr(cpu_times, 'steal', 0),     # mostly Linux
    }

def calculate_cpu_usage():
    """
    Calculate CPU usage % manually based on jiffies/time deltas.
    Returns CPU usage percentage (0 to 100).
    """
    global _last_cpu_times, _last_cpu_time_stamp

    current_times = _get_raw_cpu_jiffies()
    current_time = time.time()

    if _last_cpu_times is None:
        # First call, just store and return 0
        _last_cpu_times = current_times
        _last_cpu_time_stamp = current_time
        return 0.0

    # Calculate deltas
    delta_user = current_times['user'] - _last_cpu_times['user']
    delta_nice = current_times['nice'] - _last_cpu_times['nice']
    delta_system = current_times['system'] - _last_cpu_times['system']
    delta_idle = current_times['idle'] - _last_cpu_times['idle']
    delta_iowait = current_times['iowait'] - _last_cpu_times['iowait']
    delta_irq = current_times['irq'] - _last_cpu_times['irq']
    delta_softirq = current_times['softirq'] - _last_cpu_times['softirq']
    delta_steal = current_times['steal'] - _last_cpu_times['steal']

    total_delta = (delta_user + delta_nice + delta_system + delta_idle + 
                   delta_iowait + delta_irq + delta_softirq + delta_steal)

    busy_delta = total_delta - delta_idle - delta_iowait

    # Avoid division by zero
    if total_delta <= 0:
        cpu_usage_percent = 0.0
    else:
        cpu_usage_percent = (busy_delta / total_delta) * 100.0

    # Update stored values
    _last_cpu_times = current_times
    _last_cpu_time_stamp = current_time

    # Clamp between 0 and 100
    return max(0.0, min(cpu_usage_percent, 100.0))

#How much Memory is used /Memory usage deta hai in % and GB.
def get_memory_info():
    """
    Return memory info dictionary:
    {
        'percentage': float (used percent),
        'used_gb': float,
        'total_gb': float
    }
    """
    mem = psutil.virtual_memory()
    return {
        'percentage': mem.percent,
        'used_gb': mem.used / (1024 ** 3),
        'total_gb': mem.total / (1024 ** 3)
    }

#Disk calculate
def get_disk_usage(path='/'):
    """
    Return disk usage info dictionary:
    {
        'percentage': float (used percent),
        'used_gb': float,
        'total_gb': float
    }
    """
    disk = psutil.disk_usage(path)
    return {
        'percentage': disk.percent,
        'used_gb': disk.used / (1024 ** 3),
        'total_gb': disk.total / (1024 ** 3)
    }

#claculate network speed in kbs
def calculate_network_io_rates():
    """
    Calculate network IO rates in KB/s since last call.
    Returns:
    {
        'sent_kbps': float,
        'recv_kbps': float
    }
    """
    global _last_net_io, _last_net_time_stamp

    current_net = psutil.net_io_counters()
    current_time = time.time()

    if _last_net_io is None:
        _last_net_io = current_net
        _last_net_time_stamp = current_time
        return {'sent_kbps': 0.0, 'recv_kbps': 0.0}

    delta_time = current_time - _last_net_time_stamp
    if delta_time <= 0:
        return {'sent_kbps': 0.0, 'recv_kbps': 0.0}

    sent_bytes = current_net.bytes_sent - _last_net_io.bytes_sent
    recv_bytes = current_net.bytes_recv - _last_net_io.bytes_recv

    sent_kbps = (sent_bytes / 1024) / delta_time
    recv_kbps = (recv_bytes / 1024) / delta_time

    _last_net_io = current_net
    _last_net_time_stamp = current_time

    return {'sent_kbps': sent_kbps, 'recv_kbps': recv_kbps}

#System kab se chal raha hai uska time (uptime) deta hai in HH:MM:SS.
def get_system_uptime():
    """
    Return system uptime as string HH:MM:SS
    """
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    hrs, rem = divmod(int(uptime_seconds), 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs:02}:{mins:02}:{secs:02}"

#System ke top 10 CPU consuming processes ka data deta hai:
def calculate_process_cpu_usage(top_n=10):
    """
    Calculate CPU and memory usage for processes and return top_n by CPU%.
    Returns list of dicts with keys:
    pid, name, cpu_percent, memory_percent, threads, user
    """
    global _last_process_cpu_times, _last_process_time_stamp

    current_time = time.time()

    if _last_process_time_stamp is None:
        # First call: initialize dictionary with cpu_times
        _last_process_cpu_times = {}
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                cpu_times = proc.cpu_times()
                _last_process_cpu_times[proc.pid] = cpu_times.user + cpu_times.system
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        _last_process_time_stamp = current_time
        # Return empty first time
        return []

    delta_time = current_time - _last_process_time_stamp
    if delta_time <= 0:
        delta_time = 1  # avoid div zero

    process_info_list = []

    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'num_threads']):
        try:
            current_cpu_times = proc.cpu_times()
            prev_cpu_time = _last_process_cpu_times.get(proc.pid, 0)
            current_cpu_time = current_cpu_times.user + current_cpu_times.system
            cpu_delta = current_cpu_time - prev_cpu_time
            cpu_percent = (cpu_delta / delta_time) * 100.0

            _last_process_cpu_times[proc.pid] = current_cpu_time

            process_info_list.append({
                'pid': proc.pid,
                'name': proc.info['name'],
                'cpu_percent': cpu_percent,
                'memory_percent': proc.info['memory_percent'],
                'threads': proc.info['num_threads'],
                'user': proc.info['username']
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    _last_process_time_stamp = current_time

    # Sort descending by CPU%
    process_info_list.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return process_info_list[:top_n]
