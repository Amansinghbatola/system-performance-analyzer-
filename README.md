# 🖥️ System Performance Analyzer (Manual Calculation)

A Python-based desktop application that monitors and displays key system metrics in real-time using `tkinter` and **manual calculations** with `psutil`. Built for learning system internals and real-time performance monitoring.

---

## 📌 Features

- ✅ **CPU Usage** (manual jiffies calculation)
- ✅ **Memory Usage** (% and GB)
- ✅ **Disk Usage** (% and GB)
- ✅ **Network I/O Speed** (KB/s sent & received)
- ✅ **System Uptime** (HH:MM:SS)
- ✅ **Top 10 CPU-consuming processes** (PID, Name, CPU%, Mem%, Threads, User)

---

## 🗂️ Project Structure

system-performance-analyzer/
├── main.py # Tkinter GUI frontend
├── system_monitor_manual.py # Core system metrics (manual calculation)
├── README.md # Documentation file
├── requirements.txt # Dependency list (psutil)

yaml
Copy
Edit

---

## 🔧 Requirements

- Python 3.7 or higher
- `psutil`
- `tkinter` (bundled with Python)

Install required package:

```bash
pip install psutil
🚀 How to Run
Clone the repository:

bash
Copy
Edit
git clone https://github.com/Amansinghbatola/system-performance-analyzer-.git
cd system-performance-analyzer-
Run the app:

bash
Copy
Edit
python main.py
A GUI window will launch and begin monitoring your system every 3 seconds.

📚 How It Works
CPU % is calculated using raw jiffies (psutil.cpu_times()) and time deltas.

Network speed is manually derived from bytes sent/received per interval.

Memory & Disk info is retrieved from psutil.virtual_memory() and psutil.disk_usage().

Process monitoring uses psutil.process_iter() and tracks per-process CPU time.

📸 GUI Screenshot
(Optional)
Upload a screenshot and include it here
Example:

📈 Future Enhancements (Ideas)
📊 Add live charts with matplotlib or Canvas

📤 Export stats to CSV or JSON

🌙 Add dark mode

🧰 Create standalone .exe using PyInstaller

📄 License
Licensed under the MIT License.
Feel free to use, share, and modify with attribution.

👤 Author
Aman Singh Batola
🔗 GitHub: @Amansinghbatola

🤝 Contributing
Pull requests and suggestions are welcome.
For significant changes, please open an issue to discuss.

📎 requirements.txt
nginx
Copy
Edit
psutil
markdown
Copy
Edit

✅ **To finish:**
- Paste this into a `README.md` in your repo.
- Commit & push to GitHub.

Let me know if you want:
- `.exe` build guide using PyInstaller
- Hindi version
- Submission format for college

Happy coding! 🚀