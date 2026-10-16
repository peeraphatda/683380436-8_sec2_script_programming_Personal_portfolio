# src/cli_interface.py
# UI only: all print() / input() live here. Business logic is in TaskManager.
import datetime


class CLIInterface:
    def __init__(self, task_manager):
        self.manager = task_manager

    # ---------- display ----------
    def display_menu(self):
        print("\n" + "=" * 46)
        print("     Enhanced Task Manager (Week 11)")
        print("=" * 46)
        print("1. เพิ่มงานทั่วไป (Add Normal Task)")
        print("2. เพิ่มงานที่มีวันครบกำหนด (Add Due Date Task)")
        print("3. เพิ่มงานที่มีระดับความสำคัญ (Add Priority Task)")
        print("4. แสดงรายการงานทั้งหมด (List All Tasks)")
        print("5. เปลี่ยนสถานะงานเป็นเสร็จสิ้น (Complete Task)")
        print("6. ลบงาน (Delete Task)")
        print("7. ค้นหางาน (Search Tasks)")
        print("8. กรองงาน (Filter Tasks)")
        print("9. เรียงลำดับงาน (Sort Tasks)")
        print("0. ออกจากโปรแกรม (Exit)")
        print("-" * 46)

    def show_tasks(self, tasks, title):
        if not tasks:
            print(f"\nไม่พบงาน (No tasks found) - {title}")
            return
        print(f"\n--- {title} ({len(tasks)} รายการ) ---")
        for t in tasks:
            print(f"- {t}")

    # ---------- input helpers ----------
    def get_user_choice(self):
        return input("เลือกเมนู (0-9): ").strip()

    def get_task_description(self):
        while True:
            d = input("กรอกรายละเอียดงาน (Description): ").strip()
            if d:
                return d
            print("ข้อผิดพลาด: รายละเอียดงานต้องไม่เป็นค่าว่าง กรุณาลองใหม่อีกครั้ง")

    def get_due_date_input(self):
        while True:
            s = input("กรอกวันครบกำหนด (YYYY-MM-DD เช่น 2024-12-31): ").strip()
            try:
                datetime.datetime.strptime(s, '%Y-%m-%d')
                return s
            except ValueError:
                print("ข้อผิดพลาด: รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD")

    def get_optional_date(self, prompt):
        """วันที่แบบเว้นว่างได้ (Enter = ข้าม)"""
        while True:
            s = input(prompt).strip()
            if not s:
                return None
            try:
                datetime.datetime.strptime(s, '%Y-%m-%d')
                return s
            except ValueError:
                print("ข้อผิดพลาด: รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD หรือกด Enter เพื่อข้าม")

    def get_priority_input(self):
        while True:
            p = input("กรอกระดับความสำคัญ (High/Medium/Low): ").strip().capitalize()
            if p in ("High", "Medium", "Low"):
                return p
            print("ข้อผิดพลาด: กรุณากรอก High, Medium หรือ Low")

    def get_optional_priority(self):
        while True:
            p = input("ระดับความสำคัญ (High/Medium/Low, Enter = ข้าม): ").strip().capitalize()
            if p == "" :
                return None
            if p in ("High", "Medium", "Low"):
                return p
            print("ข้อผิดพลาด: กรุณากรอก High, Medium, Low หรือกด Enter เพื่อข้าม")

    def get_tags_input(self):
        s = input("กรอกป้ายกำกับ (Tags คั่นด้วยจุลภาค เช่น work,urgent,home - หรือว่างไว้): ").strip()
        return [t.strip() for t in s.split(',') if t.strip()]

    def get_task_id(self, prompt):
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("ข้อผิดพลาด: กรุณากรอก ID เป็นตัวเลข")
            return None

    # ---------- feature handlers ----------
    def handle_search(self):
        keyword = input("กรอกคำค้นหา (ค้นใน description และ tags): ").strip()
        if not keyword:
            print("ข้อผิดพลาด: ต้องกรอกคำค้นหา")
            return
        self.show_tasks(self.manager.search_tasks(keyword), f"ผลการค้นหา '{keyword}'")

    def handle_filter(self):
        print("\n--- กรองงาน (กด Enter เพื่อข้ามเงื่อนไขที่ไม่ต้องการ) ---")
        s = input("สถานะ (1=เสร็จแล้ว, 2=ยังไม่เสร็จ, Enter=ทั้งหมด): ").strip()
        status = {"1": True, "2": False}.get(s)
        due_before = self.get_optional_date("ครบกำหนดก่อนหรือเท่ากับวันที่ (YYYY-MM-DD): ")
        due_after = self.get_optional_date("ครบกำหนดตั้งแต่วันที่ (YYYY-MM-DD): ")
        priority = self.get_optional_priority()
        tag = input("Tag ที่ต้องการ (Enter = ข้าม): ").strip() or None

        results = self.manager.filter_tasks(
            status=status, due_before=due_before, due_after=due_after, priority=priority, tag=tag
        )
        self.show_tasks(results, "ผลการกรอง")

    def handle_sort(self):
        print("เรียงตาม: id, due_date, priority, status, description")
        criterion = input("เลือกเกณฑ์ (ค่าเริ่มต้น: id): ").strip().lower() or "id"
        reverse = input("เรียงย้อนกลับ? (yes/no, ค่าเริ่มต้น: no): ").strip().lower() == "yes"
        try:
            tasks = self.manager.sort_tasks(criterion, reverse)
        except ValueError:
            print("ข้อผิดพลาด: ไม่รู้จักเกณฑ์การเรียง")
            return
        self.show_tasks(tasks, f"เรียงตาม {criterion}{' (ย้อนกลับ)' if reverse else ''}")

    # ---------- main loop ----------
    def run(self):
        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice == '1':
                desc = self.get_task_description()
                t = self.manager.add_normal_task(desc, tags=self.get_tags_input())
                print(f"[สำเร็จ]: เพิ่มงานทั่วไป ID {t.id} เรียบร้อยแล้ว")
            elif choice == '2':
                desc = self.get_task_description()
                due = self.get_due_date_input()
                t = self.manager.add_due_date_task(desc, due, tags=self.get_tags_input())
                print(f"[สำเร็จ]: เพิ่มงานครบกำหนด ID {t.id} (ครบกำหนด: {t.due_date}) เรียบร้อยแล้ว")
            elif choice == '3':
                desc = self.get_task_description()
                pr = self.get_priority_input()
                t = self.manager.add_priority_task(desc, pr, tags=self.get_tags_input())
                print(f"[สำเร็จ]: เพิ่มงานสำคัญ ID {t.id} (Priority: {t.priority}) เรียบร้อยแล้ว")
            elif choice == '4':
                self.show_tasks(self.manager.get_all_tasks(), "รายการงานทั้งหมด")
            elif choice == '5':
                tid = self.get_task_id("กรอก ID ของงานที่เสร็จสิ้น: ")
                if tid is not None:
                    print(self.manager.complete_task(tid)[1])
            elif choice == '6':
                tid = self.get_task_id("กรอก ID ของงานที่ต้องการลบ: ")
                if tid is not None:
                    print(self.manager.delete_task(tid)[1])
            elif choice == '7':
                self.handle_search()
            elif choice == '8':
                self.handle_filter()
            elif choice == '9':
                self.handle_sort()
            elif choice == '0':
                print("ออกจากโปรแกรม ขอบคุณที่ใช้งาน!")
                break
            else:
                print("ตัวเลือกไม่ถูกต้อง กรุณาเลือก 0-9")
