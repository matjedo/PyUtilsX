import base64
import binascii
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox
from urllib.parse import quote, unquote

APP_NAME = 'Cipher++'
VERSION = '1.0.0'

DESCRIPTIONS = {
    'Base64': 'Encodes binary/text data into Base64 or decodes Base64 back to text.',
    'Base32': 'Encodes text into Base32 or decodes Base32 back to text.',
    'Hex': 'Converts text to hexadecimal bytes or decodes hexadecimal back to text.',
    'Binary': 'Converts text to binary byte representation or decodes binary back to text.',
    'URL': 'Percent-encodes text for URLs or decodes percent-encoded text.',
    'ASCII': 'Converts text to ASCII character codes or decodes character codes back to text.',
    'ROT13': 'Applies the ROT13 substitution cipher. Encoding and decoding are the same operation.',
    'Caesar': 'Shifts alphabetic characters by a configurable number of positions.',
    'Atbash': 'Replaces each letter with its mirrored letter in the alphabet.',
    'Vigenere': 'Encrypts/decrypts alphabetic text using a repeating keyword.',
    'XOR': 'Applies a repeating XOR key to UTF-8 bytes and represents the result as hexadecimal.',
    'MD5': 'Generates a 128-bit MD5 hash. Useful for legacy checks, not modern security.',
    'SHA-1': 'Generates a 160-bit SHA-1 hash. Useful for compatibility and identification.',
    'SHA-256': 'Generates a 256-bit SHA-256 cryptographic hash.',
    'SHA-384': 'Generates a 384-bit SHA-384 cryptographic hash.',
    'SHA-512': 'Generates a 512-bit SHA-512 cryptographic hash.',
    'SHA-3-256': 'Generates a 256-bit SHA-3 cryptographic hash.',
    'SHA-3-512': 'Generates a 512-bit SHA-3 cryptographic hash.',
}

HASH_METHODS = {'MD5', 'SHA-1', 'SHA-256', 'SHA-384', 'SHA-512', 'SHA-3-256', 'SHA-3-512'}


def caesar_transform(text, shift):
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            result.append(chr((ord(char) - 97 + shift) % 26 + 97))
        elif 'A' <= char <= 'Z':
            result.append(chr((ord(char) - 65 + shift) % 26 + 65))
        else:
            result.append(char)
    return ''.join(result)


def atbash_transform(text):
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            result.append(chr(122 - (ord(char) - 97)))
        elif 'A' <= char <= 'Z':
            result.append(chr(90 - (ord(char) - 65)))
        else:
            result.append(char)
    return ''.join(result)


def vigenere_transform(text, key, decrypt=False):
    key = ''.join(char for char in key if char.isalpha() and char.isascii())
    if not key:
        raise ValueError('Enter a Vigenere key containing letters.')
    result = []
    key_index = 0
    for char in text:
        if char.isalpha() and char.isascii():
            base = 65 if char.isupper() else 97
            key_char = key[key_index % len(key)]
            shift = ord(key_char.upper()) - 65
            if decrypt:
                shift = -shift
            result.append(chr((ord(char) - base + shift) % 26 + base))
            key_index += 1
        else:
            result.append(char)
    return ''.join(result)


def xor_encode(text, key):
    key_bytes = key.encode('utf-8')
    if not key_bytes:
        raise ValueError('Enter an XOR key.')
    data = text.encode('utf-8')
    return bytes(v ^ key_bytes[i % len(key_bytes)] for i, v in enumerate(data)).hex()


def xor_decode(text, key):
    key_bytes = key.encode('utf-8')
    if not key_bytes:
        raise ValueError('Enter an XOR key.')
    try:
        data = bytes.fromhex(''.join(text.split()))
    except ValueError:
        raise ValueError('XOR decode expects hexadecimal input.')
    result = bytes(v ^ key_bytes[i % len(key_bytes)] for i, v in enumerate(data))
    try:
        return result.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError('The XOR result is not valid UTF-8 text.')


class CipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry('900x720')
        self.root.minsize(760, 620)
        self.root.configure(bg='#f5f5f5')
        self.setup_style()
        self.build_ui()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use('vista')
        except tk.TclError:
            style.theme_use('clam')
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10))
        style.configure('Section.TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('Small.TLabel', font=('Segoe UI', 9))
        style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Card.TFrame', relief='solid', borderwidth=1)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=24)
        main.pack(fill='both', expand=True)
        header = ttk.Frame(main)
        header.pack(fill='x', pady=(0, 18))
        ttk.Label(header, text=APP_NAME, style='Title.TLabel').pack(anchor='w')
        ttk.Label(header, text='Encoding, ciphers & hash toolkit', style='Subtitle.TLabel').pack(anchor='w', pady=(2, 0))

        controls = ttk.Frame(main, style='Card.TFrame', padding=14)
        controls.pack(fill='x', pady=(0, 14))
        ttk.Label(controls, text='Method', style='Section.TLabel').grid(row=0, column=0, sticky='w')
        self.method_var = tk.StringVar(value='Base64')
        self.method_box = ttk.Combobox(controls, textvariable=self.method_var, state='readonly', values=[
            'Base64', 'Base32', 'Hex', 'Binary', 'URL', 'ASCII', 'ROT13', 'Caesar', 'Atbash',
            'Vigenere', 'XOR', 'MD5', 'SHA-1', 'SHA-256', 'SHA-384', 'SHA-512', 'SHA-3-256', 'SHA-3-512'
        ], width=20)
        self.method_box.grid(row=1, column=0, sticky='w', padx=(0, 12))
        self.method_box.bind('<<ComboboxSelected>>', self.on_method_change)

        ttk.Label(controls, text='Mode', style='Section.TLabel').grid(row=0, column=1, sticky='w')
        self.mode_var = tk.StringVar(value='Encode')
        self.mode_box = ttk.Combobox(controls, textvariable=self.mode_var, state='readonly', values=['Encode', 'Decode'], width=14)
        self.mode_box.grid(row=1, column=1, sticky='w', padx=(0, 12))
        self.mode_box.bind('<<ComboboxSelected>>', self.update_controls)

        self.key_label = ttk.Label(controls, text='Key', style='Section.TLabel')
        self.key_entry = ttk.Entry(controls, width=24)
        self.shift_label = ttk.Label(controls, text='Shift', style='Section.TLabel')
        self.shift_entry = ttk.Entry(controls, width=10)
        self.shift_entry.insert(0, '3')

        self.description = ttk.Label(controls, text=DESCRIPTIONS['Base64'], style='Small.TLabel', wraplength=760, justify='left')
        self.description.grid(row=3, column=0, columnspan=3, sticky='w', pady=(14, 0))

        text_frame = ttk.Frame(main)
        text_frame.pack(fill='both', expand=True)
        left = ttk.Frame(text_frame)
        left.pack(side='left', fill='both', expand=True, padx=(0, 7))
        right = ttk.Frame(text_frame)
        right.pack(side='left', fill='both', expand=True, padx=(7, 0))
        ttk.Label(left, text='Input', style='Section.TLabel').pack(anchor='w', pady=(0, 6))
        self.input_text = tk.Text(left, height=16, wrap='word', font=('Consolas', 10), relief='solid', borderwidth=1, undo=True)
        self.input_text.pack(fill='both', expand=True)
        ttk.Label(right, text='Output', style='Section.TLabel').pack(anchor='w', pady=(0, 6))
        self.output_text = tk.Text(right, height=16, wrap='word', font=('Consolas', 10), relief='solid', borderwidth=1)
        self.output_text.pack(fill='both', expand=True)

        buttons = ttk.Frame(main)
        buttons.pack(fill='x', pady=(14, 0))
        ttk.Button(buttons, text='Process', style='Action.TButton', command=self.process).pack(side='left')
        ttk.Button(buttons, text='Copy Output', command=self.copy_output).pack(side='left', padx=8)
        ttk.Button(buttons, text='Clear', command=self.clear).pack(side='left')
        self.status_var = tk.StringVar(value='Ready')
        ttk.Label(buttons, textvariable=self.status_var, style='Small.TLabel').pack(side='right')
        ttk.Label(main, text=f'Cipher++ v{VERSION} • PyUtilsX', style='Small.TLabel').pack(anchor='center', pady=(12, 0))
        self.update_controls()

    def on_method_change(self, _event=None):
        method = self.method_var.get()
        self.description.configure(text=DESCRIPTIONS.get(method, ''))
        self.mode_box.configure(state='disabled' if method in HASH_METHODS else 'readonly')
        self.update_controls()

    def update_controls(self, _event=None):
        method = self.method_var.get()
        if method == 'Caesar':
            self.shift_label.grid(row=0, column=2, sticky='w')
            self.shift_entry.grid(row=1, column=2, sticky='w')
        else:
            self.shift_label.grid_remove()
            self.shift_entry.grid_remove()
        if method in ('Vigenere', 'XOR'):
            self.key_label.grid(row=0, column=2, sticky='w')
            self.key_entry.grid(row=1, column=2, sticky='w')
        else:
            self.key_label.grid_remove()
            self.key_entry.grid_remove()
        if method in HASH_METHODS:
            self.mode_var.set('Encode')

    def process(self):
        method = self.method_var.get()
        mode = self.mode_var.get()
        text = self.input_text.get('1.0', 'end-1c')
        try:
            if method in HASH_METHODS:
                result = self.generate_hash(text, method)
            elif method == 'Base64':
                result = base64.b64encode(text.encode()).decode() if mode == 'Encode' else base64.b64decode(text, validate=True).decode()
            elif method == 'Base32':
                result = base64.b32encode(text.encode()).decode() if mode == 'Encode' else base64.b32decode(''.join(text.split()).upper(), casefold=True).decode()
            elif method == 'Hex':
                result = text.encode().hex() if mode == 'Encode' else bytes.fromhex(''.join(text.split())).decode()
            elif method == 'Binary':
                if mode == 'Encode':
                    result = ' '.join(f'{b:08b}' for b in text.encode())
                else:
                    groups = text.split()
                    if any(len(g) != 8 or any(bit not in '01' for bit in g) for g in groups):
                        raise ValueError('Binary input must contain 8-bit groups.')
                    result = bytes(int(g, 2) for g in groups).decode()
            elif method == 'URL':
                result = quote(text, safe='') if mode == 'Encode' else unquote(text)
            elif method == 'ASCII':
                if mode == 'Encode':
                    result = ' '.join(str(ord(c)) for c in text)
                else:
                    values = [int(v) for v in text.split()]
                    if any(v < 0 or v > 127 for v in values):
                        raise ValueError
                    result = ''.join(chr(v) for v in values)
            elif method == 'ROT13':
                result = caesar_transform(text, 13)
            elif method == 'Caesar':
                shift = int(self.shift_entry.get().strip())
                result = caesar_transform(text, shift if mode == 'Encode' else -shift)
            elif method == 'Atbash':
                result = atbash_transform(text)
            elif method == 'Vigenere':
                result = vigenere_transform(text, self.key_entry.get(), mode == 'Decode')
            elif method == 'XOR':
                result = xor_encode(text, self.key_entry.get()) if mode == 'Encode' else xor_decode(text, self.key_entry.get())
            else:
                raise ValueError('Unsupported method.')
            self.output_text.delete('1.0', 'end')
            self.output_text.insert('1.0', result)
            self.status_var.set('Completed')
        except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
            self.status_var.set('Error')
            messagebox.showerror(APP_NAME, str(exc) or 'Invalid input.')

    @staticmethod
    def generate_hash(text, method):
        algorithms = {
            'MD5': hashlib.md5, 'SHA-1': hashlib.sha1, 'SHA-256': hashlib.sha256,
            'SHA-384': hashlib.sha384, 'SHA-512': hashlib.sha512,
            'SHA-3-256': hashlib.sha3_256, 'SHA-3-512': hashlib.sha3_512,
        }
        return algorithms[method](text.encode()).hexdigest()

    def copy_output(self):
        output = self.output_text.get('1.0', 'end-1c')
        if not output:
            self.status_var.set('Nothing to copy')
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        self.root.update()
        self.status_var.set('Copied to clipboard')

    def clear(self):
        self.input_text.delete('1.0', 'end')
        self.output_text.delete('1.0', 'end')
        self.status_var.set('Ready')


def main():
    root = tk.Tk()
    CipherApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
