import paho.mqtt.client as mqtt
import tkinter as tk
import cv2 as cv
from tkinter import messagebox, filedialog, Menu, Scrollbar
import base64


def noTopicError():
    messagebox.showinfo(title="Error", message="Please, input a topic!")


def unsubFrom(client, topicWindow, topics, mw):
    topic = topicWindow.get()
    if len(topic) == 0:
        noTopicError()
        return
    topics.remove(topic)
    client.loop_start()
    client.unsubscribe(topic)
    mw.insert("end", "Unsubscribed from " + topic)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Succesfully connected to the broker")
    else:
        print("Error code: ", rc)
        print("1: Connection refused - incorrect protocol version")
        print("2: Connection refused - invalid client identifier")
        print("3: Connection refused - server unavailable")
        print("4: Connection refused - bad username or password ")
        print("5: Connection refused - not authorised")
        print("6-255: Currently unused.")


def connectBrok(hostWindow, portWindow, clientId, mesw):
    id = clientId.get()
    host = hostWindow.get()
    if not host:
        noError("Please, input a host!")
        return
    port = portWindow.get()
    if not port:
        noError("Please, input a port!")
        return
    mesw.insert("end", "Connected to the broker!")


def noError(error):
    messagebox.showinfo(title="Error", message=error)


def discon(client, mesWin):
    client.disconnect()
    mesWin.insert("end", "Disconnected from the broker!")


def on_subscribe(client, userdata, mid, qos):
    print("Succesfully subscribed to the topic!")
    print("MID:", mid)
    print("QOS:", qos)


def on_unsubscribe(client, data, mid):
    print("Succesfully unsubscribed from the topic!")
    print("MID:", mid)


def on_message(client, userdata, message):
    print("Recieved: " + str(message.payload) + "\nOn topic: " + message.topic + "\nQoS: " + str(message.qos))
    decode = base64.decodebytes(message.payload)
    with open("Files/file1.mp4", "wb") as video:
        video.write(base64.decodebytes(message.payload))
    messages.insert("end", "You have one message on topic: " + message.topic)


def setting(messageWind):
    root = tk.Tk()
    root.title("Settings")
    root.geometry("400x220")
    root.config(bg="white")
    tk.Label(root, text="Host:", bg="#ebebeb", padx=1, pady=0.35).place(x=32, y=44)
    host = tk.Entry(root, width=26, bg="#b3b3b3")
    host.place(x=73, y=46)

    tk.Label(root, text="Port:", padx=1, bg="#ebebeb", pady=0.35).place(x=34, y=77)
    port = tk.Entry(root, width=26, bg="#b3b3b3")
    port.place(x=73, y=79)

    tk.Label(root, text="ClientId:", padx=1, bg="#ebebeb", pady=0.35).place(x=15, y=110)
    clientId = tk.Entry(root, width=26, bg="#b3b3b3")
    clientId.place(x=73, y=112)

    connectButton = tk.Button(root, text="Connect", bg="#b3b3b3", padx=24, pady=8,
                              command=lambda: connectBrok(host, port, clientId, messageWind))
    connectButton.place(x=264, y=45)

    disconnectButton = tk.Button(root, text="Disconnect", bg="#b3b3b3", padx=17, pady=8,
                                 command=lambda: discon(client, messageWind))
    disconnectButton.place(x=264, y=92)
    root.mainloop()


def GUI(client, view, topics, path, messages):
    scrollY = Scrollbar(view)
    scrollY.place(x=390, y=33, height=324)

    scrollX = Scrollbar(view, orient="horizontal")
    scrollX.place(x=266, y=357, width=124)

    mesWindow = messages
    mesWindow.place(x=266, y=33)
    scrollY.config(command=mesWindow.yview)
    scrollX.config(command=mesWindow.xview)

    mesWindow.insert("end", "Isn't connected!")
    mesWindow.insert("end", "=============================")
    mesWindow.insert("end", "Connection settings: File -> settings")
    mesWindow.insert("end", "=============================")

    menu = Menu(view, bg="#b3b3b3")
    view.config(menu=menu)
    filemenu = Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Settings", command=lambda: setting(mesWindow))
    filemenu.add_command(label="Exit", command=view.destroy)
    help = Menu(menu)
    menu.add_cascade(label="Help", menu=help)
    help.add_command(label="About")

    canvas = tk.Canvas(view, bg="#e8e8e8", width=229, height=134)
    canvas.place(x=12, y=33)

    canvas = tk.Canvas(view, bg="#e8e8e8", width=229, height=182)
    canvas.place(x=12, y=186)

    tk.Label(view, text="Topic: ", bg="#e8e8e8").place(x=25, y=50)
    topic = tk.Entry(view, width=26, bg="#b3b3b3")
    topic.place(x=70, y=49)

    tk.Label(view, text="QoS:", bg="#e8e8e8", padx=1, pady=0.35).place(x=30, y=87)

    q = tk.IntVar()
    qos_0 = tk.Radiobutton(view, text="0", variable=q, bg="#e8e8e8", value=0)
    qos_0.place(x=70, y=86)

    qos_1 = tk.Radiobutton(view, text="1", variable=q, bg="#e8e8e8", value=1)
    qos_1.place(x=126, y=86)

    qos_2 = tk.Radiobutton(view, text="2", variable=q, bg="#e8e8e8", value=2)
    qos_2.place(x=179, y=86)

    sub = tk.Button(view, text="Subscribe", bg="#b3b3b3", padx=19,
                    command=lambda: subOn(client, topic, q.get(), topics, mesWindow))  # replace 2 to qos
    sub.place(x=25, y=121)

    unsub = tk.Button(view, text="Unsubscribe", bg="#b3b3b3", padx=12,
                      command=lambda: unsubFrom(client, topic, topics, mesWindow))
    unsub.place(x=132, y=121)

    watch = tk.Button(view, text="Watch message", bg="#b3b3b3", padx=11,
                      command=showVideo)
    watch.place(x=70, y=300)

    allTopic = tk.Button(view, padx=15, text="View all topics", bg="#b3b3b3",
                         command=lambda: viewTopics(topics, mesWindow))
    allTopic.place(x=70, y=250)

    saveMes = tk.Button(view, padx=16, text="Save message", bg="#b3b3b3", command=lambda: saveFile(mesWindow))
    saveMes.place(x=70, y=200)

    view.mainloop()


def saveFile(mw):
    path = filedialog.asksaveasfilename(initialdir="/", title="Save as",
                                        defaultextension=(("Image", "*.jpg"), ("Video", "*.mp4"), ("All files", "*.*")),
                                        filetypes=(("Image", "*.jpg"), ("Video", "*.mp4"), ("All files", "*.*")))
    file = open(path, "wb")
    with open("Files/file1.mp4", "rb") as videoFile:
        video = videoFile.read()
    file.write(video)
    file.close()
    mw.insert("end", "Message has been saved!")
    print(path)


def viewTopics(topics, mw):
    if not topics:
        messagebox.showinfo(title="Error", message="Please, subscribe on a topic!")
        return
    mw.insert("end", "===Subscribed topics===")
    for topic in topics:
        mw.insert("end", "\n" + topic)
    mw.insert("end", "=======================")


def subOn(client, topicWindow, qos, topics, mw):
    topic = topicWindow.get()
    if len(topic) == 0:
        noTopicError()
        return
    topics.append(topic)
    client.loop_start()
    client.subscribe(topic, qos)
    mw.insert("end", "Subscribed on '" + topic + "' with qos=" + str(qos))


def showVideo():
    file = cv.VideoCapture("Files/file1.mp4")
    if file.isOpened() == False:
        print("Can't open a file!")
        messagebox.showinfo(title="Error", message="There is no messages to watch!")
        return
    else:
        print("Succesfully open a file!")
    while file.isOpened():
        retval, image = file.read()

        if retval == True:
            cv.imshow("MQTT-Player", image)

        if cv.waitKey(20) & 0xFF == ord("q"):
            break
    file.release()
    cv.destroyAllWindows()



topics = []
path = []

view = tk.Tk()
view.title("MQTT Client: Subscriber")
view.resizable(1, 0)
view.geometry("420x380")
view.config(bg="white")

messages = tk.Listbox(view, bg="#e8e8e8", height=20)

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_unsubscribe = on_unsubscribe
GUI(client, view, topics, path, messages)

