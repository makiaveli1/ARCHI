import json
import os
import re
import zipfile
import rarfile
import shutil
import tarfile
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog
from tkinter import simpledialog
from ttkthemes import ThemedTk
from collections import defaultdict


class ArchiStackApp(ThemedTk):
    def __init__(self):
        super().__init__()
        self.title('ArchiStack')
        self.minsize(800, 600)
        self.load_theme()
        self.set_theme(self.default_theme)

        self.create_widgets()

    def create_widgets(self):
        self.mod_organizer_frame = ModOrganizerFrame(self)
        self.mod_organizer_frame.grid(
            column=0, row=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Add mod name label and entry
        mod_label = ttk.Label(self, text="Mod Name:")
        mod_label.grid(column=0, row=1, padx=5, pady=5, sticky="w")

        self.mod_entry = ttk.Entry(self)
        self.mod_entry.grid(column=1, row=1, padx=5, pady=5, sticky="ew")

        # Create a combobox for mod categories
        categories_label = ttk.Label(self, text="Category:")
        categories_label.grid(column=0, row=2, padx=5, pady=5, sticky="w")

        self.categories = ["Animals", "Anime and Video Games", "Celebrity Sims", "Character Sims", "Child Related", "Create-A-Sim Content", "Crime, Punishment, and Public Service", "Decorating Themes", "Cemeteries/Death",
                           "Dining, Retail, Parks and Pools", "EA Match", "Fantasy/Sci-Fi", "Food", "Game Mods and Hacks", "Historical and Ethnic", "Holidays", "Medical", "Sims 4 Pose Database", "Religious", "Weddings and Marriage", "Work & School"]
        self.selected_category = tk.StringVar()
        self.category_combobox = ttk.Combobox(
            self, textvariable=self.selected_category, values=self.categories)
        self.category_combobox.grid(
            column=1, row=2, padx=5, pady=5, sticky="ew")

        # Add the extract archive button
        self.extract_button = ttk.Button(
            self, text="Extract Archive", command=self.extract_archive_dialog)
        self.extract_button.grid(
            column=0, row=3, padx=5, pady=5, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Add button for user-defined categories
        self.add_category_button = ttk.Button(
            self, text="Add Categories", command=self.add_user_defined_categories
        )
        self.add_category_button.grid(
            column=1, row=3, padx=5, pady=5, sticky="ew")

    def create_menu(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.settings_menu.add_command(
            label="Change Theme", command=self.show_settings)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)

    def show_settings(self):
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("300x200")

        theme_frame = ttk.Frame(settings_window)
        theme_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        theme_label = ttk.Label(theme_frame, text="Select a theme:")
        theme_label.pack(side=tk.TOP, pady=(0, 10))

        self.create_theme_listbox(theme_frame)

        apply_theme_button = ttk.Button(
            theme_frame, text="Apply",
            command=lambda: self.change_theme(
                self.theme_listbox.get(self.theme_listbox.curselection()))
        )
        apply_theme_button.pack(side=tk.BOTTOM, pady=(10, 0))

    def create_theme_listbox(self, parent):
        self.theme_listbox = tk.Listbox(parent)
        self.theme_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.theme_listbox.bind('<<ListboxSelect>>', self.on_theme_selected)

        for theme in sorted(self.get_themes()):
            self.theme_listbox.insert(tk.END, theme)

        current_theme_index = self.theme_listbox.get(
            0, tk.END).index(self.default_theme)
        self.theme_listbox.selection_set(current_theme_index)

    def on_theme_selected(self, event):
        selected_theme = self.theme_listbox.get(
            self.theme_listbox.curselection())
        self.change_theme(selected_theme)

    def change_theme(self, selected_theme):
        if selected_theme and selected_theme in self.get_themes():
            self.set_theme(selected_theme)
            self.default_theme = selected_theme
            self.save_theme(selected_theme)
        else:
            messagebox.showerror("Error", "Invalid theme selected.")

    def load_theme(self):
        config_file = 'config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                config = json.load(file)
                self.default_theme = config.get('theme', 'arc')
        else:
            self.default_theme = 'arc'

    def save_theme(self, theme):
        config_file = 'config.json'
        config = {'theme': theme}
        with open(config_file, 'w') as file:
            json.dump(config, file)

    def extract_archive_dialog(self):
        if archive_path := filedialog.askopenfilename(
            title="Select Archive",
            filetypes=[
                ("Archives", "*.zip *.rar *.tar *.gz *.bz2"),
                ("All Files", "*.*"),
            ],
        ):
            if destination_path := filedialog.askdirectory(
                title="Select Destination Folder"
            ):
                self.extract_archive(archive_path, destination_path)

    def extract_archive(self, archive_path, destination_path):
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        extracted_path = os.path.join(
            destination_path, "temp_extraction_folder")
        os.makedirs(extracted_path)
        archive_extension = os.path.splitext(archive_path)[1]

        if archive_extension == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(destination_path)
        elif archive_extension == '.rar':
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                rar_ref.extractall(destination_path)
        elif archive_extension == '.tar':
            with tarfile.open(archive_path, 'r') as tar_ref:
                tar_ref.extractall(destination_path)
        elif archive_extension in ['.gz', '.bz2']:
            compression = 'gz' if archive_extension == '.gz' else 'bz2'
            with tarfile.open(archive_path, f'r|{compression}') as tar_ref:
                tar_ref.extractall(destination_path)
        else:
            raise ValueError(
                f"Unsupported archive format: {archive_extension}")
        categorized_files = self.categorize_files(extracted_path)

        for category, files in categorized_files.items():
            category_folder = os.path.join(destination_path, category)
            os.makedirs(category_folder, exist_ok=True)

            for file in files:
                file_name = os.path.basename(file)
                shutil.move(file, os.path.join(category_folder, file_name))

        shutil.rmtree(extracted_path)

    def add_user_defined_categories(self):
        if user_defined_categories := simpledialog.askstring(
            "Add Categories", "Enter new categories separated by commas:"
        ):
            new_categories = [category.strip()
                              for category in user_defined_categories.split(",")]
            self.categories.extend(new_categories)
            self.category_combobox["values"] = self.categories

    def categorize_files(self, extracted_path):
        categorized_files = defaultdict(list)

        for root, _, files in os.walk(extracted_path):
            for file in files:
                file_path = os.path.join(root, file)
                category = self.identify_file_category(file)
                categorized_files[category].append(file_path)

        return categorized_files

    def identify_file_category(self, file_name):

        file_name = file_name.lower()

        # File extension-based categories
        extension_map = {
            ".package": "Package Mods",
            ".sims3pack": "Sims3Pack Mods",
            ".sim": "Sim Characters",
            ".blueprint": "Blueprints",
            ".bak": "Backup Files",
        }

        file_extension = os.path.splitext(file_name)[1]
        if category := extension_map.get(file_extension):
            return category

        # Pattern-based categories
        pattern_map = {
            "cas": "Create-A-Sim",
            "clothing": "Clothing",
            "hair": "Hair",
            "acc": "Accessories",
            "makeup": "Makeup",
            "build": "Build Mode",
            "buy": "Buy Mode",
            "script": "Script Mods",
        }

        return next(
            (
                category
                for pattern, category in pattern_map.items()
                if pattern in file_name
            ),
            "Unknown",
        )


class ModOrganizerFrame(ttk.Frame):
    """A frame for managing mods and custom content in the application."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.mod_tags = {}

        self.create_widgets()

    def create_widgets(self):
        """Create and configure the necessary widgets."""
        self.create_mods_label()
        self.create_treeview()
        self.create_scrollbar()
        self.create_search_bar()
        self.create_entry_box()  # added new method to create the mod_entry widget
        self.create_buttons()

    def create_entry_box(self):
        """Create the entry box for adding new mods."""
        self.mod_entry_label = ttk.Label(
            self, text="Add a new mod or custom content:")
        self.mod_entry_label.grid(
            row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.mod_entry = ttk.Entry(self)
        self.mod_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        self.mod_category_label = ttk.Label(self, text="Category:")
        self.mod_category_label.grid(
            row=2, column=2, padx=(20, 0), pady=10, sticky=tk.W)

        self.category_options = ["CAS", "Build/Buy", "Gameplay", "Other"]
        self.selected_category = tk.StringVar(value=self.category_options[0])
        self.category_menu = ttk.OptionMenu(
            self, self.selected_category, *self.category_options)
        self.category_menu.grid(row=2, column=3, pady=10, sticky=tk.W)

    def create_mods_label(self):
        """Create the mods label."""
        self.mods_label = ttk.Label(self, text="Mods and Custom Content")
        self.mods_label.grid(row=0, column=0, padx=10,
                             pady=(10, 0), sticky=tk.W)

    def mod_exists(self, mod_name):
        """Check if a mod with the given name already exists in the treeview."""
        return any(
            self.treeview.item(item, "values")[0] == mod_name
            for item in self.treeview.get_children()
        )

    def create_treeview(self):
        self.treeview = ttk.Treeview(self, columns=(
            'Name', 'Category', 'Tags', 'Source'), show='headings', selectmode="extended")
        self.treeview.heading("#0", text="Mod Name")
        self.treeview.heading('Name', text='Name')
        self.treeview.heading('Category', text='Category')
        self.treeview.heading('Tags', text='Tags')
        self.treeview.heading('Source', text='Source')
        self.treeview.grid(row=1, column=0, padx=10,
                           pady=(5, 10), sticky=tk.NSEW)
        self.treeview.bind('<Up>', self.navigate_treeview)
        self.treeview.bind('<Down>', self.navigate_treeview)
        self.treeview.grid(row=1, column=0, padx=10, pady=(
            5, 10), sticky=tk.W+tk.E+tk.N+tk.S)
        self.bind_treeview_sort()

    def create_scrollbar(self):
        self.scrollbar = ttk.Scrollbar(
            self, orient='vertical', command=self.treeview.yview)
        self.scrollbar.grid(row=1, column=1, pady=(5, 10), sticky=tk.NS)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)

    def create_search_bar(self):
        self.search_label = ttk.Label(self, text="Search:")
        self.search_label.grid(
            row=0, column=1, sticky=tk.E, padx=(50, 0), pady=(10, 0))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_search)
        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=2, padx=10, pady=(10, 0))

    def create_buttons(self):
        self.button_frame = ttk.Frame(self)

        self.add_button = self.create_button(
            'Add', self.add_mod, 0, "Add a new mod or custom content.")
        self.edit_button = self.create_button(
            'Edit', self.edit_mod, 1, "Edit the selected mod or custom content.")
        self.remove_button = self.create_button(
            'Remove', self.remove_mod, 2, "Remove the selected mod or custom content.")
        self.manage_tags_button = self.create_button(
            'Manage Tags', self.manage_tags, 3, "Manage tags for mods and custom content.")
        self.save_mods_button = self.create_button(
            'Save Mods', self.save_mods, 4, "Save the current list of mods and custom content.")
        self.load_mods_button = self.create_button(
            'Load Mods', self.load_mods, 5, "Load a saved list of mods and custom content.")

        self.button_frame.grid(row=2, column=0, columnspan=2,
                               padx=10, pady=10, sticky=tk.W)

        self.add_button.config(command=self.add_mod)
        self.edit_button.config(command=self.edit_mod)
        self.remove_button.config(command=self.remove_mod)
        self.manage_tags_button.config(command=self.manage_tags)
        self.save_mods_button.config(command=self.save_mods)
        self.load_mods_button.config(command=self.load_mods)

    def create_button(self, text, command, column, tooltip_text):
        button = ttk.Button(self.button_frame, text=text,
                            command=command, width=10)
        button.grid(row=0, column=column, padx=(0 if column == 0 else 5, 5))
        self.create_tooltip(button, tooltip_text)
        return button

    def create_tooltip(self, widget, text):
        tooltip = ToolTip(widget, text)
        widget.bind('<Enter>', tooltip.show)
        widget.bind('<Leave>', tooltip.hide)

    def navigate_treeview(self, event):
        """Navigate the treeview using arrow keys."""
        key = event.keysym
        if cur_item := self.treeview.focus():
            cur_index = self.treeview.index(cur_item)
            new_index = None

            if key == 'Up' and cur_index > 0:
                new_index = cur_index - 1
            elif key == 'Down':
                new_index = cur_index + 1

            if new_index is not None:
                items = self.treeview.get_children()
                if 0 <= new_index < len(items):
                    self.treeview.selection_set(items[new_index])
                    self.treeview.focus(items[new_index])

    def update_search(self, *args):
        search_term = self.search_var.get().lower()
        self._extracted_from_filter_treeview_items_3(search_term)

    def filter_treeview_items(self, search_term):
        self._extracted_from_filter_treeview_items_3(search_term)

    # TODO Rename this here and in `update_search` and `filter_treeview_items`
    def _extracted_from_filter_treeview_items_3(self, search_term):
        for item in self.treeview.get_children():
            mod_name = self.treeview.item(item)["values"][0].lower()
            mod_category = self.treeview.item(item)["values"][1].lower()
            mod_tags = ' '.join(self.mod_tags.get(mod_name, [])).lower()
            if (
                search_term in mod_name
                or search_term in mod_category
                or search_term in mod_tags
            ):
                self.treeview.item(item, tags=("matched", ))
            else:
                self.treeview.item(item, tags=("not_matched", ))
        self.treeview.tag_configure("matched", background=None)
        self.treeview.tag_configure("not_matched", background="gray")

    def sort_treeview(self, column):
        """Sort the treeview by the selected column."""

        # Get the current sort order and reverse it
        current_sort = self.treeview.heading(column, "option", "sortorder")
        new_sort = "ascending" if current_sort == "descending" else "descending"

        # Get the current treeview items
        items = [(self.treeview.set(child, column), child)
                 for child in self.treeview.get_children('')]

        # Sort the items based on the new sort order
        items.sort(reverse=current_sort == "ascending",
                   key=lambda x: x[0].lower() if isinstance(x[0], str) else x[0])

        # Rearrange the items in the treeview
        for index, (_, child) in enumerate(items):
            self.treeview.move(child, '', index)

        # Update the sort order for the column
        self.treeview.heading(column, sortorder=new_sort)

    # Bind the treeview column headers to the sorting function
    def bind_treeview_sort(self):
        for col in self.treeview["columns"]:
            self.treeview.heading(
                col, text=col, command=lambda c=col: self.sort_treeview(c))

    def add_mod(self):
        # Add mod(s) to the treeview
        mod_files = filedialog.askopenfilenames(
            initialdir="/", title="Select mod files", filetypes=[("Package files", "*.package")])

        for mod_file in mod_files:
            mod_name = os.path.basename(mod_file)

            # Automatically categorize the mod file based on its name
            category = self.detect_category(mod_name)

            if mod_name and not self.mod_exists(mod_name):
                self.treeview.insert(
                    '', 'end', values=(mod_name, category))
                self.mod_tags[mod_name] = []

    def detect_category(self, mod_name):
        """Detect the category of the mod based on the file name."""
        category_regexes = {
            "CAS": r"cas|create a sim|sim customization|sim creation|sim appearance",
            "Build/Buy": r"build|buy|build and buy|furniture|decor",
            "Gameplay": r"gameplay|gameplay changes|gameplay tweaks|gameplay mods|gameplay adjustments",
            "Other": r"other|miscellaneous|uncategorized|unknown"
        }

        return next(
            (
                category
                for category, regex in category_regexes.items()
                if re.search(regex, mod_name, re.IGNORECASE)
            ),
            "Other",
        )

    def get_mod_source(self, mod_name):
        mod_name_lower = mod_name.lower()
        if "maxismatch" in mod_name_lower:
            return "MaxisMatch"
        elif "alpha" in mod_name_lower:
            return "Alpha"
        else:
            return "Unknown"

    def remove_mod(self):
        if selected_items := self.treeview.selection():
            for item in selected_items:
                self.treeview.delete(item)

    def manage_tags(self):
        selected_items = self.treeview.selection()

        if not selected_items:
            messagebox.showerror(
                "Error", "Please select a mod to manage tags.")
            return

        manage_tags_window = tk.Toplevel(self.parent)
        manage_tags_window.title("Manage Tags")
        manage_tags_window.geometry("300x300")

        tags_frame = ttk.Frame(manage_tags_window)
        tags_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tags_label = ttk.Label(tags_frame, text="Custom Tags:")
        tags_label.pack(side=tk.TOP)

        tags_listbox = tk.Listbox(tags_frame, selectmode=tk.MULTIPLE)
        tags_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Load tags for the selected mod(s)
        tags_to_load = set()
        for item in selected_items:
            mod_name = self.treeview.item(item)["values"][0]
            mod_tags = self.mod_tags.get(mod_name, [])
            tags_to_load.update(mod_tags)
        for tag in tags_to_load:
            tags_listbox.insert(tk.END, tag)

        add_tag_button = ttk.Button(
            tags_frame, text="Add Tag", command=lambda: self.add_tag(tags_listbox))
        add_tag_button.pack(side=tk.LEFT, padx=5, pady=10)
        remove_tag_button = ttk.Button(
            tags_frame, text="Remove Tag", command=lambda: self.remove_tag(tags_listbox))
        remove_tag_button.pack(side=tk.LEFT, padx=5, pady=10)

        # Update the tags of the selected mod(s) when the window is closed
        def on_close():
            new_tags = tags_listbox.get(0, tk.END)
            for item in selected_items:
                mod_name = self.treeview.item(item)["values"][0]
                self.mod_tags[mod_name] = list(new_tags)
            manage_tags_window.destroy()

        manage_tags_window.protocol("WM_DELETE_WINDOW", on_close)

    def add_tag(self, tags_listbox):
        # Add a tag to the listbox
        new_tag = simpledialog.askstring("Add Tag", "Enter the new tag:")
        if new_tag and new_tag not in tags_listbox.get(0, tk.END):
            tags_listbox.insert(tk.END, new_tag)

    def remove_tag(self, tags_listbox):
        if selected_tag := tags_listbox.curselection():
            tags_listbox.delete(selected_tag)

    def save_mods(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[
                                                ("JSON files", "*.json")], title="Save Mods")
        if file_path:
            mods_to_save = [{"name": self.treeview.item(item)["values"][0],
                            "category": self.treeview.item(item)["values"][1],
                             "tags": self.treeview.item(item)["values"][2],
                             "source": self.treeview.item(item)["values"][3]} for item in self.treeview.get_children()]
        with open(file_path, "w") as file:
            json.dump(mods_to_save, file)

    def load_mods(self):
        if file_path := filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Load Mods",
        ):
            with open(file_path, "r") as file:
                mods_to_load = json.load(file)
            self.treeview.delete(*self.treeview.get_children())
            for mod in mods_to_load:
                self.treeview.insert('', 'end', values=(
                    mod["name"], mod["category"], mod["tags"], mod["source"]))

    def edit_mod(self):
        if not (selected_items := self.treeview.selection()):
            return
        for item in selected_items:
            old_mod_name = self.treeview.item(item)["values"][0]
            old_mod_category = self.treeview.item(item)["values"][1]
            old_mod_tags = self.treeview.item(item)["values"][2] if len(
                self.treeview.item(item)["values"]) >= 3 else ""
            old_mod_source = self.treeview.item(item)["values"][3] if len(
                self.treeview.item(item)["values"]) >= 4 else ""

            new_mod_name = simpledialog.askstring(
                "Edit Mod Name", "Enter the new mod name:", initialvalue=old_mod_name)
            new_mod_category = simpledialog.askstring(
                "Edit Mod Category", "Enter the new mod category:", initialvalue=old_mod_category)
            new_mod_tags = simpledialog.askstring(
                "Edit Mod Tags", "Enter the new mod tags (comma-separated):", initialvalue=old_mod_tags)
            new_mod_source = simpledialog.askstring(
                "Edit Mod Source", "Enter the new mod source:", initialvalue=old_mod_source)

            if new_mod_name and new_mod_category and new_mod_tags and new_mod_source:
                self.treeview.item(item, values=(
                    new_mod_name, new_mod_category, new_mod_tags, new_mod_source))
                if old_mod_name in self.mod_tags:
                    self.mod_tags[new_mod_name] = self.mod_tags.pop(
                        old_mod_name)


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

    def show(self, event):
        """Show the tooltip."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip_window, text=self.text,
                          background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide(self, event):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


if __name__ == "__main__":
    app = ArchiStackApp()
    app.mainloop()
