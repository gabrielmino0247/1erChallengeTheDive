# El Laberinto del Gato y el Ratón - Simulador con Minimax

¡Bienvenido a esta aventura estratégica donde un gato implacable y un ratón astuto se enfrentan en un tablero lleno de decisiones!

---

## ¿Qué hace este proyecto?

- Simula una partida entre un gato y un ratón usando el algoritmo Minimax.
- Incluye tres modos de juego:
  1. IA vs IA
  2. Usuario (ratón) vs IA (gato)
  3. Usuario (gato) vs IA (ratón)
- Registra cada jugada en una base de datos SQLite (`partidas.db`).
- Permite consultar estadísticas de todas las partidas desde el menú principal.

---

## Tecnologías utilizadas

- Python (sin librerías externas)
- Algoritmo Minimax
- SQLite
- Interfaz 100% por consola

---

## Cómo ejecutar

Desde la terminal, ejecutá:

```
python app.py
```

---

## Qué aprendí

Más que un simple proyecto, esto fue una especie rompecabeza para entender el verdadero comportamiento de Minimax en un entorno dinámico y con múltiples decisiones posibles. Aprendí:

- A implementar Minimax desde cero y hacerlo funcionar en un juego personalizado.
- A ajustar cuidadosamente la lógica para que el resultado no esté sesgado: al principio o ganaba siempre el ratón o el gato. Tuvimos que hacer muchas pruebas, ajustes de profundidad y hasta fijar un máximo de turnos basados en el tamaño del tablero.
- A manejar errores lógicos frecuentes, como movimientos inválidos que se repetían constantemente o el tablero que se imprimía dos veces al finalizar.
- A estructurar una base de datos que registre cada movimiento y resultado de las partidas.
- A trabajar con clases, bucles, condiciones, y a pensar en cómo una IA podría anticiparse al comportamiento del otro jugador.

---

## Algunas dificultades que enfrentamos

- Detectar y prevenir bucles de movimientos repetitivos sin romper el juego.
- Entender el minimax, y como conectarlo con todo y hacer que los mejores movimientos no entren en conflicto y se elija random si hay varios buenos siempre y cuando minimicen la distancia.
- Entender como aplicar la recursividad.
- Imprimir el tablero en el momento correcto (ni antes ni después de que termine el juego).
- Coordinar cuándo debe jugar el gato o el ratón, y quién debe tener prioridad para garantizar una experiencia justa en todos los modos.
- Lograr un sistema de estadísticas útil sin depender de interfaces gráficas o librerías externas.

---

## Créditos

Desarrollado por Angel Miño — con más pruebas, errores y reinicios de los que me gustaría admitir