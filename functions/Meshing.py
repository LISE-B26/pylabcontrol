__author__ = 'Experiment'
import numpy as np

def get_points_along_line(pos1, pos2, xpts):
    dx = 1.*(pos2[0] - pos1[0]) / (xpts - 1)
    dy = 1.*(pos2[1] - pos1[1]) / (xpts - 1)

    xy = np.zeros([xpts, 2])

    for i in np.arange(xpts):
        xy[i] = pos1[0] + 1.*i * dx, pos1[1] + i * dy
    return xy


def get_points_on_a_grid(pos_left_bottom, pos_right_top, xpts, ypts):
    '''

    :param pos_left_bottom:
    :param pos_right_top:
    :param xpts:
    :param ypts:
    :return: list of points on a grid (dimension: xpts * ypts,  2)
    '''
    dx = 1.*(pos_right_top[0] - pos_left_bottom[0]) / (xpts - 1)
    dy = 1.*(pos_right_top[1] - pos_left_bottom[1]) / (ypts - 1)

    xy = np.zeros([xpts, ypts, 2])

    for ix in np.arange(xpts):
        for iy in np.arange(xpts):
            xy[ix, iy] = pos_left_bottom[0] + 1.*ix * dx, pos_left_bottom[1] + iy * dy


    return xy.reshape(xpts * ypts,2)


def two_pts_to_center_size(pt1, pt2):

    width = abs(pt1[0] - pt2[0])
    height = abs(pt1[1] - pt2[1])

    x0 = min(pt1[0], pt2[0]) + width / 2.
    y0 = min(pt1[1], pt2[1]) + height / 2

    center = [x0, y0]
    return center, width, height

def two_pts_to_roi(pt1, pt2, xPts = None, yPts = None):
    center, width, height = two_pts_to_center_size(pt1, pt2)

    roi = {
        "xo": center[0],
        "yo": center[1],
        "dx": width,
        "dy": height,
        "xPts": xPts,
        "yPts": yPts
    }
    return roi



def shift_line_perp(pos1, pos2, shift):
    '''
        returns the two points shifted by 'shift' perpedicular to the line defined be the two points
    '''

    p1 = np.array(pos1)
    p2 = np.array(pos2)

    dp = p2 - p1

    nperp = np.array([1, -dp[0]/dp[1]])
    nperp /= np.sqrt(nperp[0]**2 + nperp[1]**2)

    return p1 + shift * nperp, p2 + shift * nperp

# pt1, pt2 = [1,2],[2,3]
#
# center, width, height = two_pts_to_center_size(pt1, pt2)
#
# print center, width, height