import math
import random
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats


# funcion de intensidad del proceso de Poisson
def f(x):
    return (8+4*math.sin((math.pi*x)/12))/60


# funcion que genera una variable aleatoria con distribucion exponencial de parametro "lamda" y la retorna
def gen_va_exp(lamda):
    return (-math.log(1-random.random())/lamda)


# Devuelve el primer evento ocurrido luego de un tiempo "t_actual", segun una funcion de intensidad "f" y una cota superior de f "lamda_max"
def gen_va_poisson(f, lamda_max, t_actual):
    t = t_actual
    while True:
        e = gen_va_exp(lamda_max)
        t = t + e
        u = random.random()
        if u < f(t) / lamda_max:
            return (t - t_actual)


# EJERCICIO 1a)
def sim_servidores_serie(lamda_p, lamda_s1, lamda_s2, N):

    # Inicializacion
    # t = tiempo de simulacion
    # na = n° de llegadas al sistema
    # nd = n° de salidas del sistema
    # n1 = n° de clientes en el primer sistema (incluidos en cola y en servicio)
    # n2 = n° de clientes en el segundo sistema (incluidos en cola y en servicio)
    # ta = tiempo en el que llegará el proximo cliente al sistema
    # t1 = tiempo en el que el proximo cliente saldrá del primer sistema (o entrará al segundo sistema)
    # t2 = tiempo en el que el proximo cliente saldrá del segundo sistema (o del sistema en general)
    # lista_llegadas_sistema = contiene el tiempo de llegada del cliente n°i al sistema
    # lista_llegadas_s2 = contiene el tiempo de llegada del cliente n°i al segundo sistema
    # lista_salidas_sistema = contiene el tiempo de salida del cliente n°i al sistema
    # tiempo_total_acumulado = se usa para calcular la suma acumulada del tiempo de espera de los clientes en el sistema

    t, na, nd, n1, n2 = 0, 0, 0, 0, 0
    ta = gen_va_poisson(f, lamda_p, t)
    t1 = math.inf
    t2 = math.inf
    numCliente = 0
    lista_llegadas_sistema = []
    lista_llegadas_s2 = []
    lista_salidas_sistema = []
    tiempo_total_acumulado = 0

    # Fase de Actualizacion
    while ta < math.inf or t1 < math.inf or t2 < math.inf:

        # Determinamos cual será el evento mas proximo a suceder
        evento_proximo = min(ta, t1, t2)

        # Caso en el que un cliente llegó al sistema
        if evento_proximo == ta:
            t = ta
            na = na+1
            n1 = n1+1
            ta = t + gen_va_poisson(f, lamda_p, t)
            if na == N:
                ta = math.inf
            if n1 == 1:
                t1 = t + gen_va_exp(lamda_s1)
            lista_llegadas_sistema.append(t)

        # Caso en el que un cliente sale del primer sistema (o entra al segundo)
        elif evento_proximo == t1:
            t = t1
            n1 = n1-1
            if n1 == 0:
                t1 = math.inf
            else:
                t1 = t + gen_va_exp(lamda_s1)
            n2 = n2+1
            if n2 == 1:
                t2 = t + gen_va_exp(lamda_s2)
            numCliente = na - n1
            lista_llegadas_s2.append(t)

        # Caso en el que un cliente termina el segundo servicio y sale del sistema
        elif evento_proximo == t2:
            t = t2
            nd = nd+1
            n2 = n2-1

            # Caso en el que no hay mas clientes en el segundo sistema /en la cola)
            if n2 == 0:
                t2 = math.inf

            else:
                t2 = t + gen_va_exp(lamda_s2)
            numCliente = na - n1 - n2
            lista_salidas_sistema.append(t)
            tiempo_total_acumulado += (t - lista_llegadas_sistema[nd - 1])
    promedio_espera = tiempo_total_acumulado/nd
    return promedio_espera, lista_llegadas_sistema, lista_salidas_sistema


# EJERCICIO 1b)
# Estima el tiempo promedio de permanencia de los clientes en el sistema, queremos la
# longitud del intervalo de confianza del 95% sea inferior a 0.5
# L = longitud del intervalo de confianza del 95%
# N = Limite de clientes que llegaran al sistema
# Al terminar devuelve la estimacion del promedio (media), la desviacion estandar del
# estimador, el numero de iteraciones requeridas para lograr esa desviacion, y los limites del intervalo

def t_promedio_permanencia(L, N):
    media = sim_servidores_serie(0.2, 1/4, 1/6, N)[0]
    scuad = 0.0
    n = 1
    d = L/(1.96*2)
    while (n < 100) or math.sqrt(scuad/n) > d:
        n = n+1
        x = sim_servidores_serie(0.2, 1/4, 1/6, N)[0]
        media_ant = media
        media = media_ant + (x - media)/n
        scuad = scuad*(1-1/(n-1)) + n*((media_ant - media)**2)
        if n % 100 == 0:
            print(
                f"Iteración: {n} | Error actual: {math.sqrt(scuad/n):.6f} | Objetivo: {d}")
    intervalo = [media - 1.96 *
                 math.sqrt(scuad/n), media + 1.96*math.sqrt(scuad/n)]
    return media, math.sqrt(scuad/n), n, intervalo


# EJERCICIO 1b)
def imprimir_ej1b(N=10000):
    print("REALIZANDO EJERCICIO 1b)")
    print(
        f"Empezando estimacion del tiempo promedio de clientes en el sistema para {N} clientes")
    resultados = t_promedio_permanencia(0.5, N)
    media = resultados[0]
    desv_est_muestral = resultados[1]
    n_replicas = resultados[2]
    intervalo = resultados[3]

    print(f"Media estimada: {media:.4f} minutos")
    print(
        f"Desviacion muestral del estimador: {desv_est_muestral:.4f}")
    print(f"Numero de iteraciones requeridas: {n_replicas}")
    print(f"Intervalo de confianza del 95%: {intervalo}")


# EJERCICIO 1c)

# Dado una lista de tiempos de salidas, y una lista de tiempos de llegadas de clientes, devuelve una nueva lista con los
# tiempos en el sistema de cada cliente
def obtener_tiempos_espera(t_salidas, t_llegadas):
    t_espera = []
    for i in range(len(t_salidas)):
        t_espera.append(t_salidas[i]-t_llegadas[i])
    return t_espera


# Muestra en pantalla un histograma del tiempo de espera de los clientes en el sistema
def imprimir_ej1c(N=10000):
    resultados = sim_servidores_serie(0.2, 1/4, 1/6, N)
    lista_t_llegadas = resultados[1]
    lista_t_salidas = resultados[2]
    lista_t_espera = obtener_tiempos_espera(lista_t_salidas, lista_t_llegadas)
    print("REALIZANDO EJERCICIO 1c)")
    print("Imprimiendo diagrama")

    plt.figure(figsize=(11, 6))

    # density=True hace que el eje Y muestre la densidad de probabilidad
    plt.hist(lista_t_espera, bins='fd', color='skyblue',
             edgecolor='black')

    val_max = int(max(lista_t_espera)) + 20
    posiciones_x = list(range(0, val_max, 10))

    # Pasamos las posiciones de los numeros directamente como etiquetas
    plt.xticks(posiciones_x, posiciones_x, fontsize=10)

    plt.title(
        'Histograma de Tiempos de Permanencia en el Sistema (Primeros 10.000 clientes)', fontsize=14)
    plt.xlabel('Tiempo de permanencia en el sistema (Minutos)', fontsize=12)
    plt.ylabel('Cantidad de clientes (frecuencia)', fontsize=12)
    plt.grid(True, alpha=0.3)

    # Mostrar el gráfico en pantalla
    plt.show()


# Dada el tamaño de una muestra, calcula el numero de intervalos necesarios para agrupar una muestra
def calcular_numero_intervalos(N):
    k = 1 + 3.332*math.log10(N)
    k = round(k)
    if k % 2 == 0:
        k = k+1
    return k


def dar_muestra_intervalos(k, muestra):
    # Encontramos el rango de la muestra
    minimo = min(muestra)
    maximo = max(muestra)
    rango = maximo - minimo

    # Calculamos el ancho de cada uno de los k intervalos
    ancho_intervalo = rango / k

    # Construimos los límites de los intervalos, si tenemos k intervalos, necesitamos k + 1 limites.
    limites = []
    for i in range(k + 1):
        limites.append(minimo + i * ancho_intervalo)

    # Creamos una lista de ceros para contar las frecuencias observadas
    frecuencias_observadas = [0] * k

    # Clasificamos cada dato de la muestra en su intervalo correspondiente
    for dato in muestra:
        # Buscamos en cual de los k intervalos cae el dato
        for i in range(k):
            # Para el ultimo intervalo, también incluimos el limite superior estricto.
            if i == k - 1:
                if limites[i] <= dato <= limites[i+1]:
                    frecuencias_observadas[i] += 1
                    break
            else:
                if limites[i] <= dato < limites[i+1]:
                    frecuencias_observadas[i] += 1
                    break

    return frecuencias_observadas, limites


# Realizamos un test de bondad de ajuste Chi-cuadrado con un nivel de significancia del 5% para evaluar si
# los tiempos de espera de un sistema de servidores en serie se adaptan a
# una distribución Gamma continua con parametros alfa y beta desconocidos pero estimados.
def p_valor_gamma(N=10000):

    # Corremos la simulacion una vez
    resultados = sim_servidores_serie(0.2, 1/4, 1/6, N)

    # Obtenemos una muestra de los tiempos de espera
    muestra = obtener_tiempos_espera(resultados[2], resultados[1])
    muestra_np = np.array(muestra)

    # Calculamos la media y la varianza de la muestra
    media_est = np.mean(muestra_np)
    varianza_est = np.var(muestra_np, ddof=1)

    # Estimamos alfa y beta
    beta_est = varianza_est/media_est
    alfa_est = media_est**2 / varianza_est

    # Calculamos el numero de intervalos para agrupar nuestra muestra
    k = calcular_numero_intervalos(N)

    # Obtenemos una muestra agrupada, es decir los Ni
    muestra_agrupada, limites = dar_muestra_intervalos(k, muestra_np)

    # Calculamos las probabilidad teoricas para cada intervalo usando la distribucion Gamma con los parametros alfa y beta estimados
    # Es decir, calculamos los pi
    prob = np.array([
        stats.gamma.cdf(limites[i+1], a=alfa_est, loc=0, scale=beta_est) -
        stats.gamma.cdf(limites[i], a=alfa_est, loc=0, scale=beta_est)
        for i in range(k)
    ])

    # Obtenemos las frencuencias esperadas teoricas que obtuvimos a partir de la probabilidad teorica
    frecuencias_esperadas = N*prob

    # Realizamos la sumatoria de los (Ni-N*pi)**2 /N*pi
    t = np.sum((muestra_agrupada-frecuencias_esperadas)**2 /
               frecuencias_esperadas)

    # Ahora calculamos el pvalor teorico usando la distribucion Chi-cuadrada
    # Como tenemos 2 parametros desconocidos, 15 terminos en la sumatoria, los grados de libertad son 15-1-2
    pvalor = stats.chi2.sf(t, df=k-2-1)
    print(f"RESULTADOS DEL TEST CHI-CUADRADO (GAMMA)")
    print(f"Estadístico T calculado: {t}")
    print(f"P-valor obtenido: {pvalor}")

    if pvalor < 0.05:
        print("\nCONCLUSIÓN: RECHAZO H0 (P-valor < 0.05).")
        print(
            f"Hay evidencia estadística suficiente para afirmar que los tiempos de espera NO siguen una distribución Gamma con parámetros alfa = {alfa_est:.4f} y beta = {beta_est:.4f}.")
    else:
        print("\nCONCLUSIÓN: NO RECHAZO H0 (P-valor >= 0.05).")
        print(
            f"No hay evidencia suficiente para descartar H0. La distribución Gamma con parámetros alfa = {alfa_est:.4f} y beta = {beta_est:.4f} modela de forma ADECUADA los tiempos de espera.")

    return pvalor, t


# Realizamos un test de bondad de ajuste Chi-cuadrado con un nivel de significancia del 5% asintótico para
# evaluar si los tiempos de espera de un sistema de servidores en serie se adaptan a
# una distribución Log-normal con parametros mu y sigma estimados.
def p_valor_lognormal(N=10000):
    # Corremos la simulacion una vez
    resultados = sim_servidores_serie(0.2, 1/4, 1/6, N)

    # Obtenemos una muestra de los tiempos de espera
    muestra = obtener_tiempos_espera(resultados[2], resultados[1])
    muestra_np = np.array(muestra)

    # Aplicamos logaritmo natural para estimar los parametros de la Log-normal
    datos_log = np.log(muestra_np)
    mu_est = np.mean(datos_log)
    sigma_est = np.std(datos_log, ddof=1)

    # Calculamos el numero de intervalos para agrupar nuestra muestra
    k = calcular_numero_intervalos(N)

    # Obtenemos una muestra agrupada, es decir los Ni
    muestra_agrupada, limites = dar_muestra_intervalos(k, muestra_np)

    # Calculamos las probabilidad teoricas para cada intervalo usando la distribucion Log-normal
    prob = np.array([
        stats.lognorm.cdf(limites[i+1], s=sigma_est, loc=0, scale=np.exp(mu_est)) -
        stats.lognorm.cdf(limites[i], s=sigma_est, loc=0, scale=np.exp(mu_est))
        for i in range(k)
    ])

    # Obtenemos las frencuencias esperadas teoricas que obtuvimos a partir de la probabilidad teorica
    frecuencias_esperadas = N * prob

    # Realizamos la sumatoria de los (Ni-N*pi)**2 /N*pi
    t = np.sum((muestra_agrupada - frecuencias_esperadas)
               ** 2 / frecuencias_esperadas)

    # Ahora calculamos el pvalor teorico usando la distribucion Chi-cuadrada
    # Al igual que antes, estimamos 2 parametros (mu y sigma), por lo que df = k - 2 - 1
    grados_libertad = k - 2 - 1
    pvalor = stats.chi2.sf(t, df=grados_libertad)

    print(f"RESULTADOS DEL TEST CHI-CUADRADO (LOG-NORMAL)")
    print(f"Estadístico T calculado: {t}")
    print(f"P-valor obtenido: {pvalor}")

    if pvalor < 0.05:
        print("\nCONCLUSIÓN: RECHAZO H0 (P-valor < 0.05).")
        print(
            f"Hay evidencia estadística suficiente para afirmar que los tiempos de espera NO siguen una distribución Log-normal con parámetros mu = {mu_est:.4f} y sigma = {sigma_est:.4f}.")
    else:
        print("\nCONCLUSIÓN: NO RECHAZO H0 (P-valor >= 0.05).")
        print(
            f"No hay evidencia suficiente para descartar H0. La distribución Log-normal con parámetros mu = {mu_est:.4f} y sigma = {sigma_est:.4f} modela de forma ADECUADA los tiempos de espera.")

    return pvalor, t


imprimir_ej1b()
imprimir_ej1c()
p_valor_gamma()
p_valor_lognormal()
