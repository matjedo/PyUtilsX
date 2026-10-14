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

### 🔐 Cipher++

Cipher++ is a PyUtilsX utility focused on **encoding, decoding, and hash generation**.

With Cipher++, you can:

- Encode and decode text using different methods
- Work with various cipher and encoding formats
- Generate hashes from text and data
- Quickly copy generated results
- Use multiple text and security utilities in one place

The goal of Cipher++ is to provide a simple and centralized toolkit for working with **text, encodings, ciphers, and hashes**, without requiring multiple websites or applications.

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
        Cipher++
        └── main.py
```

New tools can be added inside the `apps` folder without modifying the launcher.

## 📦 Installation

Download the latest installer from the project's **Releases** page and run:

```text
PyUtilsX-Setup-v1.1.0.exe
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
pyinstaller --noconfirm --clean --onefile --windowed --icon="assets/pyutilsx.ico" --name PyUtilsX --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox  --hidden-import=queue --hidden-import=tkinter.ttk main.py
```

After building, place the `apps` folder next to the executable:

```text
dist/
├── PyUtilsX.exe
└── apps/
    └── FileX/
        └── main.py
        Cipher++
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
- [x] More utilities
- [ ] Update system
- [ ] Individual tool icons
- [ ] Better application management

## 📄 License

This project is licensed under the terms specified in the `LICENSE` file.

---

**PyUtilsX v1.0.0**  
Made with Python 🐍
A vibe-coded project for your system's vibes.
