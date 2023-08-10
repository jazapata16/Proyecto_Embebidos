import multiprocessing
import numpy as np
import math
import time
import turtle
import cmath
import socket
import json
import sys
import logging



Routes=[]

METER_TO_PIXEL = 130
ANCHORS=["1784","1785","1786","1787"]

##
centero_coodinate=(2.7,0.7)
def draw_location (x, y, txt, t):
    t.setpos(x, y)
    f=('Arial', 12, 'bold')
    t.write(txt, move=False, align='center', font=f)


    return


##

Altura_Anchor = 1.74
Altura_Tag =0.47
O_X_Y=[-230,325]
offset_X_Y=[-0.08,-0.45]
anchor_matrix=np.array([[0,0],[3.47,0],[0,4.87],[3.47,4.47]])

_x=anchor_matrix[:,0]
_y=anchor_matrix[:,1]
k = _x**2 + _y**2
d = np.zeros(len(anchor_matrix))


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
    UDP_IP = "172.27.206.153"#socket.gethostbyname(HOSTNAME)
    

logger.info("UDP Server")
logger.info("Hostname: %s | IP: %s" % (str(HOSTNAME), str(UDP_IP)))
logger.info("Esperando establecer la conexion con el cliente UDP...")


def proyeccion_dist(distancia):
    h=Altura_Anchor-Altura_Tag
    dis= math.sqrt(abs((distancia**2)-(h**2)))
    return dis

# Turtle draw function
def screen_init(width=1200, height=800, t=turtle):
    t.setup(width, height)
    t.tracer(False)
    t.hideturtle()
    t.speed(0)

def turtle_init(t=turtle):
    t.hideturtle()
    t.speed(0)
    t.penup()

def draw_ranges(x, y, txt, t):
    t.setpos(x, y)
    f=('Arial', 12, 'bold')
    t.write(txt, move=False, align='center', font=f)

def draw_uwb_anchor(x, y, txt, t):
    t.hideturtle()
    t.speed(0)
    r = 20
    t.up()
    t.goto(x, y)
    t.dot(r,"blue")
    f=('Arial', 12, 'bold')
    t.write(txt, move=False, align='left', font=f)

def draw_uwb_tag(x, y, txt, t): 
    pos_x = O_X_Y[0] + int(x * METER_TO_PIXEL)
    pos_y = O_X_Y[1] - int(y * METER_TO_PIXEL)
    t.color(1,0,0)
    t.pensize(4)
    t.goto(pos_x,pos_y)
    t.shape("circle")
    f=('Arial', 12, 'bold')
    t.write(txt, move=False, align='left', font=f)


def tag_pos(d):

    try:
        A = np.zeros((len(d) - 1, 2))
        b = np.zeros(len(d) - 1)

        for i in range(1, len(d)):
            A[i - 1] = np.array([_x[i], _y[i]]) - np.array([_x[0], _y[0]])
            b[i - 1] = d[0]**2 - d[i]**2 + k[i] - k[0]

        b = np.array(b)[np.newaxis]

        r = np.dot(np.linalg.pinv(A),b.T)/2

        x = r[0][0]
        y = r[1][0]

        return round(x+offset_X_Y[0], 2), round(y+offset_X_Y[1], 2)
    except:
        print("Error pos data")
        return -1, -1

# def uwb_range_offset(uwb_range):
#     temp = uwb_range
#     return temp

def Reciver_UDP(q):
    # UDP Init Connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        try:
            line = sock.recv(1024).decode()
            uwb_data = json.loads(line)
            data = uwb_data["links"]   
                
            if not q.empty():
                for i in range(q.qsize()): 
                    q.get()
            q.put(data)
            pass
        except KeyboardInterrupt:
            exit()

if __name__ == '__main__':

#Creating Turtle Objects
    t_a1 = turtle.Turtle()
    t_a2 = turtle.Turtle()
    t_a3 = turtle.Turtle()
    t_a4 = turtle.Turtle()
    t_a5 = turtle.Turtle()
    ANCH_OBJ=[t_a1,t_a2,t_a3,t_a4]

    t_c1 = turtle.Turtle()
    t_c2 = turtle.Turtle()
    t_c3 = turtle.Turtle()
    t_c4 = turtle.Turtle()
    ANCH_txtRg=np.array([[-400,300,t_c1],[-400,250,t_c2],[-400,200,t_c3],[-400,150,t_c4]])

##Screen BackGround
    Screen= turtle.Screen()
    Screen.setup(1366,768,0,0)
    Screen.screensize(1500,1500)
    t_img=turtle.Turtle()
    Screen.addshape("BG_R.gif")
    t_img.shape("BG_R.gif")

##Drawing Fix Anchors
    for i in range(len(ANCHORS)):
        turtle_init(ANCH_txtRg[i][2])
        draw_uwb_anchor(O_X_Y[0] + METER_TO_PIXEL * anchor_matrix[i][0],O_X_Y[1] -  METER_TO_PIXEL * anchor_matrix[i][1], "A" + ANCHORS[i] + "(" + str(anchor_matrix[i][0])+","+ str(anchor_matrix[i][1])+")", ANCH_OBJ[i])
        
#Threads
    queue = multiprocessing.Queue()
    multiprocessing.Process(target=Reciver_UDP, args=(queue,)).start()

#Main loop (Refreshing Tag Position)
    while True:
        try: 
            list = queue.get()
            for one in list:
                if one["A"] in ANCHORS:
                    indice=ANCHORS.index(one["A"])
                    d[indice]=proyeccion_dist(float(one["R"]))
                    ANCH_txtRg[indice][2].clear()
                    draw_ranges(ANCH_txtRg[indice][0],ANCH_txtRg[indice][1],"A" + ANCHORS[indice] +": "+ str(one["R"]) + "m",ANCH_txtRg[indice][2])

            if len(list) == 4:
                x, y = tag_pos(d)
                if(x != -1):
                    t_a5.clear()
                    draw_uwb_tag(x, y, "TAG"+": ("+str(x)+" , "+str(y)+")", t_a5)
    
        except KeyboardInterrupt:
            exit()