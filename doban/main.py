import csv
import time
import requests
import os
from bs4 import BeautifulSoup
import re
from lxml import html
from fake_useragent import UserAgent


class Movie:
    def __init__(
        self,
        orderNumber: str,
        title: str,
        info: str,
        score: str,
    ) -> None:
        self.排名序号 = orderNumber
        self.电影名称 = title
        self.电影基本信息 = info
        self.评分 = score


class BaseDouban:
    def __init__(self, name: str) -> None:
        self.urls = [
            f"https://movie.douban.com/top250?start={i}&filter="
            for i in range(0, 100, 25)
        ]
        self.headers = {"User-Agent": UserAgent().random}
        self.csv_headers = ["排名序号", "电影名称", "电影基本信息", "评分"]
        self.work_path = os.getcwd()
        self.storage_dir = os.path.join(self.work_path, "豆瓣前100电影")
        self.storage_path = os.path.join(self.storage_dir, f"使用{name}爬取.csv")
        self.movies: list[Movie] = []
        self.check_dir_exists()

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
            writer.writeheader()  # 写入csv头
            writer.writerows(self.movies)  # 写入全部电影数据

    def run(self):
        pass

    def get_one_page(self):
        pass


class XpathDouban(BaseDouban):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def run(self):
        for url in self.urls:
            self.get_one_page(url)
        self.storage_csv()
        print("---------------\033[32m爬取完成\033[0m---------------")
        print("使用lxml库xpath方法爬取完成")

    def get_one_page(self, url):
        page_content = requests.get(url, headers=self.headers).text
        page_etree = html.etree.HTML(page_content)
        orderNumbers: list[str] = page_etree.xpath(
            '//*[@id="content"]/div/div[1]/ol/li/div/div[1]/em/text()'
        )

        titles: list[str] = page_etree.xpath(
            '//*[@id="content"]/div/div[1]/ol/li/div/div[2]/div[1]/a/span[1]/text()'
        )

        infos: list[str] = page_etree.xpath(
            '//*[@id="content"]/div/div[1]/ol/li/div/div[2]/div[2]/p[1]/text()'
        )
        infos = [info.strip() for info in infos]

        scores: list[str] = page_etree.xpath(
            '//*[@id="content"]/div/div[1]/ol/li/div/div[2]/div[2]/div/span[2]/text()'
        )

        for i in range(len(orderNumbers)):
            movie = Movie(
                orderNumber=orderNumbers[i],
                title=titles[i],
                info=infos[i],
                score=scores[i],
            )
            self.movies.append(movie.__dict__)


class SelectDouban(BaseDouban):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def run(self):
        for url in self.urls:
            self.get_one_page(url)
        self.storage_csv()
        print("---------------\033[32m爬取完成\033[0m---------------")
        print("使用bs4库CSS选择器方法爬取完成")

    def get_one_page(self, url):
        page_content = requests.get(url, headers=self.headers).text
        page_soup = BeautifulSoup(page_content, "html.parser")

        orderNumbers: list[str] = [e.get_text() for e in page_soup.select("li em")]

        titles: list[str] = [
            e.get_text() for e in page_soup.select("li .title:nth-child(1)")
        ]
        infos: list[str] = [
            e.get_text().strip() for e in page_soup.select("li p:nth-child(1)")
        ]

        scores: list[str] = [
            e.get_text().strip() for e in page_soup.select("li .rating_num")
        ]

        for i in range(len(orderNumbers)):
            movie = Movie(
                orderNumber=orderNumbers[i],
                title=titles[i],
                info=infos[i],
                score=scores[i],
            )
            self.movies.append(movie.__dict__)


class RegularDouban(BaseDouban):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def run(self):
        for url in self.urls:
            self.get_one_page(url)
        self.storage_csv()
        print("---------------\033[32m爬取完成\033[0m---------------")
        print("使用re库正则表达式爬取完成")

    def get_one_page(self, url):
        page_content = requests.get(url, headers=self.headers).text
        orderNumbers = re.findall(r'<em class="">(\d+)</em>', page_content)
        titles = re.findall(r'<span class="title">([^&]+)</span>', page_content)
        infos = re.findall(
            r'<div class="bd">\s*<p class="">\s*(.*?)\s*s*<br>\s*(.*?)\s*</p>',
            page_content,
        )
        scores = re.findall(
            r'<span class="rating_num" property="v:average">(\d.+)</span',
            page_content,
        )

        for i in range(len(orderNumbers)):
            movie = Movie(
                orderNumber=orderNumbers[i],
                title=titles[i],
                info=infos[i][0].replace("&nbsp;", ""),
                score=scores[i],
            )
            self.movies.append(movie.__dict__)


def main():
    xpathDouban = XpathDouban("xpath")
    regularDouban = RegularDouban("正则表达式")
    selectDouban = SelectDouban("css选择器")

    print("豆瓣前100电影爬虫系统菜单:")
    print("1. 使用lxml库xpath方法爬取")
    print("2. 使用bs4库CSS选择器方法爬取")
    print("3. 使用re库正则表达式爬取")
    print("4. 退出程序")
    choice = input("请选择一个选项: ")
    start_time = time.time()  # 记录程序开始运行时间
    if choice == "1":
        xpathDouban.run()
    elif choice == "2":
        selectDouban.run()
    elif choice == "3":
        regularDouban.run()
    elif choice == "4":
        pass

    end_time = time.time()  # 记录程序结束运行时间
    print("运行耗时 %.2f 秒" % (end_time - start_time))


# 结束提示信息
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序崩溃,发生异常:{e}")
