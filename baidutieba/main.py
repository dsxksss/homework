import csv
import time
import os
import re
from lxml import html
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options


class Post:
    def __init__(
        self,
        title: str,
        author: str,
        comment_num: str,
        date: str,
    ) -> None:
        self.贴子标题 = title
        self.发帖人 = author
        self.评论数量 = comment_num
        self.最后回复时间 = date


class BaseTeiba:
    def __init__(self, name: str, count: int) -> None:
        self.urls = [
            f"https://tieba.baidu.com/f?kw=python&ie=utf-8&pn={i}"
            for i in range(0, 50 * count, 50)
        ]
        self.headers = {"User-Agent": UserAgent().random}
        self.csv_headers = ["贴子标题", "发帖人", "评论数量", "最后回复时间"]
        self.work_path = os.getcwd()
        self.storage_dir = os.path.join(self.work_path, "百度贴吧爬虫内容")
        self.storage_path = os.path.join(self.storage_dir, f"{name}爬取.csv")
        self.posts: list[Post] = []
        self.check_dir_exists()

    def run(self):
        pass

    def get_one_page(self):
        pass

    def check_dir_exists(self):
        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)
            open(self.storage_path, "w", encoding="utf-8")
        elif not os.path.exists(self.storage_path):
            open(self.storage_path, "w", encoding="utf-8")

    def storage_csv(self):
        # 生成爬取后的文件
        with open(self.storage_path, "w", newline="", encoding="utf-8") as w:
            writer = csv.DictWriter(w, fieldnames=self.csv_headers)
            writer.writeheader()
            writer.writerows(self.posts)


class Xpath(BaseTeiba):
    def __init__(self, name: str, count: int) -> None:
        super().__init__(name, count)
        self.chrome_options = Options()
        self.chrome_options.add_argument("blink-settings=imagesEnabled=false")  # 不显示图片
        self.chrome_options.add_argument("--log-level=3")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def run(self):
        for url in self.urls:
            self.get_one_page(url)
        self.storage_csv()
        print("xpath爬取完成")

    def get_one_page(self, url):
        self.driver.get(url)
        time.sleep(2)  # 等待页面加载完成

        page_content = self.driver.page_source
        page_etree = html.etree.HTML(page_content)

        titles = page_etree.xpath(
            '//*[@id="thread_list"]/li/div/div[2]/div[1]/div[1]/a/text()'
        )

        authors = page_etree.xpath(
            '//*[@id="thread_list"]/li/div/div[2]/div[1]/div[2]/span[1]/span[1]/a/text()'
        )

        comment_nums = page_etree.xpath(
            '//*[@id="thread_list"]/li/div/div[1]/span/text()'
        )

        dates = page_etree.xpath(
            '//*[@id="thread_list"]/li/div/div[2]/div[2]/div[2]/span[2]/text()'
        )
        dates = [date.strip() for date in dates]

        # 避免获取信息时发生遗漏问题，根据获取到的最小长度来导入
        lengths = [len(titles), len(authors), len(comment_nums), len(dates)]

        for i in range(min(lengths)):
            post = Post(
                title=titles[i],
                author=authors[i],
                comment_num=comment_nums[i],
                date=dates[i],
            )
            self.posts.append(post.__dict__)


class Selector(BaseTeiba):
    def __init__(self, name: str, count: int) -> None:
        super().__init__(name, count)
        self.chrome_options = Options()
        self.chrome_options.add_argument("blink-settings=imagesEnabled=false")  # 不显示图片
        self.chrome_options.add_argument("--log-level=3")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def run(self):
        for url in self.urls:
            self.get_one_page(url)
        self.storage_csv()
        print("CSS选择器爬取完成")

    def get_one_page(self, url):
        self.driver.get(url)
        time.sleep(2)  # 等待页面加载完成

        page_content = self.driver.page_source
        page_soup = BeautifulSoup(page_content, "html.parser")

        titles = [
            e.get_text()
            for e in page_soup.select(".j_thread_list .threadlist_title > .j_th_tit")
        ]

        authors = [
            e.get_text()
            for e in page_soup.select(
                ".j_thread_list .col2_right:nth-child(2) > .threadlist_lz .frs-author-name"
            )
        ]

        comment_nums = [
            e.get_text()
            for e in page_soup.select(
                ".j_thread_list .col2_left:nth-child(1) > .threadlist_rep_num"
            )
        ]

        dates = [
            e.get_text().strip()
            for e in page_soup.select(
                "#thread_list > li > div > div.col2_right.j_threadlist_li_right > div.threadlist_detail.clearfix > div.threadlist_author.pull_right > span.threadlist_reply_date.pull_right.j_reply_data"
            )
        ]

        # 避免获取信息时发生遗漏问题，根据获取到的最小长度来导入
        lengths = [len(titles), len(authors), len(comment_nums), len(dates)]

        for i in range(min(lengths)):
            post = Post(
                title=titles[i],
                author=authors[i],
                comment_num=comment_nums[i],
                date=dates[i],
            )
            self.posts.append(post.__dict__)

    def __del__(self):
        self.driver.quit()


class Regular(BaseTeiba):
    def __init__(self, name: str, count: int) -> None:
        super().__init__(name, count)
        self.chrome_options = Options()
        self.chrome_options.add_argument("blink-settings=imagesEnabled=false")  # 不显示图片
        self.chrome_options.add_argument("--log-level=3")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def run(self):
        for url in self.urls:
            self.get_one_page(url)
        self.storage_csv()
        print("正则表达式爬取完成")

    def get_one_page(self, url):
        self.driver.get(url)
        time.sleep(2)  # 等待页面加载完成

        page_content = self.driver.page_source
        titles = re.findall(
            r'target="_blank" class="j_th_tit ">(.*?)</a>', page_content
        )
        titles = [title.strip() for title in titles]
        authors = re.findall(
            r'class="frs-author-name j_user_card ".*?target="_blank">(.*?)</a></span>',
            page_content,
        )
        authors = [author.strip() for author in authors]
        comment_nums = re.findall(r'title="回复">(\d.*?)</span>', page_content)
        dates = re.findall(
            r'title="最后回复时间">\s\s(.*?)</span>',
            page_content,
        )
        dates = [date.strip() for date in dates]

        # 避免获取信息时发生遗漏问题，根据获取到的最小长度来导入
        lengths = [len(titles), len(authors), len(comment_nums), len(dates)]

        for i in range(min(lengths)):
            post = Post(
                title=titles[i],
                author=authors[i],
                comment_num=comment_nums[i],
                date=dates[i],
            )
            self.posts.append(post.__dict__)

    def __del__(self):
        self.driver.quit()


def main():
    print("欢迎使用Python吧爬虫程序")
    count = int(input("请输入你要爬取的页数1-20(数值如果超过则为20页,少于规定值则1页):"))
    count = max(1, min(20, count))
    print(count)
    Xpath("Xpath", count).run()
    Selector("CSS选择器", count).run()
    Regular("正则表达式", count).run()

    print("\033[32m内容全部爬取完成\033[0m")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"异常:{e}")
