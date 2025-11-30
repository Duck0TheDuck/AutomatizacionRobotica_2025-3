import networkx as nx
import matplotlib.pyplot as plt


def busqueda_local_voraz(grafo, inicio, meta):

    camino = [inicio]
    actual = inicio
    visitados = {inicio}
    costo_total = 0

    print(f" Iniciando Búsqueda Local desde {inicio} a {meta} ---")

    while actual != meta:
        vecinos = list(grafo.neighbors(actual))

        # Filtramos vecinos que no hemos visitado para evitar ciclos simples
        vecinos_no_visitados = [v for v in vecinos if v not in visitados]

        if not vecinos_no_visitados:
            print(f"¡Atascado en {actual}! No hay vecinos nuevos. (Limitante de Búsqueda Local)")
            return None, 0

        # --- CORAZÓN DE LA BÚSQUEDA LOCAL ---
        mejor_vecino = None
        menor_peso = float('inf')

        for vecino in vecinos_no_visitados:
            peso = grafo[actual][vecino]['weight']
            if peso < menor_peso:
                menor_peso = peso
                mejor_vecino = vecino

        # Toma la decisión final, se mueve y "guarda la partida"
        costo_total += menor_peso
        visitados.add(mejor_vecino)
        camino.append(mejor_vecino)
        actual = mejor_vecino
        print(f"Moviendo a {actual} (Costo arista: {menor_peso})")

    return camino, costo_total


# 1. Crear el Grafo Ponderado
mapa = nx.Graph()

# Añadimos Nodos con pesos (Nodo1, Nodo2, Peso)
aristas = [
    ('A', 'B', 20),
    ('A', 'C', 4),
    ('B', 'D', 8),
    ('B', 'E', 30),
    ('C', 'F', 2),
    ('D', 'Z', 20),
    ('E', 'Z', 5),
    ('F', 'Z', 2),
    ('A', 'H', 10),
    ('H', 'K', 50)
]

mapa.add_weighted_edges_from(aristas)

# 2. Ejecutar el Algoritmo
inicio = 'A'
meta = 'Z'
camino_encontrado, costo = busqueda_local_voraz(mapa, inicio, meta)

print(f"\nCamino Final: {camino_encontrado}")
print(f"Costo Total: {costo}")

# 3. Visualización
plt.figure(figsize=(10, 8))

# Disposición de los nodos (Layout)
pos = nx.spring_layout(mapa, seed=42)

# Dibujar nodos y todas las aristas
nx.draw_networkx_nodes(mapa, pos, node_size=700, node_color='lightblue')
nx.draw_networkx_edges(mapa, pos, width=2, edge_color='gray')
nx.draw_networkx_labels(mapa, pos, font_size=12, font_family='sans-serif')

# Dibujar las etiquetas de los pesos
etiquetas_aristas = nx.get_edge_attributes(mapa, 'weight')
nx.draw_networkx_edge_labels(mapa, pos, edge_labels=etiquetas_aristas)

# RESALTAR EL CAMINO ENCONTRADO
if camino_encontrado:
    aristas_camino = list(zip(camino_encontrado, camino_encontrado[1:]))
    nx.draw_networkx_edges(mapa, pos, edgelist=aristas_camino, width=6, edge_color='red')
    nx.draw_networkx_nodes(mapa, pos, nodelist=camino_encontrado, node_color='lightgreen')

plt.title(f"Búsqueda Local (Greedy) de {inicio} a {meta}\nCosto: {costo}", fontsize=15)
plt.axis('off')
plt.show()