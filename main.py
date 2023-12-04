import json
import os
import questionary
from datetime import datetime

class System:
    def __init__(self):        
        self.WORK_PATH = os.getcwd()
        self.CURRENT_TIME = datetime.now().strftime("%Y-%m-%d")
        self.STORAGE_DIR = os.path.join(self.WORK_PATH,"题库目录") 
        self.STORAGE_PATH = os.path.join(self.STORAGE_DIR,f"{self.CURRENT_TIME}_题库.json")
        if not os.path.exists(self.STORAGE_DIR):
            os.mkdir(self.STORAGE_DIR)
            
        

    def read_data(self):
        pass


    def write_data(self):
        pass
    

    def add_topic(self):
        pass
    
    
    def show_topic(self):
        pass
    


def main():
    try:
        instance = System()
        
    except Exception as e:
        print(f"程序崩溃,发生异常:{e}")


if __name__ == "__main__":
    main()