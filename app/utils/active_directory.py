# Este código en Python permite validar si un usuario es válido en un entorno de Active Directory (AD) utilizando el protocolo LDAP.
# Primero, importa las clases necesarias del módulo ldap3 para establecer una conexión con el servidor AD.
# validate_user_ad que recibe el nombre de usuario, contraseña, dominio, servidor AD y la base DN. Dentro de la función,
# el nombre de usuario completo con el dominio, se conecta al servidor AD y autentica el usuario con las credenciales proporcionadas
# verifica si el usuario existe y si se encuentra, se revisa el atributo userAccountControl para asegurarse de que la cuenta esté activa
# (no deshabilitada). Si todo está correcto, imprime información del usuario (nombre y correo) y retorna True; de lo contrario,
# retorna False y muestra mensajes de error o advertencia según el caso.

from ldap3 import Server, Connection, ALL, NTLM

def validate_user_ad(username: str, password: str, domain: str, ad_server: str, ad_base_dn: str):
    """
    Valida usuario contra Active Directory (LDAP)
    
    :param username: Usuario (sin dominio)
    :param password: Contraseña
    :param domain: Dominio (ejemplo: 'bancolombia.com')
    :param ad_server: Dirección del servidor AD (ejemplo: 'ldap.bancolombia.com')
    :param ad_base_dn: Base DN (ejemplo: 'DC=bancolombia,DC=com')
    :return: True si válido, False si no
    """
    try:
        user = f"{domain}\\{username}"
        server = Server(ad_server, get_info=ALL)
        conn = Connection(server, user=user, password=password, authentication=NTLM, auto_bind=True)
        
        # Si queremos validar que el usuario existe y está activo:
        search_filter = f"(&(sAMAccountName={username})"
        conn.search(ad_base_dn, search_filter, attributes=['userAccountControl', 'displayName', 'mail'])
        
        if not conn.entries:
            print(f"Usuario {username} no encontrado en AD.")
            return False
        
        # Validar estado del usuario (userAccountControl)
        entry = conn.entries[0]
        user_account_control = int(entry.userAccountControl.value)
        # 2 = Cuenta deshabilitada
        if user_account_control & 2:
            print(f"Usuario {username} está deshabilitado.")
            return False
        
        print(f"Usuario {username} válido en AD. Nombre: {entry.displayName.value}, Email: {entry.mail.value}")
        return True
        
    except Exception as e:
        print(f"Error al validar usuario {username}: {e}")
        return False