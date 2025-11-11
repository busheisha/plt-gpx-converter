import xml.etree.ElementTree as ET
import shutil
from datetime import datetime

def fix_gpx(filename: str):
    # Загружаем XML
    tree = ET.parse(filename)
    root = tree.getroot()

    # Определим пространство имён
    gpx_ns = root.tag.split("}")[0].strip("{")
    ET.register_namespace("", gpx_ns)  # регистрируем как "дефолтное", чтобы не было ns0
    ns = {"gpx": gpx_ns}

    # Проверяем наличие <trk>
    trk = root.find("gpx:trk", ns)
    if trk is not None:
        return "Track already exists, no changes made."

    # Делаем резервную копию
    backup_filename = filename.replace(".gpx", "_orig.gpx")
    shutil.copy(filename, backup_filename)

    # Собираем все точки <wpt>
    waypoints = root.findall("gpx:wpt", ns)
    if not waypoints:
        return "No waypoints found in file, nothing to fix."

    # Считаем времена всех wpt
    times = []
    for wpt in waypoints:
        t = wpt.find("gpx:time", ns)
        if t is not None and t.text:
            try:
                times.append(datetime.fromisoformat(t.text.replace("Z", "+00:00")))
            except Exception:
                pass

    if not times:
        return "No valid timestamps in waypoints, cannot fix file."

    min_time = min(times)
    max_time = max(times)

    # Берем координаты первой по времени точки
    first_wpt = min(
        waypoints,
        key=lambda w: datetime.fromisoformat(
            w.find("gpx:time", ns).text.replace("Z", "+00:00")
        ),
    )
    lat = first_wpt.get("lat")
    lon = first_wpt.get("lon")

    # Создаем <trk> (с правильным namespace)
    trk = ET.SubElement(root, f"{{{gpx_ns}}}trk")
    name = ET.SubElement(trk, f"{{{gpx_ns}}}name")
    name.text = "points"

    trkseg = ET.SubElement(trk, f"{{{gpx_ns}}}trkseg")

    # Первая точка
    trkpt1 = ET.SubElement(trkseg, f"{{{gpx_ns}}}trkpt", attrib={"lat": lat, "lon": lon})
    time1 = ET.SubElement(trkpt1, f"{{{gpx_ns}}}time")
    time1.text = min_time.isoformat().replace("+00:00", "Z")

    # Вторая точка
    trkpt2 = ET.SubElement(trkseg, f"{{{gpx_ns}}}trkpt", attrib={"lat": lat, "lon": lon})
    time2 = ET.SubElement(trkpt2, f"{{{gpx_ns}}}time")
    time2.text = max_time.isoformat().replace("+00:00", "Z")

    # Сохраняем изменения
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    return "Waypoints file corrected"
