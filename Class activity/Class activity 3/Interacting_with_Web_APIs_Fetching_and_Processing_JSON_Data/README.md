# My API Data Fetcher CLI (Week 10)

โปรแกรม CLI สำหรับดึงและประมวลผลข้อมูล JSON จาก [JSONPlaceholder](https://jsonplaceholder.typicode.com/) ด้วยไลบรารี `requests`

## ฟีเจอร์
1. **Fetch Single TODO** – ดึง TODO รายการเดียวตาม ID (`/todos/{id}`)
2. **Fetch All Posts** – ดึงโพสต์ทั้งหมด (`/posts`) แสดง 5 รายการแรก
3. **Fetch TODOs by User ID** – ดึง TODO ตามผู้ใช้ (`/todos?userId={id}`)
4. จัดการ error: HTTPError, ConnectionError, Timeout, JSONDecodeError

## วิธีรัน
```bash
git clone https://github.com/YOUR_USERNAME/my-api-fetcher.git
cd my-api-fetcher
pip install -r requirements.txt
python main.py
```

## โครงสร้างโปรเจกต์
```
my-api-fetcher/
├── src/
│   ├── __init__.py
│   └── api_client.py   # ติดต่อ API
├── main.py             # CLI เมนูหลัก
├── requirements.txt
├── .gitignore
└── README.md
```
