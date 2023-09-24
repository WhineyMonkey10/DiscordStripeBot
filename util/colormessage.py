import colorama


def colormsg(message):
    return f"{colorama.Fore.WHITE}[{colorama.Fore.GREEN}StripeBot{colorama.Fore.WHITE}] {colorama.Fore.CYAN}{message}{colorama.Fore.WHITE}"
