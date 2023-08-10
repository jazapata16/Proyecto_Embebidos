import multiprocessing
import time
import turtle
import cmath
import socket
import json
import sys
import logging

ANCHOR_ID_1 = "1785"
ANCHOR_ID_2 = "1786"

DISTANCE_ANCHOR = 3.0
METER_TO_PIXEL = 150

UDP_PORT = 8080

HOSTNAME = socket.gethostname()


logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch1 = logging.StreamHandler()
ch2 = logging.FileHandler('test.log')
ch1.setFormatter(formatter)
ch2.setFormatter(formatter)
logger.addHandler(ch1)
logger.addHandler(ch2)

if sys.platform == 'linux': # Linux OS
    
    INNTERFACE = 'wlp0s20f3'  # execute in your terminal $: ip a or $: ip addr
    import netifaces
    
    UDP_IP = netifaces.ifaddresses(INNTERFACE)[netifaces.AF_INET][0]['addr']
    
else: # Windows OS 
    UDP_IP = socket.gethostbyname(HOSTNAME)

logger.info("UDP Server")
logger.info("Hostname: %s | IP: %s" % (str(HOSTNAME), str(UDP_IP)))
logger.info("Esperando establecer la conexion con el cliente UDP...")

# UDP Init Connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, UDP_PORT))

# Turtle draw function
def screen_init(width=1200, height=800, t=turtle):
    t.setup(width, height)
    t.tracer(False)
    t.hideturtle()
    t.speed(0)

def turtle_init(t=turtle):
    t.hideturtle()
    t.speed(0)

def draw_line(x0, y0, x1, y1, color="black", t=turtle):
    t.pencolor(color)

    t.up()
    t.goto(x0, y0)
    t.down()
    t.goto(x1, y1)
    t.up()

def draw_fastU(x, y, length, color="black", t=turtle):
    draw_line(x, y, x, y + length, color, t)

def draw_fastV(x, y, length, color="black", t=turtle):
    draw_line(x, y, x + length, y, color, t)

def draw_cycle(x, y, r, color="black", t=turtle):
    t.pencolor(color)

    t.up()
    t.goto(x, y - r)
    t.setheading(0)
    t.down()
    t.circle(r)
    t.up()

def fill_cycle(x, y, r, color="black", t=turtle):
    t.up()
    t.goto(x, y)
    t.down()
    t.dot(r, color)
    t.up()

def write_txt(x, y, txt, color="black", t=turtle, f=('Arial', 12, 'normal')):

    t.pencolor(color)
    t.up()
    t.goto(x, y)
    t.down()
    t.write(txt, move=False, align='left', font=f)
    t.up()

def draw_rect(x, y, w, h, color="black", t=turtle):
    t.pencolor(color)

    t.up()
    t.goto(x, y)
    t.down()
    t.goto(x + w, y)
    t.goto(x + w, y + h)
    t.goto(x, y + h)
    t.goto(x, y)
    t.up()

def fill_rect(x, y, w, h, color=("black", "black"), t=turtle):
    t.begin_fill()
    draw_rect(x, y, w, h, color, t)
    t.end_fill()
    pass

def clean(t=turtle):
    t.clear()

def draw_ui(t):
    write_txt(-300, 250, "UWB Positon", "black",  t, f=('Arial', 32, 'normal'))
    fill_rect(-400, 200, 800, 40, "black", t)
    write_txt(-50, 205, "WALL", "yellow",  t, f=('Arial', 24, 'normal'))

def draw_uwb_anchor(x, y, txt, range, t):
    r = 20
    fill_cycle(x, y, r, "blue", t)
    write_txt(x + r, y, txt + ": " + str(range) + "M",
              "black",  t, f=('Arial', 16, 'normal'))

def draw_uwb_tag(x, y, txt, t):
    pos_x = -250 + int(x * METER_TO_PIXEL)
    pos_y = 150 - int(y * METER_TO_PIXEL)
    r = 20
    fill_cycle(pos_x, pos_y, r, "red", t)
    write_txt(pos_x, pos_y, txt + ": (" + str(x) + "," + str(y) + ")",
              "black",  t, f=('Arial', 16, 'normal'))

def tag_pos(a, b, c):
    if a < 0 or b < 0:
        return -1, -1

    try:
        cos_a = (b * b + c*c - a * a) / (2 * b * c)
        x = b * cos_a
        y = b * cmath.sqrt(1 - cos_a * cos_a)
        return round(x.real, 1), round(y.real, 1)
    except:
        print("Error pos data")
        return -1, -1

def uwb_range_offset(uwb_range):

    temp = uwb_range
    return temp

def Reciver_UDP(q):
    while True:
        try:
            line = sock.recv(4096).decode('UTF-8')
            uwb_data = json.loads(line)
            data = uwb_data["links"]
            
            if not q.empty():
                for i in range(q.qsize()): 
                    q.get()
            q.put(data)
        except KeyboardInterrupt:
            exit()

if __name__ == '__main__':

    t_ui = turtle.Turtle()
    t_a1 = turtle.Turtle()
    t_a2 = turtle.Turtle()
    t_a3 = turtle.Turtle()
    turtle_init(t_ui)
    turtle_init(t_a1)
    turtle_init(t_a2)
    turtle_init(t_a3)

    a1_range = 0.0
    a2_range = 0.0

    draw_ui(t_ui)
    
    queue = multiprocessing.Queue()
    multiprocessing.Process(target=Reciver_UDP, args=(queue,)).start()

    while True:
        try: 
            node_count = 0
            list = queue.get()

            for one in list:
                if one["A"] == ANCHOR_ID_1:
                    clean(t_a1)
                    a1_range = uwb_range_offset(float(one["R"]))
                    draw_uwb_anchor(-250, 150, "A" + ANCHOR_ID_1 + "(0,0)", a1_range, t_a1)
                    node_count += 1

                if one["A"] == ANCHOR_ID_2:
                    clean(t_a2)
                    a2_range = uwb_range_offset(float(one["R"]))
                    draw_uwb_anchor(-250 + METER_TO_PIXEL * DISTANCE_ANCHOR,
                                    150, "A" + ANCHOR_ID_2 + "(" + str(DISTANCE_ANCHOR)+",0)", a2_range, t_a2)
                    node_count += 1

            if node_count == 2:
                x, y = tag_pos(a2_range, a1_range, DISTANCE_ANCHOR)
                if(x != -1):
                    clean(t_a3)
                    draw_uwb_tag(x, y, "TAG", t_a3)
        

        except KeyboardInterrupt:
            exit()
