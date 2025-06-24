import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from functions.run_python import run_python_file

def run_tests():
    print("== Test 1: Run main.py ==")
    print(run_python_file("calculator", "main.py"))
    print("\n" + "="*60 + "\n")

    print("== Test 2: Run tests.py ==")
    print(run_python_file("calculator", "tests.py"))
    print("\n" + "="*60 + "\n")

    print("== Test 3: Attempt to run ../main.py (outside dir) ==")
    print(run_python_file("calculator", "../main.py"))
    print("\n" + "="*60 + "\n")

    print("== Test 4: Run nonexistent.py (doesn't exist) ==")
    print(run_python_file("calculator", "nonexistent.py"))
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    run_tests()

