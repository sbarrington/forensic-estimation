import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import math

json_file = "simulation_files/test/skeleton_t_pose.json"

class JsonSkeleton:
    def __init__(self, json_file):
        self.joint_to_coord = json.load(open(json_file))
        #print(self.joint_to_coord)
    
    def plot_eye_2D(self):
        xs = []
        ys = []
        
        plt.clf()

        for joint in self.joint_to_coord:
            if 'eye' in joint or 'nose' in joint:
                joint_coord = self.joint_to_coord[joint]
                xs.append(joint_coord[0])
                ys.append(-1*joint_coord[1])
                plt.text(joint_coord[0], -1*joint_coord[1], joint)
        plt.scatter(xs, ys)
        plt.show()

    def plot_skeleton(self, labels=True):
        xs = []
        ys = []
        zs = []

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for joint in self.joint_to_coord:
            joint_coord = self.joint_to_coord[joint]
            xs.append(joint_coord[2])
            ys.append(joint_coord[1])
            zs.append(joint_coord[0])
            #if "eye" in joint and "brow" not in joint:
            ax.text(joint_coord[2], joint_coord[1], joint_coord[0], joint, fontsize=6)

        ax.scatter(xs, ys, zs)

        ax.set_xlabel('X')
        ax.set_xlim3d(-1, 1)
        ax.set_ylabel('Y')
        ax.set_ylim3d(-1, 1)
        ax.set_zlabel('Z')
        ax.set_zlim3d(-1, 1)
        plt.show()

    def get_euclidian_distance(self, pointA, pointB):
        return math.sqrt((pointA[0] - pointB[0])**2 +  (pointA[1] -
        pointB[1])**2 + (pointA[2] - pointB[2])**2 )

    def get_bone_length(self, jointA, jointB):
        pointA = self.joint_to_coord[jointA]
        pointB = self.joint_to_coord[jointB]
        return self.get_euclidian_distance(pointA, pointB)

    def get_height_approximation(self):
        height = self.get_right_lower_leg_length()
        height += self.get_right_upper_leg_length()

        height += self.get_bone_length("pelvis", "neck")
        return height

    def get_right_lower_leg_length(self):
        return self.get_bone_length("right_knee", "right_ankle")

    def get_right_upper_leg_length(self):
        return self.get_bone_length("right_knee", "right_hip")

    def get_left_lower_leg_length(self):
        return self.get_bone_length("left_knee", "left_ankle")

    def get_left_upper_leg_length(self):
        return self.get_bone_length("left_knee", "left_hip")

    def get_right_lower_arm_length(self):
        return self.get_bone_length("right_elbow", "right_wrist")

    def get_right_upper_arm_length(self):
        return self.get_bone_length("right_elbow", "right_shoulder")

    def get_left_lower_arm_length(self):
        return self.get_bone_length("left_elbow", "left_wrist")

    def get_left_upper_arm_length(self):
        return self.get_bone_length("left_elbow", "left_shoulder")

    def get_across_shoulder_length(self):
        pass
    
    def average_2_points(self, pointA, pointB):
        return [(pointA[0] + pointB[0])/2, (pointA[1] + pointB[1])/2, (pointA[2] + pointB[2])/2]
    def get_IPD(self):
        # get average of right eye outer and inner corner
        right_eye_outer = self.joint_to_coord["right_eye1"]
        right_eye_inner = self.joint_to_coord["right_eye4"]
        right_eye_mid = self.average_2_points(right_eye_inner, right_eye_outer) 
       
        # same for left
        left_eye_outer = self.joint_to_coord["left_eye1"]
        left_eye_inner = self.joint_to_coord["left_eye4"]
        left_eye_mid = self.average_2_points(left_eye_inner, left_eye_outer) 
        return self.get_euclidian_distance(right_eye_mid, left_eye_mid)


# json_skeleton = JsonSkeleton(json_file)
# #json_skeleton.plot_eye_2D()
# json_skeleton.plot_skeleton()