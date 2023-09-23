from typing import Optional, Tuple, Union
import customtkinter
from customtkinter import *
import stripe
import os
import json
import requests
import click
import asyncio
import discord
from discord import *
import InquirerPy
import colorama

class setupGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x600")
        self.title("StripeBot Setup")

        # Make there be mulitple input boxes to setupo the user's stripe bot. Make there be these following options: prefix, token, webhook, and a button to save the config.
        
        
        self.entry2 = CTkEntry(self, width=300)
        self.entry2.place(x=300, y=150)
        self.label2 = CTkLabel(self, text="Stripe Publishable Key: ")
        self.label2.place(x=150, y=150)
        
        self.entry7 = CTkEntry(self, width=300)
        self.entry7.place(x=290, y=100)
        self.label7 = CTkLabel(self, text="Stripe Secret Key: ")
        self.label7.place(x=150, y=100)
        
        self.entry4 = CTkEntry(self, width=300)
        self.entry4.place(x=250, y=250)
        self.label4 = CTkLabel(self, text="Bot Prefix: ")
        self.label4.place(x=150, y=250)
        
        self.entry6 = CTkEntry(self, width=300)
        self.entry6.place(x=250, y=300)
        self.label6 = CTkLabel(self, text="Bot Token: ")
        self.label6.place(x=150, y=300)

        self.button = CTkButton(self, text="Save and Continue", command=lambda: self.saveConfig({
            "publish_key": self.entry2.get(),
            "secret_key": self.entry7.get(),
            "prefix": self.entry4.get(),
            "bot_token": self.entry6.get()
        }))        
        self.button.place(x=250, y=350)
    
        
    def saveConfig(self, config):
        with open("config.json", "w") as f:
            json.dump(config, f)
        self.destroy()


sysmessage = lambda message: print(f"{colorama.Fore.WHITE}[{colorama.Fore.GREEN}StripeBot{colorama.Fore.WHITE}] {colorama.Fore.CYAN}{message}{colorama.Fore.WHITE}")

def cliApp():
    questions = [
        {
            "type": "list",
            "message": "What would you like to do?",
            "choices": ["Run The Bot", "Setup The Bot", "Install Requirements", "Exit"],
            "name": "action"
        }
    ]
    answers = InquirerPy.prompt(questions)
    
    if answers["action"] == "Run The Bot":
        os.system("python bot.py")
        
    elif answers["action"] == "Setup The Bot":
        sysmessage("Bot Setup GUI opened.")
        setup = setupGUI()
        setup.mainloop()
    
    elif answers["action"] == "Install Requirements":
        sysmessage("Installing requirements...")
        os.system("pip install -r requirements.txt")
        sysmessage("Requirements installed.")    
    
    elif answers["action"] == "Exit":
        exit()
        
cliApp()