#!/usr/bin/env python
""" module docstring, yo! """

import sys
import socket
import rospy
import tf_conversions
from geometry_msgs.msg import Pose


UDP_IP = ''
UDP_PORT = 30001
TEST_COMMAND = "[X=-312.74 Y=1.00 Z=900.00 A=-0.00 B=-1.13 C=0.00]"
SOCK = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

# sock.settimeout(10)
SOCK.bind((UDP_IP, UDP_PORT))


def callback(data):
    """ function docstring, yo! """
    print data


def talker_listener():

    cartesian_pose_pub = rospy.Publisher('cartesian_pose', Pose, queue_size=1)
    #rospy.init_node('kuka_cartesian_pose', anonymous=True)
    rospy.init_node('kuka_udp_comms', anonymous=True)
    rospy.Subscriber("target_EE_pose", Pose, callback)
    rate = rospy.Rate(10)  # 10hz


    #while not rospy.is_shutdown():
    try:

        msg = Pose()
        # msg.header.stamp = rospy.get_rostime()

        data, addr = SOCK.recvfrom(1024)

        d = dict(
            item.split('=') for item in data[1:len(data)-1].split(' ')
            )

        msg.position.x = float(d["X"])
        msg.position.y = float(d["Y"])
        msg.position.z = float(d["Z"])

        msg.orientation = tf_conversions.transformations.quaternion_from_euler(
            float(d['A']), float(d['B']), float(d['C']),
            'szyx'
            )

        cartesian_pose_pub.publish(msg)

        SOCK.sendto(TEST_COMMAND, addr)
        SOCK.close()
    except Exception as exception_e:
        rospy.logerr("%s", exception_e)

    # rate.sleep()


if __name__ == '__main__':
    MYARGV = rospy.myargv(argv=sys.argv)

    print("args I don't care about: ", MYARGV)
    try:
        talker_listener()
    except rospy.ROSInterruptException:
        SOCK.close()
