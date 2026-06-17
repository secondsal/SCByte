import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Точний текст із декомпілятора
HEADER_TEXT = "再乱改就跑路，谁也别想玩！"
HEADER_BYTES = HEADER_TEXT.encode('utf-8')

class ScpakMatrixTool:
    def __init__(self, root):
        self.root = root
        self.root.title("SCBYTE UI v1.0")
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        
        # Налаштування інтерфейсу
        style = ttk.Style()
        style.theme_use('clam')
        
        self.mode = tk.StringVar(value="create")  # Пріоритет за замовчуванням на СТВОРЕННЯ
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        self.create_widgets()

    def create_widgets(self):
        # --- Блок вибору режиму ---
        mode_frame = ttk.LabelFrame(self.root, text="Select Mode", padding=10)
        mode_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Radiobutton(mode_frame, text="Creation (.zip ➔ .scpak)", variable=self.mode, value="create", command=self.on_mode_change).pack(side="left", padx=20)
        ttk.Radiobutton(mode_frame, text="Extraction (.scpak ➔ .zip)", variable=self.mode, value="extract", command=self.on_mode_change).pack(side="left", padx=20)

        # --- Блок вибору шляхів до файлів ---
        paths_frame = ttk.Frame(self.root, padding=5)
        paths_frame.pack(fill="x", padx=15, pady=5)
        
        self.lbl_src = ttk.Label(paths_frame, text="Input File:")
        self.lbl_src.grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(paths_frame, textvariable=self.input_path, width=54).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(paths_frame, text="Browse...", command=self.browse_input).grid(row=0, column=2, pady=5)
        
        self.lbl_dst = ttk.Label(paths_frame, text="Save As:")
        self.lbl_dst.grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(paths_frame, textvariable=self.output_path, width=54).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(paths_frame, text="Browse...", command=self.browse_output).grid(row=1, column=2, pady=5)

        # --- Кнопка запуску процесу ---
        self.btn_process = ttk.Button(self.root, text="Start (5 sec)", width=40, command=self.process_files)
        self.btn_process.pack(pady=25)

    def on_mode_change(self):
        self.input_path.set("")
        self.output_path.set("")
        if self.mode.get() == "create":
            self.lbl_src.config(text="New .zip:")
            self.lbl_dst.config(text="Processed .scpak:")
        else:
            self.lbl_src.config(text="Original .scpak:")
            self.lbl_dst.config(text="Restored .zip:")

    def browse_input(self):
        exts = [("ZIP archives", "*.zip")] if self.mode.get() == "create" else [("SCPAK files", "*.scpak")]
        filename = filedialog.askopenfilename(filetypes=exts + [("All files", "*.*")])
        if filename:
            self.input_path.set(filename)
            base, _ = os.path.splitext(filename)
            self.output_path.set(base + (".scpak" if self.mode.get() == "create" else ".zip"))

    def browse_output(self):
        ext = ".scpak" if self.mode.get() == "create" else ".zip"
        filename = filedialog.asksaveasfilename(defext=ext, filetypes=[("Archive", f"*{ext}")])
        if filename:
            self.output_path.set(filename)

    def process_files(self):
        src, dst = self.input_path.get(), self.output_path.get()
        if not src or not dst:
            messagebox.showerror("Помилка", "Будь ласка, заповніть усі поля!")
            return

        try:
            if self.mode.get() == "create":
                #   РЕЖИМ СТВОРЕННЯ МОДУ (.zip ➔ .scpak)
                with open(src, 'rb') as f:
                    clean_zip = f.read()
                
                zip_len = len(clean_zip)
                # Створюємо порожній буфер під перемішані байти
                scpak_payload = bytearray(zip_len)
                
                # Математичний розподіл за формулою розробника (Interleaving)
                num3 = (zip_len + 1) // 2
                num = 0
                num2 = 0
                
                for j in range(zip_len):
                    if j % 2 == 0:
                        scpak_payload[num] = clean_zip[j]
                        num += 1
                    else:
                        scpak_payload[num3 + num2] = clean_zip[j]
                        num2 += 1
                
                # Склеюємо китайський заголовок та перемішані байти
                final_data = HEADER_BYTES + scpak_payload
                
                with open(dst, 'wb') as f_out:
                    f_out.write(final_data)
                    
                messagebox.showinfo("Success!", f"File successfully encrypted for the game!\n\nSaved: {dst}")

            else:
                # ==========================================
                #   РЕЖИМ РОЗПАКУВАННЯ (.scpak ➔ .zip)
                # ==========================================
                with open(src, 'rb') as f:
                    array = f.read()

                # Перевіряємо наявність китайського тексту на початку
                if array.startswith(HEADER_BYTES):
                    array2_len = len(array) - len(HEADER_BYTES)
                    array2 = bytearray(array2_len)
                    
                    num = 0
                    num2 = 0
                    num3 = (array2_len + 1) // 2
                    
                    # Дзеркальне відновлення оригінального розташування байтів
                    for j in range(array2_len):
                        if j % 2 == 0:
                            array2[j] = array[len(HEADER_BYTES) + num]
                            num += 1
                        else:
                            array2[j] = array[len(HEADER_BYTES) + num3 + num2]
                            num2 += 1
                            
                    with open(dst, 'wb') as f_out:
                        f_out.write(array2)
                        
                    messagebox.showinfo("Success!", "Original game file successfully decoded into a working .zip!\nIt will now open in any archive manager.")
                else:
                    messagebox.showerror("Protection Error", "No official Chinese signature found in the selected file. The file may not be encrypted or could be corrupted.")

        except Exception as e:
            messagebox.showerror("Error!", f"Error when processing file:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScpakMatrixTool(root)
    root.mainloop()
