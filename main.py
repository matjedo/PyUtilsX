import sys
import os
import runpy
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path


APP_NAME = "PyUtilsX"
VERSION = "1.0.0"


class PyUtilsXHub:
    def __init__(self, root):
        self.root = root

        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("820x620")
        self.root.resizable(False, False)

        self.setup_style()

        # =========================================================
        # LOCALIZAÇÃO DO PROGRAMA
        # =========================================================

        # Quando compilado:
        #
        # C:\Program Files\PyUtilsX\
        # ├── PyUtilsX.exe
        # └── apps\
        #     └── FileX\
        #         └── main.py
        #
        # Quando executado como .py:
        # usa a pasta do main.py.

        if getattr(sys, "frozen", False):
            self.base_dir = Path(sys.executable).resolve().parent
        else:
            self.base_dir = Path(__file__).resolve().parent

        self.apps_dir = self.base_dir / "apps"

        self.build_ui()
        self.load_apps()

    # =============================================================
    # ESTILO
    # =============================================================

    def setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("vista")
        except tk.TclError:
            style.theme_use("clam")

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(14, 8)
        )

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 24, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "AppName.TLabel",
            font=("Segoe UI", 12, "bold")
        )

        style.configure(
            "AppDescription.TLabel",
            font=("Segoe UI", 9)
        )

    # =============================================================
    # INTERFACE
    # =============================================================

    def build_ui(self):
        main = ttk.Frame(
            self.root,
            padding=30
        )

        main.pack(
            fill="both",
            expand=True
        )

        # Título
        ttk.Label(
            main,
            text="PyUtilsX",
            style="Title.TLabel"
        ).pack(anchor="w")

        # Subtítulo
        ttk.Label(
            main,
            text="Python utilities, all in one place",
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            pady=(2, 25)
        )

        ttk.Separator(main).pack(
            fill="x",
            pady=(0, 20)
        )

        # Applications
        ttk.Label(
            main,
            text="Applications",
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        self.apps_frame = ttk.Frame(main)

        self.apps_frame.pack(
            fill="both",
            expand=True
        )

        # Rodapé
        ttk.Separator(main).pack(
            fill="x",
            pady=(20, 10)
        )

        footer = ttk.Frame(main)

        footer.pack(fill="x")

        ttk.Label(
            footer,
            text=f"PyUtilsX v{VERSION}",
            style="Subtitle.TLabel"
        ).pack(side="left")

        ttk.Button(
            footer,
            text="Refresh",
            command=self.load_apps
        ).pack(side="right")

    # =============================================================
    # PROCURAR APLICATIVOS
    # =============================================================

    def load_apps(self):

        # Limpa a lista
        for widget in self.apps_frame.winfo_children():
            widget.destroy()

        # Se apps não existir
        if not self.apps_dir.exists():

            ttk.Label(
                self.apps_frame,
                text="No applications found.",
                font=("Segoe UI", 10)
            ).pack(
                anchor="w",
                pady=(20, 5)
            )

            ttk.Label(
                self.apps_frame,
                text=f"Apps folder not found:\n{self.apps_dir}",
                style="Subtitle.TLabel"
            ).pack(anchor="w")

            return

        apps_found = []

        # Procura todas as pastas
        for folder in sorted(self.apps_dir.iterdir()):

            if not folder.is_dir():
                continue

            main_file = folder / "main.py"

            if main_file.is_file():
                apps_found.append(
                    (
                        folder.name,
                        main_file
                    )
                )

        # Nenhum app
        if not apps_found:

            ttk.Label(
                self.apps_frame,
                text="No applications found.",
                font=("Segoe UI", 10)
            ).pack(
                anchor="w",
                pady=(20, 5)
            )

            ttk.Label(
                self.apps_frame,
                text=f"Put applications inside:\n{self.apps_dir}",
                style="Subtitle.TLabel"
            ).pack(anchor="w")

            return

        # Criar cards
        for app_name, main_file in apps_found:

            self.create_app_card(
                app_name,
                main_file
            )

    # =============================================================
    # CARD DO APP
    # =============================================================

    def create_app_card(
        self,
        app_name,
        main_file
    ):

        card = ttk.Frame(
            self.apps_frame,
            relief="solid",
            borderwidth=1,
            padding=15
        )

        card.pack(
            fill="x",
            pady=6
        )

        left = ttk.Frame(card)

        left.pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Label(
            left,
            text=self.format_name(app_name),
            style="AppName.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            left,
            text="Python utility",
            style="AppDescription.TLabel"
        ).pack(
            anchor="w",
            pady=(3, 0)
        )

        ttk.Button(
            card,
            text="Open",
            command=lambda: self.launch_app(main_file)
        ).pack(side="right")

    # =============================================================
    # EXECUTAR APLICATIVO
    # =============================================================

    def launch_app(self, main_file):

        try:

            main_file = Path(main_file).resolve()

            if getattr(sys, "frozen", False):

                # =================================================
                # PYUTILSX COMPILADO
                # =================================================
                #
                # O próprio PyUtilsX.exe executa o .py.
                #
                # Não precisamos de outro Python instalado.
                #

                subprocess.Popen(
                    [
                        sys.executable,
                        "--run-app",
                        str(main_file)
                    ],
                    cwd=str(main_file.parent)
                )

            else:

                # =================================================
                # PYUTILSX RODANDO COMO .PY
                # =================================================

                subprocess.Popen(
                    [
                        sys.executable,
                        str(Path(__file__).resolve()),
                        "--run-app",
                        str(main_file)
                    ],
                    cwd=str(main_file.parent)
                )

        except Exception as error:

            messagebox.showerror(
                "PyUtilsX",
                "Could not open the application.\n\n"
                f"{error}"
            )

    # =============================================================
    # FORMATAR NOME
    # =============================================================

    @staticmethod
    def format_name(name):

        name = name.replace("_", " ")
        name = name.replace("-", " ")

        return name


# =============================================================
# MODO DE EXECUÇÃO DE APP
# =============================================================

def run_app_mode():

    # Pega o caminho do aplicativo
    app_path = Path(sys.argv[2]).resolve()

    if not app_path.exists():

        messagebox.showerror(
            "PyUtilsX",
            f"Application not found:\n\n{app_path}"
        )

        return

    try:

        # Faz o aplicativo acreditar que foi
        # executado diretamente.

        sys.argv = [
            str(app_path)
        ]

        # Coloca a pasta do aplicativo como diretório atual.
        os.chdir(app_path.parent)

        # Executa o Python normalmente.
        runpy.run_path(
            str(app_path),
            run_name="__main__"
        )

    except Exception as error:

        messagebox.showerror(
            "PyUtilsX",
            "The application crashed.\n\n"
            f"{error}"
        )


# =============================================================
# MAIN
# =============================================================

def main():

    # =============================================================
    # MODO APP
    # =============================================================

    if (
        len(sys.argv) >= 3
        and sys.argv[1] == "--run-app"
    ):

        run_app_mode()
        return

    # =============================================================
    # MODO HUB
    # =============================================================

    root = tk.Tk()

    PyUtilsXHub(root)

    root.mainloop()


if __name__ == "__main__":
    main()