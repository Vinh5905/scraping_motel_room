import ast
import re
import shutil
import json
from pathlib import Path
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

def reset_previous_crawl():
    previous_multi_crawl_path = Path('./working_with_file/save_data/previous_crawl_info.json')

    try:
        with open(previous_multi_crawl_path, 'r') as file:
            previous_multi_crawl = json.load(file)

        for index in range(len(previous_multi_crawl['running_thread'])):
            previous_multi_crawl['running_thread'][index]['isCrawling'] = False

        with open(previous_multi_crawl_path, 'w') as file:
            json.dump(previous_multi_crawl, file)
    except:
        return        

# Sử dụng:
if __name__ == '__main__':
    # print("BIG STYLE : ")
    # print_banner_colored("", 'big')

    # print("SMALL STYLE : ")
    # print_banner_colored("", 'small')

    # print('DANGER STYLE : ')
    # print_banner_colored("", 'danger')

    # print('DANGER STYLE : ')
    # print_banner_colored("", 'success')
    reset_previous_crawl()
