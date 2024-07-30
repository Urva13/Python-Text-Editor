import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import os
import re
import webbrowser
import datetime

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Text Editor")
        self.root.geometry("800x600")

        # Create menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        # Create file menu
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Create edit menu
        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut", command=self.cut_text)
        self.edit_menu.add_command(label="Copy", command=self.copy_text)
        self.edit_menu.add_command(label="Paste", command=self.paste_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find", command=self.find_text)
        self.edit_menu.add_command(label="Replace", command=self.replace_text)
        self.edit_menu.add_command(label="Select All", command=self.select_all)
        self.edit_menu.add_command(label="Undo", command=self.undo)
        self.edit_menu.add_command(label="Redo", command=self.redo)

        # Create format menu
        self.format_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Format", menu=self.format_menu)
        self.format_menu.add_command(label="Font", command=self.change_font)
        self.format_menu.add_command(label="Color", command=self.change_color)
        self.format_menu.add_command(label="Background Color", command=self.change_background_color)
        self.format_menu.add_command(label="Alignment", command=self.change_alignment)

        # Create view menu
        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Zoom In", command=self.zoom_in)
        self.view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        self.view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        self.view_menu.add_command(label="Fullscreen", command=self.fullscreen)

        # Create help menu
        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.about)
        self.help_menu.add_command(label="Documentation", command=self.documentation)
        self.help_menu.add_command(label="Check for Updates", command=self.check_for_updates)

        # Create text area
        self.text_area = tk.Text(self.root, font=("Arial", 12))
        self.text_area.pack(fill="both", expand=True)

        # Create line number area
        self.line_number_area = tk.Text(self.root, width=5, font=("Arial", 12))
        self.line_number_area.pack(side="left", fill="y")

        # Create scrollbar
        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_area.yview)

        # Initialize line numbers
        self.update_line_numbers()

        # Initialize undo and redo stacks
        self.undo_stack = []
        self.redo_stack = []

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.text_area.delete(1.0, tk.END)
            with open(file_path, "r") as file:
                self.text_area.insert(tk.END, file.read())
            self.root.title(f"Python Text Editor - {os.path.basename(file_path)}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.root.title(f"Python Text Editor - {os.path.basename(file_path)}")

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w")as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.root.title(f"Python Text Editor - {os.path.basename(file_path)}")

    def cut_text(self):
        self.text_area.clipboard_clear()
        self.text_area.clipboard_append(self.text_area.selection_get())
        self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
        self.undo_stack.append((self.text_area.get(1.0, tk.END), "cut"))
        self.redo_stack = []

    def copy_text(self):
        self.text_area.clipboard_clear()
        self.text_area.clipboard_append(self.text_area.selection_get())
        self.undo_stack.append((self.text_area.get(1.0, tk.END), "copy"))
        self.redo_stack = []

    def paste_text(self):
        text = self.text_area.clipboard_get()
        self.text_area.insert(tk.END, text)
        self.undo_stack.append((self.text_area.get(1.0, tk.END), "paste"))
        self.redo_stack = []

    def find_text(self):
        find_window =tk.Toplevel(self.root)
        find_window.title("Find")
        find_label = tk.Label(find_window, text="Find:")
        find_label.pack()
        find_entry = tk.Entry(find_window)
        find_entry.pack()
        find_button = tk.Button(find_window, text="Find", command=lambda: self.find_text_in_area(find_entry.get()))
        find_button.pack()

    def find_text_in_area(self, text):
        self.text_area.tag_remove("found", "1.0", tk.END)
        s = self.text_area.get(1.0, tk.END)
        if text:
            idx = "1.0"
            while 1:
                idx = s.find(text, idx)
                if idx!= -1:
                    self.text_area.tag_add("found", f"1.{idx}", f"1.{idx + len(text)}")
                    self.text_area.mark_set("insert", f"1.{idx + len(text)}")
                    self.text_area.see(f"1.{idx}")
                    idx += len(text)
                else:
                    break
        else:
            messagebox.showerror("Error", "Please enter a search term.")

    def replace_text(self):
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Replace")
        find_label = tk.Label(replace_window, text="Find:")
        find_label.pack()
        find_entry = tk.Entry(replace_window)
        find_entry.pack()
        replace_label = tk.Label(replace_window, text="Replace with:")
        replace_label.pack()
        replace_entry = tk.Entry(replace_window)
        replace_entry.pack()
        replace_button = tk.Button(replace_window, text="Replace", command=lambda: self.replace_text_in_area(find_entry.get(), replace_entry.get()))
        replace_button.pack()

    def replace_text_in_area(self, find_text, replace_text):
        s = self.text_area.get(1.0, tk.END)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, s.replace(find_text, replace_text))
        self.undo_stack.append((self.text_area.get(1.0, tk.END), "replace"))
        self.redo_stack = []

    def select_all(self):
        self.text_area.tag_add("sel", "1.0", tk.END)

    def undo(self):
        if self.undo_stack:
            action, text = self.undo_stack.pop()
            if action == "cut":
                self.text_area.insert(tk.END, text)
            elif action == "copy":
                self.text_area.insert(tk.END, text)
            elif action == "paste":
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            elif action == "replace":
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, text)
            self.redo_stack.append((self.text_area.get(1.0, tk.END), action))

    def redo(self):
        if self.redo_stack:
            action, text = self.redo_stack.pop()
            if action == "cut":
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            elif action == "copy":
                pass
            elif action == "paste":
                self.text_area.insert(tk.END, text)
            elif action == "replace":
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, text)
            self.undo_stack.append((self.text_area.get(1.0, tk.END), action))

    def change_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Font")
        font_label = tk.Label(font_window, text="Font:")
        font_label.pack()
        font_entry = tk.Entry(font_window)
        font_entry.pack()
        size_label = tk.Label(font_window, text="Size:")
        size_label.pack()
        size_entry = tk.Entry(font_window)
        size_entry.pack()
        style_label = tk.Label(font_window, text="Style:")
        style_label.pack()
        style_entry = tk.Entry(font_window)
        style_entry.pack()
        ok_button = tk.Button(font_window, text="OK", command=lambda: self.change_font_in_area(font_entry.get(), int(size_entry.get()), style_entry.get()))
        ok_button.pack()

    def change_font_in_area(self, font, size, style):
        self.text_area.config(font=(font, size, style))

    def change_color(self):
        color = colorchooser.askcolor()
        self.text_area.config(fg=color[1])

    def change_background_color(self):
        color = colorchooser.askcolor()
        self.text_area.config(bg=color[1])

    def change_alignment(self):
        alignment_window = tk.Toplevel(self.root)
        alignment_window.title("Alignment")
        left_button = tk.Radiobutton(alignment_window, text="Left", value="left", command=lambda: self.change_alignment_in_area("left"))
        left_button.pack()
        center_button = tk.Radiobutton(alignment_window, text="Center", value="center", command=lambda: self.change_alignment_in_area("center"))
        center_button.pack()
        right_button = tk.Radiobutton(alignment_window, text="Right", value="right", command=lambda: self.change_alignment_in_area("right"))
        right_button.pack()

    def change_alignment_in_area(self, alignment):
        self.text_area.config(justify=alignment)

    def zoom_in(self):
        current_font_size = int(self.text_area.cget("font").split()[1])
        self.text_area.config(font=(self.text_area.cget("font").split()[0], current_font_size + 1))

    def zoom_out(self):
        current_font_size = int(self.text_area.cget("font").split()[1])
        self.text_area.config(font=(self.text_area.cget("font").split()[0], current_font_size - 1))

    def reset_zoom(self):
        self.text_area.config(font=("Arial", 12))

    def fullscreen(self):
        if self.root.state() == "normal":
            self.root.state("zoomed")
        else:
            self.root.state("normal")

    def about(self):
        messagebox.showinfo("About", "Python Text Editor\nVersion 1.0\nCreated by [Your Name]\nCopyright [Year]")

    def documentation(self):
        webbrowser.open("https://www.example.com/documentation")

    def check_for_updates(self):
        messagebox.showinfo("Updates", "The text editor is up to date.")

    def update_line_numbers(self):
        line_number = int(self.text_area.index(tk.END).split(".")[0])
        self.line_number_area.delete(1.0, tk.END)
        for i in range(1, line_number + 1):
            self.line_number_area.insert(tk.END, f"{i}\n")

if __name__ == "__main__":
    root = tk.Tk()
    text_editor = TextEditor(root)
    root.mainloop()