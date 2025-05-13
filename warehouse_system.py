"""
Пример информационной системы склада на Python с использованием 6 паттернов проектирования GoF.

Реализованы паттерны:
1. Factory Method - создание разных видов товаров.
2. Builder - поэтапная сборка заказа.
3. Facade - упрощение операций кладовщика.
4. Composite - организация товаров и групп товаров.
5. Template Method - алгоритм приёма товара.
6. Visitor - операции с товарами без изменения их классов.

Пользователи: Кладовщик, Администратор, Менеджер склада.
"""

from abc import ABC, abstractmethod

# ---------------------------
# 1. Factory Method
# ---------------------------

class Product(ABC):
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @abstractmethod
    def get_type(self):
        pass

    def accept(self, visitor):
        visitor.visit(self)

class Clothing(Product):
    def get_type(self):
        return "Одежда"

class Electronics(Product):
    def get_type(self):
        return "Электроника"

class Food(Product):
    def get_type(self):
        return "Продукты"

class ProductFactory:
    @staticmethod
    def create_product(product_type, name, price):
        if product_type == "clothing":
            return Clothing(name, price)
        elif product_type == "electronics":
            return Electronics(name, price)
        elif product_type == "food":
            return Food(name, price)
        else:
            raise ValueError(f"Неизвестный тип товара: {product_type}")

# ---------------------------
# 2. Builder
# ---------------------------

class Order:
    def __init__(self):
        self.products = []
        self.packaging = None

    def add_product(self, product):
        self.products.append(product)

    def set_packaging(self, packaging):
        self.packaging = packaging

    def __str__(self):
        prod_list = ', '.join([p.name for p in self.products])
        return f"Заказ: [{prod_list}], Упаковка: {self.packaging}"

class OrderBuilder:
    def __init__(self):
        self.order = Order()

    def add_product(self, product):
        self.order.add_product(product)
        return self

    def set_packaging(self, packaging):
        self.order.set_packaging(packaging)
        return self

    def build(self):
        return self.order

# ---------------------------
# 3. Facade
# ---------------------------

class WarehouseFacade:
    """
    Фасад для упрощения операций кладовщика.
    Метод обработать_поставку() вызывает регистрацию, проверку и сохранение поставки.
    """
    def __init__(self, inventory, database):
        self.inventory = inventory
        self.database = database

    def process_supply(self, product, quantity):
        print(f"Обработка поставки: {product.name}, количество: {quantity}")
        self.register_supply(product, quantity)
        self.check_inventory(product)
        self.save_to_database(product, quantity)
        print("Поставка обработана.\n")

    def register_supply(self, product, quantity):
        print(f"Регистрация поставки: {product.name} x{quantity}")
        self.inventory.add_stock(product, quantity)

    def check_inventory(self, product):
        qty = self.inventory.get_stock(product)
        print(f"Проверка наличия товара '{product.name}': {qty} шт.")

    def save_to_database(self, product, quantity):
        self.database.save_supply(product, quantity)

# ---------------------------
# 4. Composite
# ---------------------------

class ProductComponent(ABC):
    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def accept(self, visitor):
        pass

class SingleProduct(ProductComponent):
    def __init__(self, product):
        self.product = product

    def get_price(self):
        return self.product.price

    def accept(self, visitor):
        self.product.accept(visitor)

class ProductGroup(ProductComponent):
    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, component):
        self.children.append(component)

    def remove(self, component):
        self.children.remove(component)

    def get_price(self):
        total = 0
        for child in self.children:
            total += child.get_price()
        return total

    def accept(self, visitor):
        for child in self.children:
            child.accept(visitor)

# ---------------------------
# 5. Template Method
# ---------------------------

class ProductReceivingProcess(ABC):
    """
    Шаблонный метод для приёма товара:
    1. Сканирование
    2. Проверка
    3. Размещение на складе
    """
    def receive_product(self, product, quantity):
        self.scan(product)
        if self.check(product, quantity):
            self.store(product, quantity)
            self.maintenance()
        else:
            print("Ошибка при приёме товара.")

    def scan(self, product):
        print(f"Сканирование товара: {product.name}")

    @abstractmethod
    def check(self, product, quantity):
        pass

    def store(self, product, quantity):
        print(f"Размещение {quantity} шт. товара '{product.name}' на складе")

    def maintenance(self):
        # По умолчанию ничего не делаем, может переопределяться
        pass

class StorekeeperReceivingProcess(ProductReceivingProcess):
    def __init__(self, inventory):
        self.inventory = inventory

    def check(self, product, quantity):
        # Пример проверки: количество не должно быть отрицательным
        if quantity > 0:
            print("Проверка пройдена")
            return True
        else:
            print("Проверка не пройдена: количество должно быть положительным")
            return False

    def store(self, product, quantity):
        super().store(product, quantity)
        self.inventory.add_stock(product, quantity)

    def maintenance(self):
        print("Техобслуживание после приёма товара (если необходимо)")

# ---------------------------
# 6. Visitor
# ---------------------------

class ProductVisitor(ABC):
    @abstractmethod
    def visit(self, product):
        pass

class CostCalculatorVisitor(ProductVisitor):
    def __init__(self):
        self.total_cost = 0

    def visit(self, product):
        self.total_cost += product.price

class ReportVisitor(ProductVisitor):
    def __init__(self):
        self.report_lines = []

    def visit(self, product):
        line = f"Товар: {product.name}, Тип: {product.get_type()}, Цена: {product.price}"
        self.report_lines.append(line)

    def get_report(self):
        return "\n".join(self.report_lines)

# ---------------------------
# Вспомогательные классы
# ---------------------------

class Inventory:
    def __init__(self):
        self.stock = {}

    def add_stock(self, product, quantity):
        key = (product.get_type(), product.name)
        self.stock[key] = self.stock.get(key, 0) + quantity

    def get_stock(self, product):
        key = (product.get_type(), product.name)
        return self.stock.get(key, 0)

class Database:
    def __init__(self):
        self.supplies = []

    def save_supply(self, product, quantity):
        self.supplies.append((product.name, quantity))
        print(f"Данные о поставке сохранены в БД: {product.name} x{quantity}")

# ---------------------------
# Пользователи системы
# ---------------------------

class Storekeeper:
    def __init__(self, facade, receiving_process):
        self.facade = facade
        self.receiving_process = receiving_process

    def receive_supply(self, product, quantity):
        print("Кладовщик начинает приём поставки...")
        self.receiving_process.receive_product(product, quantity)
        self.facade.process_supply(product, quantity)

    def check_product_availability(self, product):
        self.facade.check_inventory(product)

class Administrator:
    def __init__(self, inventory):
        self.inventory = inventory

    def update_stock(self, product, quantity):
        print(f"Администратор обновляет данные о наличии товара: {product.name} x{quantity}")
        self.inventory.add_stock(product, quantity)

    def manage_accounts(self):
        print("Администратор управляет учётными записями (пример)")

class WarehouseManager:
    def __init__(self, inventory):
        self.inventory = inventory

    def control_stock(self):
        print("Менеджер контролирует запасы:")
        for (ptype, pname), qty in self.inventory.stock.items():
            print(f" - {pname} ({ptype}): {qty} шт.")

    def generate_report(self, product_components):
        print("Менеджер формирует отчёт по складу:")
        report_visitor = ReportVisitor()
        for component in product_components:
            component.accept(report_visitor)
        print(report_visitor.get_report())

    def perform_maintenance(self):
        print("Менеджер выполняет техобслуживание склада")

# ---------------------------
# Демонстрация использования
# ---------------------------

def main():
    # Создаем фабрику продуктов
    factory = ProductFactory()

    # Создаем продукты
    tshirt = factory.create_product("clothing", "Футболка", 500)
    laptop = factory.create_product("electronics", "Ноутбук", 50000)
    apple = factory.create_product("food", "Яблоко", 50)

    # Создаем инвентарь и базу данных
    inventory = Inventory()
    database = Database()

    # Создаем фасад для кладовщика
    facade = WarehouseFacade(inventory, database)

    # Создаем процесс приёма товара для кладовщика
    receiving_process = StorekeeperReceivingProcess(inventory)

    # Создаем пользователей
    storekeeper = Storekeeper(facade, receiving_process)
    admin = Administrator(inventory)
    manager = WarehouseManager(inventory)

    # Кладовщик принимает поставку
    storekeeper.receive_supply(tshirt, 10)
    storekeeper.receive_supply(laptop, 5)
    storekeeper.receive_supply(apple, 100)

    # Администратор обновляет данные о наличии товара
    admin.update_stock(tshirt, 5)

    # Менеджер контролирует запасы
    manager.control_stock()

    # Создаем заказ с помощью билдера
    builder = OrderBuilder()
    order = (builder.add_product(tshirt)
                   .add_product(apple)
                   .set_packaging("Коробка №1")
                   .build())
    print(order)

    # Создаем составные группы товаров (Composite)
    box1 = ProductGroup("Коробка 1")
    box1.add(SingleProduct(tshirt))
    box1.add(SingleProduct(apple))

    box2 = ProductGroup("Коробка 2")
    box2.add(SingleProduct(laptop))

    shipment = ProductGroup("Партия товаров")
    shipment.add(box1)
    shipment.add(box2)

    # Менеджер формирует отчёт по всей партии
    manager.generate_report([shipment])

    # Менеджер выполняет техобслуживание
    manager.perform_maintenance()

    # Используем Visitor для подсчёта стоимости всей партии
    cost_visitor = CostCalculatorVisitor()
    shipment.accept(cost_visitor)
    print(f"Общая стоимость партии: {cost_visitor.total_cost} руб.")

if __name__ == "__main__":
    main()
