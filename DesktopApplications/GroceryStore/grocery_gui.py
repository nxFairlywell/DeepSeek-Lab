# grocery_gui.py - الواجهة الرسومية (الإصدار المصحح)
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
from grocery_manager import GroceryStoreManager

class GroceryStoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة محل المواد الغذائية")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # إنشاء كائن المدير
        self.manager = GroceryStoreManager()
        
        # إنشاء واجهة المستخدم
        self.create_widgets()
        
        # تحميل البيانات الأولية
        self.refresh_products()
    
    def create_widgets(self):
        # إنشاء تبويبات
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # تبويب عرض السلع
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text="عرض السلع")
        
        # تبويب إضافة سلعة
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="إضافة سلعة")
        
        # تبويب تعديل سلعة
        self.edit_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.edit_tab, text="تعديل سلعة")
        
        # تبويب البيع
        self.sell_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sell_tab, text="بيع سلعة")
        
        # تبويب الإحصائيات
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="الإحصائيات")
        
        # بناء كل تبويب
        self.build_products_tab()
        self.build_add_tab()
        self.build_edit_tab()
        self.build_sell_tab()
        self.build_stats_tab()
    
    def build_products_tab(self):
        # إطار البحث
        search_frame = ttk.Frame(self.products_tab)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(search_frame, text="بحث:").pack(side='right', padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side='right', padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(search_frame, text="عرض الكل", 
                  command=self.refresh_products).pack(side='right', padx=5)
        
        ttk.Button(search_frame, text="السلع المنخفضة", 
                  command=self.show_low_stock).pack(side='right', padx=5)
        
        # جدول السلع
        columns = ('رقم السلعة', 'الاسم', 'الفئة', 'السعر', 'الكمية', 'المباع', 'الحالة')
        self.products_tree = ttk.Treeview(self.products_tab, columns=columns, show='headings', height=20)
        
        # تعريف العناوين
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=120)
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(self.products_tab, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        self.products_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
    
    def build_add_tab(self):
        # نموذج إضافة سلعة
        form_frame = ttk.Frame(self.add_tab)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(form_frame, text="اسم السلعة:").grid(row=0, column=1, padx=10, pady=10, sticky='e')
        self.add_name = ttk.Entry(form_frame, width=30)
        self.add_name.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="الفئة:").grid(row=1, column=1, padx=10, pady=10, sticky='e')
        self.add_category = ttk.Entry(form_frame, width=30)
        self.add_category.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="السعر:").grid(row=2, column=1, padx=10, pady=10, sticky='e')
        self.add_price = ttk.Entry(form_frame, width=30)
        self.add_price.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="الكمية:").grid(row=3, column=1, padx=10, pady=10, sticky='e')
        self.add_quantity = ttk.Entry(form_frame, width=30)
        self.add_quantity.grid(row=3, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="حد المخزون الأدنى:").grid(row=4, column=1, padx=10, pady=10, sticky='e')
        self.add_min_stock = ttk.Entry(form_frame, width=30)
        self.add_min_stock.insert(0, "5")
        self.add_min_stock.grid(row=4, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="تاريخ الانتهاء:").grid(row=5, column=1, padx=10, pady=10, sticky='e')
        self.add_expiry = ttk.Entry(form_frame, width=30)
        self.add_expiry.grid(row=5, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Button(form_frame, text="إضافة السلعة", 
                  command=self.add_product).grid(row=6, column=0, columnspan=2, pady=20)
        
        # منطقة النتائج
        self.add_result = scrolledtext.ScrolledText(form_frame, width=60, height=10, state='disabled')
        self.add_result.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
    
    def build_edit_tab(self):
        # نموذج تعديل سلعة
        form_frame = ttk.Frame(self.edit_tab)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(form_frame, text="رقم السلعة:").grid(row=0, column=1, padx=10, pady=10, sticky='e')
        self.edit_id = ttk.Entry(form_frame, width=30)
        self.edit_id.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        ttk.Button(form_frame, text="جلب البيانات", 
                  command=self.load_product_data).grid(row=0, column=2, padx=10)
        
        ttk.Label(form_frame, text="اسم السلعة:").grid(row=1, column=1, padx=10, pady=10, sticky='e')
        self.edit_name = ttk.Entry(form_frame, width=30)
        self.edit_name.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="الفئة:").grid(row=2, column=1, padx=10, pady=10, sticky='e')
        self.edit_category = ttk.Entry(form_frame, width=30)
        self.edit_category.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="السعر:").grid(row=3, column=1, padx=10, pady=10, sticky='e')
        self.edit_price = ttk.Entry(form_frame, width=30)
        self.edit_price.grid(row=3, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="الكمية:").grid(row=4, column=1, padx=10, pady=10, sticky='e')
        self.edit_quantity = ttk.Entry(form_frame, width=30)
        self.edit_quantity.grid(row=4, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="حد المخزون الأدنى:").grid(row=5, column=1, padx=10, pady=10, sticky='e')
        self.edit_min_stock = ttk.Entry(form_frame, width=30)
        self.edit_min_stock.grid(row=5, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="تاريخ الانتهاء:").grid(row=6, column=1, padx=10, pady=10, sticky='e')
        self.edit_expiry = ttk.Entry(form_frame, width=30)
        self.edit_expiry.grid(row=6, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Button(form_frame, text="تحديث البيانات", 
                  command=self.update_product).grid(row=7, column=0, pady=20)
        
        ttk.Button(form_frame, text="حذف السلعة", 
                  command=self.delete_product).grid(row=7, column=1, pady=20)
        
        # منطقة النتائج
        self.edit_result = scrolledtext.ScrolledText(form_frame, width=60, height=10, state='disabled')
        self.edit_result.grid(row=8, column=0, columnspan=3, padx=10, pady=10)
    
    def build_sell_tab(self):
        # نموذج البيع
        form_frame = ttk.Frame(self.sell_tab)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(form_frame, text="رقم السلعة:").grid(row=0, column=1, padx=10, pady=10, sticky='e')
        self.sell_id = ttk.Entry(form_frame, width=30)
        self.sell_id.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Label(form_frame, text="الكمية المباعة:").grid(row=1, column=1, padx=10, pady=10, sticky='e')
        self.sell_quantity = ttk.Entry(form_frame, width=30)
        self.sell_quantity.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        ttk.Button(form_frame, text="إتمام البيع", 
                  command=self.sell_product).grid(row=2, column=0, columnspan=2, pady=20)
        
        # منطقة النتائج
        self.sell_result = scrolledtext.ScrolledText(form_frame, width=60, height=15, state='disabled')
        self.sell_result.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    
    def build_stats_tab(self):
        # عرض الإحصائيات
        stats_frame = ttk.Frame(self.stats_tab)
        stats_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, width=80, height=20, state='disabled')
        self.stats_text.pack(fill='both', expand=True)
        
        ttk.Button(stats_frame, text="تحديث الإحصائيات", 
                  command=self.show_stats).pack(pady=10)
        
        # عرض الإحصائيات عند فتح التبويب - مؤقتاً سنعلق هذا السطر
        # self.show_stats()  # تم تعليق هذا السطر لحل المشكلة
    
    def refresh_products(self):
        # تحديث جدول السلع
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        df = self.manager.get_all_products()
        for _, row in df.iterrows():
            self.products_tree.insert('', 'end', values=(
                row['product_id'],
                row['name'],
                row['category'],
                f"{row['price']:.2f}",
                row['quantity'],
                row['sold_quantity'],
                row['status']
            ))
    
    def on_search(self, event):
        # البحث أثناء الكتابة
        search_term = self.search_entry.get()
        if search_term:
            df = self.manager.search_products(search_term)
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            for _, row in df.iterrows():
                self.products_tree.insert('', 'end', values=(
                    row['product_id'],
                    row['name'],
                    row['category'],
                    f"{row['price']:.2f}",
                    row['quantity'],
                    row['sold_quantity'],
                    '---'
                ))
    
    def show_low_stock(self):
        # عرض السلع المنخفضة المخزون
        df = self.manager.get_low_stock_products()
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        for _, row in df.iterrows():
            self.products_tree.insert('', 'end', values=(
                row['product_id'],
                row['name'],
                row['category'],
                f"{row['price']:.2f}",
                row['quantity'],
                '---',
                'منخفض'
            ))
    
    def add_product(self):
        # إضافة سلعة جديدة
        try:
            name = self.add_name.get()
            category = self.add_category.get()
            price = float(self.add_price.get())
            quantity = int(self.add_quantity.get())
            min_stock = int(self.add_min_stock.get() or "5")
            expiry = self.add_expiry.get() or None
            
            if not name or not category:
                messagebox.showerror("خطأ", "الاسم والفئة مطلوبان")
                return
            
            product_id = self.manager.add_product(name, category, price, quantity, min_stock, expiry)
            
            self.add_result.config(state='normal')
            self.add_result.delete(1.0, tk.END)
            self.add_result.insert(tk.END, f"تم إضافة السلعة بنجاح!\nرقم السلعة: {product_id}\nالاسم: {name}\nالفئة: {category}\nالسعر: {price}\nالكمية: {quantity}")
            self.add_result.config(state='disabled')
            
            # تفريغ الحقول
            self.add_name.delete(0, tk.END)
            self.add_category.delete(0, tk.END)
            self.add_price.delete(0, tk.END)
            self.add_quantity.delete(0, tk.END)
            self.add_min_stock.delete(0, tk.END)
            self.add_expiry.delete(0, tk.END)
            self.add_min_stock.insert(0, "5")
            
            # تحديث جدول السلع
            self.refresh_products()
            
        except ValueError as e:
            messagebox.showerror("خطأ", "تأكد من صحة البيانات المدخلة")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def load_product_data(self):
        # جلب بيانات سلعة للتعديل
        try:
            product_id = int(self.edit_id.get())
            df = self.manager.get_all_products()
            product = df[df['product_id'] == product_id]
            
            if product.empty:
                messagebox.showerror("خطأ", "لم يتم العثور على السلعة")
                return
            
            product = product.iloc[0]
            
            self.edit_name.delete(0, tk.END)
            self.edit_name.insert(0, product['name'])
            
            self.edit_category.delete(0, tk.END)
            self.edit_category.insert(0, product['category'])
            
            self.edit_price.delete(0, tk.END)
            self.edit_price.insert(0, str(product['price']))
            
            self.edit_quantity.delete(0, tk.END)
            self.edit_quantity.insert(0, str(product['quantity']))
            
            self.edit_min_stock.delete(0, tk.END)
            self.edit_min_stock.insert(0, str(product['min_stock_level']))
            
            self.edit_expiry.delete(0, tk.END)
            if pd.notna(product['expiry_date']):
                self.edit_expiry.insert(0, str(product['expiry_date']))
            
            self.edit_result.config(state='normal')
            self.edit_result.delete(1.0, tk.END)
            self.edit_result.insert(tk.END, f"تم تحميل بيانات السلعة:\n{product['name']}")
            self.edit_result.config(state='disabled')
            
        except ValueError:
            messagebox.showerror("خطأ", "رقم السلعة يجب أن يكون رقماً")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def update_product(self):
        # تحديث بيانات سلعة
        try:
            product_id = int(self.edit_id.get())
            updates = {}
            
            if self.edit_name.get():
                updates['name'] = self.edit_name.get()
            if self.edit_category.get():
                updates['category'] = self.edit_category.get()
            if self.edit_price.get():
                updates['price'] = float(self.edit_price.get())
            if self.edit_quantity.get():
                updates['quantity'] = int(self.edit_quantity.get())
            if self.edit_min_stock.get():
                updates['min_stock_level'] = int(self.edit_min_stock.get())
            if self.edit_expiry.get():
                updates['expiry_date'] = self.edit_expiry.get()
            
            if updates:
                success = self.manager.update_product(product_id, **updates)
                if success:
                    self.edit_result.config(state='normal')
                    self.edit_result.delete(1.0, tk.END)
                    self.edit_result.insert(tk.END, "تم تحديث بيانات السلعة بنجاح")
                    self.edit_result.config(state='disabled')
                    
                    # تحديث جدول السلع
                    self.refresh_products()
                else:
                    messagebox.showerror("خطأ", "فشل في تحديث البيانات")
            else:
                messagebox.showwarning("تحذير", "لم تدخل أي بيانات للتحديث")
                
        except ValueError:
            messagebox.showerror("خطأ", "تأكد من صحة البيانات المدخلة")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def delete_product(self):
        # حذف سلعة
        try:
            product_id = int(self.edit_id.get())
            
            if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذه السلعة؟"):
                success = self.manager.delete_product(product_id)
                if success:
                    self.edit_result.config(state='normal')
                    self.edit_result.delete(1.0, tk.END)
                    self.edit_result.insert(tk.END, "تم حذف السلعة بنجاح")
                    self.edit_result.config(state='disabled')
                    
                    # تفريغ الحقول
                    self.edit_id.delete(0, tk.END)
                    self.edit_name.delete(0, tk.END)
                    self.edit_category.delete(0, tk.END)
                    self.edit_price.delete(0, tk.END)
                    self.edit_quantity.delete(0, tk.END)
                    self.edit_min_stock.delete(0, tk.END)
                    self.edit_expiry.delete(0, tk.END)
                    
                    # تحديث جدول السلع
                    self.refresh_products()
                else:
                    messagebox.showerror("خطأ", "فشل في حذف السلعة")
                    
        except ValueError:
            messagebox.showerror("خطأ", "رقم السلعة يجب أن يكون رقماً")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def sell_product(self):
        # بيع سلعة
        try:
            product_id = int(self.sell_id.get())
            quantity = int(self.sell_quantity.get())
            
            success = self.manager.sell_product(product_id, quantity)
            if success:
                self.sell_result.config(state='normal')
                self.sell_result.delete(1.0, tk.END)
                self.sell_result.insert(tk.END, f"تم البيع بنجاح!\n\nالكمية المباعة: {quantity}\nرقم السلعة: {product_id}")
                self.sell_result.config(state='disabled')
                
                # تفريغ الحقول
                self.sell_id.delete(0, tk.END)
                self.sell_quantity.delete(0, tk.END)
                
                # تحديث جدول السلع
                self.refresh_products()
            else:
                messagebox.showerror("خطأ", "فشل في عملية البيع")
                
        except ValueError:
            messagebox.showerror("خطأ", "تأكد من صحة البيانات المدخلة")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def show_stats(self):
        # عرض الإحصائيات
        stats = self.manager.get_product_stats()
        
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        
        self.stats_text.insert(tk.END, "الإحصائيات العامة:\n")
        self.stats_text.insert(tk.END, "="*30 + "\n\n")
        
        for key, value in stats.items():
            # معالجة القيم الفارغة أو None
            if value is None:
                value = 0
            
            if 'قيمة' in key:
                self.stats_text.insert(tk.END, f"{key}: {value:,.2f} ريال\n")
            else:
                self.stats_text.insert(tk.END, f"{key}: {value}\n")
        
        self.stats_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryStoreGUI(root)
    root.mainloop()
