from universal_class import UniClass as u
import json 

def main(path):
    return u(path)

if __name__ == "__main__":
    path = "sample_data.ini"
    res = main(path)
    