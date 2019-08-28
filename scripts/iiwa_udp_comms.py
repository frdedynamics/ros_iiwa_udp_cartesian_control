#!/usr/bin/env python
""" module docstring, yo! """

import sys
import socket
import rospy
import tf_conversions
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped, Quaternion


UDP_IP = ''
UDP_PORT = 30001
TEST_COMMAND = "[X=-312.74 Y=1.00 Z=900.00 A=-0.00 B=-1.13 C=0.00]"
CURRENT_COMMAND = ""
SOCK = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

SOCK.settimeout(5)
SOCK.bind((UDP_IP, UDP_PORT))


def callback(data):
    """ function docstring, yo! """
    global CURRENT_COMMAND  # shame! shame! shame!
    tmp = tf_conversions.transformations.euler_from_quaternion(
        (
            data.orientation.x,
            data.orientation.y,
            data.orientation.z,
            data.orientation.w
        )
        )

    C = tmp[0]
    B = tmp[1]
    A = tmp[2]

    X = data.position.x
    Y = data.position.y
    Z = data.position.z

    CURRENT_COMMAND = "[X=%s Y=%s Z=%s A=%s B=%s C=%s]" % (X, Y, Z, A, B, C)


def talker_listener():
    global CURRENT_COMMAND  # shame! shame! shame!
    cartesian_pose_pub = rospy.Publisher(
        'cartesian_pose',
        PoseStamped,
        queue_size=1
        )

    rospy.init_node('kuka_udp_comms', anonymous=True)
    rospy.Subscriber("target_EE_pose", Pose, callback)
    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
        try:

            msg = PoseStamped()
            msg.header.stamp = rospy.get_rostime()

            data, addr = SOCK.recvfrom(1024)

            d = dict(
                item.split('=') for item in data[1:len(data)-1].split(' ')
                )

            msg.pose.position.x = float(d["X"])
            msg.pose.position.y = float(d["Y"])
            msg.pose.position.z = float(d["Z"])

            msg.pose.orientation = Quaternion(
                *tf_conversions.transformations.quaternion_from_euler(
                    float(d['C']),
                    float(d['B']),
                    float(d['A'])
                    )
                    )

            cartesian_pose_pub.publish(msg)

            SOCK.sendto(CURRENT_COMMAND, addr)

        except socket.timeout as exception_e:
            rospy.logerr("socket timeout. check connection to iiwa.")
        except Exception as exception_e:
            rospy.logerr("%s", exception_e)

    rate.sleep()


if __name__ == '__main__':
    MYARGV = rospy.myargv(argv=sys.argv)

    print("args I don't care about: ", MYARGV)
    try:
        talker_listener()
    except rospy.ROSInterruptException:
        SOCK.close()
