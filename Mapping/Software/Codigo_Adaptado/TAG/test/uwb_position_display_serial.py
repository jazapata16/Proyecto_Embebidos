import time
import turtle
import cmath
import serial
import json

DISTANCE_ANCHOR = 1.1
METER_TO_PIXEL = 150

ANCHOR_ID_1 = "1786"
AHCHOR_ID_2 = "1785"

Serial = serial.Serial(port='COM4', baudrate=115200,timeout=0.01)

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s
    
    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i]
                self.buf[0:] = data[i:]
                return r
            else:
                self.buf.extend(data)

# Turtle draw function      ################################################


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
    fill_cycle(x, y, r, "green", t)
    write_txt(x + r, y, txt + ": " + str(range) + "M",
              "black",  t, f=('Arial', 16, 'normal'))


def draw_uwb_tag(x, y, txt, t):
    pos_x = -250 + int(x * METER_TO_PIXEL)
    pos_y = 150 - int(y * METER_TO_PIXEL)
    r = 20
    fill_cycle(pos_x, pos_y, r, "blue", t)
    write_txt(pos_x, pos_y, txt + ": (" + str(x) + "," + str(y) + ")",
              "black",  t, f=('Arial', 16, 'normal'))

def read_data():

    try:
        data_line = ReadLine(Serial).readline().decode()
        uwb_list = []
        uwb_data = json.loads(data_line) 
        uwb_list = uwb_data["links"]
        print(data_line)

    except:
        pass
        #exit()
    return uwb_list


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

# Main                      ################################################
def main():

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

    while True:
        node_count = 0
        list = read_data()

        for one in list:
            if one["A"] == ANCHOR_ID_1:
                clean(t_a1)
                a1_range = uwb_range_offset(float(one["R"]))
                draw_uwb_anchor(-250, 150, "A1786(0,0)", a1_range, t_a1)
                node_count += 1

            if one["A"] == AHCHOR_ID_2:
                clean(t_a2)
                a2_range = uwb_range_offset(float(one["R"]))
                draw_uwb_anchor(-250 + METER_TO_PIXEL * DISTANCE_ANCHOR,
                                150, "A1785(" + str(DISTANCE_ANCHOR)+")", a2_range, t_a2)
                node_count += 1

        if node_count == 2:
            x, y = tag_pos(a2_range, a1_range, DISTANCE_ANCHOR)
            if(x != -1):
                # print(x, y)
                clean(t_a3)
                draw_uwb_tag(x, y, "TAG", t_a3)

        time.sleep(0.1)

    turtle.mainloop()


if __name__ == '__main__':
    main()