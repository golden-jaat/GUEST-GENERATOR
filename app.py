import hmac, hashlib, requests, string, random, json, codecs, time, os, sys, base64, signal, threading, re, subprocess, importlib
from datetime import datetime
from flask import Flask, jsonify, request
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from colorama import Fore, Style, init
import urllib3

# Initialization
init(autoreset=True)
urllib3.disable_warnings()
app = Flask(__name__)

# ========== HIDDEN - MULTI LAYER ENCODED  ==========
_H3 = "VkFRU1RVRkZWREVGRlJXUUE9PQ=="
_XOR = [0x42, 0x59, 0x5F, 0x53, 0x54, 0x41, 0x52, 0x5F, 0x47, 0x4D, 0x52]

def _get_hidden():
    try:
        s1 = base64.b64decode(_H3).decode()
        s2 = s1[::-1]
        s3 = base64.b64decode(s2).decode()
        return ''.join(chr(ord(s3[i]) ^ _XOR[i % len(_XOR)]) for i in range(len(s3)))
    except:
        return "BYSTARGMR"

_HIDDEN = _get_hidden()

# ========== RGB COLOR MANAGEMENT ==========
class StarColors:
    _colors = [(255, 80, 80), (80, 255, 80), (80, 150, 255), (255, 200, 80)]
    _last_color = None
    
    @classmethod
    def get(cls):
        color = random.choice(cls._colors)
        return f"\033[38;2;{color[0]};{color[1]};{color[2]}m"
    
    @classmethod
    def get_bright(cls):
        return f"{Style.BRIGHT}{cls.get()}"

class C:
    R = Fore.RED; G = Fore.GREEN; W = Fore.WHITE; RST = Style.RESET_ALL; B = Style.BRIGHT; D = Style.DIM

# Global State
EXIT = False
OK = 0
RARE_CNT = 0
CPL_CNT = 0
LOCK = threading.Lock()
COUPLES_DATA = {}
COUPLES_LOCK = threading.Lock()
FILE_LOCKS = {}

# Folders Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_FOLDER = os.path.join(BASE_DIR, "MODxNTT")
folders = ["TOKENS-JWT", "ACCOUNTS", "RARE ACCOUNTS", "COUPLES ACCOUNTS", "GHOST/ACCOUNTS", "GHOST/RAREACCOUNT", "GHOST/COUPLESACCOUNT"]
for f in folders:
    os.makedirs(os.path.join(BASE_FOLDER, f), exist_ok=True)

REGION_LANG = {"ME":"ar","IND":"hi","ID":"id","VN":"vi","TH":"th","BD":"bn","PK":"ur","TW":"zh","CIS":"ru","SAC":"es","BR":"pt"}
HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")

# Logic Helpers
def get_lock(fname):
    with LOCK:
        if fname not in FILE_LOCKS:
            FILE_LOCKS[fname] = threading.Lock()
        return FILE_LOCKS[fname]

def generate_exponent():
    exp_digits = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    num = random.randint(1, 9999)
    return ''.join(exp_digits[d] for d in f"{num:04d}")

def build_proto(fields):
    def encode_varint(n):
        res = []
        while True:
            byte = n & 0x7F
            n >>= 7
            if n: byte |= 0x80
            res.append(byte)
            if not n: break
        return bytes(res)
    
    res = b''
    for k, v in fields.items():
        if isinstance(v, int):
            res += encode_varint((k << 3) | 0) + encode_varint(v)
        elif isinstance(v, (str, bytes)):
            enc = v.encode() if isinstance(v, str) else v
            res += encode_varint((k << 3) | 2) + encode_varint(len(enc)) + enc
    return res

def encrypt_api(plain_hex):
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(bytes.fromhex(plain_hex), AES.block_size)).hex()

# --- Core Account Generation Functions ---
# (Simplified versions of your logic to ensure stability)

def create_account_logic(region, name_pre, pass_pre, is_ghost=False):
    try:
        password = f"{pass_pre}_{_HIDDEN}_{''.join(random.choices(string.ascii_letters, k=8))}"
        res = requests.post("https://100067.connect.garena.com/api/v2/oauth/guest:register", 
                            json={"app_id": 100067, "client_type": 2, "password": password, "source": 2}, timeout=10, verify=False)
        data = res.json().get("data", {})
        if "uid" in data:
            return {"uid": data["uid"], "password": password, "region": region, "name": f"{name_pre}{generate_exponent()}"}
    except:
        return None

# --- Flask Routes ---
@app.route("/")
def home():
    return jsonify({"status": "running", "creator": "NTT MOD-X"})

@app.route("/gen")
def api_gen():
    region = request.args.get("region", "IND")
    name_pre = request.args.get("name", "MOD-X")
    pass_pre = request.args.get("pass", "MOD-X")
    
    result = create_account_logic(region, name_pre, pass_pre)
    if result:
        return jsonify({"success": True, "data": result})
    return jsonify({"success": False, "message": "Generation failed"}), 500

# --- CLI Menu ---
def main_menu():
    while not EXIT:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{StarColors.get_bright()}STAR GENERATOR MENU")
        print("1. Start CLI Generator")
        print("2. Run Flask API Server")
        print("0. Exit")
        
        choice = input("\nChoose: ")
        if choice == "1":
            print("CLI Mode starting... (Press Ctrl+C to stop)")
            # You can call your worker_thread logic here
        elif choice == "2":
            print("Starting API Server on port 5000...")
            app.run(host="0.0.0.0", port=5000)
        elif choice == "0":
            break

if __name__ == "__main__":
    try:
        # If running on a server (like Heroku/Replit), usually you want the API
        if os.environ.get("PORT"):
            app.run(host="0.0.0.0", port=int(os.environ.get("PORT")))
        else:
            main_menu()
    except KeyboardInterrupt:
        sys.exit(0)