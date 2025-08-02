# -*- coding: utf-8 -*-

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

if os.name == 'nt':
    import ctypes
    ctypes.windll.kernel32.SetConsoleCP(65001)
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)

def get_folder_size(path):
    total = 0
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_dir(follow_symlinks=False):
                    total += get_folder_size(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
            except Exception:
                pass
    except Exception:
        pass
    return total

def list_folders_with_size(path, max_workers=4):
    folders = [
        (name, os.path.join(path, name))
        for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))
    ]
    total = len(folders)
    print(f"\nScanning {total} folders...\n")

    folder_sizes = []
    done = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(get_folder_size, full_path): name
            for name, full_path in folders
        }

        for future in as_completed(futures):
            name = futures[future]
            size = future.result()
            done += 1
            prog = f"[{done}/{total}] {name}"
            print(prog.ljust(80), end='\r', flush=True)
            if size >= 50 * 1024 * 1024:
                folder_sizes.append((name, size))

    print(' ' * 80, end='\r')

    folder_sizes.sort(key=lambda x: x[1], reverse=True)

    print("Folders larger than 50 MB (descending order):\n")
    for name, size in folder_sizes:
        print(f"{name:<30} {size / (1024**2):8.2f} MB")

if __name__ == "__main__":
    while True:
        target = input("\nEnter the path to the folder to scan (or 'exit' to exit): ").strip()
        if target.lower() == 'exit':
            print("Exiting the program.")
            break
        if not os.path.isdir(target):
            print("Error: The path does not exist or is not a folder.")
            continue
        list_folders_with_size(target, max_workers=4)
