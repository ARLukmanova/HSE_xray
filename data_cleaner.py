import os
import hashlib
from tqdm import tqdm
from PIL import Image
import matplotlib.pyplot as plt
import shutil


def copy_test_folder(src_dataset_dir, dst_dataset_dir):
    """
    Копирует папку test из исходного датасета в новый без изменений
    
    Args:
        src_dataset_dir (str): Путь к исходному датасету
        dst_dataset_dir (str): Путь к целевому датасету
        
    Returns:
        str: Путь к скопированной папке test
    """
    src_test_dir = os.path.join(src_dataset_dir, 'test')
    dst_test_dir = os.path.join(dst_dataset_dir, 'test')
    
    if not os.path.exists(src_test_dir):
        print(f"Папка test не найдена в {src_dataset_dir}")
        return None
    
    # Копируем всю папку test рекурсивно
    shutil.copytree(src_test_dir, dst_test_dir, dirs_exist_ok=True)
    print(f"Папка test скопирована в {dst_test_dir}")
    return dst_test_dir


def get_hash(file_path):
    """Вычисляет MD5 хеш файла"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def find_duplicates(folder_path):
    """Находит дубликаты файлов"""
    hashes = {}
    duplicates = []
    duplicates_files = set()

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.jpeg', '.jpg', '.png')):
                file_path = os.path.join(root, file)
                file_hash = get_hash(file_path)

                if file_hash in hashes:
                    duplicates.append((file_path, hashes[file_hash]))
                    duplicates_files.add(file_path)
                else:
                    hashes[file_hash] = file_path

    return duplicates, duplicates_files

def visualize_duplicates(duplicates_dict):
    """Визуализация дубликатов"""
    for cls, dup_list in duplicates_dict.items():
        print(f"\nКласс: {cls}")
        print(f"Всего пар дубликатов: {len(dup_list)}")

        for i, (dup1, dup2) in enumerate(dup_list[:3]):
            try:
                img1 = Image.open(dup1)
                img2 = Image.open(dup2)

                plt.figure(figsize=(8, 4))
                plt.subplot(1, 2, 1)
                plt.imshow(img1, cmap='gray')
                plt.title(f"Дубликат {i+1}\n{os.path.basename(dup1)}")
                plt.axis('off')

                plt.subplot(1, 2, 2)
                plt.imshow(img2, cmap='gray')
                plt.title(f"Оригинал {i+1}\n{os.path.basename(dup2)}")
                plt.axis('off')

                plt.tight_layout()
                plt.show()
            except Exception as e:
                print(f"Ошибка при отображении: {e}")

def clean_dataset(src_dir, dst_dir, classes, all_duplicates_files):
    """Создание очищенного датасета"""
    total_copied = 0
    total_skipped = 0

    for cls in tqdm(classes, desc="Обработка классов"):
        src_class_dir = os.path.join(src_dir, cls)
        dst_class_dir = os.path.join(dst_dir, cls)
        dup_files = all_duplicates_files.get(cls, set())

        os.makedirs(dst_class_dir, exist_ok=True)
        
        for root, _, files in os.walk(src_class_dir):
            for file in files:
                if file.lower().endswith(('.jpeg', '.jpg', '.png')):
                    src_path = os.path.join(root, file)
                    
                    if src_path not in dup_files:
                        relative_path = os.path.relpath(root, src_dir)
                        dst_path_dir = os.path.join(dst_dir, relative_path)
                        os.makedirs(dst_path_dir, exist_ok=True)
                        
                        dst_path = os.path.join(dst_path_dir, file)
                        shutil.copy2(src_path, dst_path)
                        total_copied += 1
                    else:
                        total_skipped += 1

    print(f"\nИтоги:")
    print(f"Скопировано уникальных файлов: {total_copied}")
    print(f"Пропущено дубликатов: {total_skipped}")
    return dst_dir