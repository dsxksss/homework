import json
import os
import questionary
from tqdm import tqdm
from enum import Enum
from colorama import Fore, Style


class Answer(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Options:
    def __init__(self, option1, option2, option3, option4):
        self.options1 = option1
        self.options2 = option2
        self.options3 = option3
        self.options4 = option4


class Topic:
    def __init__(self, title: str, options: Options, answer: Answer):
        self.title = title
        self.options = options
        self.answer = answer


class ExamSystem:
    @staticmethod
    def run():
        instance = ExamSystem()
        instance.check_dir_exists()
        instance.show_ui()

    def __init__(self):
        self.work_path = os.getcwd()
        self.storage_dir = os.path.join(self.work_path, "题库目录")
        self.storage_path = os.path.join(self.storage_dir, "题库.json")
        self.topic_reader_cache: list[Topic] = []
        self.topic_writer_cache: list[Topic] = []

    def check_dir_exists(self):
        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)
            open(self.storage_path, "w", encoding="utf-8")
        elif not os.path.exists(self.storage_path):
            open(self.storage_path, "w", encoding="utf-8")

    def read_data(self):
        with open(self.storage_path, "r", encoding="utf-8") as r:
            self.topic_reader_cache = json.load(r)

    def write_data(self):
        with open(self.storage_path, "+a", encoding="utf-8") as w:
            for topic in tqdm(
                self.topic_writer_cache, total=len(self.topic_writer_cache)
            ):
                data = {
                    "题干": topic.title,
                    "备选答案": {},# TODO add
                    "正确答案": topic.answer,
                }
                print(data)
                json.dump(data, w)
        print(Fore.RED + "录入成功!" + Style.RESET_ALL)

    def add_topic(self):
        title = questionary.text("题干: ").ask()
        option1 = questionary.text("选项A: ").ask()
        option2 = questionary.text("选项B: ").ask()
        option3 = questionary.text("选项C: ").ask()
        option4 = questionary.text("选项D: ").ask()
        answer = questionary.select(
            "正确答案为选项几: ",
            [
                Answer.A.value,
                Answer.B.value,
                Answer.C.value,
                Answer.D.value,
            ],
        ).ask()
        options = Options(option1, option2, option3, option4)
        topic = Topic(title=title, options=options, answer=answer)
        self.topic_writer_cache.append(topic)
        self.write_data()

    def show_topic(self):
        count = questionary.text("请输入题目数量: ").ask()
        pass

    def show_ui(self):
        menu_options: dict = {
            "答题": self.show_topic,
            "试题录入": self.add_topic,
            "退出程序": exit,
        }
        selected = questionary.select("请选择功能(键盘上下方向键选择,按回车确定): ", menu_options).ask()  # type: ignore
        menu_options[selected]()


def main():
    try:
        ExamSystem().run()

    except Exception as e:
        print(f"程序崩溃,发生异常:{e}")


if __name__ == "__main__":
    main()
