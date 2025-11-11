import gpxpy
import gpxpy.gpx
from datetime import datetime, timedelta
import os
import sys

def validate_coordinates(lat, lon):
    """Проверяет корректность координат"""
    return -90 <= lat <= 90 and -180 <= lon <= 180

def validate_elevation(elevation):
    """Проверяет корректность высоты"""
    return elevation is None or -1000 <= elevation <= 10000

def fix_corrupted_date(date_str):
    """Исправляет поврежденные символы в дате"""
    if not date_str:
        return date_str
    
    # Заменяем поврежденные символы на правильные
    date_str = date_str.replace('', 'сен')  # Заменяем поврежденные символы на сен
    date_str = date_str.replace('', 'сен')  # На случай других вариантов повреждения
    date_str = date_str.replace('', 'сен')  # Еще один вариант
    
    return date_str

def format_timestamp_for_gpx(timestamp):
    """Форматирует время в ISO 8601 для GPX"""
    if timestamp is None:
        return None
    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z')

def plt_to_gpx(plt_file, gpx_file):
    try:
        # Проверяем существование входного файла
        if not os.path.exists(plt_file):
            raise FileNotFoundError(f"Файл {plt_file} не найден!")
        
        # Проверяем расширение файла
        if not plt_file.lower().endswith('.plt'):
            print(f"Предупреждение: файл {plt_file} не имеет расширения .plt")
        
        gpx = gpxpy.gpx.GPX()
        
        # Добавляем метаданные
        gpx.time = datetime.now()
        
        # Создаем трек
        track = gpxpy.gpx.GPXTrack()
        track_name = os.path.splitext(os.path.basename(plt_file))[0]
        track.name = track_name
        track.description = track_name
        
        # Создаем сегмент трека
        segment = gpxpy.gpx.GPXTrackSegment()
        track.segments.append(segment)
        gpx.tracks.append(track)

        print(f"Читаю файл: {plt_file}")
        
        # Пробуем разные кодировки
        lines = None
        encodings_to_try = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                with open(plt_file, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                print(f"Файл успешно прочитан с кодировкой: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if lines is None:
            raise ValueError("Не удалось прочитать файл ни с одной из попробованных кодировок!")

        if len(lines) < 7:
            raise ValueError("Файл PLT слишком короткий! Должно быть минимум 7 строк (6 заголовков + данные)")

        # В PLT первые 6 строк – заголовок
        data_lines = lines[6:]
        points_processed = 0
        points_skipped = 0

        for line_num, line in enumerate(data_lines, start=7):
            try:
                parts = line.strip().split(',')
                if len(parts) < 2:
                    points_skipped += 1
                    continue

                # Валидация и парсинг координат
                try:
                    lat = float(parts[0])
                    lon = float(parts[1])
                except ValueError as e:
                    print(f"Ошибка в строке {line_num}: неверные координаты - {e}")
                    points_skipped += 1
                    continue

                # Проверяем корректность координат
                if not validate_coordinates(lat, lon):
                    print(f"Предупреждение в строке {line_num}: координаты вне допустимого диапазона (lat={lat}, lon={lon})")
                    points_skipped += 1
                    continue

                # Фиксированная дата: 15 сентября 2025
                fixed_date = datetime(2025, 9, 15)
                
                # Парсим время из столбца 6 (время отдельно)
                timestamp = None
                if len(parts) > 6 and parts[6].strip():
                    try:
                        # Парсим время: "7:32:16"
                        time_str = parts[6].strip()
                        hour, minute, second = map(int, time_str.split(':'))
                        
                        # Создаем timestamp с фиксированной датой и парсенным временем
                        timestamp = datetime(2025, 9, 15, hour, minute, second)
                        
                    except (ValueError, IndexError) as e:
                        print(f"Предупреждение в строке {line_num}: не удалось распарсить время '{parts[6].strip()}' - {e}")

                # Создаем точку трека с полными данными
                track_point = gpxpy.gpx.GPXTrackPoint(lat, lon)
                
                # Добавляем время
                if timestamp is not None:
                    track_point.time = timestamp
                
                segment.points.append(track_point)
                
                # Отладочная информация (можно убрать в продакшене)
                if points_processed < 3:  # Показываем только первые 3 точки
                    print(f"Точка {points_processed + 1}: lat={lat}, lon={lon}, time={timestamp}")
                points_processed += 1

            except Exception as e:
                print(f"Ошибка обработки строки {line_num}: {e}")
                points_skipped += 1
                continue

        if points_processed == 0:
            raise ValueError("Не удалось обработать ни одной точки из файла!")

        # Добавляем bounds (границы) в метаданные
        if segment.points:
            lats = [point.latitude for point in segment.points]
            lons = [point.longitude for point in segment.points]
            gpx.bounds = gpxpy.gpx.GPXBounds(
                min_latitude=min(lats),
                max_latitude=max(lats),
                min_longitude=min(lons),
                max_longitude=max(lons)
            )

        # Сохраняем GPX
        print(f"Сохраняю результат в: {gpx_file}")
        with open(gpx_file, 'w', encoding='utf-8') as f:
            f.write(gpx.to_xml())

        print(f"✅ Конвертация завершена успешно!")
        print(f"📊 Обработано точек: {points_processed}")
        if points_skipped > 0:
            print(f"⚠️  Пропущено точек: {points_skipped}")
        print(f"📁 Результат сохранен: {gpx_file}")

    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Ошибка данных: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)
