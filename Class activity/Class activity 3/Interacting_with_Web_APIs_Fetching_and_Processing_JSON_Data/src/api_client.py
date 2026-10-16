"""api_client.py - ตัวกลางติดต่อกับ JSONPlaceholder API"""
import json
from typing import Any, Optional

import requests


class APIClient:
    """Client สำหรับเรียกใช้ JSONPlaceholder API"""

    BASE_URL = "https://jsonplaceholder.typicode.com"
    TIMEOUT = 10  # วินาที

    def _make_request(self, endpoint: str) -> Optional[Any]:
        """ส่ง GET request ไปที่ endpoint คืนค่า JSON ที่แปลงแล้ว หรือ None ถ้าล้มเหลว"""
        url = f"{self.BASE_URL}{endpoint}"
        print(f"[INFO] กำลังส่งคำขอ (GET) ไปที่: {url}")
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()  # 4xx / 5xx -> HTTPError
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"[ERROR] HTTP Error: {err}")
        except requests.exceptions.ConnectionError as err:
            print(f"[ERROR] เชื่อมต่อเซิร์ฟเวอร์ไม่ได้: {err}")
        except requests.exceptions.Timeout as err:
            print(f"[ERROR] หมดเวลารอการตอบกลับ: {err}")
        except requests.exceptions.RequestException as err:
            print(f"[ERROR] เกิดข้อผิดพลาดที่ไม่คาดคิด: {err}")
        except json.JSONDecodeError:
            print("[ERROR] ไม่สามารถแปลงข้อมูลตอบกลับเป็น JSON ได้")
        return None

    def fetch_single_todo(self, todo_id: int) -> Optional[dict]:
        """ดึง TODO รายการเดียวตาม ID"""
        return self._make_request(f"/todos/{todo_id}")

    def fetch_all_posts(self) -> Optional[list]:
        """ดึงโพสต์ทั้งหมด"""
        return self._make_request("/posts")

    def fetch_user_todos(self, user_id: int) -> Optional[list]:
        """ดึง TODO ทั้งหมดของผู้ใช้ตาม User ID"""
        return self._make_request(f"/todos?userId={user_id}")
