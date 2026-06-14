#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_images.py — подготовка картинок для тренажёра «Стереотренировки».

Что делает:
  • берёт все картинки (PNG/JPG/JPEG/WEBP/BMP/GIF) из папки-источника;
  • уменьшает так, чтобы большая сторона была не больше 1024 px (меньшие не трогает);
  • фон и кадрировку НЕ меняет (как есть);
  • сохраняет как PNG с именами img1.png, img2.png, img3.png ...;
  • кладёт результат в папку images/ рядом со скриптом (или указанную);
  • создаёт images/manifest.json со списком файлов — его читает сайт,
    чтобы показать тренировки «из коробки».

Зависимость: Pillow  ->  pip install Pillow

Запуск:
  python prepare_images.py "C:\\путь\\к\\исходным\\картинкам"
  python prepare_images.py "/путь/к/картинкам" --out images --max 1024

Если путь не указать — скрипт спросит его интерактивно.
"""

import sys
import os
import json
import argparse

try:
    from PIL import Image, ImageOps
except ImportError:
    print("ОШИБКА: не установлена библиотека Pillow.")
    print("Установите её командой:  pip install Pillow")
    sys.exit(1)

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def collect_images(src):
    files = []
    for name in sorted(os.listdir(src)):
        path = os.path.join(src, name)
        if os.path.isfile(path) and os.path.splitext(name)[1].lower() in EXTS:
            files.append(path)
    return files


def process(src, out_dir, max_side):
    if not os.path.isdir(src):
        print(f"ОШИБКА: папка не найдена: {src}")
        return 1

    os.makedirs(out_dir, exist_ok=True)
    images = collect_images(src)
    if not images:
        print(f"В папке нет картинок: {src}")
        return 1

    print(f"Найдено картинок: {len(images)}")
    manifest = []
    idx = 0

    for path in images:
        try:
            im = Image.open(path)
            # учитываем EXIF-поворот (с телефонов)
            im = ImageOps.exif_transpose(im)
            # в RGBA, чтобы сохранить прозрачность, если она есть
            im = im.convert("RGBA")

            w, h = im.size
            scale = min(1.0, max_side / float(max(w, h)))
            if scale < 1.0:
                new = (max(1, round(w * scale)), max(1, round(h * scale)))
                im = im.resize(new, Image.LANCZOS)

            idx += 1
            out_name = f"img{idx}.png"
            out_path = os.path.join(out_dir, out_name)
            im.save(out_path, "PNG", optimize=True)
            manifest.append(out_name)

            before_kb = os.path.getsize(path) // 1024
            after_kb = os.path.getsize(out_path) // 1024
            print(f"  {os.path.basename(path):<32} -> {out_name:<10} "
                  f"{w}x{h} -> {im.size[0]}x{im.size[1]}  ({before_kb} КБ -> {after_kb} КБ)")
        except Exception as e:
            print(f"  ПРОПУЩЕНО {os.path.basename(path)}: {e}")

    # manifest.json — список файлов для сайта
    manifest_path = os.path.join(out_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"images": manifest}, f, ensure_ascii=False, indent=2)

    print(f"\nГотово. Обработано: {len(manifest)}")
    print(f"Папка с результатом: {os.path.abspath(out_dir)}")
    print(f"Список файлов:       {os.path.abspath(manifest_path)}")
    print("\nТеперь скопируйте папку images/ (вместе с manifest.json) в репозиторий рядом с index.html.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Подготовка картинок для тренажёра")
    ap.add_argument("src", nargs="?", help="папка с исходными картинками")
    ap.add_argument("--out", default="images", help="папка назначения (по умолчанию images)")
    ap.add_argument("--max", type=int, default=1024, help="макс. сторона в px (по умолчанию 1024)")
    args = ap.parse_args()

    src = args.src
    if not src:
        src = input("Укажите путь к папке с картинками: ").strip().strip('"').strip("'")

    sys.exit(process(src, args.out, args.max))


if __name__ == "__main__":
    main()
