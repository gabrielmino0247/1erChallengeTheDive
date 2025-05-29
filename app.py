
import random
import sqlite3
from datetime import datetime

# Crear conexión y tabla si no existe
conexion = sqlite3.connect("partidas.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_partida INTEGER,
    turno INTEGER,
    jugador TEXT,
    tipo_control TEXT,
    desde_x INTEGER,
    desde_y INTEGER,
    hasta_x INTEGER,
    hasta_y INTEGER,
    tablero TEXT,
    FOREIGN KEY(id_partida) REFERENCES partidas(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modo TEXT,
    resultado TEXT,
    turnos_totales INTEGER,
    fecha TEXT
)
""")

conexion.commit()  #el commit es como en git, guarda los cambios en este caso en la bbdd

def guardar_movimiento_sql(cursor, jugada, id_partida):
    '''
    Guarda un movimiento en la base de datos
    '''
    cursor.execute("""
        INSERT INTO movimientos (
            id_partida, turno, jugador, tipo_control,
            desde_x, desde_y, hasta_x, hasta_y, tablero
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_partida,
        jugada["turno"],
        jugada["jugador"],
        jugada["tipo_control"],
        jugada["desde"][0],
        jugada["desde"][1],
        jugada["hasta"][0],
        jugada["hasta"][1],
        str(jugada["tablero"])
    ))


class Juego:
    def __init__(self, gato_pos, raton_pos, dimensiones=(8,8)):
        self.turnos = 0
        self.dimensiones = dimensiones
        self.gato = gato_pos
        self.raton = raton_pos
        self.tablero = [['.' for _ in range(self.dimensiones[1])] for _ in range(self.dimensiones[0])] #forma muy eficiente de crear el tablero
        self.obstaculos = self.generar_obstaculos(12) 
        for obs in self.obstaculos:
            self.tablero[obs[0]][obs[1]] = '█'
        self.tablero[self.gato[0]][self.gato[1]] = 'G'
        self.tablero[self.raton[0]][self.raton[1]] = 'R'

    def copiar_estado(self):
        # Esta es la forma correcta de copiar el estado: crea una nueva instancia con los mismos datos
        nuevo_juego = Juego(self.gato, self.raton, self.dimensiones)
        nuevo_juego.turnos = self.turnos # se debe copiar SI O SIII esta parte
        return nuevo_juego
    
    def es_posicion_valida(self, pos):
        '''Verifica si la posición está dentro del tablero y no hay un obstáculo.'''
        dentro_del_tablero = 0 <= pos[0] < self.dimensiones[0] and 0 <= pos[1] < self.dimensiones[1]
        libre_de_obstaculo = pos not in self.obstaculos
        return dentro_del_tablero and libre_de_obstaculo
    
    def generar_obstaculos(self, cantidad):
        '''Genera una cantidad elegida de obstáculos en posiciones aleatorias del tablero.'''
        obstaculos = set()
        while len(obstaculos) < cantidad:
            fila = random.randint(0, self.dimensiones[0] - 1)
            col = random.randint(0, self.dimensiones[1] - 1)
            pos = (fila, col)
            
            if pos != self.gato and pos != self.raton:
                obstaculos.add(pos)
        
        return list(obstaculos)

    def max_turnos(self):
        return ((self.dimensiones[0] + self.dimensiones[1]) // 2 ) # Definimos una cantidad máxima de turnos como la mitad del perímetro del tablero para que no se incline  siempre hacia algun personaje
    
    def imprimir_tablero(self):
        for obs in self.obstaculos:
            self.tablero[obs[0]][obs[1]] = '█'
        for fila in self.tablero:
            print(' '.join(fila)) #sirve como unircadenas en EXCEL 
        print(f"Gato en: {self.gato}, Ratón en: {self.raton}")
    
    def imprimir_tablero_final(self):
        for obs in self.obstaculos:
            self.tablero[obs[0]][obs[1]] = '█'
        for fila in self.tablero:
            print(' '.join(fila))  #sirve como unircadenas en EXCEL 

    def mover_gato(self, nueva_pos, ruido=False):
        if self.es_posicion_valida(nueva_pos):
            self.tablero[self.gato[0]][self.gato[1]] = '.'
            self.gato = nueva_pos
            if self.gato == self.raton:
                self.tablero[self.gato[0]][self.gato[1]] = 'X'  
            else:
                self.tablero[self.gato[0]][self.gato[1]] = 'G'
        else:
            if not ruido:
                print("Movimiento inválido para el gato.")

    def mover_raton(self, nueva_pos, ruido=False):
        if self.es_posicion_valida(nueva_pos):
            self.tablero[self.raton[0]][self.raton[1]] = '.'
            self.raton = nueva_pos
            self.tablero[self.raton[0]][self.raton[1]] = 'R'
            if self.raton == self.gato:
                self.tablero[self.raton[0]][self.raton[1]]= 'X'
        else:
            if not ruido:
                print("Movimiento inválido para el ratón.")   #este era el mensaje para testear cuantas veces se llamaba y salia mal su movimiento, pero para el juego se usa ruido true para que no se vea

    def obtener_posibles_movimientos(self, personaje_pos, es_raton=False):
        movimientos_posibles = []
        
        # Define los movimientos para el gato en 8 direcciones
        direcciones_gato = [(-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinales
                             (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonales
                            ]    

        # Define los movimientos para el ratón en 8 direcciones
        direcciones_raton = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinales
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonales
        ]

        direcciones_a_usar = direcciones_raton if es_raton else direcciones_gato

        for dx, dy in direcciones_a_usar:
            nueva_pos = (personaje_pos[0] + dx, personaje_pos[1] + dy)
            if self.es_posicion_valida(nueva_pos):
                movimientos_posibles.append(nueva_pos)
        return movimientos_posibles

    def es_gato_ganador(self): # El gato gana si su posición es igual a la del ratón
        return self.gato == self.raton
    
    def es_raton_ganador(self):  # El ratón gana si sobrevive la cantidad máxima de turnos sin ser atrapado
        return self.turnos >= self.max_turnos() and not self.es_gato_ganador()

    def es_fin_de_juego(self): # El juego termina si el gato gana O el ratón gana
        return self.es_gato_ganador() or self.es_raton_ganador()    

    def evaluar_estado(self):
        if self.es_gato_ganador():
            return 1000  # Puntuación muy alta para el gato (maximizador)
        
        if self.es_raton_ganador():
            return -1000 # Puntuación muy baja para el gato (victoria del ratón)

        '''Heurística para estados intermedios:
        Usamos la distancia de Manhattan: abs(x1-x2) + abs(y1-y2)
        Cuanto menor sea la distancia entre gato y ratón, mejor para el gato.
        Por lo tanto, regresamos un valor negativo de la distancia, así Minimax
        intentará MINIMIZAR la distancia (que se traduce en MAXIMIZAR - distancia)
        '''
        distancia = abs(self.gato[0] - self.raton[0]) + abs(self.gato[1] - self.raton[1])
        return -distancia
    
    def minimax(self, estado, profundidad, es_turno_maximizador):
        #1 Casos Base: Si el juego ha terminado o hemos llegado a la profundidad límite
        if estado.es_fin_de_juego() or profundidad == 0:
            return estado.evaluar_estado()

        #2 Turno del Jugador Maximizador (Gato)
        if es_turno_maximizador: # El gato quiere maximizar la puntuación
            mejor_valor = float('-inf') # Inicializar con el valor más bajo posible
            
            # Iterar sobre todos los movimientos posibles del gato
            for mov_gato in estado.obtener_posibles_movimientos(estado.gato, es_raton=False):
                # Crear un nuevo estado hipotético aplicando el movimiento del gato
                nuevo_estado = estado.copiar_estado()
                nuevo_estado.mover_gato(mov_gato, ruido = True)
                
                # Llamada recursiva para el turno del ratón (minimizador)
                valor = self.minimax(nuevo_estado, profundidad - 1, False)
                mejor_valor = max(mejor_valor, valor) # El gato elige el movimiento que da la puntuación más alta
            return mejor_valor

        #3 Turno del Jugador Minimizador (Ratón)
        else: # El ratón quiere minimizar la puntuación (del gato)
            mejor_valor = float('inf') # Inicializar con el valor más alto posible
            
            # Iterar sobre todos los movimientos posibles del ratón
            for mov_raton in estado.obtener_posibles_movimientos(estado.raton, es_raton=True):
                # Crear un nuevo estado hipotético aplicando el movimiento del ratón
                nuevo_estado = estado.copiar_estado()
                nuevo_estado.mover_raton(mov_raton, ruido = True)
                
                # Llamada recursiva para el turno del gato (maximizador)
                valor = self.minimax(nuevo_estado, profundidad - 1, True)
                mejor_valor = min(mejor_valor, valor) # El ratón elige el movimiento que da la puntuación más baja al gato
            return mejor_valor

    
    def obtener_mejor_movimiento_gato(self, profundidad):
        mejor_valor = float('-inf')
        mejores_movimientos = [] # cambiar a una lista para tener múltiples movimientos
        
        for mov_gato in self.obtener_posibles_movimientos(self.gato, es_raton=False):
            estado_despues_mov_gato = self.copiar_estado()
            estado_despues_mov_gato.mover_gato(mov_gato, ruido=True)
            
            valor = self.minimax(estado_despues_mov_gato, profundidad - 1, False)
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejores_movimientos = [mov_gato] # Si encontramos uno mejor, reiniciamos la lista
            elif valor == mejor_valor:
                mejores_movimientos.append(mov_gato) # Si encontramos uno igual de bueno, lo añadimos
        
        if mejores_movimientos:
            return random.choice(mejores_movimientos) # Elegir uno al azar de los mejores
        return None # No hay movimientos posibles

    def obtener_mejor_movimiento_raton(self, profundidad):
        mejor_valor = float('inf')
        mejores_movimientos = [] # Cambiar a una lista para tener múltiples movimientos

        for mov_raton in self.obtener_posibles_movimientos(self.raton, es_raton=True):
            estado_despues_mov_raton = self.copiar_estado()
            estado_despues_mov_raton.mover_raton(mov_raton, ruido=True)

            valor = self.minimax(estado_despues_mov_raton, profundidad - 1, True)

            if valor < mejor_valor: # El ratón busca minimizar la puntuación del gato
                mejor_valor = valor
                mejores_movimientos = [mov_raton]
            elif valor == mejor_valor:
                mejores_movimientos.append(mov_raton)
        
        if mejores_movimientos:
            return random.choice(mejores_movimientos) # Elegir uno al azar de los mejores
        return None # No hay movimientos posibles

def leer_movimiento_usuario(pos_actual):
    teclas = {
        "w": (-1, 0),   # arriba
        "s": (1, 0),    # abajo
        "a": (0, -1),   # izquierda
        "d": (0, 1),    # derecha
        "q": (-1, -1),  # arriba izquierda
        "e": (-1, 1),   # arriba derecha
        "z": (1, -1),   # abajo izquierda
        "c": (1, 1)     # abajo derecha
    }
    
    while True:
        tecla = input("Movimiento (W A S D Q E Z C): ").lower()
        if tecla in teclas:
            dx, dy = teclas[tecla]
            nueva_pos = (pos_actual[0] + dx, pos_actual[1] + dy)
            return nueva_pos
        else:
            print("Tecla inválida. Usa W, A, S, D, Q, E, Z o C.")

def mostrar_estadisticas():
    import sqlite3
    conexion = sqlite3.connect("partidas.db")
    cursor = conexion.cursor()

    print("\nEstadísticas de Partidas\n")

    cursor.execute("SELECT COUNT(*) FROM partidas")
    total = cursor.fetchone()[0]   #El método devuelve un solo registro o Ninguno si no hay más filas disponibles. y como calculamos el conteo de partidas, siempre habrá al menos una fila
    print(f"Total de partidas registradas: {total}")

    cursor.execute("SELECT resultado, COUNT(*) FROM partidas GROUP BY resultado")
    for resultado, cantidad in cursor.fetchall(): #fetchall() devuelve una lista de tuplas, donde cada tupla representa una fila del resultado de la consulta
        jugador = "Ratón" if resultado == "raton" else "Gato"
        print(f"Ganadas por {jugador}: {cantidad}")

    cursor.execute("SELECT modo, resultado, COUNT(*) FROM partidas GROUP BY modo, resultado")
    resumen = {}
    for modo, resultado, count in cursor.fetchall():
        if modo not in resumen:
            resumen[modo] = {"gato": 0, "raton": 0}
        resumen[modo][resultado] = count

    print("\nResultados por modo:")
    for modo, datos in resumen.items():
        print(f" - {modo}: Gato = {datos.get('gato', 0)} | Ratón = {datos.get('raton', 0)}")

    cursor.execute("SELECT AVG(turnos_totales) FROM partidas")
    promedio_turnos = cursor.fetchone()[0]
    print(f"\nPromedio de duración: {promedio_turnos:.2f} turnos")

    conexion.close()
    input("\nPresioná Enter para volver al menú principal...")

def finalizar_partida(juego, resultado, id_partida, cursor, conexion):
    juego.imprimir_tablero_final()
    print("El ratón ha sobrevivido!!! GANA EL RATÓN." if resultado == "raton" else "El gato ha atrapado al ratón!!! GANA EL GATO.")
    cursor.execute("""
        UPDATE partidas SET resultado = ?, turnos_totales = ? WHERE id = ?
    """, (resultado, juego.turnos, id_partida))
    conexion.commit()
    conexion.close()


def jugar_partida_minimax(modo):
    conexion = sqlite3.connect("partidas.db")
    cursor = conexion.cursor()
    registro_partida = [] 
    gato_pos = (0, 0)
    raton_pos = (5, 5)
    juego = Juego(gato_pos, raton_pos)

    profundidad_busqueda = 4 # se puede ajustar esto pero mientras mayor sea la profundidad = más "inteligente" pero más lento.
    modo_juego = {
    "1": "IA vs IA",
    "2": "Usuario (ratón) vs IA",
    "3": "Usuario (gato) vs IA"
    }[modo] #sirve solo para el sql
    cursor.execute("""
    INSERT INTO partidas (modo, resultado, turnos_totales, fecha)
    VALUES (?, ?, ?, ?)
    """, (modo_juego, "", 0, datetime.now().isoformat()))  #no sabia que se podria usar las variables en las sentencias sql de esta manera
    id_partida = cursor.lastrowid #lastrowid obtiene el último ID insertado en la tabla, que es el ID de la partida recién creada
    print("--- comienza el juego ---")
    print("\nTablero de Juego:")
    if modo == "1":
            print("¡Modo IA vs IA activado! Observá cómo se enfrentan el Gato y el Ratón.")
    # juego.imprimir_tablero()
    while True:
        juego.imprimir_tablero()
        print(f"Turno: {juego.turnos}")
        
        # Usuario juega como ratón
        if modo == "2": 
            print("\nTurno del Ratón:") 
            while True:
                desde= juego.raton
                nueva_pos = leer_movimiento_usuario(juego.raton)
                if juego.es_posicion_valida(nueva_pos):
                    juego.mover_raton(nueva_pos)
                    juego.imprimir_tablero()
                    if juego.es_fin_de_juego():
                        finalizar_partida(juego, "raton" if juego.es_raton_ganador() else "gato", id_partida, cursor, conexion)
                        return
                    registro_partida.append({
                        "turno": juego.turnos,
                        "jugador": "raton",
                        "tipo_control": "usuario",
                        "desde": desde,
                        "hasta": juego.raton,
                        "tablero": [fila.copy() for fila in juego.tablero]
                    })
                    guardar_movimiento_sql(cursor, registro_partida[-1], id_partida)
                    break
                else:
                    print("Movimiento inválido. Intentalo de nuevo.")

        # IA juega como ratón
        elif modo == "1":
            print("Ratón (IA) pensando...")
            mov_raton = juego.obtener_mejor_movimiento_raton(profundidad_busqueda)
            if mov_raton is None:
                print("El ratón no tiene movimientos válidos. ¡El gato ha ganado!")
                break
            desde = juego.raton
            juego.mover_raton(mov_raton, ruido=True)
            print(f"Ratón se mueve a: {mov_raton}")
            juego.imprimir_tablero()
            if juego.es_fin_de_juego():
                finalizar_partida(juego, "raton" if juego.es_raton_ganador() else "gato", id_partida, cursor, conexion)
                return
            registro_partida.append({
                "turno": juego.turnos,
                "jugador": "raton",
                "tipo_control": "IA",
                "desde": desde,
                "hasta": juego.raton,
                "tablero": [fila.copy() for fila in juego.tablero]
            })
            guardar_movimiento_sql(cursor, registro_partida[-1], id_partida)

        # if juego.es_fin_de_juego():
        #     juego.imprimir_tablero()
        #     print("¡El ratón ha sobrevivido! GANA EL RATÓN." if juego.es_raton_ganador() else "¡El gato ha atrapado al ratón! GANA EL GATO.")
        #     break

        # Usuario juega como gato
        if modo == "3":
            print("\nTurno del Gato:")  
            if juego.es_fin_de_juego():
                finalizar_partida(juego, "raton" if juego.es_raton_ganador() else "gato", id_partida, cursor, conexion)
                return
            while True:
                desde = juego.gato #guardar la posicion del gato antes de mover y darle otro valor
                nueva_pos = leer_movimiento_usuario(desde)
                if juego.es_posicion_valida(nueva_pos):
                    juego.mover_gato(nueva_pos)
                    juego.imprimir_tablero()
                    if juego.es_fin_de_juego():
                       finalizar_partida(juego, "gato", id_partida, cursor, conexion)
                       return
                    registro_partida.append({
                        "turno": juego.turnos,
                        "jugador": "gato",
                        "tipo_control": "usuario",
                        "desde": desde,
                        "hasta": juego.gato,
                        "tablero": [fila.copy() for fila in juego.tablero]
                    })
                    guardar_movimiento_sql(cursor, registro_partida[-1], id_partida)
                    break
                else:
                    print("Movimiento inválido. Intentalo de nuevo.")
        
        # IA juega como gato
        elif modo == "1":
            print("Gato (IA) pensando...")
            mov_gato = juego.obtener_mejor_movimiento_gato(profundidad_busqueda)
            if mov_gato is None:
                print("El gato no tiene movimientos válidos. ¡El ratón ha escapado!")
                break
            desde = juego.gato
            juego.mover_gato(mov_gato, ruido=True)
            print(f"Gato se mueve a: {mov_gato}")
            if juego.es_fin_de_juego():
                resultado = "raton" if juego.es_raton_ganador() else "gato"
                finalizar_partida(juego, resultado, id_partida, cursor, conexion)
                return
            registro_partida.append({
                "turno": juego.turnos,
                "jugador": "gato",
                "tipo_control": "IA",
                "desde": desde,
                "hasta": juego.gato,
                "tablero": [fila.copy() for fila in juego.tablero]
            })
            guardar_movimiento_sql(cursor, registro_partida[-1], id_partida)

        
        # if juego.es_fin_de_juego():
        #     juego.imprimir_tablero()
        #     print("¡El gato ha atrapado al ratón! GANA EL GATO." if juego.es_gato_ganador() else "¡El ratón ha sobrevivido! GANA EL RATÓN.")
        #     break

        
        juego.turnos += 1  #esto es lo mas importante del ciclo, para que sume el turno y no se quede en 0 siempre


#hacemos un menu para que sea mas facil de jugar y poder hacer las consultas en la bd sin hacer mucho rollo en el def del juego principal
def menu_principal():
    while True:
        print("""
        \n--- LABERINTO DEL GATO Y EL RATÓN ---
        1. IA vs IA
        2. Usuario (ratón) vs IA (gato)
        3. Usuario (gato) vs IA (ratón)
        4. Ver estadísticas
        5. Salir
        """)

        opcion = input("\nSeleccioná una opción (1 a 5): ").strip()

        if opcion in ["1", "2", "3"]:  ##revisar porque siempre al final imprime dos veces el tablero
            jugar_partida_minimax(opcion)
        elif opcion == "4":
            mostrar_estadisticas()
        elif opcion == "5":
            print("\n\n Gracias por jugar!!!!\n\n\n")
            break
        else:
            print("\nOpción inválida.\n")



# para ejecutar el juego desde el menu
menu_principal()