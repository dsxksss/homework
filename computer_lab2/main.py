import pymongo
from datetime import datetime


# 定义学生类
class Student:
    def __init__(self, student_id, class_name, name, start_time, end_time):
        self.student_id = student_id
        self.class_name = class_name
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.charge = 0

    def calculate_charge(self, rate):
        duration = (self.end_time - self.start_time).total_seconds() / 60
        self.charge = duration * rate


# 定义数据库类
class Database:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["machine_room"]
        self.collection = self.db["students"]

    def insert_student(self, student):
        student_dict = {
            "student_id": student.student_id,
            "class_name": student.class_name,
            "name": student.name,
            "start_time": student.start_time,
            "end_time": student.end_time,
            "charge": student.charge,
        }
        self.collection.insert_one(student_dict)

    def update_student(self, student_id, update_dict):
        self.collection.update_one({"student_id": student_id}, {"$set": update_dict})

    def delete_student(self, student_id):
        self.collection.delete_one({"student_id": student_id})

    def search_student(self, query_dict):
        result = self.collection.find(query_dict)
        for student_dict in result:
            student = Student(
                student_dict["student_id"],
                student_dict["class_name"],
                student_dict["name"],
                student_dict["start_time"],
                student_dict["end_time"],
            )
            student.charge = student_dict["charge"]
            yield student


# 定义菜单类
class Menu:
    def __init__(self):
        self.db = Database()

        # 收费标准设置
        self.rate = 0.1

    def display_menu(self):
        print("*" * 26)
        print("**", "机房收费管理系统\t**".center(18), sep="")
        print("**", "1. 输入学生信息\t**".center(18), sep="")
        print("**", "2. 计算上机费用\t**".center(18), sep="")
        print("**", "3. 修改学生信息\t**".center(18), sep="")
        print("**", "4. 查询学生信息\t**".center(18), sep="")
        print("**", "5. 退出系统\t**".center(16), sep="")
        print("*" * 26)

    def input_student_info(self):
        student_id = input("请输入学生学号：")
        class_name = input("请输入学生班级：")
        name = input("请输入学生姓名：")
        start_time_str = input("请输入开始上机时间（格式为年-月-日 时:分:秒）：")
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        end_time_str = input("请输入结束上机时间（格式为年-月-日 时:分:秒）：")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        student = Student(student_id, class_name, name, start_time, end_time)
        self.db.insert_student(student)
        print("学生信息已保存！")

    def calculate_charge(self):
        for student in self.db.search_student({}):
            student.calculate_charge(self.rate)
            self.db.update_student(student.student_id, {"charge": student.charge})
            print(f"{student.name}的上机费用为%.2f元" % (student.charge))

    def update_student_info(self):
        student_id = input("请输入要修改的学生学号：")
        update_dict = {}
        while True:
            print("请选择要修改的信息：")
            print("1. 班级")
            print("2. 姓名")
            print("3. 开始上机时间")
            print("4. 结束上机时间")
            print("5. 完成修改")
            choice = input("请输入选项：")
            if choice == "1":
                class_name = input("请输入班级：")
                update_dict["class_name"] = class_name
            elif choice == "2":
                name = input("请输入姓名：")
                update_dict["name"] = name
            elif choice == "3":
                start_time_str = input("请输入开始上机时间（格式为年-月-日 时:分:秒）：")
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                update_dict["start_time"] = start_time
            elif choice == "4":
                end_time_str = input("请输入结束上机时间（格式为年-月-日 时:分:秒）：")
                end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                update_dict["end_time"] = end_time
            elif choice == "5":
                break
            else:
                print("无效选项！")
        self.db.update_student(student_id, update_dict)
        print("学生信息已更新！")

    def search_student_info(self):
        query_dict = {}
        while True:
            print("请选择查询条件：")
            print("1. 班级")
            print("2. 学号")
            print("3. 姓名")
            print("4. 完成查询")
            choice = input("请输入选项：")
            if choice == "1":
                class_name = input("请输入班级：")
                query_dict["class_name"] = class_name
            elif choice == "2":
                student_id = input("请输入学号：")
                query_dict["student_id"] = student_id
            elif choice == "3":
                name = input("请输入姓名：")
                query_dict["name"] = name
            elif choice == "4":
                break
            else:
                print("无效选项！")
        for student in self.db.search_student(query_dict):
            print("-" * 40)
            print(
f"""学号：{student.student_id}
班级：{student.class_name}
姓名：{student.name}
开始上机时间：{student.start_time}
结束上机时间：{student.end_time}
上机费用：%.2f元"""
% (student.charge)
            )
            print("-" * 40)

    def run(self):
        while True:
            self.display_menu()
            choice = input("请输入选项：")
            if choice == "1":
                self.input_student_info()
            elif choice == "2":
                self.calculate_charge()
            elif choice == "3":
                self.update_student_info()
            elif choice == "4":
                self.search_student_info()
            elif choice == "5":
                print("感谢使用！")
                break
            else:
                print("无效选项！")


# 主程序入口
if __name__ == "__main__":
    menu = Menu()
    menu.run()
