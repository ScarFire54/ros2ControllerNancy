from std_msgs.msg import String
import rclpy
from rclpy.node import Node
import socket
import threading
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile

#ros2 run rsp_comm rosController

MAX_LIN_VEL = 0.26
MAX_ANG_VEL = 1.82

LIN_VEL_STEP_SIZE = 0.01
ANG_VEL_STEP_SIZE = 0.1

def make_simple_profile(output, input, slop):
    if input > output:
        output = min(input, output + slop)
    elif input < output:
        output = max(input, output - slop)
    else:
        output = input
    return output

def print_vels(target_linear_velocity, target_angular_velocity):
    str = 'currently:\tlinear velocity {0}\t angular velocity {1} '.format(
        target_linear_velocity,
        target_angular_velocity)
    return str

def constrain(input_vel, low_bound, high_bound):
    if input_vel < low_bound:
        input_vel = low_bound
    elif input_vel > high_bound:
        input_vel = high_bound
    else:
        input_vel = input_vel
    return input_vel

def check_linear_limit_velocity(velocity):
    return constrain(velocity, -MAX_LIN_VEL, MAX_LIN_VEL)

def check_angular_limit_velocity(velocity):
    return constrain(velocity, -MAX_ANG_VEL, MAX_ANG_VEL)

def thread_arret_urgence(socket_urg):
    data, addr = socket_urg.recvfrom(1024)
    print(data)
    return False
class socketNode(Node):
    def __init__(self):
        print('debug')
        super().__init__("socket_receiver")
        
        
        
        # CHANGE IP HERE
        #  I
        #  I
        #  I
        #  I
        #  V
        
        
        self.HOST='10.0.2.4'
        self.PORT=5432
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.HOST, self.PORT))
        socketurg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
        socketurg.bind((self.HOST,self.PORT+1))
        
        self.target_linear_velocity = 0.0
        self.target_angular_velocity = 0.0
        self.control_linear_velocity = 0.0
        self.control_angular_velocity = 0.0
        
        qos = QoSProfile(depth=10)
        self.publisher=self.create_publisher(Twist, 'cmd_vel', qos)
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
            msg = String()
            msg.data = str(data)
            
            # Publier le message sur un topic ROS 2
            
            # Envoyer la commande au cmd_vel
            if str(msg.data) == 'up':
                self.target_linear_velocity =\
                    check_linear_limit_velocity(self.target_linear_velocity + LIN_VEL_STEP_SIZE)
            elif str(msg.data) == 'down':
                self.target_linear_velocity =\
                    check_linear_limit_velocity(self.target_linear_velocity - LIN_VEL_STEP_SIZE)
            elif str(msg.data) == 'turn_left':
                self.target_angular_velocity =\
                    check_angular_limit_velocity(self.target_angular_velocity + ANG_VEL_STEP_SIZE)
            elif str(msg.data) == 'turn_right':
                self.target_angular_velocity =\
                    check_angular_limit_velocity(self.target_angular_velocity - ANG_VEL_STEP_SIZE)
            elif str(msg.data) == 'stop':
                self.target_linear_velocity = 0.0
                self.control_linear_velocity = 0.0
                self.target_angular_velocity = 0.0
                self.control_angular_velocity = 0.0
            
            twist = Twist()
            
            self.control_linear_velocity = make_simple_profile(
                self.control_linear_velocity,
                self.target_linear_velocity,
                (LIN_VEL_STEP_SIZE / 2.0))

            twist.linear.x = self.control_linear_velocity
            twist.linear.y = 0.0
            twist.linear.z = 0.0

            self.control_angular_velocity = make_simple_profile(
                self.control_angular_velocity,
                self.target_angular_velocity,
                (ANG_VEL_STEP_SIZE / 2.0))

            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = self.control_angular_velocity
            
            
            self.get_logger().info('Publishing: "%s"' % msg.data)
            self.get_logger().info('Target speed: '+print_vels(self.target_linear_velocity, self.target_angular_velocity))
            self.publisher.publish(twist)

        print("socket fermé")
        conn.close()


def main(args=None):
    rclpy.init(args=None)
    node = socketNode()
    node.socket.close()
    print("start")

    stopping_robot = Twist()
    
    stopping_robot.linear.x = 0.0
    stopping_robot.linear.y = 0.0
    stopping_robot.linear.z = 0.0
    
    stopping_robot.angular.x = 0.0
    stopping_robot.angular.y = 0.0
    stopping_robot.angular.z = 0.0
    
    node.publisher.publish(stopping_robot)
    
    rclpy.spin(node)
    
    stopping_robot = Twist()
    node.publisher.publish(stopping_robot)
    
    rclpy.shutdown()



if __name__ == '__main__':
    main()


