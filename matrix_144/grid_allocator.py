"""Ортогональная сетка квантования геоида: 12 широтных × 12 долготных зон = 144 ячейки.

Ячейка — угловой сектор 15° × 30°, поэтому сетка ГРУБАЯ (почти вся Украина — одна ячейка).
Для локальной работы используйте locate_path(): рекурсивное деление ячейки снова на 12×12.
"""
from __future__ import annotations

import math


class GridAllocator:
    def __init__(self, lat_zones: int = 12, lon_zones: int = 12):
        self.lat_zones = lat_zones
        self.lon_zones = lon_zones
        self.total_cells = lat_zones * lon_zones

    # --- геометрия ---
    def calculate_cell_coordinates(self, cell_id: int) -> dict:
        if not (1 <= cell_id <= self.total_cells):
            raise ValueError(f"Идентификатор ячейки должен быть в диапазоне от 1 до {self.total_cells}.")
        idx = cell_id - 1
        lat_i, lon_i = divmod(idx, self.lon_zones)
        dlat, dlon = 180.0 / self.lat_zones, 360.0 / self.lon_zones
        lat0, lon0 = -90.0 + lat_i * dlat, -180.0 + lon_i * dlon
        return {"cell_id": cell_id,
                "lat_range": (round(lat0, 2), round(lat0 + dlat, 2)),
                "lon_range": (round(lon0, 2), round(lon0 + dlon, 2))}

    def center(self, cell_id: int) -> tuple[float, float]:
        c = self.calculate_cell_coordinates(cell_id)
        return (sum(c["lat_range"]) / 2.0, sum(c["lon_range"]) / 2.0)

    def locate(self, lat: float, lon: float) -> int:
        """Номер ячейки (1..144) по координатам."""
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            raise ValueError("lat в [-90, 90], lon в [-180, 180]")
        lat_i = min(int((lat + 90.0) // (180.0 / self.lat_zones)), self.lat_zones - 1)
        lon_i = min(int((lon + 180.0) // (360.0 / self.lon_zones)), self.lon_zones - 1)
        return lat_i * self.lon_zones + lon_i + 1

    def locate_path(self, lat: float, lon: float, depth: int = 2) -> list[int]:
        """Путь по вложенным сеткам 12×12: [ячейка верхнего уровня, подъячейка, ...]."""
        if depth < 1:
            raise ValueError("depth >= 1")
        self.locate(lat, lon)  # валидация
        lat0, lat1, lon0, lon1 = -90.0, 90.0, -180.0, 180.0
        path = []
        for _ in range(depth):
            dlat, dlon = (lat1 - lat0) / self.lat_zones, (lon1 - lon0) / self.lon_zones
            lat_i = min(int((lat - lat0) // dlat), self.lat_zones - 1)
            lon_i = min(int((lon - lon0) // dlon), self.lon_zones - 1)
            path.append(lat_i * self.lon_zones + lon_i + 1)
            lat0, lat1 = lat0 + lat_i * dlat, lat0 + (lat_i + 1) * dlat
            lon0, lon1 = lon0 + lon_i * dlon, lon0 + (lon_i + 1) * dlon
        return path

    def neighbors(self, cell_id: int) -> list[int]:
        """Соседи по сторонам (С, Ю, В, З). По долготе сетка замкнута, у полюсов — нет."""
        self.calculate_cell_coordinates(cell_id)
        lat_i, lon_i = divmod(cell_id - 1, self.lon_zones)
        out = []
        if lat_i + 1 < self.lat_zones:
            out.append((lat_i + 1) * self.lon_zones + lon_i + 1)
        if lat_i > 0:
            out.append((lat_i - 1) * self.lon_zones + lon_i + 1)
        out.append(lat_i * self.lon_zones + (lon_i + 1) % self.lon_zones + 1)
        out.append(lat_i * self.lon_zones + (lon_i - 1) % self.lon_zones + 1)
        return out

    def area_weight(self, cell_id: int) -> float:
        """Доля площади сферы, приходящаяся на ячейку (сумма по всем ячейкам = 1)."""
        c = self.calculate_cell_coordinates(cell_id)
        s0, s1 = (math.sin(math.radians(x)) for x in c["lat_range"])
        return (s1 - s0) / 2.0 * (360.0 / self.lon_zones) / 360.0

    # --- ресурсы ---
    def allocate_resource_by_geometry(self, cell_id: int, base_volume: float, efficiency_factor: float) -> float:
        """Исходная формула: cos(средней широты) · (эффективность / число ячеек) · объём."""
        c = self.calculate_cell_coordinates(cell_id)
        mid_lat = sum(c["lat_range"]) / 2.0
        norm = math.cos(math.radians(mid_lat)) * (efficiency_factor / self.total_cells)
        return round(base_volume * abs(norm), 4)

    def distribute(self, total_volume: float) -> dict[int, float]:
        """Разделить объём по всем ячейкам пропорционально площади (сумма = total_volume)."""
        return {i: total_volume * self.area_weight(i) for i in range(1, self.total_cells + 1)}


if __name__ == "__main__":
    g = GridAllocator()
    lat, lon = 46.97, 31.99  # Николаев
    cid = g.locate(lat, lon)
    print("Николаев → ячейка", cid, g.calculate_cell_coordinates(cid))
    print("Путь по вложенным сеткам:", g.locate_path(lat, lon, depth=3))
