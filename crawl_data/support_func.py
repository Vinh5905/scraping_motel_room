import ast
import re
import shutil
from colorama import Fore, Style
from global_variable.variable_static import terminal_width

# Cần chỉnh sửa theo tùy loại text
# style = ['big', 'small', 'danger', 'success']
def print_banner_colored(title: str = '', style='small'):
    text_default = {
        'small': 'FOR TITLE OF SOME SMALL THING :>',
        'big': 'FOR TITLE OF BIGGER THING :>',
        'danger': 'HOLYYYY NOOOO~~ LET TRY AGAINNN',
        'success': 'YESSS~~ ITS WORKINGG'
    }

    title = title.upper() or text_default[style]

    size_max = terminal_width

    match style:
        case 'small':
            banner = "─" * (terminal_width // 2)

            print('\n')
            print(Fore.LIGHTRED_EX + f"╭{banner}╮".center(terminal_width) + Style.RESET_ALL)
            print(Fore.MAGENTA + title.center(terminal_width) + Style.RESET_ALL)
            print(Fore.LIGHTRED_EX + f"╰{banner}╯".center(terminal_width) + Style.RESET_ALL)
        
        case 'big':
            banner = "─" * (terminal_width - 2)

            print('\n')
            print(Fore.YELLOW + f"╭{banner}╮".center(terminal_width) + Style.RESET_ALL  + '\n')
            print(Fore.GREEN + f"║{title.center(terminal_width - 2)}║" + Style.RESET_ALL  + '\n')
            print(Fore.YELLOW + f"╰{banner}╯".center(terminal_width) + Style.RESET_ALL)

        case 'danger':
            title = '────── ⛔ ' + title + ' ⛔ ──────'
            print(Fore.RED + title.center(size_max) + Style.RESET_ALL)

        case 'success':
            title = '────── 🎉 ' + title + ' 🎉 ──────'
            print(Fore.GREEN + title.center(size_max) + Style.RESET_ALL)

def string_to_dict(text: str):
    # Erase indent start and end of string (if not -> IndentationError: unexpected indent)
    text = text.strip()
    # Some marks are wrong
    text = text.replace('`', "'").replace('"', "'")
    # Key need to be in quotes
    text = re.sub(r'(\w+): ', r"'\1': ", text)
    # Change to dict
    value_dict_type = ast.literal_eval(text)

    return value_dict_type

# Sử dụng:
if __name__ == '__main__':
    print("BIG STYLE : ")
    print_banner_colored("", 'big')

    print("SMALL STYLE : ")
    print_banner_colored("", 'small')

    print('DANGER STYLE : ')
    print_banner_colored("", 'danger')

    print('DANGER STYLE : ')
    print_banner_colored("", 'success')
