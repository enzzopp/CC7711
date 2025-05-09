from controller import Supervisor
import time
import math
import random

MAX_VELOCIDADE = 6.28
TIME_STEP = 450
NUM_CAIXAS = 3
TOLERANCIA_DISTANCIA = 0.10
LIMITE_SENSOR = 80
MOVER = 1

# Função auxiliar para monitorar as posições em tempo real
def imprimir_posicoes_caixas(caixas):
    print("\nPosições atuais das caixas:")
    for i, caixa in enumerate(caixas):
        pos = caixa.getPosition()
        print(f"CAIXA_{i}: x={pos[0]:.2f}, y={pos[1]:.2f}")
        time.sleep(0.05)

# Função para instanciar caixas e registrar posições iniciais
def get_caixas(supervisor, num_caixas):
    caixas = []
    posicoes_iniciais = {}

    for i in range(num_caixas):
        nome_def = f"CAIXA_{i}"
        caixa = supervisor.getFromDef(nome_def)

        if caixa is None:
            print(f"ERRO: Caixa {nome_def} não foi encontrada.")
            continue

        caixas.append(caixa)
        pos = caixa.getPosition()
        posicoes_iniciais[nome_def] = (pos[0], pos[1])  # x e y

    return caixas, posicoes_iniciais

# Função para verificar se as caixas se moveram após tentativa de empurrão
def verificar_movimento_caixas(caixas, posicoes_iniciais):
    posicoes_finais = {}

    for i, caixa in enumerate(caixas):
        nome = f"CAIXA_{i}"
        pos = caixa.getPosition()
        posicoes_finais[nome] = (pos[0], pos[1])

    print("\nResultado da análise de movimento:")
    for nome in posicoes_iniciais:
        xi, yi = posicoes_iniciais[nome]
        xf, yf = posicoes_finais[nome]

        dx = xf - xi
        dy = yf - yi
        dist = math.sqrt(dx**2 + dy**2)

        if dist == 0:
            print(f"{nome} é PESADA (deslocamento {dist:.4f})")
        else:
            print(f"{nome} é LEVE (deslocamento {dist:.4f})")

# Função para gerar os objetivos das caixas
def gerar_objetivos_caixas(posicoes_iniciais):
    objetivos = []
    for nome, (x, y) in posicoes_iniciais.items():
        objetivos.append((x, y))
    return objetivos

# Função para instanciar os sensores de proximidade
def inicializar_sensores(supervisor):
    sensores = []
    for i in range(8):
        sensor = supervisor.getDevice(f"ps{i}")
        sensor.enable(TIME_STEP)
        sensores.append(sensor)
    return sensores

# ler sensores de proximidade
def ler_sensores_proximidade(sensores):
    leituras = []
    for sensor in sensores:
        valor = sensor.getValue()
        leituras.append(valor)
    return leituras

# funcao de controle de movimento
def controlar_movimento(robo_node, caixa_node, sensores, motor_esq, motor_dir, last_distance=0):
    # Posição e distância
    pos_robo = robo_node.getField("translation").getSFVec3f()
    pos_caixa = caixa_node.getPosition()
    x_robo, y_robo = pos_robo[0], pos_robo[1]
    x_caixa, y_caixa = pos_caixa[0], pos_caixa[1]
    dx = x_caixa - x_robo
    dy = y_caixa - y_robo
    distancia = math.sqrt(dx**2 + dy**2)

    # Ângulo desejado e atual
    angulo_desejado = math.atan2(dy, dx)
    rot_robo = robo_node.getField("rotation").getSFRotation()
    angulo_atual = rot_robo[3] * (1 if rot_robo[1] >= 0 else -1)
    erro = angulo_desejado - angulo_atual
    erro = (erro + math.pi) % (2 * math.pi) - math.pi

    # Leitura dos sensores
    leituras = ler_sensores_proximidade(sensores)
    frente = (leituras[0] + leituras[7]) / 2
    direita = sum(leituras[1:4]) / 3
    esquerda = sum(leituras[4:7]) / 3

    print(f"Frente: {frente:.2f}, Direita: {direita:.2f}, Esquerda: {esquerda:.2f}")

    # Detectou obstáculo à frente
    if frente > LIMITE_SENSOR:
        # inicia evasão por alguns ciclos
        if direita > esquerda:
            motor_esq.setVelocity(MOVER * -1.5)
            motor_dir.setVelocity(MOVER * 1.5)
        else:
            motor_esq.setVelocity(MOVER * 1.5)
            motor_dir.setVelocity(MOVER * -1.5)
        print("Obstáculo a frente! Iniciando evasão...")
        return
    
    #Detectou obstáculo à direita
    if direita > LIMITE_SENSOR:
        motor_esq.setVelocity(MOVER * -1.5)
        motor_dir.setVelocity(MOVER * 1.5)
        print("Obstáculo à direita! Iniciando evasão...")
        return
    
    # Detectou obstáculo à esquerda
    if esquerda > LIMITE_SENSOR:
        motor_esq.setVelocity(MOVER * 1.5)
        motor_dir.setVelocity(MOVER * -1.5)
        print("Obstáculo à esquerda! Iniciando evasão...")
        return
    
    # Gira totalmente se de costas
    if abs(erro) > 2.5:
        giro = 2.5 if erro > 0 else -2.5
        motor_esq.setVelocity(MOVER * -giro)
        motor_dir.setVelocity(MOVER * giro)
        print("Giro completo: estava de costas.")
        delay(supervisor, TIME_STEP, 500)
        return

    # Alinhado ou progredindo: navegação proporcional adaptativa
    k = 0.6 * (1.0 + distancia)
    v_base = 5.0
    ajuste = max(min(k * erro, v_base), -v_base)

    if abs(erro) < 0.1:
        vel_e = min(v_base, MAX_VELOCIDADE)
        vel_d = min(v_base, MAX_VELOCIDADE)
    else:
        vel_e = max(min(v_base - ajuste, MAX_VELOCIDADE), -MAX_VELOCIDADE)
        vel_d = max(min(v_base + ajuste, MAX_VELOCIDADE), -MAX_VELOCIDADE)

    motor_esq.setVelocity(MOVER * vel_e)
    motor_dir.setVelocity(MOVER * vel_d)

# delay 
def delay(supervisor, TIME_STEP, time_milisec="RANDOM"):

    if time_milisec == "RANDOM":
        random_time = random.randint(1, 5)
        time_milisec = random_time * 100  # converte para milissegundos


    time_target = time_milisec / 1000.0  # converte para segundos
    init_time = supervisor.getTime()
    while supervisor.getTime() - init_time < time_target:
        supervisor.step(TIME_STEP)

# Função para navegar até a caixa
def navigate_to_box(caixa_node, robo_node, sensores, motor_esq, motor_dir):
    pos_robo = robo_node.getField("translation").getSFVec3f()
    pos_caixa = caixa_node.getPosition()

    x_robo, y_robo = pos_robo[0], pos_robo[1]
    x_caixa, y_caixa = pos_caixa[0], pos_caixa[1]

    dx = x_caixa - x_robo
    dy = y_caixa - y_robo
    distancia = math.sqrt(dx**2 + dy**2)
    print(f"Distância até a caixa: {distancia:.2f}")

    if round(distancia, 2) <= TOLERANCIA_DISTANCIA:
        motor_esq.setVelocity(MOVER * 0.0)
        motor_dir.setVelocity(MOVER * 0.0)
        print("Robo parou.")
        return True  # Chegou ao destino

    controlar_movimento(robo_node, caixa_node, sensores, motor_esq, motor_dir)
    return False  # Ainda em movimento

# função para encapsular a funcao navigate_to_box
def success_navigate_to_box(caixa_node, robo_node, sensores, motor_esq, motor_dir):
    return navigate_to_box(caixa_node, robo_node, sensores, motor_esq, motor_dir)
    
# Função para empurrar a caixa
def empurrar_caixa_durante(supervisor, motor_esq, motor_dir, TIME_STEP, duracao_segundos=2):
    print("Empurrando a caixa...")
    motor_esq.setVelocity(MOVER * MAX_VELOCIDADE)
    motor_dir.setVelocity(MOVER * MAX_VELOCIDADE)

    steps_necessarios = int((1000 * duracao_segundos) / TIME_STEP)
    for _ in range(steps_necessarios):
        supervisor.step(TIME_STEP)

    motor_esq.setVelocity(MOVER * 0.0)
    motor_dir.setVelocity(MOVER * 0.0)
    print("Empurrão concluído.")


# Função para mostrar os valores dos sensores
def mostrar_valores_sensores(sensores):
    nomes = [f"ps{i}" for i in range(len(sensores))]
    valores = [f"{sensor.getValue():6.1f}" for sensor in sensores]

    print("\nLeitura dos sensores de proximidade:")
    for nome, valor in zip(nomes, valores):
        print(f"  {nome}: {valor}")


def encontrar_caixa_mais_proxima(robo_node, caixas_restantes):
    pos_robo = robo_node.getField("translation").getSFVec3f()
    x_robo, y_robo = pos_robo[0], pos_robo[1]

    menor_dist = float('inf')
    caixa_mais_proxima = None
    indice = -1

    for i, caixa in enumerate(caixas_restantes):
        pos = caixa.getPosition()
        x_caixa, y_caixa = pos[0], pos[1]
        dist = math.sqrt((x_caixa - x_robo)**2 + (y_caixa - y_robo)**2)
        if dist < menor_dist:
            menor_dist = dist
            caixa_mais_proxima = caixa
            indice = i

    return indice, caixa_mais_proxima



# -------------------- EXECUÇÃO PRINCIPAL --------------------



#SUPERVISOR ---------------------------------------------------------
supervisor = Supervisor()

# ROBÔ --------------------------------------------------------------
motor_esq = supervisor.getDevice("left wheel motor")
motor_dir = supervisor.getDevice("right wheel motor")
motor_esq.setPosition(float('inf'))
motor_dir.setPosition(float('inf'))
sensores = inicializar_sensores(supervisor)

# CAIXAS -------------------------------------------------------------
caixas, posicoes_iniciais = get_caixas(supervisor, NUM_CAIXAS)
objetivos_caixas = gerar_objetivos_caixas(posicoes_iniciais)

# NÓ do robô (certifique-se de que o robô tenha DEF ROBO no Webots)
robo_node = supervisor.getFromDef("ROBO")

# Lista de caixas restantes a visitar
caixas_restantes = caixas.copy()



# Loop principal ------------------------------------------------------------------------
while supervisor.step(TIME_STEP) != -1:
    # Se não houver mais caixas, finaliza
    if not caixas_restantes:
        print("Todas as caixas foram visitadas.")
        verificar_movimento_caixas(caixas, posicoes_iniciais)
        break

    # Descobre a caixa mais próxima
    indice_local, caixa_destino = encontrar_caixa_mais_proxima(robo_node, caixas_restantes)

    # Navega até ela
    chegou = success_navigate_to_box(caixa_destino, robo_node, sensores, motor_esq, motor_dir)

    if chegou:
        print(f"Robo chegou à CAIXA_{indice_local}.")
        empurrar_caixa_durante(supervisor, motor_esq, motor_dir, TIME_STEP, duracao_segundos=2)

        # Remove a caixa visitada da lista
        caixas_restantes.pop(indice_local)