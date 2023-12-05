import redis
import random
import questionary
import json

# 配置Redis连接
redis_host = "localhost"
redis_port = 6379
redis_password = ""

# 连接到Redis
r = redis.StrictRedis(
    host=redis_host, port=redis_port, password=redis_password, decode_responses=True
)


class Question:
    def __init__(self, prompt, options, answer):
        self.prompt = prompt
        self.options = options
        self.answer = answer

    def to_dict(self):
        return {"prompt": self.prompt, "options": self.options, "answer": self.answer}

    @staticmethod
    def from_dict(data):
        return Question(data["prompt"], data["options"], data["answer"])


class ExamSystem:
    def __init__(self):
        self.questions_key = "exam:questions"

    def add_question(self, question):
        question_data = question.to_dict()
        r.rpush(self.questions_key, json.dumps(question_data,ensure_ascii=False))

    def get_random_questions(self, n):
        questions_count = r.llen(self.questions_key)
        question_indices = random.sample(range(questions_count), n)
        questions = [
            Question.from_dict(json.loads(r.lindex(self.questions_key, idx)))
            for idx in question_indices
        ]
        return questions

    def take_exam(self, n):
        count = r.llen(self.questions_key)

        if n > count:
            print("\033[31m你输入的题目数量大于题库数量,请重新选择!\033[0m")

            exit(0)

        questions = self.get_random_questions(n)
        score = 0

        for i, question in enumerate(questions, start=1):
            answer = questionary.select(
                f"题目 {i}: {question.prompt}", choices=question.options
            ).ask()

            if answer == question.answer:
                score += 1

        return 100 // count * score

    def run(self):
        while True:
            action = questionary.select(
                "请选择你想要运行的功能(上下方向键选择,回车键确定)", choices=["添加题目", "开始考试", "退出程序"]
            ).ask()

            if action == "添加题目":
                prompt = questionary.text("请输入题干:").ask()
                options = [
                    questionary.text(f"请输入备选答案 {i}:").ask()
                    for i in ["A", "B", "C", "D"]
                ]
                answer = questionary.select("请选择对应的正确答案:", choices=options).ask()
                self.add_question(Question(prompt, options, answer))
            elif action == "开始考试":
                count = r.llen(self.questions_key)

                n = questionary.text(
                    f"你想考几道题目?(已有{count}道题目)",
                    validate=lambda text: text.isdigit(),
                ).ask()
                score = self.take_exam(int(n))
                print(f"你的分数是: {score}/满分100.")
            elif action == "退出程序":
                break


def main():
    try:
        # 创建考试系统实例
        exam_system = ExamSystem()

        # 运行考试系统
        exam_system.run()

    except Exception as e:
        print(f"程序崩溃,发生异常:{e}")


if __name__ == "__main__":
    main()
