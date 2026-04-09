# 📱 Androscan – Complete Android System Analyzer for Termux

[![Termux](https://img.shields.io/badge/Termux-Android-blue.svg)](https://termux.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Androscan** is a powerful, all‑in‑one system information tool for Android devices, running entirely inside **Termux** – **no root required**. It displays **RAM, CPU, storage, system health, battery stats, installed apps, background processes, network details, sensors**, and much more in a beautiful, color‑coded terminal output.

![Demo Screenshot](https://via.placeholder.com/800x450?text=Colorful+Terminal+Output+Example)

---

## ✨ Features

| Category | Details |
|----------|---------|
| 📱 **Device** | Manufacturer, model, Android version, SDK level, kernel version |
| 🧠 **RAM** | Total, used, free, available, usage percentage (from `/proc/meminfo`) |
| ⚙️ **CPU** | Model, core count, max/current frequency, architecture, load average |
| 💾 **Storage** | Internal `/data` and external `/sdcard` usage (used / total) |
| 🏥 **System Health** | Uptime, CPU temperature (°C/°F), thermal throttling status |
| 🔋 **Battery** | Level %, temperature, voltage, health, technology, charging status |
| 🌐 **Network** | Wi‑Fi SSID, IP address (wlan0), data RX/TX since boot |
| 📦 **Installed Apps** | Number of user apps, system apps, top 5 user package names |
| 🔄 **Background Processes** | Top 8 processes by CPU% and MEM% (from `top`) |
| 📡 **Sensors** | List of available hardware sensors (accelerometer, gyroscope, etc.) |

> **All data is read directly from Android’s kernel interfaces (`/proc`, `/sys`, `getprop`) – no fake or mock values.**

---

## 🚀 Installation from Scratch (First Time in Termux)

Follow these steps **exactly** – even if you’ve never used Termux before.

### 1. Install Termux

- **Recommended:** Download Termux from [F‑Droid](https://f-droid.org/repo/com.termux_118.apk) (more stable and up‑to‑date than the Play Store version).
- Install the APK on your Android device.

### 2. Open Termux and update packages

```bash
pkg update && pkg upgrade -y
```

### 3. Install required tools

```bash
pkg install git python -y
```

### 4. Grant storage permission (to access `/sdcard`)

```bash
termux-setup-storage
```

A popup will ask for storage permission – tap **Allow**.

### 5. Clone the DroidInfo repository

```bash
git clone https://github.com/YOUR_USERNAME/droidinfo-advanced
cd droidinfo-advanced
```

> **Important:** Replace `YOUR_USERNAME/droidinfo-advanced` with your actual GitHub username and repository name.

### 6. Run the installer

```bash
bash install.sh
```

### 7. Launch DroidInfo

```bash
droidinfo
```

That’s it! You will see a detailed, color‑coded report of your Android device.

---

## 🔥 Quick One‑Liner (if you already have Termux & git)

```bash
git clone https://github.com/YOUR_USERNAME/droidinfo-advanced && cd droidinfo-advanced && bash install.sh && droidinfo
```

---

## 🔧 Optional Features (For Even More Data)

### Install Termux:API for sensor access

```bash
pkg install termux-api
```

After installation, you may need to grant **sensor permission** in:
- **Android Settings** → **Apps** → **Termux** → **Permissions** → Enable **Sensors**.

### Re‑run the storage permission (if `/sdcard` is not showing)

```bash
termux-setup-storage
```

### Update DroidInfo to the latest version

```bash
cd ~/droidinfo-advanced
git pull
bash install.sh
```

---

## 🗑️ Uninstall

To completely remove DroidInfo:

```bash
rm $PREFIX/bin/droidinfo
rm -rf ~/droidinfo-advanced
```

---

## 📊 Example Output

```
═══════════════════════════════════════════════════════════
           ADVANCED ANDROID SYSTEM ANALYZER
═══════════════════════════════════════════════════════════

📱 DEVICE INFORMATION
   Manufacturer   : OnePlus
   Model          : ONEPLUS A6013
   Android Version: 11 (SDK 30)
   Kernel         : 4.9.227-perf+

📊 RAM USAGE
   Total   : 7.2 GiB
   Used    : 4.1 GiB (57%)
   Free    : 3.1 GiB
   Available: 5.0 GiB

⚙️ CPU INFORMATION
   Model        : sdm845
   Cores        : 8
   Max Frequency: 2803 MHz
   Curr Frequency: 1766 MHz
   Architecture : ARM64 (AArch64)
   Load Average : 1.52 (1m), 1.28 (5m), 1.05 (15m)

💾 STORAGE
   /data   : 52G used / 108G total (48% used)
   /sdcard : 18G used / 112G total (16% used)

🏥 SYSTEM HEALTH
   Uptime       : 2d 14h 23m
   CPU Temp     : 45.2°C (113.4°F)
   Thermal Throttle: No
   Load Average : ['1.52', '1.28', '1.05']

🔋 BATTERY HEALTH
   Level      : 78%
   Temperature: 36.5°C (97.7°F)
   Voltage    : 4350 mV
   Health     : Good
   Technology : Li-poly
   Status     : Discharging

🌐 NETWORK
   Wi-Fi SSID : MyHomeNetwork
   IP Address : 192.168.1.105
   Data RX/TX : 124.5 MiB / 45.2 MiB (since boot)

📦 INSTALLED APPS
   User apps   : 127
   System apps : 214
   Top user apps:
      - com.whatsapp
      - com.instagram.android
      - com.twitter.android
      - com.reddit.frontpage
      - com.spotify.music

🔄 BACKGROUND PROCESSES (top CPU/RAM)
   12.5% CPU | 8.2% MEM → com.android.chrome
   8.1% CPU  | 4.5% MEM → com.whatsapp
   5.2% CPU  | 2.1% MEM → termux

📡 SENSORS DETECTED
   - accel
   - gyro
   - light
   - proximity
   - magnetometer

═══════════════════════════════════════════════════════════
Tip: Install Termux:API (pkg install termux-api) for more sensor data.
```

---

## ❓ Troubleshooting

### ❌ `bash: droidinfo: command not found`
- Ensure you ran `bash install.sh` successfully.
- Check that `$PREFIX/bin` is in your PATH (default in Termux).

### ❌ `Permission denied` when running `droidinfo`
- Run `chmod +x $PREFIX/bin/droidinfo` once.

### ❌ Storage info shows "Not mounted"
- Run `termux-setup-storage` again and grant permission.

### ❌ No Wi‑Fi SSID / IP address
- Your device must be connected to Wi‑Fi.
- Some Android versions restrict `dumpsys`; you may see `Unknown`. This is normal.

### ❌ Sensors not showing
- Install `pkg install termux-api` and grant sensor permission in Android settings.

### ❌ The script runs slowly the first time
- That’s because it calls `pm list packages` and `top` – subsequent runs will be faster due to caching.

### ❌ I see "mock data" / "Unknown"
- The script uses real kernel interfaces (`/proc`, `/sys`, `getprop`). If something is `Unknown`, your device either doesn’t expose that information or Termux lacks permission. **RAM, CPU cores, storage, and battery are always real.**

### ❌ Error: `termux-sensor: command not found`
- Install Termux:API: `pkg install termux-api`. Then close and reopen Termux.

---

## 📝 How to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/amazing-feature`).
3. Make your changes.
4. Commit (`git commit -m 'Add some amazing feature'`).
5. Push (`git push origin feature/amazing-feature`).
6. Open a Pull Request.

---


## 🙏 Acknowledgements

- [Termux](https://termux.com/) – amazing terminal emulator for Android.
- Android `/proc` and `/sys` filesystem documentation.
- All open‑source contributors.

---

## 📬 Contact

Project Link: [https://github.com/YOUR_USERNAME/droidinfo-advanced](https://github.com/YOUR_USERNAME/droidinfo-advanced)

---

**Enjoy monitoring your Android device!**  
If you like this tool, please ⭐ star the repository and share it with friends.
```

This README is **comprehensive** – it includes a table of contents, step‑by‑step installation, optional features, uninstall instructions, a full example output, troubleshooting, and contribution guidelines. Replace `YOUR_USERNAME` with your actual GitHub username before publishing.
