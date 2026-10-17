"""Gabarito do exercício 2."""
import pymysql


class ProductRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_schema(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS product (id INT AUTO_INCREMENT PRIMARY KEY, "
                "sku VARCHAR(20) NOT NULL COLLATE utf8mb4_bin, name VARCHAR(60) NOT NULL, "
                "stock INT NOT NULL DEFAULT 0, UNIQUE KEY uq_sku (sku)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")
        self.conn.commit()

    def add(self, sku, name, stock=0):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO product (sku, name, stock) VALUES (%s, %s, %s)", (sku, name, stock))
            except pymysql.err.IntegrityError as error:
                self.conn.rollback()
                raise ValueError(f"SKU repetido: {sku!r}") from error
            new_id = cursor.lastrowid
        self.conn.commit()
        return self.get(new_id)

    def get(self, product_id):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM product WHERE id = %s", (product_id,))
            row = cursor.fetchone()
        self.conn.commit()                                   # encerra a transação de leitura (snapshot)
        return row

    def add_stock(self, sku, quantity):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT stock FROM product WHERE sku = %s FOR UPDATE", (sku,))
            row = cursor.fetchone()
            if row is None:
                self.conn.rollback()
                raise KeyError(sku)
            if row["stock"] + quantity < 0:
                self.conn.rollback()
                raise ValueError("estoque ficaria negativo")
            cursor.execute("UPDATE product SET stock = stock + %s WHERE sku = %s", (quantity, sku))
        self.conn.commit()

    def upsert(self, sku, name, stock):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO product (sku, name, stock) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE name = VALUES(name), stock = stock + VALUES(stock)", (sku, name, stock))
            inserted = cursor.rowcount == 1
        self.conn.commit()
        return inserted
