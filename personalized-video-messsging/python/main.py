import os
from src.PVMessenger import PVMessenger
from constants import *

if __name__ == "__main__":
    
    
    root_dir = os.getcwd()
    
    pvm =  PVMessenger(root_dir, SYNCLABS_API_KEY, ELEVENLABS_API_KEY)
    output_path = pvm.run(INPUT_CSV_PATH, OUTPUT_CSV_PATH) 
    print(f'The final csv output is stored at {output_path}')
    