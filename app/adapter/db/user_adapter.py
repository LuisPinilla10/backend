
# Version anterior
# Este código define una clase llamada UserAdapter que extiende de BaseAdapter y se encarga de manejar operaciones relacionadas con
# usuarios, tanto en una base de datos como en Active Directory. Aquí te explico qué hace cada parte:

# from app.adapter.db.base_adapter import BaseAdapter
# from datetime import datetime
# from ldap3 import Server, Connection, ALL, AUTO_BIND_NO_TLS, NONE
# import logging
# import json

# logger = logging.getLogger(__name__)

# class UserAdapter(BaseAdapter):
#     def __init__(self):
#         super().__init__()

#     def validate_user_active_directory(self, username: str, password: str) -> bool:
#         ad_server = "bancolombia.corp"
#         ad_base_dn = "OU=Banistmo,OU=Usuarios,DC=bancolombia,DC=corp"
#         user_dn = f"{username}@bancolombia.corp"

#         try:
#             server = Server(ad_server, get_info=NONE)
#             print(server)
#             print("-----")
#             conn = Connection(server, user=user_dn, password=password, auto_bind=AUTO_BIND_NO_TLS, receive_timeout=5)
#             print(conn)
#             print("-----")
#             search_filter = f"(&(sAMAccountName={username})*"
#             print(search_filter)
#             print("-----")
#             conn.search(ad_base_dn, search_filter, attributes=['userAccountControl', 'displayName', 'mail'])
#             print(conn)
#             print("-----")

#             """" Responde
#             displayName: Juan Esteban Valencia
#             mail: juan.e.valencia@banistmo.com
#             userAccountControl: 512
#             """

#             if not conn.entries:
#                 logger.warning(f"Usuario {username} no encontrado en AD.")
#                 return False

#             entry = conn.entries[0]
#             user_account_control = int(entry.userAccountControl.value)
#             if user_account_control & 2:
#                 logger.warning(f"Usuario {username} está deshabilitado en AD.")
#                 return False

#             logger.info(f"Usuario {username} válido en AD: {entry.displayName.value}, {entry.mail.value}")
#             return True

#         except Exception as e:
#             logger.error(f"Error al validar usuario {username} contra AD: {e}")
#             return False

#     def user_exists(self, username: str):
#         query = "EXEC dbo.sp_user_exists :username"
#         return self.fetch_one(query, {"username": username})

#     def get_user_by_username(self, username: str):
#         try:
#             query = "EXEC dbo.sp_get_user_by_username :username"
#             result = self.fetch_one(query, {"username": username})
#             if result:
#                 return {
#                     "user_name": result[0],
#                     "full_name": result[1],
#                     "email": result[2],
#                     "status": result[3],
#                     "created_at": result[4],
#                     "updated_at": result[5]
#                 }
#             return None
#         except Exception as e:
#             logger.error(f"❌ Error al consultar usuario {username} con SP: {e}")
#             return None

#     # def get_cesantias_by_user(self, username str):
#     #     query = "EXEC dbo.sp_cesantias_by_username: username"
#     #     result = self.fetch_one(query, {"username": username})
#     #     if result:
#     #         return {
#     #             "user_name": result[0],
#     #             "full_name": result[1]
#     #         }

#     def create_user(self, username: str, full_name: str, email: str, actor: str):
#         logger.info(f"▶ create_user iniciado con: {username}, {full_name}, {email}")

#         if not self.validate_user_active_directory(username):
#             return "Usuario no válido en directorio activo"

#         if self.user_exists(username):
#             return "Usuario ya existe"

#         try:
#             self.execute_query("""
#                 EXEC dbo.sp_create_user :username, :full_name, :email
#                 """, {
#                     "username": username,
#                     "full_name": full_name,
#                     "email": email
#                 })
#             logger.info("▶ Usuario insertado vía SP")
#         except Exception as e:
#             logger.error(f"❌ Error al insertar usuario con SP: {e}")
#             return f"Error al insertar usuario: {e}"

#         self.insert_log(actor, "create", f"Crear usuario: {username}")
#         return "Usuario creado exitosamente"

#     import json

#     def update_user(self, username: str, actor: str, full_name: str = "", email: str = "", status: int = None, log_action: str = "Actualizar usuario", last_access: datetime = None):
#         try:
#             json_data = json.dumps({
#                 "actor": actor,
#                 "detail": f"{log_action}: {username}",
#                 "last_access": last_access.isoformat() if last_access else None
#             })

#             self.execute_query("EXEC dbo.sp_update_user :data", {"data": json_data})
#         except Exception as e:
#             logger.error(f"❌ Error actualizando usuario con SP JSON: {e}")
#             return f"Error al actualizar: {e}"

#         return "Usuario actualizado exitosamente"

#     def get_user(self, username: str):
#         user = self.user_exists(username)
#         return user or "Usuario no encontrado"

#     def assign_role(self, rol_id: int, username: str, asigno: int):
#         user = self.user_exists(username)
#         if not user or user.status != 1:
#             return "Usuario no válido"

#         try:
#             self.execute_query("""
#                 EXEC dbo.sp_assign_role :rol_id, :username, :asigno
#                 """, {
#                     "rol_id": rol_id,
#                     "username": username,
#                     "asigno": asigno
#                 })
#         except Exception as e:
#             logger.error(f"❌ Error en assign_role con SP: {e}")
#             return f"Error al asignar/desasignar rol: {e}"

#         action = "Asignar rol" if asigno else "Desasignar rol"
#         self.insert_log(username, action)
#         return f"Rol {'asignado' if asigno else 'desasignado'} correctamente"

# app/adapter/db/user_adapter.py
# CAMBIOS MÍNIMOS: Solo agregar función para validar empleados autorizados

from app.adapter.db.base_adapter import BaseAdapter
from datetime import datetime
from ldap3 import Server, Connection, ALL, AUTO_BIND_NO_TLS, NONE
import logging
import json

logger = logging.getLogger(__name__)

class UserAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()

    # ← NUEVO: Lista de empleados autorizados (misma del frontend)
    MOCK_EMPLEADOS = [
        {"idEmpleado": 1, "nombre": "Luis Alberto Reyes Pinilla", "cedula": "8-984-369", "nombreEmpresa": "BANISTMO S.A."},
        {"idEmpleado": 2, "nombre": "María Elena Rodríguez Santos", "cedula": "8-756-432", "nombreEmpresa": "BANISTMO S.A."},
        {"idEmpleado": 3, "nombre": "José Antonio Méndez Vargas", "cedula": "8-123-789", "nombreEmpresa": "BANISTMO S.A."},
        {"idEmpleado": 4, "nombre": "Carmen Patricia González López", "cedula": "8-456-123", "nombreEmpresa": "BANISTMO S.A."},
        {"idEmpleado": 5, "nombre": "Roberto Carlos Herrera Díaz", "cedula": "8-789-456", "nombreEmpresa": "BANISTMO S.A."},
        {"idEmpleado": 6, "nombre": "Ana Isabel Morales Cruz", "cedula": "8-321-654", "nombreEmpresa": "BANISTMO S.A."},
        {"idEmpleado": 7, "nombre": "Pedro Miguel Castillo Ruiz", "cedula": "8-654-987", "nombreEmpresa": "BANISTMO S.A."},
        {"idEmpleado": 8, "nombre": "Sofía Alejandra Vega Peña", "cedula": "8-987-321", "nombreEmpresa": "BANISTMO S.A."}
    ]

    def validate_user_active_directory(self, username: str, password: str) -> bool:
        ad_server = "bancolombia.corp"
        ad_base_dn = "OU=Banistmo,OU=Usuarios,DC=bancolombia,DC=corp"
        user_dn = f"{username}@bancolombia.corp"

        try:
            server = Server(ad_server, get_info=NONE)
            print(server)
            print("-----")
            conn = Connection(server, user=user_dn, password=password, auto_bind=AUTO_BIND_NO_TLS, receive_timeout=5)
            print(conn)
            print("-----")
            search_filter = f"(&(sAMAccountName={username})*"
            print(search_filter)
            print("-----")
            conn.search(ad_base_dn, search_filter, attributes=['userAccountControl', 'displayName', 'mail'])
            print(conn)
            print("-----")

            """" Responde
            displayName: Juan Esteban Valencia
            mail: juan.e.valencia@banistmo.com
            userAccountControl: 512
            """

            if not conn.entries:
                logger.warning(f"Usuario {username} no encontrado en AD.")
                return False

            entry = conn.entries[0]
            user_account_control = int(entry.userAccountControl.value)
            if user_account_control & 2:
                logger.warning(f"Usuario {username} está deshabilitado en AD.")
                return False

            logger.info(f"Usuario {username} válido en AD: {entry.displayName.value}, {entry.mail.value}")
            return True

        except Exception as e:
            logger.error(f"Error al validar usuario {username} contra AD: {e}")
            return False

    # ← NUEVO: Validar si un usuario es empleado autorizado (misma lógica del frontend)
    def validate_employee_from_msal(self, user_email: str, user_name: str):
        """Valida si un usuario de MSAL está en la lista de empleados autorizados"""
        try:
            logger.info(f"🔍 Validando empleado: {user_email} - {user_name}")
            
            # Buscar empleado que coincida
            for empleado in self.MOCK_EMPLEADOS:
                # Verificación por email corporativo
                email_match = self._match_by_email(user_email, empleado)
                # Verificación por nombre
                name_match = self._match_by_name(user_name, empleado['nombre'])
                
                if email_match or name_match:
                    logger.info(f"✅ Usuario autorizado: {empleado}")
                    return empleado
            
            logger.warning(f"❌ Usuario NO autorizado: {user_email}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error validando empleado: {e}")
            return None

    def _match_by_email(self, user_email: str, empleado: dict) -> bool:
        """Misma lógica que el frontend para verificar email"""
        if not user_email:
            return False
        
        email = user_email.lower()
        dominios_banistmo = ['banistmo.com', 'banistmo.pa', 'banistmo.com.pa']
        
        # Verificar dominio
        es_banistmo = any(dominio in email for dominio in dominios_banistmo)
        if not es_banistmo:
            return False
        
        # Verificar nombre en email
        nombre_partes = empleado['nombre'].lower().split(' ')
        nombre_partes = [parte for parte in nombre_partes if len(parte) > 2]
        return any(parte in email for parte in nombre_partes)

    def _match_by_name(self, user_name: str, empleado_nombre: str) -> bool:
        """Misma lógica que el frontend para verificar nombre"""
        if not user_name or len(user_name) < 3:
            return False
        
        user_name_clean = user_name.lower().strip()
        empleado_name_clean = empleado_nombre.lower().strip()
        
        # Verificar coincidencia completa
        if empleado_name_clean in user_name_clean or user_name_clean in empleado_name_clean:
            return True
        
        # Verificar partes del nombre (requiere 2+ coincidencias)
        user_parts = [part for part in user_name_clean.split(' ') if len(part) > 2]
        empleado_parts = [part for part in empleado_name_clean.split(' ') if len(part) > 2]
        
        coincidencias = []
        for user_part in user_parts:
            for emp_part in empleado_parts:
                if emp_part in user_part or user_part in emp_part:
                    coincidencias.append(user_part)
                    break
        
        return len(coincidencias) >= 2

    # ← Resto del código existente sin cambios...
    def user_exists(self, username: str):
        query = "EXEC dbo.sp_user_exists :username"
        return self.fetch_one(query, {"username": username})

    def get_user_by_username(self, username: str):
        try:
            query = "EXEC dbo.sp_get_user_by_username :username"
            result = self.fetch_one(query, {"username": username})
            if result:
                return {
                    "user_name": result[0],
                    "full_name": result[1],
                    "email": result[2],
                    "status": result[3],
                    "created_at": result[4],
                    "updated_at": result[5]
                }
            return None
        except Exception as e:
            logger.error(f"❌ Error al consultar usuario {username} con SP: {e}")
            return None

    def create_user(self, username: str, full_name: str, email: str, actor: str):
        logger.info(f"▶ create_user iniciado con: {username}, {full_name}, {email}")

        if not self.validate_user_active_directory(username):
            return "Usuario no válido en directorio activo"

        if self.user_exists(username):
            return "Usuario ya existe"

        try:
            self.execute_query("""
                EXEC dbo.sp_create_user :username, :full_name, :email
                """, {
                    "username": username,
                    "full_name": full_name,
                    "email": email
                })
            logger.info("▶ Usuario insertado vía SP")
        except Exception as e:
            logger.error(f"❌ Error al insertar usuario con SP: {e}")
            return f"Error al insertar usuario: {e}"

        self.insert_log(actor, "create", f"Crear usuario: {username}")
        return "Usuario creado exitosamente"

    def update_user(self, username: str, actor: str, full_name: str = "", email: str = "", status: int = None, log_action: str = "Actualizar usuario", last_access: datetime = None):
        try:
            json_data = json.dumps({
                "actor": actor,
                "detail": f"{log_action}: {username}",
                "last_access": last_access.isoformat() if last_access else None
            })

            self.execute_query("EXEC dbo.sp_update_user :data", {"data": json_data})
        except Exception as e:
            logger.error(f"❌ Error actualizando usuario con SP JSON: {e}")
            return f"Error al actualizar: {e}"

        return "Usuario actualizado exitosamente"

    def get_user(self, username: str):
        user = self.user_exists(username)
        return user or "Usuario no encontrado"

    def assign_role(self, rol_id: int, username: str, asigno: int):
        user = self.user_exists(username)
        if not user or user.status != 1:
            return "Usuario no válido"

        try:
            self.execute_query("""
                EXEC dbo.sp_assign_role :rol_id, :username, :asigno
                """, {
                    "rol_id": rol_id,
                    "username": username,
                    "asigno": asigno
                })
        except Exception as e:
            logger.error(f"❌ Error en assign_role con SP: {e}")
            return f"Error al asignar/desasignar rol: {e}"

        action = "Asignar rol" if asigno else "Desasignar rol"
        self.insert_log(username, action)
        return f"Rol {'asignado' if asigno else 'desasignado'} correctamente"