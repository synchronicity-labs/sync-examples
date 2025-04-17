import os
from src.Translator import Translator
from args import Args

if __name__ == "__main__":

    root_dir = os.getcwd()
    args = Args()
    translator =  Translator(root_dir, args)
    translator.run() 
    