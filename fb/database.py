import os
from fb.fb import Firebase 
import pyrebase
path='/user'

class Database(Firebase):

    def __init__(self):
        # super(Database,self).__init__()
        firebase=super(Database,self).getInstance()
        self.database=firebase.database()
    
    def upload(self,path,item):
        self.database.child(path).push(item)
    
    
