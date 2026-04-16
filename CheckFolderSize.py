# -*- coding: utf-8 -*-
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Для Windows — устанавливаем консоль в UTF‑8
if os.name == 'nt':
    import ctypes
    ctypes.windll.kernel32.SetConsoleCP(65001)
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)


def pick_folder(initial_dir=None):
    """Открывает диалог выбора папки. Возвращает путь или None если отменено."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()          # скрываем главное окно
        root.attributes('-topmost', True)  # диалог поверх всех окон

        folder = filedialog.askdirectory(
            title="Выберите папку для сканирования",
            initialdir=initial_dir or os.path.expanduser("~"),
        )
        root.destroy()
        return folder if folder else None

    except ImportError:
        print("Tkinter недоступен — введите путь вручную.")
        return None
    except Exception as e:
        print(f"Диалог выбора папки недоступен ({e}) — введите путь вручную.")
        return None


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


def format_size(size_bytes):
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / (1024**3):8.2f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / (1024**2):8.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:8.2f} KB"
    else:
        return f"{size_bytes:8d}  B"


def get_entry_type(entry_path):
    """Определяет тип элемента: папка, файл (с расширением или без), симлинк и т.д."""
    try:
        if os.path.islink(entry_path):
            return "[симлинк]"
        elif os.path.isdir(entry_path):
            return "[папка]"
        elif os.path.isfile(entry_path):
            ext = os.path.splitext(entry_path)[1]
            if ext:
                return f"[{ext.lower()}]"
            else:
                return "[без расш.]"
        else:
            return "[прочее]"
    except Exception:
        return "[?]"


def scan_directory(path, min_size_mb=0, max_workers=8):
    min_size_bytes = int(min_size_mb * 1024 * 1024)

    try:
        entries_raw = list(os.scandir(path))
    except PermissionError:
        print("Ошибка: нет доступа к папке.")
        return
    except Exception as e:
        print(f"Ошибка при сканировании: {e}")
        return

    total = len(entries_raw)
    print(f"\nНайдено элементов: {total}. Вычисляем размеры...\n")

    results = []
    done = 0

    def process_entry(entry):
        try:
            if entry.is_dir(follow_symlinks=False):
                size = get_folder_size(entry.path)
            elif entry.is_file(follow_symlinks=False):
                size = entry.stat(follow_symlinks=False).st_size
            else:
                try:
                    size = entry.stat(follow_symlinks=False).st_size
                except Exception:
                    size = 0
            return entry.name, entry.path, size
        except Exception:
            return entry.name, entry.path, 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_entry, e): e for e in entries_raw}
        for future in as_completed(futures):
            name, full_path, size = future.result()
            done += 1
            prog = f"[{done}/{total}] {name}"
            print(prog.ljust(80), end='\r', flush=True)
            if size >= min_size_bytes:
                entry_type = get_entry_type(full_path)
                results.append((name, full_path, size, entry_type))

    print(' ' * 80, end='\r')

    results.sort(key=lambda x: x[2], reverse=True)

    filter_label = f">= {min_size_mb} МБ" if min_size_mb > 0 else "все"
    print(f"Элементы ({filter_label}), по убыванию размера:\n")
    print(f"{'Тип':<12} {'Имя':<40} {'Размер':>12}")
    print("-" * 66)

    for name, full_path, size, entry_type in results:
        name_col = (name[:38] + "..") if len(name) > 40 else name
        print(f"{entry_type:<12} {name_col:<40} {format_size(size):>12}")

    print("-" * 66)
    total_shown = sum(r[2] for r in results)
    print(f"{'Итого показано:':<53} {format_size(total_shown):>12}\n")


if __name__ == "__main__":
    last_dir = None  # запоминаем последнюю папку для удобства

    while True:
        print("\n" + "=" * 66)
        print("  Выберите папку через диалог или введите путь вручную.")
        print("  Нажмите Enter — откроется окно выбора папки.")
        print("  Введите 'exit' для выхода.")
        print("=" * 66)

        raw = input("\nПуть к папке (Enter = диалог, exit = выход): ").strip().strip('"')

        if raw.lower() == 'exit':
            print("Выход из программы.")
            break

        if raw == "":
            # Открываем графический диалог
            target = pick_folder(initial_dir=last_dir)
            if not target:
                print("Папка не выбрана.")
                continue
            print(f"Выбрана папка: {target}")
        else:
            target = raw

        if not os.path.isdir(target):
            print("Ошибка: путь не существует или не является папкой.")
            continue

        last_dir = target  # запоминаем для следующего диалога

        size_input = input(
            "Минимальный размер для показа в МБ (0 = показать всё): "
        ).strip()
        try:
            min_mb = float(size_input) if size_input else 0
        except ValueError:
            min_mb = 0

        scan_directory(target, min_size_mb=min_mb, max_workers=8)
