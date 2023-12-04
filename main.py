import os
import random
import jsonlines
import questionary
from tqdm import tqdm
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


class ExamSystem:
    @staticmethod
    def run():
        instance = ExamSystem()
        instance.check_dir_exists()
        instance.read_data()
        instance.show_ui()

    def __init__(self):
        self.work_path = os.getcwd()
        self.storage_dir = os.path.join(self.work_path, "题库目录")
        self.storage_path = os.path.join(self.storage_dir, "题库.jsonl")
        self.topic_reader_cache = []
        self.topic_writer_cache: list[Topic] = []
        self.wrong_answers = []
        self.right_answer_count = 0

    def check_dir_exists(self):
        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)
            open(self.storage_path, "w", encoding="utf-8")
        elif not os.path.exists(self.storage_path):
            open(self.storage_path, "w", encoding="utf-8")

    def read_data(self):
        with jsonlines.open(self.storage_path) as rows:
            for row in rows:
                self.topic_reader_cache.append(row)

    def write_data(self):
        with jsonlines.open(self.storage_path, mode="a") as w:
            for topic in tqdm(
                self.topic_writer_cache, total=len(self.topic_writer_cache)
            ):
                data = {
                    "题干": topic.title,
                    "备选答案": {
                        "A": topic.options.options1,
                        "B": topic.options.options2,
                        "C": topic.options.options3,
                        "D": topic.options.options4,
                    },
                    "正确答案": topic.answer,
                }
                w.write(data)
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

    def input_topic_count(self) -> int:
        max_topic_length = len(self.topic_reader_cache)
        try:
            count = questionary.text(f"请输入题目数量(总题目数量{max_topic_length}): ").ask()
            count = int(count)
            if count > max_topic_length:
                print(Fore.RED + "题目数量不足,请重新选择!" + Style.RESET_ALL)
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
                print("你的选项: " + Fore.RED + f"{topic['你的选项']}", Style.RESET_ALL)
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
