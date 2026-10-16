"""main.py - จุดเริ่มต้นของโปรแกรม (CLI) สำหรับดึงข้อมูลจาก Web API"""
import sys

from src.api_client import APIClient

# ให้ภาษาไทยและอีโมจิแสดงผลถูกต้องบน Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SEPARATOR = "=" * 50
POST_PREVIEW_COUNT = 5
BODY_PREVIEW_LENGTH = 60


def display_menu() -> None:
    """แสดงเมนูหลัก"""
    print("\n" + SEPARATOR)
    print("   โปรแกรมดึงข้อมูลจาก Web API (JSONPlaceholder)")
    print(SEPARATOR)
    print("  1. ดึงรายการ TODO เดี่ยว (Fetch Single TODO)")
    print("  2. ดึงรายการโพสต์ทั้งหมด (Fetch All Posts)")
    print("  3. ดึงรายการ TODO ตามรหัสผู้ใช้ (Fetch User TODOs)")
    print("  4. ออกจากโปรแกรม (Exit)")
    print(SEPARATOR)


def read_positive_int(prompt: str) -> int | None:
    """อ่านเลขจำนวนเต็มบวกจากผู้ใช้ คืน None ถ้าไม่ถูกต้อง"""
    try:
        value = int(input(prompt).strip())
    except ValueError:
        print("[ERROR] กรุณากรอกเป็นตัวเลขเท่านั้น")
        return None
    if value <= 0:
        print("[ERROR] ต้องเป็นตัวเลขที่มากกว่า 0")
        return None
    return value


def handle_fetch_single_todo(client: APIClient) -> None:
    """เมนู 1: ดึง TODO รายการเดียว"""
    todo_id = read_positive_int("กรอกรหัส TODO (เช่น 1, 5, 10): ")
    if todo_id is None:
        return

    todo = client.fetch_single_todo(todo_id)
    if not todo:
        print(f"[ERROR] ไม่พบ TODO รหัส {todo_id}")
        return

    status = "เสร็จแล้ว ✅" if todo.get("completed") else "ยังไม่เสร็จ ⏳"
    print("\n--- รายละเอียด TODO ---")
    print(f"TODO ID      : {todo.get('id')}")
    print(f"User ID      : {todo.get('userId')}")
    print(f"หัวข้อ (Title): {todo.get('title')}")
    print(f"สถานะ        : {status} (completed = {todo.get('completed')})")
    print("-" * 50)


def handle_fetch_all_posts(client: APIClient) -> None:
    """เมนู 2: ดึงโพสต์ทั้งหมด แสดงแค่ 5 รายการแรก"""
    posts = client.fetch_all_posts()
    if not posts:
        print("[ERROR] ไม่สามารถดึงข้อมูลโพสต์ได้")
        return

    total = len(posts)
    print(f"\n📄 --- แสดง {POST_PREVIEW_COUNT} รายการแรก (จากทั้งหมด {total} รายการ) ---")
    for index, post in enumerate(posts[:POST_PREVIEW_COUNT], start=1):
        body = str(post.get("body", "")).replace("\n", " ")[:BODY_PREVIEW_LENGTH]
        print(f"\n[{index}] Post ID: {post.get('id')} | User ID: {post.get('userId')}")
        print(f"    หัวข้อ (Title): {post.get('title')}")
        print(f"    เนื้อหา (Body) : {body}...")

    remaining = total - POST_PREVIEW_COUNT
    if remaining > 0:
        print(f"\n... และยังมีอีก {remaining} โพสต์ที่ไม่ได้แสดงบนหน้าจอ")
    print("-" * 50)


def handle_fetch_user_todos(client: APIClient) -> None:
    """เมนู 3: ดึง TODO ทั้งหมดของผู้ใช้"""
    user_id = read_positive_int("กรอกรหัสผู้ใช้ User ID (เช่น 1, 2, 3): ")
    if user_id is None:
        return

    todos = client.fetch_user_todos(user_id)
    if todos is None:
        print(f"[ERROR] ไม่สามารถดึง TODO ของ User ID {user_id} ได้")
        return
    if not todos:
        print(f"ไม่พบ TODO ของ User ID {user_id}")
        return

    done = sum(1 for t in todos if t.get("completed"))
    print(f"\n📋 --- TODO ของ User ID {user_id} (ทั้งหมด {len(todos)} รายการ) ---")
    for todo in todos:
        icon = "✅" if todo.get("completed") else "⏳"
        print(f"{icon} [{todo.get('id'):>3}] {todo.get('title')}")
    print(f"\nสรุป: เสร็จแล้ว {done} | ยังไม่เสร็จ {len(todos) - done}")
    print("-" * 50)


def main() -> None:
    client = APIClient()
    handlers = {
        "1": handle_fetch_single_todo,
        "2": handle_fetch_all_posts,
        "3": handle_fetch_user_todos,
    }

    while True:
        display_menu()
        choice = input("กรุณาเลือกเมนู (1-4): ").strip()

        if choice == "4":
            print("ออกจากโปรแกรม ขอบคุณที่ใช้งาน 👋")
            break
        handler = handlers.get(choice)
        if handler:
            handler(client)
        else:
            print("[ERROR] เมนูไม่ถูกต้อง กรุณาเลือก 1-4")


if __name__ == "__main__":
    main()
