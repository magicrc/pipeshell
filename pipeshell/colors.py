GREEN = "\033[92m"
BLUE_BOLD = "\033[1;34m"
WHITE_BOLD = "\033[1;37m"
RESET = "\033[0m"

def colorize(text, color) -> str:
    return f"{color}{text}{RESET}"

def bold_blue(text) -> str:
    return colorize(text, BLUE_BOLD)

def bold_white(text) -> str:
    return colorize(text, WHITE_BOLD)

def green(text) -> str:
    return colorize(text, GREEN )