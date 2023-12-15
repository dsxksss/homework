# 导入redis模块，用于与Redis数据库进行交互
import redis

# 导入questionary模块，用于在命令行中进行交互式输入
import questionary

# 导入datetime模块，用于处理日期和时间
from datetime import datetime


# 定义一个学生类
class Student:
    def __init__(self, id, class_, name, start_time, end_time):
        # 学生学号
        self.id = id

        # 班级
        self.class_ = class_

        # 姓名
        self.name = name

        # 上机开始时间
        self.start_time = start_time

        # 上机结束时间
        self.end_time = end_time


# 定义一个机房类
class ComputerLab:
    def __init__(self, charge_rate):
        # 学生列表
        self.students = []

        # 上机费用计费率
        self.charge_rate = charge_rate

        # 连接Redis数据库
        self.db = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)

        # 从Redis数据库中读取已经添加的学生信息
        for key in self.db.keys():
            student_dict = eval(self.db.get(key))
            student = Student(**student_dict)
            self.students.append(student)

    def add_student(self, student):
        self.students.append(student)  # 将学生添加到学生列表中

        # 将学生信息存储到Redis数据库中
        self.db.set(student.id, str(student.__dict__))

        print("添加学生信息成功")

    def remove_student(self, id):
        for student in self.students:
            if student.id == id:
                self.students.remove(student)  # 从学生列表中移除学生

                self.db.delete(id)  # 从Redis数据库中删除学生信息
                return True

        return False

    def calculate_fee(self, id):
        for student in self.students:
            if student.id == id:
                time_diff = datetime.strptime(
                    student.end_time, "%Y-%m-%d %H:%M:%S"
                ) - datetime.strptime(student.start_time, "%Y-%m-%d %H:%M:%S")

                fee = time_diff.total_seconds() / 60 * self.charge_rate  # 计算上机费用

                return fee
        return 0.0

    def search_student(self, id=None, class_=None, name=None):
        for student in self.students:
            if (
                (id and student.id == id)
                or (class_ and student.class_ == class_)
                or (name and student.name == name)
            ):
                # 返回符合条件的学生信息
                return f"学生学号:{student.__dict__['id']}\n所在班级:{student.__dict__['class_']}\n上机时间:{student.__dict__['start_time']}\n下机时间:{student.__dict__['end_time']}\n"
        return "不存在该学生!"


# 主函数
def main():
    # 创建一个机房对象
    lab = ComputerLab(0.1)
    while True:
        action = questionary.select(
            # 提示用户选择操作
            "请在菜单中选择要运行的功能",
            choices=[
                "1、添加学生信息",
                "2、删除学生信息",
                "3、计算学生上机费用",
                "4、搜索学生上机信息",
                "5、退出程序",
            ],
        ).ask()

        if action == "1、添加学生信息":
            id = questionary.text("请输入学生学号:").ask()
            class_ = questionary.text("请输入班级:").ask()
            name = questionary.text("请输入姓名:").ask()
            start_time = questionary.text("请输入上机开始时间 (格式: YYYY-MM-DD HH:MM:SS):").ask()
            end_time = questionary.text("请输入上机结束时间 (格式: YYYY-MM-DD HH:MM:SS):").ask()
            student = Student(id, class_, name, start_time, end_time)
            lab.add_student(student)

        elif action == "2、删除学生信息":
            id = questionary.text("请输入学生学号:").ask()
            lab.remove_student(id)

        elif action == "3、计算学生上机费用":
            id = questionary.text("请输入学生学号:").ask()
            print("该学生上机的费用是:%.2f" % (lab.calculate_fee(id)))

        elif action == "4、搜索学生上机信息":
            id = questionary.text("请输入学生学号:").ask()
            print(lab.search_student(id))

        elif action == "5、退出程序":
            break


if __name__ == "__main__":
    try:
        main()  # 运行主函数
    except Exception as e:
        print(f"发生异常:{e}")
