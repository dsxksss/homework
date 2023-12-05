import os
import random
import json
import redis
import questionary
from enum import Enum
from colorama import Fore, Style


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


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

    def __dict__(self) -> dict:
        return {
            "题干": self.title,
            "备选答案": {
                "A": self.options.options1,
                "B": self.options.options2,
                "C": self.options.options3,
                "D": self.options.options4,
            },
            "正确答案": self.answer,
        }


class ExamSystem:
    @staticmethod
    def run():
        instance = ExamSystem()
        instance.read_data()
        instance.show_ui()

    def __init__(self):
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.redis_db = 0
        self.redis_key = "题库"
        self.topic_reader_cache = []
        self.topic_writer_cache: list[Topic] = []
        self.wrong_answers = []
        self.right_answer_count = 0
        self.check_redis_connection()

    def check_redis_connection(self):
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True,
            )
            self.redis_client.ping()
        except redis.ConnectionError:
            print("无法连接到Redis数据库,请确保Redis已启动并正确配置连接信息。")
            exit()

    def read_data(self):
        data = self.redis_client.lrange(self.redis_key, 0, -1)
        if data:
            for item in data:  # type: ignore
                self.topic_reader_cache.append(json.loads(item))

    def write_data(self):
        for item in self.topic_writer_cache:
            self.redis_client.rpush(
                self.redis_key, json.dumps(item.__dict__(), ensure_ascii=False)
            )
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

        is_continue = questionary.confirm("是否继续添加题目").ask()
        if is_continue:
            self.add_topic()
        else:
            self.write_data()

    def input_topic_count(self) -> int:
        max_topic_length = len(self.topic_reader_cache)
        if max_topic_length <= 0:
            print(Fore.RED + "题目数量不足足,请添加题目后重新选择!" + Style.RESET_ALL)
            exit(0)
        try:
            count = questionary.text(f"请输入题目数量(总题目数量{max_topic_length}): ").ask()
            count = int(count)
            if count > max_topic_length:
                print(Fore.RED + "题目数量不足足,请重新选择!" + Style.RESET_ALL)
                return self.input_topic_count()
            else:
                return count
        except:
            print("题目数量应该是数字,请输入数字!")
            return self.input_topic_count()

    def show_exam(self):
        selected_count = self.input_topic_count()
        random.shuffle(self.topic_reader_cache)
        for topic in self.topic_reader_cache[0:selected_count]:
            clear_terminal()
            print("题目:\t" + Fore.YELLOW + f"{topic['题干']}", Style.RESET_ALL)
            selected_option: str = questionary.select(
                "请选择你的答案(键盘上下方向键选择,按回车确定):",
                [
                    f"A、{topic['备选答案']['A']}",
                    f"B、{topic['备选答案']['B']}",
                    f"C、{topic['备选答案']['C']}",
                    f"D、{topic['备选答案']['D']}",
                ],
            ).ask()

            format_selected_option = selected_option.split("、")[0]
            if format_selected_option == topic["正确答案"]:
                self.right_answer_count += 1
            else:
                self.wrong_answers.append(
                    {
                        "题干": topic["题干"],
                        "正确答案": f"{topic['正确答案']}、{topic['备选答案'][topic['正确答案']]}",
                        "你的选项": selected_option,
                    }
                )

            input("按任意键下一题")

        self.show_final_panel()

    def show_final_panel(self):
        clear_terminal()
        print(
            "共答对" + Fore.GREEN + str(self.right_answer_count) + Style.RESET_ALL + "道题目"
        )
        if len(self.wrong_answers) > 0:
            print(
                "共答错"
                + Fore.RED
                + str(len(self.wrong_answers))
                + Style.RESET_ALL
                + "道题目"
            )
            input("按任意键查看错题")
            for topic in self.wrong_answers:
                print("题目:\t" + Fore.YELLOW + f"{topic['题干']}", Style.RESET_ALL)
                print("正确答案: " + Fore.GREEN + f"{topic['正确答案']}", Style.RESET_ALL)
                print("你的选项: " + Fore.RED + f"{topic['你的选选项']}", Style.RESET_ALL)
                print()

    def show_ui(self):
        menu_options: dict = {
            "答题": self.show_exam,
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
