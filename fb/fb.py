import os 
import pyrebase

config={
    "apiKey": "AIzaSyDFWBC1_-tqWm5HA8AfNAsmjbvIEa1sfsk",
    "authDomain": "face-detector-285211.firebaseapp.com",
    "databaseURL": "https://face-detector-285211.firebaseio.com",
    "projectId": "face-detector-285211",
    "storageBucket": "face-detector-285211.appspot.com",
    "messagingSenderId": "417890839709",
    "appId": "1:417890839709:web:9344cbaae4a02ede827874",
    "measurementId": "G-MDLVQP2TT0"
}

class Firebase(object):
    __firebase=None
    @staticmethod
    def getInstance():
        if Firebase.__firebase == None:
            Firebase()
        return Firebase.__firebase
    def __init__(self):
        if Firebase.__firebase != None:
            raise Exception("Initialize firebase once!!!")
        else:
            Firebase.__firebase=pyrebase.initialize_app(config)
    
    def upload(self,path,item):

        raise NotImplementedError


    def download(self,path,item):

        raise NotImplementedError
    

    def get_url(self,path,item):

        raise NotImplementedError

    