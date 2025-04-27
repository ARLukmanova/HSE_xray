import os
import gdown
import zipfile
from google.colab import drive
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def setup_environment():
    """Настройка окружения и загрузка данных"""
    try:
        drive.mount("/content/drive")
        DRIVE_DIR = os.path.join("/content/drive", "MyDrive")
    except ImportError:
        DRIVE_DIR = os.getcwd()

    DATASET_DIR = os.path.join(os.getcwd(), "dataset")
    ZIP_PATH = os.path.join(DRIVE_DIR, "ChestXRay2017.zip")
    os.makedirs(DATASET_DIR, exist_ok=True)
    return DRIVE_DIR, DATASET_DIR, ZIP_PATH

def download_and_extract(file_id, zip_path, dataset_dir):
    """Загрузка и распаковка архива"""
    if not os.path.exists(zip_path):
        gdown.download(
            f"https://drive.google.com/uc?id={file_id}",
            zip_path,
            quiet=False,
        )
    
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dataset_dir)
    print(f"Данные распакованы в: {dataset_dir}")

def print_directory_structure(path, indent="", max_files=10):
    """
    Рекурсивно выводит структуру папок и файлов
    """
    if not os.path.exists(path):
        print(f"Путь '{path}' не существует.")
        return

    print(f"{indent}+ {os.path.basename(path)}/")
    items = os.listdir(path)
    files = [item for item in items if os.path.isfile(os.path.join(path, item))]
    directories = [item for item in items if os.path.isdir(os.path.join(path, item))]

    file_count = 0
    for file in files:
        if file_count < max_files:
            print(f"{indent}  - {file}")
            file_count += 1
        else:
            hidden_files = len(files) - max_files
            print(f"{indent}  ... (ещё {hidden_files} файлов скрыто)")
            break

    for directory in directories:
        directory_path = os.path.join(path, directory)
        print_directory_structure(directory_path, indent + "  ", max_files)

def count_files_in_directory(path, min_files=10):
    """
    Рекурсивно подсчитывает количество файлов в каждой поддиректории,
    игнорируя папку __MACOSX и папки с файлами < min_files.
    Возвращает словарь с разделением на train и test данные.
    """
    train_counts = {}
    test_counts = {}

    for root, dirs, files in os.walk(path):
        # Игнорируем папку __MACOSX
        if '__MACOSX' in root.split(os.sep):
            continue

        num_files = len(files)
        if num_files >= min_files:
            # Определяем, это train или test данные
            if 'test' in root.lower():
                test_counts[root] = num_files
            else:  # Все остальное считаем train данными
                train_counts[root] = num_files

    return {'train': train_counts, 'test': test_counts}

def plot_vertical_file_counts(file_counts_dict):
    """
    Создает вертикальную столбчатую диаграмму с:
    - горизонтальными подписями
    - бирюзовым цветом для train
    - розовым цветом для test
    """
    train_counts = file_counts_dict['train']
    test_counts = file_counts_dict['test']

    if not train_counts and not test_counts:
        print("Нет папок с 10+ файлами для отображения.")
        return

    # Подготовка данных
    train_items = sorted(train_counts.items(), key=lambda x: x[1], reverse=True)
    test_items = sorted(test_counts.items(), key=lambda x: x[1], reverse=True)

    # Собираем все данные в один список
    all_labels = []
    all_values = []
    colors = []

    # Добавляем train данные (бирюзовый)
    for path, count in train_items:
        all_labels.append(f"train/{os.path.basename(path)}")
        all_values.append(count)
        colors.append('#40E0D0')  # Бирюзовый

    # Добавляем test данные (розовый)
    for path, count in test_items:
        all_labels.append(f"test/{os.path.basename(path)}")
        all_values.append(count)
        colors.append('#FF69B4')  # Розовый

    # Создаем фигуру с динамическим размером
    plt.figure(figsize=(6, 6))

    # Создаем вертикальный график
    bars = plt.bar(all_labels, all_values, color=colors, edgecolor='grey', linewidth=0.7)

    # Добавляем подписи значений
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{int(height)}',
                 ha='center', va='bottom', fontsize=9)

    # Настройки графика
    plt.ylabel('Количество файлов', fontsize=12)
    plt.xlabel('Папки', fontsize=12)
    plt.title('Распределение файлов по папкам (train/test)', fontsize=16, pad=20)
    plt.xticks(rotation=0, ha='center', fontsize=10)  # Горизонтальные подписи

    # Улучшаем читаемость подписей
    plt.gca().yaxis.grid(True, linestyle='--', alpha=0.6)
    plt.gca().set_axisbelow(True)

    # Добавляем легенду с новыми цветами
    train_patch = mpatches.Patch(color='#40E0D0', label='Train данные')
    test_patch = mpatches.Patch(color='#FF69B4', label='Test данные')
    plt.legend(handles=[train_patch, test_patch], fontsize=11)

    # Устанавливаем отступы
    plt.tight_layout()
    plt.show()

def analyze_dataset(path_to_scan="./dataset"):
    """
    Полный анализ датасета с визуализацией
    """
    # Подсчитываем файлы (игнорируя __MACOSX и папки с <10 файлами)
    file_counts_dict = count_files_in_directory(path_to_scan, min_files=10)

    # Создаем вертикальный график
    print("\nСоздаем вертикальный график с новыми цветами...")
    plot_vertical_file_counts(file_counts_dict)

    # Дополнительная статистика
    train_counts = file_counts_dict['train']
    test_counts = file_counts_dict['test']

    if train_counts or test_counts:
        print("\nСтатистика:")
        if train_counts:
            train_total = sum(train_counts.values())
            print(f"Train данных: {len(train_counts)} папок, {train_total} файлов")
        if test_counts:
            test_total = sum(test_counts.values())
            print(f"Test данных: {len(test_counts)} папок, {test_total} файлов")

        if train_counts and test_counts:
            ratio = test_total / train_total
            print(f"Соотношение test/train: {ratio:.2f}")
    else:
        print("Нет данных для отображения статистики.")