import numpy as np
import os
from os import listdir, rename
from os.path import isfile, join
import json


class FileHandler():
    '''
    Die Klasse uebernimmt alle Aufgaben des speicherns
    uebergeben wird ein dictionary und der filepath/filename
    dann wird geschaut ob es das File gibt, wenn es das File mit dem 
    gleichen Zeitstempel gibt dann wird das aktuell existierende Dictionary
    in das json File integriert
    '''
    def __init__(self, path_output=".\\Data_python", filename="test_filex", time_identifier = '20200308_214300'):
        self.path_output = path_output
        self.filename = os.path.join(path_output, time_identifier + "_" + filename + ".json")
        #print(f"init of FileHandler class with self.filename = {self.filename}")
        self._id = time_identifier
    
    def write(self,mydict):
        #print(f"write to file")
        # append old content if it exist
        if os.path.isfile(self.filename):
            try:
                with open(self.filename, "r") as fp:
                    dict_in_file = json.load(fp)
                mydict.update(dict_in_file)
            except:
                os.remove(self.filename)
                print("update failed writing new...")
        # nun kann ich schreiben
        self.__save_dict_as_json(mydict)

    def overwrite(self, mydict):
        self.__save_dict_as_json(mydict)

    def __save_dict_as_json(self, mydict):
        ''' speicherung der relevanten Informationen in einm json file
        '''
        #overwrite any existing file with the same name
        
        with open(self.filename, "w") as fp:   
                    json.dump(mydict, fp)


    def read(self):
        mydict = {'message': 'error'}
        with open(self.filename, "r") as fp:   
            mydict = json.load(fp)
        return mydict



if __name__ == '__main__':
    f = FileHandler()
    mydict= {'teststring': 'testeintrag', 'testzahl': 4}
    f.write(mydict)
    r = f.read()
    for k,v in r.items():
        print(f"key = {k} , {v}")
    mydict= {'teststring2': 'testeintrag2', 'testzahl2': 42}
    f.write(mydict)
    r = f.read()
    for k,v in r.items():
        print(f"key = {k} , {v}")
    mydict = {'x': 'leer'}
    print(f"overwrite")
    f.overwrite(mydict)
    r = f.read()
    for k,v in r.items():
        print(f"key = {k} , {v}")