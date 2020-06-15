import paho.mqtt.client as mqtt
import base64
import tkinter as tk
from tkinter import filedialog, Radiobutton, messagebox, Listbox, Scrollbar, Menu


def noError(error):
    messagebox.showinfo(title="Error", message=error)


def GUI(view, path, client):
    settings = tk.Canvas(view, bg="#ebebeb", width=366, height=106)
    settings.place(x=14, y=35)

    menu = Menu(view, bg="#b3b3b3")
    view.config(menu=menu)
    filemenu = Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Exit", command=view.destroy)
    help = Menu(menu)
    menu.add_cascade(label="Help", menu=help)
    help.add_command(label="About")

    scrollY = Scrollbar(view)
    scrollY.place(x=522, y=35, height=324)

    scrollX = Scrollbar(view, orient="horizontal")
    scrollX.place(x=402, y=359, width=122)

    messageWind = tk.Listbox(view, bg="#b3b3b3", height=20, yscrollcommand=scrollY.set, xscrollcommand=scrollX.set)
    scrollY.config(command=messageWind.yview)
    scrollX.config(command=messageWind.xview)
    messageWind.place(x=402, y=35)
    messageWind.insert(1, "Isn't connected!")

    messageSettings = tk.Canvas(view, bg="#ebebeb", width=366, height=207)
    messageSettings.place(x=14, y=156)

    tk.Label(view, text="Topic:", bg="#ebebeb", padx=1, pady=0.35).place(x=27, y=178)
    topic = tk.Entry(view, width=26, bg="#b3b3b3")
    topic.place(x=73, y=180)

    tk.Label(view, text="QoS:", bg="#ebebeb", padx=1, pady=0.35).place(x=33, y=210)

    q = tk.IntVar()
    qos_0 = tk.Radiobutton(view, text="0", variable=q, bg="#ebebeb", value=0)
    qos_0.place(x=73, y=209)

    qos_1 = tk.Radiobutton(view, text="1", variable=q, bg="#ebebeb", value=1)
    qos_1.place(x=126, y=209)

    qos_2 = tk.Radiobutton(view, text="2", variable=q, bg="#ebebeb", value=2)
    qos_2.place(x=179, y=209)

    tk.Label(view, text="File:", bg="#ebebeb", padx=1, pady=0.35).place(x=36, y=243)
    filename = tk.Label(view, text="Choose file!", bg="#ebebeb", padx=1, pady=0.35)
    filename.place(x=73, y=243)

    selectButton = tk.Button(view, text="Select File", bg="#b3b3b3", padx=6, pady=3,
                             command=lambda: selectFile(path, view))
    selectButton.place(x=281, y=179)

    sendButton = tk.Button(view, text="Send", bg="#b3b3b3", padx=19, pady=3,
                           command=lambda: sendFile(topic, view, path, client, q.get(), messageWind))
    sendButton.place(x=280, y=226)
    tk.Label(view, text="Host:", bg="#ebebeb", padx=1, pady=0.35).place(x=32, y=44)
    host = tk.Entry(view, width=26, bg="#b3b3b3")
    host.place(x=73, y=46)

    tk.Label(view, text="Port:", padx=1, bg="#ebebeb", pady=0.35).place(x=34, y=77)
    port = tk.Entry(view, width=26, bg="#b3b3b3")
    port.place(x=73, y=79)

    tk.Label(view, text="ClientId:", padx=1, bg="#ebebeb", pady=0.35).place(x=15, y=110)
    clientId = tk.Entry(view, width=26, bg="#b3b3b3")
    clientId.place(x=73, y=112)

    connectButton = tk.Button(view, text="Connect", bg="#b3b3b3", padx=24, pady=8,
                              command=lambda: connectBrok(host, port, clientId, messageWind))
    connectButton.place(x=264, y=45)

    disconnectButton = tk.Button(view, text="Disconnect", bg="#b3b3b3", padx=17, pady=8,
                                 command=lambda: discon(client, messageWind))
    disconnectButton.place(x=264, y=92)

    view.mainloop()


def discon(client, mesWin):
    client.disconnect()
    mesWin.insert("end", "Disconnected from the broker!")


def selectFile(path, view):
    openFile = filedialog.askopenfilename(initialdir="/", title="Select File", filetypes=(
        ("MP4", ".mp4"), ("AVI", ".avi"), ("MKV", ".mkv"), ("All Files", "*.*")))
    path.clear()
    path.append(openFile)
    filename = tk.Label(view, text=path, bg="#ebebeb", padx=1, pady=0.35)
    filename.place(x=73, y=243)


def sendFile(topicWindow, view, path, client, qos, mesWin):
    topic = topicWindow.get()
    if len(topic) == 0:
        noError("Please, input a topic!")
        return
    if not path:
        noError("Please, select a file!")
        return
    file = path[0]
    mesWin.insert("end", "Sending...")
    client.loop_start()
    print("Publishing... ")
    encoded = convertImageToBase64(file)
    inf = client.publish(topic, encoded, qos)
    mesWin.insert("end", file + " has been sent!")
    inf.wait_for_publish()


def convertImageToBase64(openFile):
    with open(openFile, "rb") as image_file:
        encoded = base64.b64encode(image_file.read())
    return encoded


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Succesfully connected to the broker")
    else:
        noError("Error code: " + rc +
                "\n1: Connection refused - i  ncorrect protocol version" +
                "\n2: Connection refused - invalid client identifier" +
                "\n3: Connection refused - server unavailable" +
                "\n4: Connection refused - bad username or password" +
                "\n5: Connection refused - not authorised" +
                "\n6-255: Currently unused.")


def on_publish(client, userdata, mid):
    print("The message has been sent to a broker!")
    print("MID:", mid)


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


def main():
    view = tk.Tk()
    view.title("MQTT Client: Publisher")
    view.geometry("550x400")
    view.configure(bg="white")
    view.resizable(1, 0)

    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    client.on_connect = on_connect
    client.on_publish = on_publish

    path = []
    clients = []
    GUI(view, path, client)


if __name__ == '__main__':
    main()