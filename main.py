#!/usr/bin/env python3
"""
Универсальный конвертер PLT в GPX с поддержкой waypoints
"""

import os
import sys
import glob
from plt_to_gpx_converter import plt_to_gpx
from add_waypoints import fix_gpx

def find_plt_files():
    """Находит все PLT файлы в текущей директории"""
    return glob.glob("*.plt")

def find_gpx_files():
    """Находит все GPX файлы в текущей директории"""
    return glob.glob("*.gpx")

def convert_plt_to_gpx():
    """Конвертирует все PLT файлы в GPX"""
    plt_files = find_plt_files()
    
    if not plt_files:
        print("❌ PLT файлы не найдены")
        return []
    
    print(f"🔄 Найдено PLT файлов: {len(plt_files)}")
    
    converted_files = []
    for plt_file in plt_files:
        gpx_file = plt_file.replace('.plt', '.gpx')
        print(f"\n📁 Конвертируем: {plt_file} → {gpx_file}")
        try:
            plt_to_gpx(plt_file, gpx_file)
            converted_files.append(gpx_file)
        except Exception as e:
            print(f"❌ Ошибка конвертации {plt_file}: {e}")
    
    return converted_files

def add_waypoints_to_gpx():
    """Добавляет треки к GPX файлам с waypoints"""
    gpx_files = find_gpx_files()
    
    if not gpx_files:
        print("❌ GPX файлы не найдены")
        return []
    
    print(f"🔄 Найдено GPX файлов: {len(gpx_files)}")
    
    processed_files = []
    for gpx_file in gpx_files:
        print(f"\n🔧 Обрабатываем: {gpx_file}")
        try:
            result = fix_gpx(gpx_file)
            print(f"📋 Результат: {result}")
            if "corrected" in result.lower():
                processed_files.append(gpx_file)
        except Exception as e:
            print(f"❌ Ошибка обработки {gpx_file}: {e}")
    
    return processed_files

def main():
    """Главная функция"""
    print("🚀 Универсальный конвертер PLT/GPX")
    print("=" * 50)
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "convert":
            print("📁 Режим: Конвертация PLT → GPX")
            convert_plt_to_gpx()
            
        elif command == "waypoints":
            print("📍 Режим: Добавление треков к waypoints")
            add_waypoints_to_gpx()
            
        elif command == "all":
            print("🔄 Режим: Полная обработка (конвертация + waypoints)")
            converted = convert_plt_to_gpx()
            if converted:
                add_waypoints_to_gpx()
            
        else:
            print_help()
    else:
        # Интерактивный режим
        print("Выберите действие:")
        print("1. Конвертировать PLT → GPX")
        print("2. Добавить треки к waypoints")
        print("3. Сделать все (конвертация + waypoints)")
        print("4. Показать справку")
        
        try:
            choice = input("\nВведите номер (1-4): ").strip()
            
            if choice == "1":
                convert_plt_to_gpx()
            elif choice == "2":
                add_waypoints_to_gpx()
            elif choice == "3":
                converted = convert_plt_to_gpx()
                if converted:
                    add_waypoints_to_gpx()
            elif choice == "4":
                print_help()
            else:
                print("❌ Неверный выбор")
                
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def print_help():
    """Показывает справку"""
    print("\n📖 Справка:")
    print("=" * 30)
    print("Использование:")
    print("  python main.py                    # Интерактивный режим")
    print("  python main.py convert           # Конвертировать PLT → GPX")
    print("  python main.py waypoints         # Добавить треки к waypoints")
    print("  python main.py all               # Сделать все операции")
    print("  python main.py help              # Показать эту справку")
    print("\nОперации:")
    print("  convert    - Конвертирует все .plt файлы в .gpx")
    print("  waypoints  - Добавляет треки к .gpx файлам с waypoints")
    print("  all        - Выполняет конвертацию, затем обработку waypoints")

if __name__ == "__main__":
    main()