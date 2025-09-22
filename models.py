from flask_login import UserMixin 

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, password):
        self.id = id_usuario     
        self.usuario = nombre
        self.password = password

    def get_id(self):
        return str(self.id)  # Flask-Login lo usa para identificar al usuario
