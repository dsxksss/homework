import pymysql
from pymysql import Error
import questionary


"""
CREATE TABLE salespersons (
    id INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE sales_records (
    salesperson_id INT,
    product_id INT,
    amount INT,
    FOREIGN KEY (salesperson_id) REFERENCES salespersons(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""


# 销售员类
class Salesperson:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.sales_records = []

    def add_sales_record(self, product_id, amount):
        self.sales_records.append({"product_id": product_id, "amount": amount})

    def get_total_sales_by_product(self, product_id):
        return sum(
            record["amount"]
            for record in self.sales_records
            if record["product_id"] == product_id
        )


# 产品类
class Product:
    def __init__(self, id, name):
        self.id = id
        self.name = name


# 销售记录类
class SalesRecord:
    def __init__(self, salesperson_id, product_id, amount):
        self.salesperson_id = salesperson_id
        self.product_id = product_id
        self.amount = amount


class SalesManager:
    def __init__(self, connection):
        self.salespersons = {}
        self.products = {}
        self.connection = connection
        self.load_data_from_db()

    # 执行数据库查询
    def execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    # 执行读取操作
    def execute_read_query(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")

    def load_data_from_db(self):
        try:
            salespersons_query = "SELECT id, name FROM salespersons"
            products_query = "SELECT id, name FROM products"
            sales_records_query = (
                "SELECT salesperson_id, product_id, amount FROM sales_records"
            )

            salespersons = self.execute_read_query(query=salespersons_query)
            for id, name in salespersons:
                self.salespersons[id] = Salesperson(id, name)

            products = self.execute_read_query(query=products_query)
            for id, name in products:
                self.products[id] = Product(id, name)

            sales_records = self.execute_read_query(query=sales_records_query)
            for salesperson_id, product_id, amount in sales_records:
                self.salespersons[salesperson_id].add_sales_record(product_id, amount)
        except Error as e:
            print(f"The error '{e}' occurred")

    # 计算销售额
    def calculate_total_sales(self, salesperson):
        total_sales = sum(record["amount"] for record in salesperson.sales_records)
        return total_sales

    # 按销售额排序销售员
    def sort_salespersons_by_sales(self):
        sorted_salespersons = sorted(
            self.salespersons.values(),
            key=lambda salesperson: self.calculate_total_sales(salesperson),
            reverse=True,
        )
        return sorted_salespersons

    def add_sales_record(self, salesperson_id, product_id, amount):
        if salesperson_id not in (self.salespersons.keys()):
            print("销售员不存在")
            return
        if product_id not in self.products.keys():
            print("产品不存在")
            return
        self.salespersons[salesperson_id].add_sales_record(product_id, amount)
        # 将新的销售记录插入到数据库中
        query = f"INSERT INTO sales_records (salesperson_id, product_id, amount) VALUES ({salesperson_id}, {product_id}, {amount})"
        self.execute_query(query)

    def update_sales_record(self, salesperson_id, product_id, new_amount):
        if salesperson_id not in self.salespersons.keys():
            print("销售员不存在")
            return
        if product_id not in self.products.keys():
            print("产品不存在")
            return
        for record in self.salespersons[salesperson_id].sales_records:
            if record["product_id"] == product_id:
                record["amount"] = new_amount
                break
        # 更新销售记录到数据库中
        query = f"UPDATE sales_records SET amount = {new_amount} WHERE salesperson_id = {salesperson_id} AND product_id = {product_id}"
        self.execute_query(query)

    def delete_sales_record(self, salesperson_id, product_id):
        if salesperson_id not in self.salespersons.keys():
            print("销售员不存在")
            return
        if product_id not in self.products.keys():
            print("产品不存在")
            return
        self.salespersons[salesperson_id].sales_records = [
            record
            for record in self.salespersons[salesperson_id].sales_records
            if record["product_id"] != product_id
        ]
        # 从数据库中删除销售记录
        query = f"DELETE FROM sales_records WHERE salesperson_id = {salesperson_id} AND product_id = {product_id}"
        self.execute_query(query)


# 数据库配置
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "test",
    "database": "sales_management",
}


# 连接数据库
def create_db_connection():
    try:
        connection = pymysql.connect(**db_config)
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")


# 主程序
def main():
    connection = create_db_connection()

    sales_manager = SalesManager(connection=connection)

    while True:
        # 使用 questionary 来实现终端菜单选择功能
        choice = questionary.select(
            "请选择操作：",
            choices=[
                "1. 添加销售记录",
                "2. 更新销售记录",
                "3. 删除销售记录",
                "4. 按销售额排序销售员",
                "5. 计算总销售额",
                "6. 退出",
            ],
        ).ask()

        if choice == "1. 添加销售记录":
            # 获取销售员ID、产品ID和销售额
            salesperson_id = int(
                questionary.text(
                    "请输入销售员ID：",
                    validate=lambda text: text.isdigit(),
                ).ask()
            )
            product_id = int(
                questionary.text(
                    "请输入产品ID：",
                    validate=lambda text: text.isdigit(),
                ).ask()
            )
            amount = int(
                questionary.text(
                    "请输入销售额：",
                    validate=lambda text: text.isdigit(),
                ).ask()
            )

            # 添加销售记录
            sales_manager.add_sales_record(salesperson_id, product_id, amount)

        elif choice == "2. 更新销售记录":
            # 获取销售员ID、产品ID和新的销售额
            salesperson_id = int(
                questionary.text(
                    "请输入销售员ID：",
                    validate=lambda text: text.isdigit(),
                ).ask()
            )
            product_id = int(
                questionary.text(
                    "请输入产品ID：",
                    validate=lambda text: text.isdigit(),
                ).ask()
            )
            new_amount = int(
                questionary.text(
                    "请输入新的销售额：",
                    validate=lambda text: text.isdigit(),
                ).ask()
            )

            # 更新销售记录
            sales_manager.update_sales_record(salesperson_id, product_id, new_amount)

        elif choice == "3. 删除销售记录":
            # 获取销售员ID和产品ID
            salesperson_id = int(
                questionary.text(
                    "请输入销售员ID：",
                    validate=lambda text: text.isdigit(),
                ).ask()
            )
            product_id = int(
                questionary.text(
                    "请输入产品ID：",
                    validate=lambda text: text.isdigit(),
                ).ask()
            )

            # 删除销售记录
            sales_manager.delete_sales_record(salesperson_id, product_id)

        elif choice == "4. 按销售额排序销售员":
            # 按销售额排序销售员
            sorted_salespersons = sales_manager.sort_salespersons_by_sales()

            # 打印排序结果
            for salesperson in sorted_salespersons:
                print(f"销售员ID: {salesperson.id}, 销售员姓名: {salesperson.name}")

        elif choice == "5. 计算总销售额":
            total_sales = 0
            sorted_salespersons = sales_manager.sort_salespersons_by_sales()
            for salesperson in sorted_salespersons:
                # 计算总销售额
                total_sales += sales_manager.calculate_total_sales(salesperson)

            # 打印总销售额
            print(f"总销售额: {total_sales}")

        elif choice == "6. 退出":
            # 退出程序
            break


if __name__ == "__main__":
    main()
