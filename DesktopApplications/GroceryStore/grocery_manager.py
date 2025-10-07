# grocery_manager.py - نفس الكود السابق تماماً
import sqlite3
import os
from datetime import datetime
import pandas as pd

class GroceryStoreManager:
    def __init__(self, db_name='grocery_store.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات وإنشاء الجداول إذا لم تكن موجودة"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # جدول المنتجات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                sold_quantity INTEGER DEFAULT 0,
                min_stock_level INTEGER DEFAULT 5,
                expiry_date TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المبيعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity_sold INTEGER,
                sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
                total_price REAL,
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"تم تهيئة قاعدة البيانات: {self.db_name}")
    
    def add_product(self, name, category, price, quantity, min_stock_level=5, expiry_date=None):
        """إضافة سلعة جديدة"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (name, category, price, quantity, min_stock_level, expiry_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, price, quantity, min_stock_level, expiry_date, datetime.now()))
        
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        
        print(f"تم إضافة السلعة '{name}' بنجاح برقم: {product_id}")
        return product_id
    
    def delete_product(self, product_id):
        """حذف سلعة بناءً على رقمها"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # التحقق من وجود السلعة
        cursor.execute('SELECT name FROM products WHERE product_id = ?', (product_id,))
        product = cursor.fetchone()
        
        if product:
            cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
            cursor.execute('DELETE FROM sales WHERE product_id = ?', (product_id,))
            conn.commit()
            conn.close()
            print(f"تم حذف السلعة '{product[0]}' بنجاح")
            return True
        else:
            conn.close()
            print(f"لا توجد سلعة برقم {product_id}")
            return False
    
    def update_product(self, product_id, **kwargs):
        """تعديل بيانات سلعة"""
        if not kwargs:
            print("لم يتم تقديم أي بيانات للتحديث")
            return False
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # التحقق من وجود السلعة
        cursor.execute('SELECT name FROM products WHERE product_id = ?', (product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            print(f"لا توجد سلعة برقم {product_id}")
            return False
        
        # بناء استعلام التحديث ديناميكياً
        allowed_fields = ['name', 'category', 'price', 'quantity', 'min_stock_level', 'expiry_date']
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            conn.close()
            print("لا توجد حقول صالحة للتحديث")
            return False
        
        values.append(product_id)
        update_fields.append("last_updated = ?")
        values.append(datetime.now())
        
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        print(f"تم تحديث بيانات السلعة '{product[0]}' بنجاح")
        return True
    
    def sell_product(self, product_id, quantity):
        """بيع كمية من السلعة"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # الحصول على بيانات السلعة
        cursor.execute('SELECT name, price, quantity FROM products WHERE product_id = ?', (product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            print(f"لا توجد سلعة برقم {product_id}")
            return False
        
        name, price, current_quantity = product
        
        if current_quantity < quantity:
            conn.close()
            print(f"الكمية المتاحة غير كافية. المتاح: {current_quantity}")
            return False
        
        # تحديث كمية السلعة
        new_quantity = current_quantity - quantity
        cursor.execute('''
            UPDATE products 
            SET quantity = ?, sold_quantity = sold_quantity + ?, last_updated = ?
            WHERE product_id = ?
        ''', (new_quantity, quantity, datetime.now(), product_id))
        
        # تسجيل عملية البيع
        total_price = price * quantity
        cursor.execute('''
            INSERT INTO sales (product_id, quantity_sold, total_price, sale_date)
            VALUES (?, ?, ?, ?)
        ''', (product_id, quantity, total_price, datetime.now()))
        
        conn.commit()
        conn.close()
        
        print(f"تم بيع {quantity} من '{name}' بقيمة إجمالية: {total_price:.2f} ريال")
        return True
    
    def get_all_products(self):
        """استعراض جميع السلع كجدول"""
        conn = sqlite3.connect(self.db_name)
        
        query = '''
            SELECT 
                product_id,
                name,
                category,
                price,
                quantity,
                sold_quantity,
                min_stock_level,
                expiry_date,
                CASE 
                    WHEN quantity = 0 THEN 'منتهي'
                    WHEN quantity <= min_stock_level THEN 'منخفض'
                    ELSE 'متوفر'
                END as status,
                (price * (quantity + sold_quantity)) as total_value
            FROM products
            ORDER BY product_id
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_product_stats(self):
        """الحصول على إحصائيات عامة"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # إحصائيات عامة
        cursor.execute('''
            SELECT 
                COUNT(*) as total_products,
                SUM(quantity) as total_quantity,
                SUM(sold_quantity) as total_sold,
                SUM(price * quantity) as current_stock_value,
                SUM(price * sold_quantity) as total_sales_value
            FROM products
        ''')
        
        stats = cursor.fetchone()
        
        # المنتجات المنتهية والمنخفضة
        cursor.execute('''
            SELECT 
                COUNT(*) as low_stock_count
            FROM products 
            WHERE quantity <= min_stock_level AND quantity > 0
        ''')
        
        low_stock = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) as out_of_stock_count
            FROM products 
            WHERE quantity = 0
        ''')
        
        out_of_stock = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'إجمالي السلع': stats[0],
            'الكمية الإجمالية': stats[1],
            'إجمالي المبيعات': stats[2],
            'قيمة المخزون الحالي': stats[3] or 0,
            'قيمة المبيعات الإجمالية': stats[4] or 0,
            'سلع منخفضة المخزون': low_stock,
            'سلع منتهية': out_of_stock
        }
    
    def search_products(self, search_term):
        """بحث عن السلع"""
        conn = sqlite3.connect(self.db_name)
        
        query = '''
            SELECT 
                product_id,
                name,
                category,
                price,
                quantity,
                sold_quantity
            FROM products 
            WHERE name LIKE ? OR category LIKE ?
            ORDER BY product_id
        '''
        
        df = pd.read_sql_query(query, conn, params=(f'%{search_term}%', f'%{search_term}%'))
        conn.close()
        
        return df
    
    def get_low_stock_products(self):
        """الحصول على السلع المنخفضة المخزون"""
        conn = sqlite3.connect(self.db_name)
        
        query = '''
            SELECT 
                product_id,
                name,
                category,
                price,
                quantity,
                min_stock_level
            FROM products 
            WHERE quantity <= min_stock_level AND quantity > 0
            ORDER BY quantity ASC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
