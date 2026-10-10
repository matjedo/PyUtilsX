import hashlib
import subprocess
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path


class FileX:
    def __init__(self, root):
        self.root = root
        self.root.title("FileX")
        self.root.geometry("820x650")
        self.root.resizable(False, False)

        self.file_path = None
        self.hashes = {}
        self.hash_times = {}

        self.setup_style()
        self.create_ui()

    # =========================
    # STYLE
    # =========================

    def setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("vista")
        except tk.TclError:
            style.theme_use("clam")

        self.root.configure(bg="#f3f3f3")

        style.configure(
            "Main.TFrame",
            background="#f3f3f3"
        )

        style.configure(
            "Card.TFrame",
            background="#ffffff"
        )

        style.configure(
            "Title.TLabel",
            background="#f3f3f3",
            foreground="#1a1a1a",
            font=("Segoe UI", 26, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background="#f3f3f3",
            foreground="#666666",
            font=("Segoe UI", 10)
        )

        style.configure(
            "HashName.TLabel",
            background="#ffffff",
            foreground="#202020",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "Hash.TEntry",
            fieldbackground="#f7f7f7",
            foreground="#202020",
            font=("Consolas", 9)
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(14, 7)
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(18, 8)
        )

    # =========================
    # USER INTERFACE
    # =========================

    def create_ui(self):
        main = ttk.Frame(
            self.root,
            style="Main.TFrame"
        )

        main.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            main,
            text="FileX",
            style="Title.TLabel"
        ).pack(pady=(28, 0))

        ttk.Label(
            main,
            text="File integrity & hash checker",
            style="Subtitle.TLabel"
        ).pack(pady=(0, 22))

        ttk.Button(
            main,
            text="Select File",
            style="Accent.TButton",
            command=self.select_file
        ).pack()

        self.file_label = ttk.Label(
            main,
            text="No file selected",
            style="Subtitle.TLabel"
        )

        self.file_label.pack(
            pady=(9, 4)
        )

        self.size_label = ttk.Label(
            main,
            text="Size: —",
            style="Subtitle.TLabel"
        )

        self.size_label.pack(
            pady=(0, 18)
        )

        # =========================
        # HASHES CARD
        # =========================

        card = ttk.Frame(
            main,
            style="Card.TFrame",
            padding=18
        )

        card.pack(
            fill="x",
            padx=35
        )

        self.hash_entries = {}

        algorithms = [
            "SHA-256",
            "SHA-1",
            "SHA-512",
            "MD5"
        ]

        for algorithm in algorithms:
            self.create_hash_row(
                card,
                algorithm
            )

        # =========================
        # SEPARATOR
        # =========================

        ttk.Separator(
            main,
            orient="horizontal"
        ).pack(
            fill="x",
            padx=35,
            pady=22
        )

        # =========================
        # HASH COMPARISON
        # =========================

        ttk.Label(
            main,
            text="Compare Hash",
            font=("Segoe UI", 14, "bold")
        ).pack()

        ttk.Label(
            main,
            text="Paste the expected hash to verify file integrity.",
            style="Subtitle.TLabel"
        ).pack(
            pady=(3, 12)
        )

        compare_frame = ttk.Frame(main)

        compare_frame.pack(
            fill="x",
            padx=35
        )

        self.algorithm_var = tk.StringVar(
            value="SHA-256"
        )

        algorithm_menu = ttk.Combobox(
            compare_frame,
            textvariable=self.algorithm_var,
            values=[
                "SHA-256",
                "SHA-1",
                "SHA-512",
                "MD5"
            ],
            state="readonly",
            width=10
        )

        algorithm_menu.pack(
            side="left",
            padx=(0, 8)
        )

        self.expected_hash = ttk.Entry(
            compare_frame
        )

        self.expected_hash.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=5
        )

        ttk.Button(
            main,
            text="Verify",
            style="Accent.TButton",
            command=self.compare_hash
        ).pack(
            pady=(12, 5)
        )

        self.result_label = ttk.Label(
            main,
            text=""
        )

        self.result_label.pack()

        ttk.Label(
            main,
            text="FileX • PyUtilsX",
            style="Subtitle.TLabel"
        ).pack(
            side="bottom",
            pady=12
        )

    # =========================
    # HASH ROW
    # =========================

    def create_hash_row(self, parent, algorithm):
        row = ttk.Frame(parent)

        row.pack(
            fill="x",
            pady=5
        )

        ttk.Label(
            row,
            text=algorithm,
            style="HashName.TLabel",
            width=10
        ).pack(
            side="left"
        )

        entry = ttk.Entry(
            row,
            style="Hash.TEntry",
            state="readonly"
        )

        entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 8)
        )

        ttk.Button(
            row,
            text="Copy",
            command=lambda a=algorithm: self.copy_hash(a)
        ).pack(
            side="right"
        )

        self.hash_entries[algorithm] = entry

    # =========================
    # SELECT FILE
    # =========================

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select File"
        )

        if not path:
            return

        self.file_path = Path(path)

        self.file_label.config(
            text=self.file_path.name
        )

        size = self.file_path.stat().st_size

        self.size_label.config(
            text=f"Size: {self.format_size(size)}"
        )

        self.calculate_hashes()

    # =========================
    # CALCULATE HASHES
    # =========================

    def calculate_hashes(self):
        self.hashes.clear()
        self.hash_times.clear()

        algorithms = {
            "SHA-256": hashlib.sha256(),
            "SHA-1": hashlib.sha1(),
            "SHA-512": hashlib.sha512(),
            "MD5": hashlib.md5()
        }

        try:
            start_time = time.perf_counter()

            with open(
                self.file_path,
                "rb"
            ) as file:

                while True:
                    chunk = file.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    for hash_object in algorithms.values():
                        hash_object.update(chunk)

            total_time = (
                time.perf_counter()
                - start_time
            )

            for name, hash_object in algorithms.items():

                result = hash_object.hexdigest()

                self.hashes[name] = result

                entry = self.hash_entries[name]

                entry.config(
                    state="normal"
                )

                entry.delete(
                    0,
                    tk.END
                )

                entry.insert(
                    0,
                    result
                )

                entry.config(
                    state="readonly"
                )

            self.hash_times["total"] = total_time

            self.result_label.config(
                text=f"Hashes calculated in {total_time:.3f} seconds."
            )

        except Exception as error:

            messagebox.showerror(
                "FileX",
                "Unable to calculate hashes.\n\n"
                f"{error}"
            )

    # =========================
    # COPY HASH
    # =========================

    def copy_hash(self, algorithm):
        if algorithm not in self.hashes:
            return

        self.root.clipboard_clear()

        self.root.clipboard_append(
            self.hashes[algorithm]
        )

        self.root.update()

        self.result_label.config(
            text=f"{algorithm} copied!"
        )

    # =========================
    # COMPARE HASH
    # =========================

    def compare_hash(self):

        if not self.file_path:
            messagebox.showwarning(
                "FileX",
                "Please select a file first."
            )
            return

        expected = (
            self.expected_hash
            .get()
            .strip()
            .lower()
        )

        if not expected:
            messagebox.showwarning(
                "FileX",
                "Please enter the expected hash."
            )
            return

        algorithm = self.algorithm_var.get()

        actual = self.hashes.get(
            algorithm,
            ""
        ).lower()

        # Measure comparison time
        start_time = time.perf_counter()

        matches = (
            expected == actual
        )

        comparison_time = (
            time.perf_counter()
            - start_time
        )

        if matches:
            result = "✓ HASHES MATCH"
            result_color = "#107c10"
        else:
            result = "✕ HASHES DO NOT MATCH"
            result_color = "#c42b1c"

        self.result_label.config(
            text=result,
            foreground=result_color
        )

        total_hash_time = self.hash_times.get(
            "total",
            0
        )

        report = (
            "FILEX — VERIFICATION REPORT\n"
            "══════════════════════════════════\n\n"

            f"File:\n"
            f"{self.file_path.name}\n\n"

            f"Size:\n"
            f"{self.format_size(self.file_path.stat().st_size)}\n\n"

            f"Algorithm:\n"
            f"{algorithm}\n\n"

            f"Expected Hash:\n"
            f"{expected}\n\n"

            f"Calculated Hash:\n"
            f"{actual}\n\n"

            f"Result:\n"
            f"{result}\n\n"

            f"Hash Calculation Time:\n"
            f"{total_hash_time:.6f} seconds\n\n"

            f"Comparison Time:\n"
            f"{comparison_time:.9f} seconds"
        )

        self.show_report(
            report,
            matches
        )

        # =========================
        # WINDOWS MESSAGE
        # =========================

        try:

            message = (
                f"FileX: {result}\n"
                f"File: {self.file_path.name}\n"
                f"Time: {total_hash_time:.3f}s"
            )

            subprocess.run(
                [
                    "msg",
                    "*",
                    message
                ],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        except Exception:
            # If the msg command is unavailable,
            # FileX continues working normally.
            pass

    # =========================
    # REPORT WINDOW
    # =========================

    def show_report(self, report, success):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "FileX — Report"
        )

        window.geometry(
            "680x560"
        )

        window.resizable(
            False,
            False
        )

        window.configure(
            bg="#f3f3f3"
        )

        ttk.Label(
            window,
            text="Verification Report",
            font=("Segoe UI", 18, "bold")
        ).pack(
            pady=(25, 5)
        )

        status_text = (
            "File verified successfully"
            if success
            else
            "The hash does not match the expected value"
        )

        status_color = (
            "#107c10"
            if success
            else
            "#c42b1c"
        )

        status = tk.Label(
            window,
            text=status_text,
            font=("Segoe UI", 10, "bold"),
            bg="#f3f3f3",
            fg=status_color
        )

        status.pack(
            pady=(0, 15)
        )

        text = tk.Text(
            window,
            width=78,
            height=21,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#202020",
            relief="solid",
            borderwidth=1,
            padx=14,
            pady=14,
            wrap="word"
        )

        text.pack(
            padx=25,
            fill="both",
            expand=True
        )

        text.insert(
            "1.0",
            report
        )

        text.config(
            state="disabled"
        )

        ttk.Button(
            window,
            text="Close",
            command=window.destroy
        ).pack(
            pady=15
        )

    # =========================
    # FILE SIZE
    # =========================

    @staticmethod
    def format_size(size):

        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB"
        ]

        for unit in units:

            if size < 1024:
                return f"{size:.2f} {unit}"

            size /= 1024

        return f"{size:.2f} PB"


# =========================
# START FILEX
# =========================

if __name__ == "__main__":

    root = tk.Tk()

    app = FileX(root)

    root.mainloop()
