import pathlib
import importlib
import os
import re
import glob
from hashlib import md5
from typing import Callable
from termcolor import cprint
from iappatcher_patcher.extractor import Extractor

exclude_imports = ["__init__.py", "Patch.py"]


class Patcher:
    def __init__(self, extractor: Extractor):
        self.extractor = extractor
        self.patches = []
        current_dir = pathlib.Path(__file__).parent / "patches"
        for path in glob.iglob(os.path.join(current_dir, "*.*")):
            if os.path.basename(path) in exclude_imports:
                continue
            module_name = "iappatcher_patcher.patches." + pathlib.Path(path).stem
            module = importlib.import_module(module_name, module_name)
            inner_class = (
                getattr(module, dir(module)[0])
                if dir(module)[0] != "Patch"
                else getattr(module, dir(module)[1])
            )
            self.patches.append(inner_class(self.extractor.temp_path))

    def patch(self):
        self.find_classes()
        self.patch_classes()

    def find_classes(self):
        patches_to_find = self.patches.copy()
        for filename in glob.iglob(
                os.path.join(self.extractor.temp_path, "**", "*.smali"), recursive=True
        ):
            if len(patches_to_find) == 0:
                break
            with open(filename, "r", encoding="utf8") as f:
                data = f.read()
            for patch in patches_to_find:
                if not patch.class_filter(data):
                    continue
                patch.class_data = data
                patch.class_path = filename
                patches_to_find.remove(patch)
        for patch in self.patches:
            if patch.class_data is None:
                cprint(f"[-] Didn't found {patch} class.", "red")

    def patch_classes(self):
        patches_globals: dict = {'apk_details': self.extractor.apk_details}
        patches_to_execute = self.patches
        while len(patches_to_execute) > 0:
            for patch in patches_to_execute:
                if any(map(lambda p: type(p) in patch.dependencies, patches_to_execute)):
                    continue
                patches_to_execute.remove(patch)
                if patch.class_data is None:
                    continue
                cprint(patch.print_message, "green")
                with open(patch.class_path, "w") as f:
                    f.write(patch.class_modifier(patch.class_data, patches_globals))
