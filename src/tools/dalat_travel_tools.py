"""
Mock travel tools for Đà Lạt lab scenario (hotel + weather + reviews).
Data matches the instructor-style trace for reproducible demos.
"""
from __future__ import annotations

from typing import Any, Dict, List


import requests

def get_weather(city: str, date: str) -> str:
    try:
        # 1. Gọi Nominatim API để lấy tọa độ thực tế (Geocoding)
        geo_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        geo_res = requests.get(geo_url, headers={"User-Agent": "Day3LabAgent/1.0"}, timeout=5)
        if geo_res.status_code != 200 or not geo_res.json():
            return f"Không tìm thấy tọa độ thực cho {city}."
        
        lat = geo_res.json()[0]["lat"]
        lon = geo_res.json()[0]["lon"]
        
        # 2. Gọi Open-Meteo API để lấy thời tiết theo tọa độ
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto&start_date={date}&end_date={date}"
        w_res = requests.get(w_url, timeout=5)
        if w_res.status_code == 200:
            data = w_res.json()
            if "daily" in data and data["daily"]["time"]:
                t_max = data["daily"]["temperature_2m_max"][0]
                t_min = data["daily"]["temperature_2m_min"][0]
                precip = data["daily"]["precipitation_sum"][0]
                return f"[DỮ LIỆU THẬT] Thời tiết {city} ngày {date}: Tối thiểu {t_min}°C, Tối đa {t_max}°C. Lượng mưa: {precip}mm."
            else:
                return f"Ngày {date} nằm ngoài phạm vi hỗ trợ dự báo miễn phí của API Open-Meteo."
        return f"Lỗi Open-Meteo API: HTTP {w_res.status_code}"
    except Exception as e:
        return f"Không thể kết nối API thời tiết. Lỗi: {str(e)}"


def search_hotels(city: str, check_in: str, check_out: str, max_price: int) -> str:
    c = city.lower()
    if "da lat" not in c and "dalat" not in c and "đà lạt" not in city.lower():
        return f"Không có inventory demo cho {city}."
    lines = [
        "[1] Ngọc Lan Hotel - 650000 VND/đêm - còn phòng (hotel_id: ngoc_lan_hotel)",
        "[2] Mimosa Boutique - 750000 VND/đêm - còn phòng (hotel_id: mimosa_boutique)",
        "[3] Sapa Lodge - 820000 VND/đêm - vượt ngân sách (hotel_id: sapa_lodge)",
        f"(check_in={check_in}, check_out={check_out}, max_price={max_price} VND)",
    ]
    return "\n".join(lines)


def get_hotel_reviews(hotel_id: str) -> str:
    hid = hotel_id.strip().lower().replace(" ", "_")
    if hid in ("ngoc_lan_hotel", "ngoc_lan", "1"):
        return (
            "Rating 4.5/5 - 320 đánh giá - Gần chợ Đà Lạt - "
            "Điểm nổi bật: sạch sẽ, view đẹp, có bãi đỗ xe."
        )
    if hid in ("mimosa_boutique", "mimosa", "2"):
        return "Rating 4.2/5 - 180 đánh giá - Yên tĩnh, decor boutique, bữa sáng ổn."
    if hid in ("sapa_lodge", "sapa", "3"):
        return "Rating 4.0/5 - 95 đánh giá - Note: listing name gây nhầm; giá thường >800k."
    return f"Không có review demo cho hotel_id={hotel_id}."


def get_tool_specs_dalat() -> List[Dict[str, Any]]:
    return [
        {
            "name": "get_weather",
            "description": (
                "Lấy dự báo thời tiết (demo). Tham số: city (tên thành phố, ví dụ 'Da Lat'), "
                "date (YYYY-MM-DD). Dùng trước khi gợi ý trang phục."
            ),
            "uses_kwargs": True,
            "run": get_weather,
        },
        {
            "name": "search_hotels",
            "description": (
                "Tìm phòng khách sạn (demo). Tham số: city, check_in (YYYY-MM-DD), "
                "check_out (YYYY-MM-DD), max_price (số VND/ngày, integer). "
                "Trả về danh sách có hotel_id để gọi get_hotel_reviews."
            ),
            "uses_kwargs": True,
            "run": search_hotels,
        },
        {
            "name": "get_hotel_reviews",
            "description": (
                "Lấy đánh giá tóm tắt (demo). Tham số: hotel_id (string, ví dụ 'ngoc_lan_hotel')."
            ),
            "uses_kwargs": True,
            "run": get_hotel_reviews,
        },
    ]
