#!/usr/bin/env python3
"""
GUI tool for updating bootmedia files with manual boot recovery statements.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import re
from pathlib import Path

class BootmediaUpdaterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bootmedia Files Updater")
        self.root.geometry("900x700")
        
        # Platform name mapping
        self.platform_names = {
            'a200': 'AFF A200',
            'a220': 'AFF A220',
            'a250': 'AFF A250',
            'a300': 'AFF A300',
            'a320': 'AFF A320',
            'a400': 'AFF A400',
            'a700': 'AFF A700',
            'a700s': 'AFF A700s',
            'a800': 'AFF A800',
            'a900': 'AFF A900',
            'c190': 'AFF C190',
            'c250': 'AFF C250',
            'c400': 'AFF C400',
            'c800': 'AFF C800',
            'asa-c250': 'ASA C250',
            'asa-c400': 'ASA C400',
            'asa-c800': 'ASA C800',
            'fas2600': 'FAS2600',
            'fas2700': 'FAS2700',
            'fas2800': 'FAS2800',
            'fas500f': 'FAS500f',
            'fas8200': 'FAS8200',
            'fas8300': 'FAS8300',
            'fas9000': 'FAS9000',
            'fas9500': 'FAS9500',
        }
        
        self.workspace_path = Path(__file__).parent
        self.selected_files = {}
        self.create_widgets()
        
    def create_widgets(self):
        # Folder selection frame
        folder_frame = ttk.LabelFrame(self.root, text="1. Select Platform Folder", padding=10)
        folder_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(folder_frame, text="Platform:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.folder_var = tk.StringVar()
        self.folder_combo = ttk.Combobox(folder_frame, textvariable=self.folder_var, width=30)
        self.folder_combo['values'] = sorted(self.platform_names.keys())
        self.folder_combo.grid(row=0, column=1, padx=5)
        self.folder_combo.bind('<<ComboboxSelected>>', self.load_bootmedia_files)
        
        ttk.Button(folder_frame, text="Load Files", command=self.load_bootmedia_files).grid(row=0, column=2, padx=5)
        
        # Platform name display
        ttk.Label(folder_frame, text="Platform Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.platform_name_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.platform_name_var, width=40).grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        # File selection frame
        file_frame = ttk.LabelFrame(self.root, text="2. Select Files to Update", padding=10)
        file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Buttons for select all/none
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        
        # Scrollable frame for checkboxes
        canvas = tk.Canvas(file_frame, height=200)
        scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=canvas.yview)
        self.file_checkboxes_frame = ttk.Frame(canvas)
        
        self.file_checkboxes_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.file_checkboxes_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(self.root, text="3. Preview Changes", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(preview_frame, text="Generate Preview", command=self.generate_preview).pack(pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="Apply Updates", command=self.apply_updates, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Close", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
    def load_bootmedia_files(self, event=None):
        folder = self.folder_var.get()
        if not folder:
            return
        
        # Set platform name
        platform_name = self.platform_names.get(folder, folder.upper())
        self.platform_name_var.set(platform_name)
        
        # Clear previous checkboxes
        for widget in self.file_checkboxes_frame.winfo_children():
            widget.destroy()
        self.selected_files.clear()
        
        # Find bootmedia files
        folder_path = self.workspace_path / folder
        if not folder_path.exists():
            messagebox.showerror("Error", f"Folder not found: {folder}")
            return
        
        bootmedia_files = sorted(folder_path.glob("bootmedia-*.adoc"))
        
        if not bootmedia_files:
            messagebox.showinfo("Info", f"No bootmedia files found in {folder}")
            return
        
        # Create checkboxes
        for i, file_path in enumerate(bootmedia_files):
            var = tk.BooleanVar(value=True)
            self.selected_files[file_path] = var
            cb = ttk.Checkbutton(self.file_checkboxes_frame, text=file_path.name, variable=var)
            cb.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
        
        messagebox.showinfo("Success", f"Found {len(bootmedia_files)} bootmedia files")
        
    def select_all(self):
        for var in self.selected_files.values():
            var.set(True)
    
    def deselect_all(self):
        for var in self.selected_files.values():
            var.set(False)
    
    def generate_preview(self):
        platform_name = self.platform_name_var.get()
        if not platform_name:
            messagebox.showerror("Error", "Please select a platform folder first")
            return
        
        selected = [path for path, var in self.selected_files.items() if var.get()]
        if not selected:
            messagebox.showerror("Error", "Please select at least one file")
            return
        
        self.preview_text.delete(1.0, tk.END)
        
        preview = f"Will update {len(selected)} files with:\n\n"
        preview += f"Platform: {platform_name}\n"
        preview += f"Statement: The {platform_name} system supports only manual boot media recovery procedures.\n\n"
        preview += "Files to update:\n"
        
        for path in selected:
            preview += f"  - {path.name}\n"
        
        preview += "\nChanges:\n"
        preview += "  ✓ Add 'manual, manual boot recovery' to keywords\n"
        preview += f"  ✓ Add statement to summary: 'The {platform_name} system supports only manual boot media recovery procedures.'\n"
        preview += f"  ✓ Add statement to lead: 'The {platform_name} system supports only manual boot media recovery procedures. Automated boot media recovery is not supported.'\n"
        
        self.preview_text.insert(1.0, preview)
    
    def apply_updates(self):
        platform_name = self.platform_name_var.get()
        if not platform_name:
            messagebox.showerror("Error", "Please select a platform folder first")
            return
        
        selected = [path for path, var in self.selected_files.items() if var.get()]
        if not selected:
            messagebox.showerror("Error", "Please select at least one file")
            return
        
        result = messagebox.askyesno(
            "Confirm Updates",
            f"This will update {len(selected)} files.\n\nAre you sure you want to proceed?"
        )
        
        if not result:
            return
        
        success_count = 0
        errors = []
        
        for file_path in selected:
            try:
                self.update_file(file_path, platform_name)
                success_count += 1
            except Exception as e:
                errors.append(f"{file_path.name}: {str(e)}")
        
        # Show results
        result_msg = f"Successfully updated {success_count} files"
        if errors:
            result_msg += f"\n\nErrors:\n" + "\n".join(errors)
            messagebox.showwarning("Completed with Errors", result_msg)
        else:
            messagebox.showinfo("Success", result_msg)
    
    def update_file(self, file_path, platform_name):
        """Update a single bootmedia file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        statement = f"The {platform_name} system supports only manual boot media recovery procedures."
        full_statement = f"{statement} Automated boot media recovery is not supported."
        
        # Update keywords - add manual and manual boot recovery if not present
        keywords_pattern = r'(keywords:.*?)(\n)'
        match = re.search(keywords_pattern, content)
        if match:
            keywords_line = match.group(1)
            if 'manual' not in keywords_line:
                # Add before the newline
                updated_keywords = keywords_line + ', manual, manual boot recovery'
                content = content.replace(keywords_line, updated_keywords)
            elif 'manual boot recovery' not in keywords_line:
                # Add manual boot recovery
                updated_keywords = keywords_line + ', manual boot recovery'
                content = content.replace(keywords_line, updated_keywords)
        
        # Update summary - add statement if not present
        summary_pattern = r'(summary:\s*["\'])(.*?)(["\'])'
        match = re.search(summary_pattern, content, re.DOTALL)
        if match and statement not in match.group(2):
            summary_content = match.group(2).strip()
            # Add statement at the end before closing quote
            updated_summary = match.group(1) + summary_content + ' ' + statement + match.group(3)
            content = content[:match.start()] + updated_summary + content[match.end():]
        
        # Update lead - add statement if not present
        lead_pattern = r'(\[\.lead\]\n)(.*?)(\n\n)'
        match = re.search(lead_pattern, content, re.DOTALL)
        if match and statement not in match.group(2):
            lead_content = match.group(2).strip()
            # Add statement at the end of lead
            updated_lead = match.group(1) + lead_content + ' ' + full_statement + match.group(3)
            content = content[:match.start()] + updated_lead + content[match.end():]
        elif match and statement in match.group(2) and 'Automated boot media recovery is not supported' not in match.group(2):
            # Statement exists but missing the full version
            lead_content = match.group(2).strip()
            if lead_content.endswith('.'):
                updated_lead = match.group(1) + lead_content[:-1] + '. Automated boot media recovery is not supported.' + match.group(3)
            else:
                updated_lead = match.group(1) + lead_content + ' Automated boot media recovery is not supported.' + match.group(3)
            content = content[:match.start()] + updated_lead + content[match.end():]
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
def main():
    root = tk.Tk()
    app = BootmediaUpdaterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
