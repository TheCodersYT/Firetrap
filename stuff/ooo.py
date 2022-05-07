
import time


class Main():
    """Test function\n
    Python testing"""
    def __init__(self):
        self.number = 0
    
    def call(self):
        if self.number < 1:
            raise SyntaxError("Number is below zero, cannot continue.")
            

        
if __name__ == "__main__":
    main = Main()
    main.call()