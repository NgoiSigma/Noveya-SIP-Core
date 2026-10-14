"""Ортогональная сетка динамического квантования геоида НОВЕЯ.
Базовая матрица: 12 широтных × 12 долготных зон = 144 ячейки верхнего уровня.

Включает рекурсивный затвор локализации (глубина по умолчанию depth=3) и модуль 
динамического нормирования ресурсов на основе геодезических коэффициентов и градиента EROI.
"""
from __future__ import annotations

import json
import math


class GridAllocator:
    def __init__(self, lat_zones: int = 12, lon_zones: int = 12, default_depth: int = 3):
        self.lat_zones = lat_zones
        self.lon_zones = lon_zones
        self.total_cells = lat_zones * lon_zones
        self.default_depth = default_depth

    def calculate_cell_coordinates(self, cell_id: int) -> dict:
        if not (1 <= cell_id <= self.total_cells):
            raise ValueError(f"Идентификатор ячейки должен быть в диапазоне от 1 до {self.total_cells}.")
        idx = cell_id - 1
        lat_i, lon_i = divmod(idx, self.lon_zones)
        dlat, dlon = 180.0 / self.lat_zones, 360.0 / self.lon_zones
        lat0, lon0 = -90.0 + lat_i * dlat, -180.0 + lon_i * dlon
        return {
            "cell_id": cell_id,
            "lat_range": (round(lat0, 4), round(lat0 + dlat, 4)),
            "lon_range": (round(lon0, 4), round(lon0 + dlon, 4))
        }

    def center(self, cell_id: int) -> tuple[float, float]:
        c = self.calculate_cell_coordinates(cell_id)
        return (sum(c["lat_range"]) / 2.0, sum(c["lon_range"]) / 2.0)

    def _get_base_cell(self, lat: float, lon: float) -> int:
        """Внутренний метод валидации и определения базовой ячейки (1..144)."""
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            raise ValueError("Координаты вне лимитов: lat в [-90, 90], lon в [-180, 180]")
        lat_i = min(int((lat + 90.0) // (180.0 / self.lat_zones)), self.lat_zones - 1)
        lon_i = min(int((lon + 180.0) // (360.0 / self.lon_zones)), self.lon_zones - 1)
        return lat_i * self.lon_zones + lon_i + 1

    def locate(self, lat: float, lon: float) -> dict:
        """Возвращает полный системный контекст локализации с учетом вложенности."""
        path = self.locate_path(lat, lon, depth=self.default_depth)
        base_cell = path[0]
        coords = self.calculate_cell_coordinates(base_cell)
        
        return {
            "requested_coords": (lat, lon),
            "base_cell_id": base_cell,
            "hierarchical_path": path,
            "lat_range": coords["lat_range"],
            "lon_range": coords["lon_range"],
            "local_eroi_gradient": self.calculate_local_eroi_gradient(lat, lon, path)
        }

    def locate_path(self, lat: float, lon: float, depth: int | None = None) -> list[int]:
        """Путь по вложенным сеткам 12×12: [ячейка верхнего уровня, подъячейка, под-подъячейка]."""
        current_depth = depth if depth is not None else self.default_depth
        if current_depth < 1:
            raise ValueError("Глубина деления depth должна быть >= 1")
        
        self._get_base_cell(lat, lon)  # Валидация координат
        lat0, lat1, lon0, lon1 = -90.0, 90.0, -180.0, 180.0
        path = []
        
        for _ in range(current_depth):
            dlat, dlon = (lat1 - lat0) / self.lat_zones, (lon1 - lon0) / self.lon_zones
            lat_i = min(int((lat - lat0) // dlat), self.lat_zones - 1)
            lon_i = min(int((lon - lon0) // dlon), self.lon_zones - 1)
            path.append(lat_i * self.lon_zones + lon_i + 1)
            lat0, lat1 = lat0 + lat_i * dlat, lat0 + (lat_i + 1) * dlat
            lon0, lon1 = lon0 + lon_i * dlon, lon0 + (lon_i + 1) * dlon
            
        return path

    def neighbors(self, cell_id: int) -> list[int]:
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
        c = self.calculate_cell_coordinates(cell_id)
        s0, s1 = (math.sin(math.radians(x)) for x in c["lat_range"])
        return (s1 - s0) / 2.0 * (360.0 / self.lon_zones) / 360.0

    def calculate_local_eroi_gradient(self, lat: float, lon: float, path: list[int]) -> float:
        """Вычисляет градиент падения энергетической рентабельности на основе вложенности.
        Используется как связующий коэффициент для CyclesSynchronizer.
        """
        # Эвристика НОВЕЯ: плотность вложенного адреса ячейки как маркер инфраструктурной нагрузки
        # Николаев (ячейка 116 -> путь) генерирует локальный коэффициент трения
        harmonic_sum = sum([math.sin(p / 144.0) for p in path])
        gradient = abs(math.cos(lat) * math.sin(lon) * harmonic_sum) % 0.4
        return round(gradient, 4)

    # --- Динамическое нормирование ресурсов ---
    def allocate_resource_by_geometry(self, cell_id: int, base_volume: float, 
                                     efficiency_factor: float, eroi_gradient: float = 0.0) -> float:
        """Формула динамического затвора НОВЕЯ:
        Ресурс распределяется пропорционально косинусу широты, но урезается/корректируется 
        в зависимости от локального градиента деградации EROI ячейки.
        """
        c = self.calculate_cell_coordinates(cell_id)
        mid_lat = sum(c["lat_range"]) / 2.0
        
        # Корректирующий коэффициент затвора: падение EROI сжимает норму прямого распределения
        gate_factor = 1.0 - eroi_gradient
        norm = math.cos(math.radians(mid_lat)) * (efficiency_factor / self.total_cells) * gate_factor
        
        return round(base_volume * abs(norm), 4)

    def distribute(self, total_volume: float) -> dict[int, float]:
        return {i: total_volume * self.area_weight(i) for i in range(1, self.total_cells + 1)}


if __name__ == "__main__":
    g = GridAllocator(default_depth=3)
    lat, lon = 46.97, 31.99  # Николаев
    
    # Получение полного системного контекста для Николаева
    context = g.locate(lat, lon)
    print("Контекст локализации узла НОВЕЯ:")
    print(json.dumps(context, ensure_ascii=False, indent=2))
    
    # Расчет динамической нормы ресурса с учетом вычисленного градиента EROI
    allocated = g.allocate_resource_by_geometry(
        cell_id=context["base_cell_id"], 
        base_volume=10000.0, 
        efficiency_factor=0.85, 
        eroi_gradient=context["local_eroi_gradient"]
    )
    print(f"\nДинамическая норма распределения ресурса для ячейки {context['base_cell_id']}: {allocated} единиц.")
