# Este código define una función llamada db_checker que verifica si la conexión a la base de datos es válida. Para hacerlo, utiliza otra
# función llamada validate_connection, que se importa desde un módulo específico (session_windows). El propósito principal es asegurarse
# de que la base de datos esté accesible antes de realizar operaciones con ella.

# Es útil en sistemas donde se necesita confirmar que la base de datos está disponible, como en pruebas, monitoreo o al iniciar una
# aplicación.


from app.db.session_windows import validate_connection

def db_checker():
    # Validar la conexión a la base de datos
    return validate_connection()