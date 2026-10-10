import os

import queue

import threading

import tkinter as tk

from tkinter import ttk, filedialog, messagebox, simpledialog

from pathlib import Path

import subprocess

import sys





APP_NAME = "Super PySearch"

APP_VERSION = "1.0.0"





class SuperPySearch:

    def __init__(self, root):

        self.root = root

        self.root.title(f"{APP_NAME} v{APP_VERSION}")

        self.root.geometry("900x650")

        self.root.minsize(760, 520)



        self.cancel_event = threading.Event()

        self.messages = queue.Queue()

        self.search_thread = None

        self.searching = False

        self.matches = 0

        self.scanned = 0



        self.setup_style()

        self.build_ui()

        self.root.after(100, self.process_messages)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)



    def setup_style(self):

        style = ttk.Style()

        try:

            style.theme_use("vista")

        except tk.TclError:

            style.theme_use("clam")



        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))

        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))

        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))

        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 6))



    def build_ui(self):

        main = ttk.Frame(self.root, padding=22)

        main.pack(fill="both", expand=True)



        ttk.Label(main, text="Super PySearch", style="Title.TLabel").pack(anchor="w")

        ttk.Label(

            main,

            text="Find files across folders, partitions, and drives.",

            style="Subtitle.TLabel",

        ).pack(anchor="w", pady=(2, 18))



        search_frame = ttk.LabelFrame(main, text="Search", padding=12)

        search_frame.pack(fill="x")



        ttk.Label(search_frame, text="File name or part of the name").grid(

            row=0, column=0, sticky="w"

        )

        self.name_var = tk.StringVar()

        self.name_entry = ttk.Entry(search_frame, textvariable=self.name_var)

        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(4, 12), padx=(0, 8))

        self.name_entry.bind("<Return>", lambda _event: self.start_search())



        ttk.Label(search_frame, text="Search location").grid(row=2, column=0, sticky="w")

        location_row = ttk.Frame(search_frame)

        location_row.grid(row=3, column=0, sticky="ew", pady=(4, 8))



        self.location_var = tk.StringVar(value=str(Path.home()))

        self.location_entry = ttk.Entry(location_row, textvariable=self.location_var)

        self.location_entry.pack(side="left", fill="x", expand=True)

        ttk.Button(location_row, text="Browse...", command=self.browse_folder).pack(

            side="left", padx=(8, 0)

        )



        options = ttk.Frame(search_frame)

        options.grid(row=4, column=0, sticky="w", pady=(2, 0))



        self.case_sensitive_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(

            options,

            text="Case-sensitive",

            variable=self.case_sensitive_var,

        ).pack(side="left")



        self.exact_match_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(

            options,

            text="Exact file name",

            variable=self.exact_match_var,

        ).pack(side="left", padx=(16, 0))



        search_frame.columnconfigure(0, weight=1)



        controls = ttk.Frame(main)

        controls.pack(fill="x", pady=(12, 12))



        self.search_button = ttk.Button(

            controls, text="Search", command=self.start_search

        )

        self.search_button.pack(side="left")



        self.cancel_button = ttk.Button(

            controls, text="Cancel", command=self.cancel_search, state="disabled"

        )

        self.cancel_button.pack(side="left", padx=(8, 0))



        ttk.Button(

            controls, text="Clear results", command=self.clear_results

        ).pack(side="left", padx=(8, 0))



        ttk.Button(

            controls, text="Open selected file", command=self.open_selected

        ).pack(side="right")



        results_frame = ttk.LabelFrame(main, text="Results", padding=8)

        results_frame.pack(fill="both", expand=True)



        columns = ("name", "path")

        self.results = ttk.Treeview(

            results_frame, columns=columns, show="headings", selectmode="browse"

        )

        self.results.heading("name", text="File name")

        self.results.heading("path", text="Full path")

        self.results.column("name", width=220, minwidth=140)

        self.results.column("path", width=520, minwidth=250)



        vertical = ttk.Scrollbar(

            results_frame, orient="vertical", command=self.results.yview

        )

        horizontal = ttk.Scrollbar(

            results_frame, orient="horizontal", command=self.results.xview

        )

        self.results.configure(

            yscrollcommand=vertical.set, xscrollcommand=horizontal.set

        )



        self.results.grid(row=0, column=0, sticky="nsew")

        vertical.grid(row=0, column=1, sticky="ns")

        horizontal.grid(row=1, column=0, sticky="ew")

        results_frame.rowconfigure(0, weight=1)

        results_frame.columnconfigure(0, weight=1)

        self.results.bind("<Double-1>", lambda _event: self.open_selected())
        self.results.bind("<Button-3>", self.show_context_menu)
        # macOS commonly uses Button-2 for a secondary click.
        self.results.bind("<Button-2>", self.show_context_menu)

        self.context_menu = tk.Menu(self.root, tearoff=False)
        self.context_menu.add_command(label="Open", command=self.open_selected)
        self.context_menu.add_command(label="Copy file path", command=self.copy_selected_path)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Create file in directory...", command=self.create_file_in_directory
        )



        self.progress = ttk.Progressbar(main, mode="indeterminate")

        self.progress.pack(fill="x", pady=(12, 5))



        self.status_var = tk.StringVar(value="Ready.")

        ttk.Label(main, textvariable=self.status_var, style="Subtitle.TLabel").pack(

            anchor="w"

        )



    def browse_folder(self):

        selected = filedialog.askdirectory(

            title="Choose a folder or drive to search",

            initialdir=self.location_var.get() or str(Path.home()),

        )

        if selected:

            self.location_var.set(selected)



    def start_search(self):

        if self.searching:

            return



        query = self.name_var.get().strip()

        location_text = self.location_var.get().strip()



        if not query:

            messagebox.showinfo(APP_NAME, "Enter a file name or part of a name.")

            self.name_entry.focus_set()

            return



        if not location_text:

            messagebox.showinfo(APP_NAME, "Choose a folder or drive to search.")

            return



        start_path = Path(location_text).expanduser()

        if not start_path.exists() or not start_path.is_dir():

            messagebox.showerror(APP_NAME, "The selected location does not exist or is not a folder.")

            return



        self.cancel_event.clear()

        self.searching = True

        self.matches = 0

        self.scanned = 0

        self.search_button.configure(state="disabled")

        self.cancel_button.configure(state="normal")

        self.progress.start(10)

        self.status_var.set("Starting search...")

        self.search_thread = threading.Thread(

            target=self.search_worker,

            args=(

                start_path,

                query,

                self.case_sensitive_var.get(),

                self.exact_match_var.get(),

            ),

            daemon=True,

        )

        self.search_thread.start()



    def search_worker(self, start_path, query, case_sensitive, exact_match):

        needle = query if case_sensitive else query.casefold()

        try:

            for current_root, dirs, files in os.walk(

                start_path, topdown=True, onerror=self.walk_error

            ):

                if self.cancel_event.is_set():

                    break



                # Skip directories that cannot be entered; os.walk handles

                # inaccessible folders through walk_error.

                self.messages.put(("directory", current_root))



                for filename in files:

                    if self.cancel_event.is_set():

                        break



                    candidate = filename if case_sensitive else filename.casefold()

                    found = candidate == needle if exact_match else needle in candidate

                    self.scanned += 1



                    if found:

                        full_path = os.path.join(current_root, filename)

                        self.matches += 1

                        self.messages.put(("result", filename, full_path, self.matches))



                    if self.scanned % 250 == 0:

                        self.messages.put(("progress", self.scanned, self.matches))



            if self.cancel_event.is_set():

                self.messages.put(("finished", "Search cancelled."))

            else:

                self.messages.put(("finished", "Search complete."))

        except Exception as error:

            self.messages.put(("error", str(error)))

            self.messages.put(("finished", "Search stopped because of an error."))



    def walk_error(self, error):

        # Ignore folders/files that Windows denies access to and continue.

        try:

            self.messages.put(("warning", str(error.filename or error)))

        except Exception:

            pass



    def process_messages(self):

        try:

            while True:

                item = self.messages.get_nowait()

                kind = item[0]



                if kind == "directory":

                    self.status_var.set(

                        f"Searching: {item[1]}   |   Files checked: {self.scanned:,}   |   Found: {self.matches:,}"

                    )

                elif kind == "result":

                    _, filename, full_path, count = item

                    self.results.insert("", "end", values=(filename, full_path))

                    self.status_var.set(

                        f"Searching...   |   Files checked: {self.scanned:,}   |   Found: {count:,}"

                    )

                elif kind == "progress":

                    _, scanned, matches = item

                    self.status_var.set(

                        f"Searching...   |   Files checked: {scanned:,}   |   Found: {matches:,}"

                    )

                elif kind == "warning":

                    # Warnings are intentionally non-blocking. One unreadable

                    # folder should not stop a drive-wide search.

                    pass

                elif kind == "error":

                    messagebox.showerror(APP_NAME, f"Search error:\n\n{item[1]}")

                elif kind == "finished":

                    self.finish_search(item[1])

        except queue.Empty:

            pass



        self.root.after(100, self.process_messages)



    def finish_search(self, message):

        self.searching = False

        self.progress.stop()

        self.search_button.configure(state="normal")

        self.cancel_button.configure(state="disabled")

        self.status_var.set(

            f"{message} Files checked: {self.scanned:,}   |   Files found: {self.matches:,}"

        )



    def cancel_search(self):

        if self.searching:

            self.cancel_event.set()

            self.cancel_button.configure(state="disabled")

            self.status_var.set("Cancelling search...")



    def clear_results(self):

        for item in self.results.get_children():

            self.results.delete(item)

        if not self.searching:

            self.status_var.set("Results cleared. Ready.")



    def open_selected(self):

        selected = self.results.selection()

        if not selected:

            messagebox.showinfo(APP_NAME, "Select a result first.")

            return



        values = self.results.item(selected[0], "values")

        if not values:

            return



        path = values[1]

        try:

            if sys.platform.startswith("win"):

                os.startfile(path)

            elif sys.platform == "darwin":

                subprocess.Popen(["open", path])

            else:

                subprocess.Popen(["xdg-open", path])

        except Exception as error:

            messagebox.showerror(APP_NAME, f"Could not open the file:\n\n{error}")



    def show_context_menu(self, event):
        row = self.results.identify_row(event.y)
        if not row:
            return

        self.results.selection_set(row)
        self.results.focus(row)
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def get_selected_path(self):
        selected = self.results.selection()
        if not selected:
            messagebox.showinfo(APP_NAME, "Select a result first.")
            return None

        values = self.results.item(selected[0], "values")
        if not values or len(values) < 2:
            return None
        return Path(values[1])

    def copy_selected_path(self):
        path = self.get_selected_path()
        if path is None:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(str(path))
        self.root.update()  # Keep the clipboard contents after the app loses focus.
        self.status_var.set("File path copied to clipboard.")

    def delete_selected(self):
        path = self.get_selected_path()
        if path is None:
            return
        if not path.exists():
            messagebox.showerror(APP_NAME, f"This file no longer exists:\n\n{path}")
            return
        if not path.is_file():
            messagebox.showerror(APP_NAME, "Only files can be deleted from search results.")
            return
        if not messagebox.askyesno(
            APP_NAME,
            f"Are you sure you want to permanently delete this file?\n\n{path}",
            icon="warning",
        ):
            return

        try:
            path.unlink()
            for item in self.results.selection():
                self.results.delete(item)
            self.status_var.set(f"Deleted: {path.name}")
        except OSError as error:
            messagebox.showerror(APP_NAME, f"Could not delete the file:\n\n{error}")

    def create_file_in_directory(self):
        directory = filedialog.askdirectory(
            title="Choose the directory where the new file will be created",
            initialdir=str(Path.home()),
        )
        if not directory:
            return

        filename = simpledialog.askstring(
            APP_NAME,
            "Enter a file name (including extension, if needed):",
            parent=self.root,
        )
        if filename is None:
            return
        filename = filename.strip()
        if not filename or filename in {".", ".."} or Path(filename).name != filename:
            messagebox.showerror(APP_NAME, "Enter a valid file name without a directory path.")
            return

        new_path = Path(directory) / filename
        try:
            # Exclusive creation avoids silently overwriting an existing file.
            with new_path.open("x", encoding="utf-8"):
                pass
            self.status_var.set(f"Created file: {new_path}")
            messagebox.showinfo(APP_NAME, f"File created successfully:\n\n{new_path}")
        except FileExistsError:
            messagebox.showerror(APP_NAME, f"A file with that name already exists:\n\n{new_path}")
        except OSError as error:
            messagebox.showerror(APP_NAME, f"Could not create the file:\n\n{error}")

    def on_close(self):

        if self.searching:

            self.cancel_event.set()

        self.root.destroy()





def main():

    root = tk.Tk()

    SuperPySearch(root)

    root.mainloop()





if __name__ == "__main__":

    main()

