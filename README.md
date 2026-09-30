# PyUtilsX

**Python utilities, all in one place.**

PyUtilsX is a lightweight hub for bringing multiple Python utilities together in a single application.

The idea is simple: **one launcher, multiple tools.**

## ✨ Current Tools

### 🔐 FileX

A file integrity and hash checking utility.

- SHA-256
- SHA-1
- SHA-512
- MD5
- Expected hash comparison
- File information
- Verification time
- Verification reports
- Tkinter-based graphical interface

## 🚀 How It Works

PyUtilsX works as a launcher for its tools:

```text
PyUtilsX
│
├── PyUtilsX.exe
│
└── apps
    └── FileX
        └── main.py
```

New tools can be added inside the `apps` folder without modifying the launcher.

## 📦 Installation

Download the latest installer from the project's **Releases** page and run:

```text
PyUtilsX-Setup-v1.0.0.exe
```

The installer will automatically set up PyUtilsX on your system.

> Python does not need to be installed separately.

## 🛠️ Development

To run the project directly from the source code:

```bash
python main.py
```

Install PyInstaller:

```bash
python -m pip install pyinstaller
```

Build the launcher:

```bash
pyinstaller --noconfirm --clean --onefile --windowed --name PyUtilsX ^
--hidden-import=tkinter.filedialog ^
--hidden-import=tkinter.messagebox ^
--hidden-import=tkinter.ttk ^
--hidden-import=tkinter.simpledialog ^
--hidden-import=tkinter.colorchooser ^
--hidden-import=tkinter.font ^
main.py
```

After building, place the `apps` folder next to the executable:

```text
dist/
├── PyUtilsX.exe
└── apps/
    └── FileX/
        └── main.py
```

## 🧩 Adding a Tool

Each tool can have its own folder:

```text
apps/
├── FileX/
│   └── main.py
│
├── SystemX/
│   └── main.py
│
└── NetworkX/
    └── main.py
```

PyUtilsX automatically detects folders containing a `main.py`.

## 🎯 Goal

The goal of PyUtilsX is to build a collection of **simple, useful, and lightweight Python utilities**, all organized and accessible from a single application.

## 📋 Roadmap

- [x] Initial hub
- [x] FileX
- [x] SHA-256
- [x] SHA-1
- [x] SHA-512
- [x] MD5
- [x] Hash comparison
- [x] Windows installer
- [ ] More utilities
- [ ] Update system
- [ ] Individual tool icons
- [ ] Better application management

## 📄 License

This project is licensed under the terms specified in the `LICENSE` file.

---

**PyUtilsX v1.0.0**  
Made with Python 🐍
A vibe-coded project for your system's vibes.
