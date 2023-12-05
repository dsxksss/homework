import redis
import json

# 连接到本地Redis服务器
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


class Student:
    def __init__(self, student_id, major, class_name, name):
        self.student_id = student_id
        self.major = major
        self.class_name = class_name
        self.name = name


class Teacher:
    def __init__(self, personnel_id, name, department):
        self.personnel_id = personnel_id
        self.name = name
        self.department = department


class Topic:
    def __init__(self, teacher, title):
        self.teacher = teacher
        self.title = title


class TopicSystem:
    def __init__(self):
        self.topics = []
        self.students = []
        self.teachers = []
        self.selections = {}

    def menu(self):
        while True:
            print("\n毕业生选题系统菜单：")
            print("1. 课题信息录入")
            print("2. 课题信息浏览")
            print("3. 选题")
            print("4. 选题结果查看")
            print("5. 退出")
            choice = input("请选择一个选项: ")
            if choice == "1":
                self.add_topic()
            elif choice == "2":
                self.view_topics()
            elif choice == "3":
                self.select_topic()
            elif choice == "4":
                self.view_selections()
            elif choice == "5":
                print("退出系统。")
                break
            else:
                print("无效的选项，请重新选择。")

    def add_topic(self):
        teacher_name = input("请输入指导教师姓名: ")
        title = input("请输入题目名称: ")
        topic = Topic(teacher_name, title)
        self.topics.append(topic)
        # 将课题信息保存到Redis
        redis_client.set(
            f"topic:{title}", json.dumps({"teacher": teacher_name, "title": title})
        )
        print("课题信息已录入。")

    def view_topics(self):
        for topic in self.topics:
            print(f"题目名称: {topic.title}, 指导教师: {topic.teacher}")

    def select_topic(self):
        student_id = input("请输入学号: ")
        title = input("请输入要选择的题目名称: ")
        # 检查是否存在该题目
        if redis_client.exists(f"topic:{title}"):
            self.selections[student_id] = title
            # 将选题结果保存到Redis
            redis_client.set(f"selection:{student_id}", title)
            print("选题成功。")
        else:
            print("选题失败，题目不存在。")

    def view_selections(self):
        search_type = input("按题目查询请输入1，按指导老师查询请输入2: ")
        if search_type == "1":
            title = input("请输入题目名称: ")
            for student_id, selected_title in self.selections.items():
                if selected_title == title:
                    print(f"学号: {student_id}, 选题: {selected_title}")
        elif search_type == "2":
            teacher_name = input("请输入指导教师姓名: ")
            for student_id, selected_title in self.selections.items():
                topic_info = json.loads(redis_client.get(f"topic:{selected_title}"))
                if topic_info["teacher"] == teacher_name:
                    print(f"学号: {student_id}, 选题: {selected_title}")
        else:
            print("无效的查询方式。")


# 实例化选题系统并启动菜单
topic_system = TopicSystem()
topic_system.menu()
