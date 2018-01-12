import socket
import sys
from threading import Thread


def start():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', listening_port))
        s.listen(max_conn)
        print("[*] Initializing Sockets... Done")
        print("[*] Socket Binded Successfully...")
        print("[*] Server Started Successfully... {}\n".format(listening_port))
    except Exception as e:
        print("[*] Unable to Initialize Socket ---> {}, {}, {}".format(e, listening_port, max_conn))
        sys.exit(2)

    while 1:
        try:
            conn, addr = s.accept()
            data = conn.recv(buffer_size)
            Thread(target=conn_string, args=(conn, data, addr)).start()
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Proxy Server Shutting Down...")
            print("[*] Have a Nice Day...")
            sys.exit()

    s.close()


def conn_string(conn, data, addr):  # Handle Client Browser Request
    try:
        first_line = str(data).split('\n')[0]
        url = first_line.split(' ')[1]
        http_pos = url.find('://')
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]

        port_pos = temp.find(':')

        webserver_pos = temp.find('/')
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ''
        port = -1

        if port_pos == -1 or webserver_pos < port_pos:
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]

        proxy_server(webserver, port, conn, addr, data)

    except Exception as e:
        print("[*] Unable to Initialize Socket -> {}".format(e))
        print("[*] {}".format(data))
        sys.exit(2)


def proxy_server(webserver, port, conn, addr, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(data)

        while 1:
            reply = s.recv(buffer_size)

            if len(reply) > 0:
                conn.send(reply)
                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "%.3s KB" % (str(dar))
                print("[*] Request Done: {} => {} <=".format(str(addr[0]), dar))
            else:
                break

        s.close()
        conn.close()

    except socket.error as e:
        print("[*] Socket Error --> {}".format(e))
        s.close()
        conn.close()
        sys.exit(1)


try:
    listening_port = int(input("[*] Enter Listening Port Number: "))
except KeyboardInterrupt:
    print("\n[*] User Requested An Interrupt")
    print("[*] Application Exiting...")
    sys.exit()
except ValueError:
    print("[*] Oops!  That was no valid number.  Try again...")
    print("[*] Application Exiting...")
    sys.exit()

max_conn = 5  # Max Connections
buffer_size = 8192  # Max Socket Buffer

start()
