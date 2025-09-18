import serial
import json
import time
import serial.tools.list_ports


def encontrar_microcontrolador():
    portas = serial.tools.list_ports.comports()
    for porta in portas:
        descricao = porta.description.lower()
        fabricante = (porta.manufacturer or "").lower()
        if any(x in descricao for x in ['arduino', 'ch340', 'usb serial', 'ttyusb', 'cu.usb']) or \
           any(x in fabricante for x in ['arduino', 'wch', 'silicon labs', 'ftdi']):
            return porta.device
    return None
def conectar_serial(porta, baudrate=9600, timeout=2):
    try:
        ser = serial.Serial(porta, baudrate=baudrate, timeout=timeout)
        time.sleep(2)
        return ser
    except serial.SerialException:
        return None

def enviar_json(ser, dados):
    mensagem = json.dumps(dados)
    ser.write((mensagem + '\n').encode('utf-8'))

def receber_json(ser):
    try:
        linha = ser.readline().decode('utf-8').strip()
        if linha:
            return json.loads(linha)
    except json.JSONDecodeError:
        return None
    return None

porta = encontrar_microcontrolador()

if porta:
    print(f"[INFO] Microcontrolador conectado na porta {porta}")
    ser = conectar_serial(porta)

    enviar_json(ser, {"cmd": "ler_nfc"})
    print("[INFO] Comando enviado: ler_nfc")

    timeout_leitura = 10  
    tempo_inicial = time.time()
    tag_lida = False

    while (time.time() - tempo_inicial) < timeout_leitura:
        resposta = receber_json(ser)
        if resposta:
            if "tag" in resposta:
                uid = resposta["tag"]
                resultado = print(uid) 
                if resultado:
                    print(f"[ACESSO LIBERADO] TAG reconhecida. Bem-vindo(a), {resultado[0]}!")
                tag_lida = True
                break
            elif "erro" in resposta:
                print(f"[ERRO NFC] {resposta['erro']}")
                tag_lida = True
                break
        time.sleep(0.1) 

    if not tag_lida:
        print("A chave não foi aproximada do sensor para ser registrada.")

else:
