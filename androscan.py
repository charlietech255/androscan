
"""
androscan ni tool iliyo undwa na charlie tech kama project yake ya kwanza kwenye safari yake ya kujifunza kutengeneza tools za termux
tool hii itakusaidia ku scan android device yako na kuona full details za kifaa chako ikiwemo malware app zinazo run at background
tool hii imeundwa kwa pure python with simple libralies ambazo haziitaj larger space wakati wa installation
"""

import os
import subprocess
import re
import json
import math
from datetime import datetime

# -------------------------------
# Terminal Colors
# -------------------------------
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
RED = "\033[0;31m"
MAGENTA = "\033[0;35m"
BOLD = "\033[1m"
RESET = "\033[0m"

# -------------------------------
# Help Functions kuzpa nguv core
# -------------------------------
def run_cmd(cmd, timeout=3):
    """Run shell command and return stdout stripped. Returns empty string on error."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except:
        return ""

def read_file(path):
    """Read a small text file and return content stripped, or empty string."""
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except:
        return ""

def format_bytes(bytes_val):
    """Convert bytes to human readable."""
    if bytes_val is None:
        return "N/A"
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PiB"

def format_temp(celsius_str):
    """Convert Celsius string to formatted output."""
    try:
        temp = float(celsius_str)
        return f"{temp:.1f}°C ({temp*9/5+32:.1f}°F)"
    except:
        return celsius_str

# -------------------------------
# 1. RAM Information (real from /proc/meminfo)
# -------------------------------
def get_ram_info():
    """Parse /proc/meminfo for accurate RAM usage."""
    try:
        with open("/proc/meminfo", "r") as f:
            mem = {}
            for line in f:
                if "MemTotal" in line:
                    mem["total"] = int(line.split()[1]) * 1024
                elif "MemAvailable" in line:
                    mem["avail"] = int(line.split()[1]) * 1024
                elif "MemFree" in line:
                    mem["free"] = int(line.split()[1]) * 1024
            if "avail" not in mem:
                # fallback: MemFree + Cached + Buffers
                cached = 0
                buffers = 0
                with open("/proc/meminfo", "r") as f2:
                    for line in f2:
                        if "Cached" in line:
                            cached = int(line.split()[1]) * 1024
                        if "Buffers" in line:
                            buffers = int(line.split()[1]) * 1024
                mem["avail"] = mem.get("free", 0) + cached + buffers
            mem["used"] = mem["total"] - mem["avail"]
            mem["used_percent"] = (mem["used"] * 100) // mem["total"] if mem["total"] else 0
            return mem
    except Exception as e:
        return None

# -------------------------------
# 2. CPU Information (real from sysfs + getprop)
# -------------------------------
def get_cpu_info():
    """CPU model, cores, max frequency, architecture, current frequency."""
    info = {
        "model": "Unknown",
        "cores": 0,
        "max_freq_mhz": "N/A",
        "curr_freq_mhz": "N/A",
        "arch": "N/A",
        "load_avg": "N/A"
    }
    # SoC name from Android properties
    soc = run_cmd("getprop ro.board.platform")
    if not soc:
        soc = run_cmd("getprop ro.hardware")
    if soc:
        info["model"] = soc.capitalize()
    else:
        # fallback to /proc/cpuinfo
        model_line = run_cmd("grep -m1 'model name' /proc/cpuinfo | cut -d':' -f2")
        if model_line:
            info["model"] = model_line.strip()
    
    # Number of cores
    cpu_dirs = [d for d in os.listdir("/sys/devices/system/cpu/") if d.startswith("cpu") and d[3:].isdigit()]
    info["cores"] = len(cpu_dirs) if cpu_dirs else 0
    if info["cores"] == 0:
        info["cores"] = int(run_cmd("nproc") or 0)
    
    # Max frequency
    max_freq = 0
    for cpu in range(min(info["cores"], 8)):  # check first 8 cores
        path = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/cpuinfo_max_freq"
        if os.path.exists(path):
            val = read_file(path)
            if val.isdigit():
                max_freq = max(max_freq, int(val))
    if max_freq > 0:
        info["max_freq_mhz"] = f"{max_freq // 1000} MHz"
    
    # Current frequency (first core)
    curr_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
    curr = read_file(curr_path)
    if curr.isdigit():
        info["curr_freq_mhz"] = f"{int(curr) // 1000} MHz"
    
    # Architecture
    arch = run_cmd("uname -m")
    if "aarch64" in arch:
        info["arch"] = "ARM64 (AArch64)"
    elif "armv" in arch:
        info["arch"] = arch.upper()
    else:
        info["arch"] = arch or "N/A"
    
    # Load average (from /proc/loadavg)
    load = read_file("/proc/loadavg")
    if load:
        parts = load.split()
        if len(parts) >= 3:
            info["load_avg"] = f"{parts[0]} (1m), {parts[1]} (5m), {parts[2]} (15m)"
    return info

# -------------------------------
# 3. Storage Information (df -h)
# -------------------------------
def get_storage_info():
    """Internal (/data) and external (/sdcard) storage."""
    info = {"internal": "", "sdcard": ""}
    df_out = run_cmd("df -h /data")
    if df_out:
        lines = df_out.splitlines()
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 6:
                info["internal"] = f"{parts[2]} used / {parts[1]} total ({parts[4]} used)"
    # SD card
    for mount in ["/sdcard", "/storage/emulated/0"]:
        if os.path.exists(mount):
            df_out = run_cmd(f"df -h {mount}")
            if df_out and "No such" not in df_out:
                lines = df_out.splitlines()
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 6:
                        info["sdcard"] = f"{parts[2]} used / {parts[1]} total ({parts[4]} used)"
                        break
    return info

# -------------------------------
# 4. System Health (uptime, temperature, throttling)
# -------------------------------
def get_system_health():
    """Uptime, CPU temperature, thermal throttle status, available sensors."""
    health = {
        "uptime": "N/A",
        "temp_cpu": "N/A",
        "temp_battery": "N/A",
        "throttling": "Unknown",
        "load_average": "N/A"
    }
    # Uptime
    uptime_sec = read_file("/proc/uptime")
    if uptime_sec:
        secs = float(uptime_sec.split()[0])
        days = int(secs // 86400)
        hours = int((secs % 86400) // 3600)
        mins = int((secs % 3600) // 60)
        health["uptime"] = f"{days}d {hours}h {mins}m"
    
    # CPU temperature (common paths)
    temp_paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/devices/virtual/thermal/thermal_zone0/temp",
        "/sys/class/hwmon/hwmon0/temp1_input"
    ]
    for path in temp_paths:
        temp_raw = read_file(path)
        if temp_raw:
            try:
                temp_val = float(temp_raw) / 1000.0  # often in millidegrees
                health["temp_cpu"] = format_temp(str(temp_val))
                break
            except:
                if temp_raw.isdigit():
                    health["temp_cpu"] = format_temp(str(int(temp_raw)/1000))
                else:
                    health["temp_cpu"] = temp_raw
                break
    
    # Throttling indicator (if any)
    throttle = read_file("/sys/class/thermal/thermal_message/thermal_throttle")
    if throttle:
        health["throttling"] = "Yes" if "throttle" in throttle.lower() else "No"
    else:
        health["throttling"] = "Not reported"
    
    # Load average (reuse from CPU)
    load = read_file("/proc/loadavg")
    if load:
        health["load_average"] = load.split()[0:3]
    
    return health

# -------------------------------
# 5. Installed Apps (using pm list packages)
# -------------------------------
def get_installed_apps(limit=5):
    """Get count of user/system apps and top largest apps (requires Termux:API for sizes)."""
    apps = {
        "total_user": 0,
        "total_system": 0,
        "top_largest": []  # list of (name, size)
    }
    # List all packages
    all_packages = run_cmd("pm list packages").splitlines()
    user_packages = run_cmd("pm list packages -3").splitlines()
    apps["total_user"] = len(user_packages)
    apps["total_system"] = len(all_packages) - apps["total_user"]
    
    # Try to get app sizes using dumpsys package (optional, slow)
    # Instead, we list top 5 by package name (no size without extra permissions)
    # For simplicity, show first 5 user packages
    if user_packages:
        top5 = []
        for i, pkg in enumerate(user_packages[:limit]):
            # format: "package:com.example.app"
            pkg_name = pkg.replace("package:", "").strip()
            top5.append(pkg_name)
        apps["top_largest"] = top5
    return apps

# -------------------------------
# 6. Background Running Processes (ps -A)
# -------------------------------
def get_background_processes(limit=10):
    """Show top CPU or memory consuming processes (using 'ps' and 'top' -n1)."""
    processes = []
    # Use 'top -b -n 1' to get CPU/memory usage (available in Termux)
    top_out = run_cmd("top -b -n 1 -o %CPU,%MEM,CMD -w 512", timeout=5)
    if top_out:
        lines = top_out.splitlines()
        # Skip header lines
        data_start = False
        for line in lines:
            if "PID" in line and "%CPU" in line:
                data_start = True
                continue
            if data_start and line.strip() and not line.startswith("top"):
                parts = line.split()
                if len(parts) >= 3:
                    cpu = parts[0]
                    mem = parts[1]
                    cmd = ' '.join(parts[2:])[:40]  # truncate
                    processes.append(f"{cpu}% CPU | {mem}% MEM → {cmd}")
                if len(processes) >= limit:
                    break
    else:
        # Fallback to plain ps
        ps_out = run_cmd("ps -A -o %CPU,%MEM,CMD --sort=-%CPU | head -n 11")
        if ps_out:
            for line in ps_out.splitlines()[1:]:  # skip header
                if line.strip():
                    processes.append(line.strip()[:60])
    return processes

# -------------------------------
# 7. Battery Health (using /sys/class/power_supply/)
# -------------------------------
def get_battery_info():
    """Battery level, temperature, voltage, health, technology, status."""
    battery = {
        "level": "N/A",
        "temperature": "N/A",
        "voltage": "N/A",
        "health": "N/A",
        "technology": "N/A",
        "status": "N/A"
    }
    base_path = "/sys/class/power_supply/battery"
    if not os.path.exists(base_path):
        # try alternative
        base_path = "/sys/class/power_supply/Battery"
    if os.path.exists(base_path):
        battery["level"] = read_file(f"{base_path}/capacity") + "%"
        temp_raw = read_file(f"{base_path}/temp")
        if temp_raw:
            try:
                temp_c = int(temp_raw) / 10  # often in tenths of degree
                battery["temperature"] = format_temp(str(temp_c))
            except:
                battery["temperature"] = temp_raw
        voltage_raw = read_file(f"{base_path}/voltage_now")
        if voltage_raw:
            try:
                volt_mv = int(voltage_raw) / 1000
                battery["voltage"] = f"{volt_mv:.0f} mV"
            except:
                battery["voltage"] = voltage_raw
        battery["health"] = read_file(f"{base_path}/health") or "N/A"
        battery["technology"] = read_file(f"{base_path}/technology") or "N/A"
        battery["status"] = read_file(f"{base_path}/status") or "N/A"
    else:
        # fallback to dumpsys battery
        dumpsys = run_cmd("dumpsys battery")
        if dumpsys:
            for line in dumpsys.splitlines():
                line = line.strip()
                if line.startswith("level:"):
                    battery["level"] = line.split(":")[1].strip() + "%"
                elif line.startswith("temperature:"):
                    temp = int(line.split(":")[1].strip()) / 10
                    battery["temperature"] = format_temp(str(temp))
                elif line.startswith("voltage:"):
                    volt = int(line.split(":")[1].strip()) / 1000
                    battery["voltage"] = f"{volt:.0f} mV"
                elif line.startswith("health:"):
                    battery["health"] = line.split(":")[1].strip()
                elif line.startswith("technology:"):
                    battery["technology"] = line.split(":")[1].strip()
                elif line.startswith("status:"):
                    battery["status"] = line.split(":")[1].strip()
    return battery

# -------------------------------
# 8. Network Info (Wi-Fi, IP, data usage)
# -------------------------------
def get_network_info():
    """Wi-Fi SSID, IP address (wlan0), mobile data usage (rough)."""
    net = {
        "ssid": "Unknown",
        "ip": "N/A",
        "rx_bytes": "N/A",
        "tx_bytes": "N/A"
    }
    # Get active connection SSID (requires Termux:API or dumpsys)
    dumpsys_conn = run_cmd("dumpsys connectivity | grep 'WIFI' -A 5")
    if dumpsys_conn:
        ssid_match = re.search(r'SSID: "(.+?)"', dumpsys_conn)
        if ssid_match:
            net["ssid"] = ssid_match.group(1)
    # Get IP address
    ip_out = run_cmd("ip -4 addr show wlan0 | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){3}'")
    if ip_out:
        net["ip"] = ip_out
    else:
        # fallback
        net["ip"] = run_cmd("ifconfig wlan0 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}'")
    
    # Data usage from /proc/net/dev
    net_dev = read_file("/proc/net/dev")
    if net_dev:
        for line in net_dev.splitlines():
            if "wlan0" in line:
                parts = line.split()
                if len(parts) >= 10:
                    rx = int(parts[1]) if parts[1].isdigit() else 0
                    tx = int(parts[9]) if parts[9].isdigit() else 0
                    net["rx_bytes"] = format_bytes(rx)
                    net["tx_bytes"] = format_bytes(tx)
                break
    return net

# -------------------------------
# 9. Sensor Info (via getevent or Termux:Sensor)
# -------------------------------
def get_sensor_info():
    """List available sensors (if Termux:API installed, else try /sys/class/sensors)."""
    sensors = []
    # Try using Termux:Sensor command
    termux_sensor = run_cmd("termux-sensor -l 2>/dev/null")
    if termux_sensor and "error" not in termux_sensor.lower():
        try:
            data = json.loads(termux_sensor)
            for sensor_name in data.keys():
                sensors.append(sensor_name)
        except:
            pass
    if not sensors:
        # Fallback: check /sys/class/sensors/
        sensor_dir = "/sys/class/sensors/"
        if os.path.exists(sensor_dir):
            for item in os.listdir(sensor_dir):
                if item.startswith("sensor"):
                    sensors.append(item)
    return sensors[:10]  # limit to 10

# -------------------------------
# 10. Additional Device Info
# -------------------------------
def get_device_info():
    """Manufacturer, model, Android version, kernel, uptime (already done)."""
    device = {}
    device["manufacturer"] = run_cmd("getprop ro.product.manufacturer") or "Unknown"
    device["model"] = run_cmd("getprop ro.product.model") or "Unknown"
    device["android_version"] = run_cmd("getprop ro.build.version.release") or "Unknown"
    device["sdk"] = run_cmd("getprop ro.build.version.sdk") or "Unknown"
    device["kernel"] = run_cmd("uname -r") or "Unknown"
    return device

# -------------------------------
# Main Display Function
# -------------------------------
def display_all():
    print(f"{BOLD}{CYAN}═══════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{GREEN}           ADVANCED ANDROID SYSTEM ANALYZER by CHARLIE{RESET}")
    print(f"{BOLD}{CYAN}═══════════════════════════════════════════════════════════{RESET}\n")
    
    # 1. Device Info
    device = get_device_info()
    print(f"{BOLD}{MAGENTA}📱 DEVICE INFORMATION{RESET}")
    print(f"   {BLUE}Manufacturer   :{RESET} {device['manufacturer']}")
    print(f"   {BLUE}Model          :{RESET} {device['model']}")
    print(f"   {BLUE}Android Version:{RESET} {device['android_version']} (SDK {device['sdk']})")
    print(f"   {BLUE}Kernel         :{RESET} {device['kernel']}")
    print()
    
    # 2. RAM
    ram = get_ram_info()
    print(f"{BOLD}{YELLOW}📊 RAM USAGE{RESET}")
    if ram:
        print(f"   {BLUE}Total   :{RESET} {format_bytes(ram['total'])}")
        print(f"   {BLUE}Used    :{RESET} {format_bytes(ram['used'])} ({ram['used_percent']}%)")
        print(f"   {BLUE}Free    :{RESET} {format_bytes(ram['free'])}")
        print(f"   {BLUE}Available:{RESET} {format_bytes(ram['avail'])}")
    else:
        print(f"   {RED}Could not read RAM info{RESET}")
    print()
    
    # 3. CPU
    cpu = get_cpu_info()
    print(f"{BOLD}{YELLOW}⚙️ CPU INFORMATION{RESET}")
    print(f"   {BLUE}Model        :{RESET} {cpu['model']}")
    print(f"   {BLUE}Cores        :{RESET} {cpu['cores']}")
    print(f"   {BLUE}Max Frequency:{RESET} {cpu['max_freq_mhz']}")
    print(f"   {BLUE}Curr Frequency:{RESET} {cpu['curr_freq_mhz']}")
    print(f"   {BLUE}Architecture :{RESET} {cpu['arch']}")
    print(f"   {BLUE}Load Average :{RESET} {cpu['load_avg']}")
    print()
    
    # 4. Storage
    storage = get_storage_info()
    print(f"{BOLD}{YELLOW}💾 STORAGE{RESET}")
    if storage['internal']:
        print(f"   {BLUE}/data   :{RESET} {storage['internal']}")
    else:
        print(f"   {BLUE}/data   :{RESET} {RED}N/A{RESET}")
    if storage['sdcard']:
        print(f"   {BLUE}/sdcard :{RESET} {storage['sdcard']}")
    else:
        print(f"   {BLUE}/sdcard :{RESET} {YELLOW}Not mounted (run termux-setup-storage){RESET}")
    print()
    
    # 5. System Health
    health = get_system_health()
    print(f"{BOLD}{MAGENTA}🏥 SYSTEM HEALTH{RESET}")
    print(f"   {BLUE}Uptime       :{RESET} {health['uptime']}")
    print(f"   {BLUE}CPU Temp     :{RESET} {health['temp_cpu']}")
    print(f"   {BLUE}Thermal Throttle:{RESET} {health['throttling']}")
    print(f"   {BLUE}Load Average :{RESET} {health['load_average']}")
    print()
    
    # 6. Battery
    battery = get_battery_info()
    print(f"{BOLD}{MAGENTA}🔋 BATTERY HEALTH{RESET}")
    print(f"   {BLUE}Level      :{RESET} {battery['level']}")
    print(f"   {BLUE}Temperature:{RESET} {battery['temperature']}")
    print(f"   {BLUE}Voltage    :{RESET} {battery['voltage']}")
    print(f"   {BLUE}Health     :{RESET} {battery['health']}")
    print(f"   {BLUE}Technology :{RESET} {battery['technology']}")
    print(f"   {BLUE}Status     :{RESET} {battery['status']}")
    print()
    
    # 7. Network
    net = get_network_info()
    print(f"{BOLD}{CYAN}🌐 NETWORK{RESET}")
    print(f"   {BLUE}Wi-Fi SSID :{RESET} {net['ssid']}")
    print(f"   {BLUE}IP Address :{RESET} {net['ip']}")
    print(f"   {BLUE}Data RX/TX :{RESET} {net['rx_bytes']} / {net['tx_bytes']} (since boot)")
    print()
    
    # 8. Installed Apps
    apps = get_installed_apps(limit=5)
    print(f"{BOLD}{GREEN}📦 INSTALLED APPS{RESET}")
    print(f"   {BLUE}User apps   :{RESET} {apps['total_user']}")
    print(f"   {BLUE}System apps :{RESET} {apps['total_system']}")
    if apps['top_largest']:
        print(f"   {BLUE}Top user apps:{RESET}")
        for pkg in apps['top_largest']:
            print(f"      - {pkg}")
    print()
    
    # 9. Background Processes
    bg_procs = get_background_processes(limit=8)
    print(f"{BOLD}{YELLOW}🔄 BACKGROUND PROCESSES (top CPU/RAM){RESET}")
    if bg_procs:
        for proc in bg_procs:
            print(f"   {proc}")
    else:
        print(f"   {YELLOW}No process info available (try 'top' manually){RESET}")
    print()
    
    # 10. Sensors (optional)
    sensors = get_sensor_info()
    if sensors:
        print(f"{BOLD}{CYAN}📡 SENSORS DETECTED{RESET}")
        for s in sensors[:5]:
            print(f"   - {s}")
        if len(sensors) > 5:
            print(f"   ... and {len(sensors)-5} more")
        print()
    
    print(f"{BOLD}{CYAN}═══════════════════════════════════════════════════════════{RESET}")
    print(f"{GREEN}Tip: Install Termux:API (pkg install termux-api) kwaajili ya sensor data.{RESET}")

if __name__ == "__main__":
    display_all()
