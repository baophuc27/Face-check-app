from cryptography.fernet import Fernet



class Handler(object):

    def __init__(self,url):
        self.key = self.load_key()
        self.url = url
        self.encrypted_url = self.encrypt_url()

    @classmethod
    def load_key(self):
        return open("image_handler/secret.key","rb").read()

    def encrypt_url(self):

        encoded_message = self.url.encode()
        f = Fernet(self.key)
        encrypted_message = f.encrypt(encoded_message)

        return encrypted_message.decode("utf-8")

    def get_url(self):
        return self.encrypted_url