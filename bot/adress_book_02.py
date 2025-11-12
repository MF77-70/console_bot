import pickle
from collections import UserDict, defaultdict
from datetime import datetime, timedelta

class AddressBook(UserDict):
    """Клас для зберігання записів (Record) та керування ними."""
    
    def add_record(self, record):
        """Додає об’єкт Record до адресної книги."""
        self.data[record.name.value] = record

    def find(self, name):
        """Знаходить і повертає об’єкт Record за ім’ям."""
        return self.data.get(name)

    def delete(self, name):
        """Видаляє запис із адресної книги за ім’ям."""
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Контакт з ім’ям '{name}' не знайдено.")

    def get_upcoming_birthdays(self):
        """
        Повертає список користувачів, яких потрібно привітати по днях на наступному тижні.
        """
        today = datetime.today().date()
        upcoming_birthdays = defaultdict(list)
        
        for record in self.data.values():
            if record.birthday is None:
                continue
            
            # Конвертуємо збережену дату народження (рядок DD.MM.YYYY) в об'єкт date
            bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            
            # Замінюємо рік на поточний
            bday_this_year = bday_date.replace(year=today.year)
            
            # Якщо день народження вже минув у цьому році, перевіряємо наступний рік
            if bday_this_year < today:
                bday_this_year = bday_date.replace(year=today.year + 1)
            
            # Розраховуємо різницю в днях
            days_difference = (bday_this_year - today).days
            
            # Перевіряємо, чи день народження припадає на наступні 7 днів (включно з сьогодні)
            if 0 <= days_difference <= 7:
                congratulation_date = bday_this_year
                
                # Переносимо привітання з вихідних на наступний понеділок
                if congratulation_date.weekday() >= 5: # 5=Субота, 6=Неділя
                    days_to_monday = 7 - congratulation_date.weekday()
                    congratulation_date += timedelta(days=days_to_monday)
                
                # Форматуємо дату для ключа
                date_key = congratulation_date.strftime("%d.%m.%Y")
                upcoming_birthdays[date_key].append(record.name.value)
                
        return upcoming_birthdays

    def save_to_file(self, filename):
        """Зберігає об'єкт AddressBook у файл за допомогою pickle."""
        with open(filename, "wb") as f: # wb - write binary
            pickle.dump(self, f)

    @classmethod
    def load_from_file(cls, filename):
        """Завантажує об'єкт AddressBook з файлу."""
        try:
            with open(filename, "rb") as f: # rb - read binary
                return pickle.load(f)
        except FileNotFoundError:
            # Якщо файл не знайдено, повертаємо новий порожній об'єкт AddressBook
            return cls()
        except Exception:
            # Обробка інших помилок (например, повреждение файла)
            return cls()
