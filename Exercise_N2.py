import math
import random
import numpy as np
import matplotlib.pyplot as plt

#funcion de intensidad del proceso de Poisson
def f(x):
    return (8+4*math.sin((math.pi*x)/12))/60

#funcion que genera una variable aleatoria con distribucion exponencial de parametro "lamda" y la retorna
def gen_va_exp(lamda):
    return (-math.log(1-random.random())/lamda)

#Devuelve el primer evento ocurrido luego de un tiempo "t_actual", segun una funcion de intensidad "f" y una cota superior de f "lamda_max" 
def gen_va_poisson(f, lamda_max, t_actual):
    t = t_actual
    while True:
        e = gen_va_exp(lamda_max)
        t = t + e
        u = random.random()
        if u < f(t) / lamda_max:
            return (t - t_actual)
        
def gen_va_bernoulli(p):
    u = random.random()
    if u < p:
        return 1
    else:
        return 0

def sim_servidores_serie(lamda_p,lamda_s1,lamda_s2,N):

    # Inicializacion
    # t = tiempo de simulacion
    # na = n° de llegadas al sistema
    # nd = n° de salidas del sistema
    # n1 = n° de clientes en el primer sistema (incluidos en cola y en servicio)
    # n2 = n° de clientes totales en el segundo sistema (incluidos en cola y en servicio)
    # l2 = lista de clientes normales en el segundo sistema (incluidos en cola y en servicio)
    # p2 = lista de clientes prioritarios en el segundo sistema (incluidos en cola y en servicio)
    # ta = tiempo en el que llegará el proximo cliente al sistema
    # t1 = tiempo en el que el proximo cliente saldrá del primer sistema (o entrará al segundo sistema)
    # t2 = tiempo en el que el proximo cliente saldrá del segundo sistema (o del sistema en general)
    # lista_llegadas_sistema = contiene el tiempo de llegada del cliente n°i al sistema
    # lista_llegadas_s2 = contiene el tiempo de llegada del cliente n°i al segundo sistema
    # lista_salidas_sistema = contiene el tiempo de salida del cliente n°i al sistema
    # tiempo_total_acumulado = se usa para calcular la suma acumulada del tiempo de espera de los clientes en el sistema

    t,na,nd,n1,n2, = 0,0,0,0,0
    ta = gen_va_poisson(f,lamda_p,t)
    t1 = math.inf
    t2 = math.inf
    numCliente = 0
    lista_llegadas_sistema = []
    lista_llegadas_s2 = []
    lista_salidas_sistema = []
    tiempo_total_acumulado = 0
    #### Listas para clientes prioritarios
    p2 = []
    l2 = []
    tiempo_total_prioritarios = []
    tiempo_total_normales = []

    ## Fase de Actualizacion
    while ta < math.inf or t1 < math.inf or t2 < math.inf:

        #Determinamos cual será el evento mas proximo a suceder
        evento_proximo = min(ta,t1,t2)

        #Caso en el que un cliente llegó al sistema
        if evento_proximo == ta:
            t = ta
            na = na+1
            n1 = n1+1
            ta = t + gen_va_poisson(f,lamda_p,t)
            if na == N:
                ta = math.inf
            if n1 == 1:
                t1 = t + gen_va_exp(lamda_s1)
            lista_llegadas_sistema.append(t)

        #Caso en el que un cliente sale del primer sistema (o entra al segundo)
        elif evento_proximo == t1:
            t = t1
            n1 = n1-1
            numCliente = na - n1
            if n1 == 0:
                t1 = math.inf
            else:
                t1 = t + gen_va_exp(lamda_s1)
            n2 = n2+1
            #Comprobacion de si el cliente que entra al segundo sistema es prioritario o no
            es_prioritario = gen_va_bernoulli(0.2)
            if es_prioritario:
                p2.append(numCliente)
                if len(p2) == 1:
                    t2 = t + gen_va_exp(lamda_s2)
                    #Se asigna el tipo de cliente que se encuentra en el segundo sistema para luego calcular su tiempo de espera total al salir del sistema
                    cliente_en_s2 = "prioritario"
                
            else:
                l2.append(numCliente)
                if len(l2) == 1 and len(p2) == 0:
                    t2 = t + gen_va_exp(lamda_s2)
                    cliente_en_s2 = "normal"
                
                  
            lista_llegadas_s2.append(t)
        
        #Caso en el que un cliente termina el segundo servicio y sale del sistema
        elif evento_proximo == t2:
            t = t2
            nd = nd+1
            n2 = n2-1
            #Se calcula el tiempo total en sistema para ambos tipos de clientes.
            #y se elimina al cliente que salio del sistema de la lista correspondiente (prioritarios o normales)
            if cliente_en_s2 == "prioritario":
                tiempo_total_prioritarios.append(t - lista_llegadas_sistema[p2[0] - 1])
                p2.pop(0)
            else:
                tiempo_total_normales.append(t - lista_llegadas_sistema[l2[0] - 1])
                l2.pop(0)
            

            #Caso en el que no hay mas clientes en el segundo sistema /en la cola)
            if n2 == 0:
                t2 = math.inf
            
            else:
                #Corroboracion de que tipo es el cliente siguiente a entrar al sistema 2
                if len(p2) > 0:
                    t2 = t + gen_va_exp(lamda_s2)
                    cliente_en_s2 = "prioritario"
                else:
                    cliente_en_s2 = "normal"
                    t2 = t + gen_va_exp(lamda_s2)     
                
            
            lista_salidas_sistema.append(t)
    
    # Calculo de los promedios de espera para ambos tipos de clientes y en general
    promedio_espera = sum(tiempo_total_prioritarios + tiempo_total_normales) / nd if nd > 0 else 0
    
    promedio_espera_prioritarios = sum(tiempo_total_prioritarios)/len(tiempo_total_prioritarios) if len(tiempo_total_prioritarios) > 0 else 0
    
    promedio_espera_normales = sum(tiempo_total_normales)/len(tiempo_total_normales) if len(tiempo_total_normales) > 0 else 0
    
    #Se devuelve tambien las listas de tiempos en crudo para poder analizarlos posteriormente
    return promedio_espera, promedio_espera_prioritarios, promedio_espera_normales, tiempo_total_normales, tiempo_total_prioritarios



def t_promedio_permanencia(L,N):
    total, prio, normal, _, _ = sim_servidores_serie(0.2,1/4,1/6,N)
    
    media_total = total
    media_prio = prio
    media_normal = normal
    
    scuad_total = 0.0
    scuad_prio = 0.0
    scuad_normal = 0.0
    n = 1
    d = L/(1.96*2)
    while (n < 100) or (math.sqrt(scuad_total/n) > d or 
                         math.sqrt(scuad_prio/n) > d or 
                         math.sqrt(scuad_normal/n) > d):
        
        n = n+1
        total, prio, norm, _, _ = sim_servidores_serie(0.2, 1/4, 1/6, N)

        media_ant_total, media_ant_prio, media_ant_normal = media_total, media_prio, media_normal

        # Actualizacion de las medias con la formula de Welford para la media muestral
        media_total += (total - media_total) / n
        media_prio += (prio - media_prio) / n
        media_normal  += (norm  - media_normal)  / n

        # Actualizacion de las scuads con la formula de Welford para varianza muestral
        scuad_total = scuad_total * (1 - 1/(n-1)) + n * (media_ant_total - media_total)**2
        scuad_prio = scuad_prio * (1 - 1/(n-1)) + n * (media_ant_prio - media_prio)**2
        scuad_normal  = scuad_normal  * (1 - 1/(n-1)) + n * (media_ant_normal  - media_normal )**2

    # Calculo de los semianchos de los intervalos de confianza para cada tipo de cliente y en general
    semi_total = 1.96 * math.sqrt(scuad_total/n)
    semi_prio = 1.96 * math.sqrt(scuad_prio/n)
    semi_normal  = 1.96 * math.sqrt(scuad_normal /n)
    
    # Imprimir resultados cada 1000 iteraciones
    if n % 1000 == 0:
        print(f"Iteración: {n} | Error actual: {math.sqrt(scuad_total/n):.6f} | Objetivo: {d}")
    
    # Devolver los resultados en un formato legible, incluyendo el número de iteraciones, 
    # las medias y los intervalos de confianza para cada tipo de cliente y en general    
    return {
        "N iteraciones": n,
        "Total":        (media_total, [media_total - semi_total, media_total + semi_total]),
        "Prioritarios": (media_prio, [media_prio - semi_prio, media_prio + semi_prio]),
        "Normales":     (media_normal,  [media_normal  - semi_normal,  media_normal  + semi_normal])
    }

print("Medias e intervalos de confianza para el tiempo promedio de permanencia en el sistema: \n")
print("Resultados para L = 0.5 minutos y N = 10000 clientes: \n")
print(t_promedio_permanencia(0.5,10000))

_, _, _, tiempos_norm, tiempos_prior = sim_servidores_serie(0.2, 1/4, 1/6, 10000)


#Histogramas
tiempos_prior = np.array(tiempos_prior)
tiempos_norm  = np.array(tiempos_norm)
tiempos_total = np.concatenate([tiempos_prior, tiempos_norm])

plt.figure(figsize=(9, 5))
plt.hist(tiempos_total, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
plt.title('Tiempos totales')
plt.xlabel('Minutos', fontsize=12)
plt.ylabel('Frecuencia', fontsize=12)
plt.show()

# Gráfico de tiempos prioritarios
plt.figure(figsize=(9, 5))
plt.hist(tiempos_prior, bins=50, color='red', alpha=0.7, edgecolor='black')
plt.title('Tiempos prioritarios', fontsize=12)
plt.ylabel('Frecuencia', fontsize=12)
plt.xlabel('Minutos', fontsize=12)
plt.show()

# Gráfico de tiempos normales
plt.figure(figsize=(9, 5))
plt.hist(tiempos_norm, bins=50, color='green', alpha=0.7, edgecolor='black')
plt.title('Tiempos normales', fontsize=12)
plt.ylabel('Frecuencia', fontsize=12)
plt.xlabel('Minutos', fontsize=12)
plt.show()

# Estadísticas descriptivas

for nombre, datos in [("Prioritarios", tiempos_prior), ("Normales", tiempos_norm)]:
    print(f"\n--- {nombre} ---")
    print(f"Media:    {np.mean(datos):.4f}")
    print(f"Mediana:  {np.median(datos):.4f}")
    print(f"P25:      {np.percentile(datos, 25):.4f}")
    print(f"P75:      {np.percentile(datos, 75):.4f}")
    print(f"P90:      {np.percentile(datos, 90):.4f}")
        
    
#calculo de probabilidades de que el tiempo total en sistema supere ciertos umbrales para ambos tipos de clientes
for x in [10, 20, 30, 60]:
    p_prior = np.mean(tiempos_prior > x)
    p_norm  = np.mean(tiempos_norm  > x)
    print(f"P(W > {x} min) - Prioritarios: {p_prior:.4f} | Normal: {p_norm:.4f}")