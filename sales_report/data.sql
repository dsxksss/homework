-- Active: 1687234487361@@127.0.0.1@3306
CREATE DATABASE sales_management USE sales_management CREATE TABLE salespersons (
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

-- 销售员数据导入
INSERT INTO
    salespersons (id, name)
VALUES
    (1, '销售员1'),
    (2, '销售员2'),
    (3, '销售员3'),
    (4, '销售员4');

-- 产品数据导入
INSERT INTO
    products (id, name)
VALUES
    (1, '产品1'),
    (2, '产品2'),
    (3, '产品3'),
    (4, '产品4'),
    (5, '产品5');

INSERT INTO
    sales_records
VALUES
    (1, 1, 202),
    (2, 2, 1050),
    (3, 3, 240),
    (4, 4, 500),
    (1, 5, 20);