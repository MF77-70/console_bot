from collections import UserDict

# --- Базові класи для полів ---

class Field:
    """Базовий клас для всіх полів запису."""
    def __init__(self, value):
        # Захищений атрибут для зберігання значення
        self._value = value

    @property
    def value(self):
        """Геттер для отримання значення."""
        return self._value

    @value.setter
    def value(self, new_value):
        """Сеттер для встановлення значення (базова реалізація без перевірок)."""
        self._value = new_value

    def __str__(self):
        # Повертає значення у вигляді рядка
        return str(self._value)


class Name(Field):
    """Клас для зберігання імені контакту (обов’язкове поле)."""
    # Наслідує Field, додаткова логіка наразі не потрібна
    pass


class Phone(Field):
    """Клас для зберігання номера телефону з валідацією."""
    def __init__(self, value):
        # Присвоєння через self.value викликає сеттер для перевірки
        self.value = value 

    @Field.value.setter
    def value(self, new_value):
        """Сеттер із валідацією: номер має складатися з 10 цифр."""
        # Перевірка — чи містить лише цифри та має довжину 10
        if not (new_value.isdigit() and len(new_value) == 10):
            # Якщо перевірку не пройдено — викликаємо помилку
            raise ValueError("Номер телефону повинен містити 10 цифр.")
        
        # Якщо все добре — зберігаємо значення у захищеному атрибуті
        self._value = new_value


# --- Клас запису контакту ---

class Record:
    """Клас для зберігання інформації про контакт: ім’я та список телефонів."""
    def __init__(self, name):
        # Зберігає об’єкт Name (ім’я контакту)
        self.name = Name(name)
        # Зберігає список об’єктів Phone
        self.phones = []

    def add_phone(self, phone_number):
        """Додає новий об’єкт Phone до списку телефонів."""
        # Під час створення Phone автоматично викликається перевірка (валідація)
        phone = Phone(phone_number)
        self.phones.append(phone)

    def find_phone(self, phone_number):
        """Шукає об’єкт Phone за рядковим значенням номера."""
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def remove_phone(self, phone_number):
        """Видаляє об’єкт Phone зі списку за номером."""
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
            return True
        return False

    def edit_phone(self, old_phone, new_phone):
        """Редагує існуючий номер телефону."""
        phone_to_edit = self.find_phone(old_phone)
        
        if phone_to_edit:
            # Присвоєння нового значення через властивість value
            # автоматично викликає сеттер класу Phone для перевірки
            phone_to_edit.value = new_phone
        else:
            # Якщо старий номер не знайдено — піднімаємо виключення
            raise ValueError(f"Старий номер телефону {old_phone} не знайдено.")

    def __str__(self):
        # Формує рядкове представлення: ім’я та всі телефони через '; '
        phones_str = '; '.join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}"


# --- Клас адресної книги ---

class AddressBook(UserDict):
    """Клас для зберігання записів (Record) та керування ними."""
    def add_record(self, record):
        """Додає об’єкт Record до адресної книги."""
        # Ключем є рядкове значення імені
        self.data[record.name.value] = record

    def find(self, name):
        """Знаходить і повертає об’єкт Record за ім’ям."""
        # Використовуємо .get() для безпечного пошуку (повертає None, якщо не знайдено)
        return self.data.get(name)

    def delete(self, name):
        """Видаляє запис із адресної книги за ім’ям."""
        if name in self.data:
            del self.data[name]
        else:
            # Якщо ім’я не знайдено — викликаємо виключення
            raise KeyError(f"Контакт з ім’ям '{name}' не знайдено.")


# --- Блок тестування (демонстрація роботи) ---

if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до книги
    book.add_record(john_record)

    # Створення та додавання запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    print("--- Усі записи в книзі ---")
    for name, record in book.data.items():
        print(record)

    print("\n--- Редагування телефону для John ---")
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")
    print(john)

    print("\n--- Пошук конкретного телефону у записі John ---")
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")

    print("\n--- Видалення запису Jane ---")
    book.delete("Jane")
    print(f"Запис Jane після видалення: {book.find('Jane')}")

    print("\n--- Перевірка валідації (очікується ValueError) ---")
    try:
        john.add_phone("123")  # Невірний формат (менше 10 цифр)
    except ValueError as e:
        print(f"Помилка валідації: {e}")
