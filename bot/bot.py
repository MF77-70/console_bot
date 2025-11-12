import pickle
from collections import UserDict, defaultdict
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# --- Инициализация и Декоратор ---

# Инициализируем colorama для корректной работы на разных ОС
init(autoreset=True)

def input_error(func):
    """
    Декоратор для обработки исключений KeyError, ValueError и IndexError,
    возникающих в функциях-обработчиках команд.
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError: 
            # Ошибка возникает, когда ключ (имя контакта) не найден в словаре.
            return Fore.RED + "Контакт не знайдено." + Style.RESET_ALL
        except ValueError as e:
            # Улучшенная обработка ValueError для более точных сообщений
            if "Номер телефону" in str(e) or "Invalid date format" in str(e) or "Старий номер телефону" in str(e):
                return Fore.RED + str(e) + Style.RESET_ALL
            # Общая ошибка распаковки (не хватает аргументов)
            return Fore.RED + "Введіть ім'я та номер телефону, будь ласка." + Style.RESET_ALL 
        except IndexError: 
            # Ошибка возникает при попытке доступа к несуществующему индексу (например, 'phone' без аргументов).
            return Fore.RED + "Введіть аргументи для команди." + Style.RESET_ALL
        except Exception as e:
            # Общий обработчик для непредвиденных ошибок
            return Fore.RED + f"Виникла непередбачена помилка: {e}" + Style.RESET_ALL
    return inner

# --- Функции Парсера ---

def parse_input(user_input):
    """
    Розбирає введений користувачем рядок на команду та її аргументи.
    Команда перетворюється у нижній регістр.
    """
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd = parts[0].lower()
    args = parts[1:]
    return cmd, args

# --- ООП-Модели ---

class Field:
    """Базовий клас для всіх полів запису."""
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __str__(self):
        return str(self._value)

class Name(Field):
    """Клас для зберігання імені контакту."""
    pass

class Phone(Field):
    """Клас для зберігання номера телефону з валідацією (10 цифр)."""
    def __init__(self, value):
        self.value = value 

    @Field.value.setter
    def value(self, new_value):
        if not (new_value.isdigit() and len(new_value) == 10):
            raise ValueError("Номер телефону повинен містити 10 цифр.")
        self._value = new_value

class Birthday(Field):
    """Клас для зберігання дати народження з валідацією формату DD.MM.YYYY."""
    def __init__(self, value):
        self.value = value

    @Field.value.setter
    def value(self, new_value):
        try:
            # Перевірка коректності формату DD.MM.YYYY
            datetime.strptime(new_value, "%d.%m.%Y")
        except ValueError:
            # Якщо формат невірний, викликаємо помилку
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
        self._value = new_value

class Record:
    """Клас для зберігання інформації про контакт: ім'я, телефони та день народження."""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None 

    def add_phone(self, phone_number):
        """Додає новий об'єкт Phone в список."""
        phone = Phone(phone_number)
        self.phones.append(phone)

    def add_birthday(self, birthday):
        """Додає день народження до контакту."""
        self.birthday = Birthday(birthday)

    def find_phone(self, phone_number):
        """Ищет объект Phone по строковому представлению номера."""
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def remove_phone(self, phone_number):
        """Удаляет объект Phone из списка по номеру."""
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
            return True
        return False

    def edit_phone(self, old_phone, new_phone):
        """Редагує існуючий номер телефону."""
        phone_to_edit = self.find_phone(old_phone)
        
        if phone_to_edit:
            # Присваивание вызывает сеттер Phone для валидации
            phone_to_edit.value = new_phone
        else:
            raise ValueError(f"Старий номер телефону {old_phone} не знайдено.")

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    """Клас для зберігання записів (Record) та керування ними, з функціоналом збереження/завантаження."""
    
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Контакт з ім'ям '{name}' не знайдено.")

    def get_upcoming_birthdays(self):
        """
        Повертає список користувачів, яких потрібно привітати по днях на наступному тижні.
        """
        today = datetime.today().date()
        upcoming_birthdays = defaultdict(list)
        
        for record in self.data.values():
            if record.birthday is None:
                continue
            
            bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            bday_this_year = bday_date.replace(year=today.year)
            
            if bday_this_year < today:
                bday_this_year = bday_date.replace(year=today.year + 1)
            
            days_difference = (bday_this_year - today).days
            
            if 0 <= days_difference <= 7:
                congratulation_date = bday_this_year
                
                # Переносимо привітання з вихідних на наступний понеділок
                if congratulation_date.weekday() >= 5: # 5=Субота, 6=Неділя
                    days_to_monday = 7 - congratulation_date.weekday()
                    congratulation_date += timedelta(days=days_to_monday)
                
                date_key = congratulation_date.strftime("%d.%m.%Y")
                upcoming_birthdays[date_key].append(record.name.value)
                
        return upcoming_birthdays

    def save_to_file(self, filename):
        """Зберігає об'єкт AddressBook у файл за допомогою pickle."""
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load_from_file(cls, filename):
        """Завантажує об'єкт AddressBook з файлу."""
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return cls()
        except Exception:
            return cls()

# --- Функции-Обработчики ---

@input_error
def add_contact(args, book: AddressBook):
    """
    Додає новий контакт або телефон до існуючого контакту.
    Очікує: [ім'я] [телефон].
    """
    name, phone, *_ = args 
    record = book.find(name)
    message = Fore.GREEN + "Контакт оновлено." + Style.RESET_ALL
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = Fore.GREEN + "Контакт додано." + Style.RESET_ALL
    
    record.add_phone(phone)
    
    return message

@input_error
def change_contact(args, book: AddressBook):
    """
    Змінює номер телефону існуючого контакту.
    Очікує 3 аргументи: [ім’я] [старий номер] [новий номер].
    """
    name, old_phone, new_phone = args
    
    record = book.find(name)
    if record is None:
        raise KeyError 
    
    record.edit_phone(old_phone, new_phone)
    return Fore.GREEN + f"Телефон {old_phone} для контакту {name} оновлено на {new_phone}." + Style.RESET_ALL

@input_error
def show_phone(args, book: AddressBook):
    """
    Показує всі номери телефонів для вказаного контакту.
    Очікує 1 аргумент: [ім’я].
    """
    name = args[0]
    
    record = book.find(name)
    if record is None:
        raise KeyError
        
    phones_str = '; '.join(p.value for p in record.phones)
    return f"{Fore.CYAN}Контакт {name}:{Style.RESET_ALL} {phones_str}"

@input_error
def show_all(book: AddressBook):
    """
    Показує всі збережені контакти.
    """
    if not book.data:
        return Fore.RED + "Немає збережених контактів." + Style.RESET_ALL
    
    result = []
    for record in book.data.values():
        result.append(str(record))
        
    return "\n".join(result)

@input_error
def add_birthday(args, book: AddressBook):
    """
    Додає дату народження до контакту.
    Очікує: [ім'я] [дата народження DD.MM.YYYY].
    """
    name, birthday, *_ = args
    
    record = book.find(name)
    if record is None:
        raise KeyError 
    
    record.add_birthday(birthday) 
    return Fore.GREEN + f"День народження для контакту {name} додано." + Style.RESET_ALL

@input_error
def show_birthday(args, book: AddressBook):
    """
    Показує день народження контакту.
    Очікує 1 аргумент: [ім’я].
    """
    name = args[0]
    
    record = book.find(name)
    if record is None:
        raise KeyError
    
    if record.birthday:
        return Fore.CYAN + f"День народження {name}:" + Style.RESET_ALL + f" {record.birthday.value}"
    else:
        return Fore.RED + f"День народження для контакту {name} не встановлено." + Style.RESET_ALL

@input_error
def birthdays(args, book: AddressBook):
    """
    Повертає список користувачів, яких потрібно привітати по днях на наступному тижні.
    """
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return Fore.CYAN + "Наступного тижня іменинників немає." + Style.RESET_ALL
    
    output = [Fore.CYAN + "Наступні дні народження:" + Style.RESET_ALL]
    
    # Сортируем даты для последовательного вывода
    sorted_dates = sorted(upcoming.keys(), key=lambda x: datetime.strptime(x, "%d.%m.%Y"))
    
    for date_str in sorted_dates:
        names = ", ".join(upcoming[date_str])
        output.append(f"{date_str}: {names}")
        
    return "\n".join(output)

@input_error
def delete_contact(args, book: AddressBook):
    """
    Видаляє запис контакту з AddressBook.
    Очікує 1 аргумент: ім'я.
    """
    name = args[0]
    book.delete(name)
    return Fore.GREEN + f"Контакт {name} видалено." + Style.RESET_ALL

# --- Основная Функция ---

FILE_NAME = "address_book.bin"

def main():
    """
    Основна функція бота, що керує циклом обробки команд.
    """
    # Завантажуємо дані при запуску.
    book = AddressBook.load_from_file(FILE_NAME)
    
    print(Fore.CYAN + "Вітаю у помічнику-боті!"+ Style.RESET_ALL)

    while True:
        user_input = input(Fore.YELLOW + "Введіть команду: " + Style.RESET_ALL)

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            # Зберігаємо дані перед виходом
            book.save_to_file(FILE_NAME)
            print(Fore.CYAN + "До побачення! Дані збережено." + Style.RESET_ALL)
            break
        elif command == "hello":
            print(Fore.CYAN + "Чим можу допомогти?" + Style.RESET_ALL)
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "delete":
            print(delete_contact(args, book))
        else:
            print(Fore.RED + "Невідома команда." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
