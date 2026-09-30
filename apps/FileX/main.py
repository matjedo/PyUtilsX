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
    # ESTILO
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
    # INTERFACE
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
            text="Selecionar arquivo",
            style="Accent.TButton",
            command=self.select_file
        ).pack()

        self.file_label = ttk.Label(
            main,
            text="Nenhum arquivo selecionado",
            style="Subtitle.TLabel"
        )

        self.file_label.pack(
            pady=(9, 4)
        )

        self.size_label = ttk.Label(
            main,
            text="Tamanho: —",
            style="Subtitle.TLabel"
        )

        self.size_label.pack(
            pady=(0, 18)
        )

        # =========================
        # CARD DE HASHES
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
        # SEPARADOR
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
        # COMPARAÇÃO
        # =========================

        ttk.Label(
            main,
            text="Comparar hash",
            font=("Segoe UI", 14, "bold")
        ).pack()

        ttk.Label(
            main,
            text="Cole o hash esperado para verificar a integridade do arquivo.",
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
            text="Verificar",
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
    # LINHA DE HASH
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
            text="Copiar",
            command=lambda a=algorithm: self.copy_hash(a)
        ).pack(
            side="right"
        )

        self.hash_entries[algorithm] = entry

    # =========================
    # SELECIONAR ARQUIVO
    # =========================

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo"
        )

        if not path:
            return

        self.file_path = Path(path)

        self.file_label.config(
            text=self.file_path.name
        )

        size = self.file_path.stat().st_size

        self.size_label.config(
            text=f"Tamanho: {self.format_size(size)}"
        )

        self.calculate_hashes()

    # =========================
    # CALCULAR HASHES
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
                text=f"Hashes calculados em {total_time:.3f} segundos."
            )

        except Exception as error:

            messagebox.showerror(
                "FileX",
                "Não foi possível calcular os hashes.\n\n"
                f"{error}"
            )

    # =========================
    # COPIAR HASH
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
            text=f"{algorithm} copiado!"
        )

    # =========================
    # COMPARAR HASH
    # =========================

    def compare_hash(self):

        if not self.file_path:
            messagebox.showwarning(
                "FileX",
                "Selecione um arquivo primeiro."
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
                "Digite o hash esperado."
            )
            return

        algorithm = self.algorithm_var.get()

        actual = self.hashes.get(
            algorithm,
            ""
        ).lower()

        # Tempo da comparação
        start_time = time.perf_counter()

        matches = (
            expected == actual
        )

        comparison_time = (
            time.perf_counter()
            - start_time
        )

        if matches:
            result = "✓ HASHES CORRESPONDEM"
            result_color = "#107c10"
        else:
            result = "✕ HASHES DIFERENTES"
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
            "FILEX — RELATÓRIO DE VERIFICAÇÃO\n"
            "══════════════════════════════════\n\n"

            f"Arquivo:\n"
            f"{self.file_path.name}\n\n"

            f"Tamanho:\n"
            f"{self.format_size(self.file_path.stat().st_size)}\n\n"

            f"Algoritmo:\n"
            f"{algorithm}\n\n"

            f"Hash esperado:\n"
            f"{expected}\n\n"

            f"Hash calculado:\n"
            f"{actual}\n\n"

            f"Resultado:\n"
            f"{result}\n\n"

            f"Tempo para calcular os hashes:\n"
            f"{total_hash_time:.6f} segundos\n\n"

            f"Tempo da comparação:\n"
            f"{comparison_time:.9f} segundos"
        )

        self.show_report(
            report,
            matches
        )

        # =========================
        # MSG DO WINDOWS
        # =========================

        try:

            message = (
                f"FileX: {result}\n"
                f"Arquivo: {self.file_path.name}\n"
                f"Tempo: {total_hash_time:.3f}s"
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
            # Se o comando msg não estiver disponível,
            # o FileX continua funcionando normalmente.
            pass

    # =========================
    # JANELA DE RELATÓRIO
    # =========================

    def show_report(self, report, success):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "FileX — Relatório"
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
            text="Relatório de verificação",
            font=("Segoe UI", 18, "bold")
        ).pack(
            pady=(25, 5)
        )

        status_text = (
            "Arquivo verificado com sucesso"
            if success
            else
            "O hash não corresponde ao esperado"
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
            text="Fechar",
            command=window.destroy
        ).pack(
            pady=15
        )

    # =========================
    # TAMANHO DO ARQUIVO
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
# INICIAR FILEX
# =========================

if __name__ == "__main__":

    root = tk.Tk()

    app = FileX(root)

    root.mainloop()