import pyrebase
from fb.fb import Firebase 

class Storage(Firebase):
    def __init__(self):
        # firebase=super(Storage,self).__init__()
        firebase=super(Storage,self).getInstance()
        self.storage=firebase.storage()

    def upload(self,item,path):
        try:
            self.storage.child(path).put(item)
        except Exception as e:
            return f"There is an error: {e}"
    
    def download(self,item,path):
        try:
            self.storage.child(path).download(item)
        except Exception as e:
            return f"There is an error: {e}"
    
    def get_link(self,path):
        try:
            link=self.storage.child(path).get_url(None)
            return link
        except Exception as e:
            return f"There is an error: {e}"
        