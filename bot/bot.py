from colorama import Fore, Style, init

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
        except ValueError:
            # Ошибка возникает при некорректной распаковке (например, 'add John').
            # Мы используем это для команды 'add'/'change', где ожидается 2 аргумента.
            return Fore.RED + "Введіть ім'я та номер телефону, будь ласка." + Style.RESET_ALL
        except IndexError:
            # Ошибка возникает при попытке доступа к несуществующему индексу (например, 'phone' без аргументов).
            return Fore.RED + "Введіть аргументи для команди." + Style.RESET_ALL
        except Exception as e:
            # Общий обработчик для непредвиденных ошибок
            return Fore.RED + f"Виникла непередбачена помилка: {e}" + Style.RESET_ALL
    return inner

def parse_input(user_input):
    """
    Розбирає введений користувачем рядок на команду та її аргументи.
    Команда перетворюється у нижній регістр.
    """
    parts = user_input.split()
    if not parts:
        return "", []
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args


# --- тут функции команд ---
@input_error
def add_contact(args, contacts):
    """
    Додає новий контакт до словника contacts.
    Очікує 2 аргументи: ім’я та номер телефону.
    """
    name, phone = args 
    contacts[name] = phone
    return Fore.GREEN + "Контакт додано." + Style.RESET_ALL

@input_error
def change_contact(args, contacts):
    """
    Змінює номер телефону існуючого контакту у словнику contacts.
    Очікує 2 аргументи: ім’я та новий номер телефону.
    """   

    name, phone = args
    if name not in contacts:
        raise KeyError
    
    contacts[name] = phone
    return Fore.GREEN + "Контакт оновлено." + Style.RESET_ALL
    
@input_error
def show_phone(args, contacts):
    """
    Показує номер телефону для вказаного контакту.
    Очікує 1 аргумент: ім’я.
    """       
    name = args[0]
    return contacts[name]


def show_all(contacts):
    """
    Показує всі збережені контакти та їхні номери телефонів.
    Не очікує аргументів.
    """
    if not contacts:
        return Fore.RED + "Немає збережених контактів." + Style.RESET_ALL
    
    result = []
    for name, phone in contacts.items():
        result.append(f"{name}: {phone}")
    return "\n".join(result)


# --- тут основна функція програми ---

def main():
    """
    Основна функція бота, що керує циклом обробки команд.
    """
    contacts = {}
    print(Fore.CYAN + "Вітаю у помічнику-боті!"+ Style.RESET_ALL)

    while True:
        user_input = input(Fore.YELLOW + "Введіть команду: " + Style.RESET_ALL)

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print(Fore.CYAN + "До побачення!" + Style.RESET_ALL)
            break
        elif command == "hello":
            print(Fore.CYAN + "Чим можу допомогти?" + Style.RESET_ALL)
        elif command == "add":
            print(add_contact(args, contacts))  # Викликаємо add_contact
        elif command == "change":
            print(change_contact(args, contacts))  # Викликаємо change_contact
        elif command == "phone":
            print(show_phone(args, contacts))  # Викликаємо show_phone
        elif command == "all":
            print(show_all(contacts))  # Викликаємо show_all
        else:
            print(Fore.RED + "Невідома команда." + Style.RESET_ALL)


if __name__ == "__main__":
    # Этот блок гарантирует, что функция main() будет вызвана только тогда,
    # когда скрипт запускается напрямую, а не импортируется как модуль.
    main()