from std_msgs.msg import String
import rclpy
from rclpy.node import Node
import socket
import threading

#ros2 run rsp_comm rosController


def thread_arret_urgence(socket_urg):
    data, addr = socket_urg.recvfrom(1024)
    print(data)
    return False
class socketNode(Node):
    def __init__(self):
        print('debug')
        super().__init__("socket_receiver")
        self.HOST='192.168.20.92'
        self.PORT=5000
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.HOST, self.PORT))
        socketurg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
        socketurg.bind((self.HOST,self.PORT+1))

        self.publisher=self.create_publisher(String, 'socket_topic', 10)
        x = threading.Thread(target=thread_arret_urgence, args=(socketurg,))
        x.start()
        while x.is_alive():
            self.socket_listener()
    def socket_listener(self):
        # Création d'une instance de socket
        self.socket.listen(1)

        print('En attente de connexion...')

        conn, addr = self.socket.accept()
        print('Connecté à', addr)

        while True:
            data = conn.recv(1024)  # Réception des données du socket
            if not data:
               break

            print('Message reçu:', data)

            # Publier le message sur un topic ROS 2

            msg = String()
            msg.data = str(data)
            self.get_logger().info('Publishing: "%s"' % msg.data)
            self.publisher.publish(msg)

        print("socket fermé")
        conn.close()


def main(args=None):
    rclpy.init(args=None)
    node = socketNode()
    node.socket.close()
    print("start")

    rclpy.spin(node)
    rclpy.shutdown()



if __name__ == '__main__':
    main()


