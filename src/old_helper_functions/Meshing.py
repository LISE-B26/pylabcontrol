__author__ = 'Experiment'
'''
    old_functions related to generating points such as grids, lines, etc.
    conversion of types that describe points or areas
'''

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
        for iy in np.arange(ypts):
            xy[ix, iy] = pos_left_bottom[0] + 1.*ix * dx, pos_left_bottom[1] + iy * dy


    return xy.reshape(xpts * ypts,2)

# Gets points on an angled grid. pt_top_left and pt_top_right define the angle, and pt3 defines the distance the box should extend from
# the line between pt_top_left and pt_top_right. pts_para gives the number of points along the 1-2 line, and pts_perp gives the number of
# orthogonal points
def get_points_on_a_grid_angled(pt_top_left, pt_top_right, pt_bot_right, pts_para, pts_perp):
    '''

    :param pos_left_bottom:
    :param pos_right_top:
    :param xpts:
    :param ypts:
    :return: list of points on a grid (dimension: xpts * ypts,  2)
    '''

    xy = list()

    #distance from line to point formula from wikipedia
    shift = (((pt_top_right[1]-pt_top_left[1])*pt_bot_right[0]-(pt_top_right[0]-pt_top_left[0])*pt_bot_right[1]+pt_top_right[0]*pt_top_left[1]-pt_top_right[1]*pt_top_left[0])/np.sqrt((pt_top_right[1]-pt_top_left[1])**2+(pt_top_right[0]-pt_top_left[0])**2))/(pts_perp-1)

    for line_num in np.arange(pts_perp):
        new_pt1, new_pt2 = shift_line_perp(pt_top_left, pt_top_right, shift*line_num)
        xy.append(get_points_along_line(new_pt1, new_pt2, pts_para))

    xy = np.asarray(xy)
    print(xy)

    return xy.reshape(pts_para * pts_perp,2)


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

def roi_to_two_pts(roi):
    pt1 = [roi['xo'] -  roi['dx']/2., roi['yo'] -  roi['dy']/2.]
    pt2 = [roi['xo'] +  roi['dx']/2., roi['yo'] +  roi['dy']/2.]

    return pt1, pt2

def roi_to_extent(roi):
    '''
    :param roi: json type file that contains roi
    :return: extend as used in pyplot.imshow
    '''
    pt1, pt2 = roi_to_two_pts(roi)

    left = min(pt1[0], pt2[0])
    right = max(pt1[0], pt2[0])
    top = min(pt1[1], pt2[1])
    bottom = max(pt1[1], pt2[1])
    return left, right, bottom, top

def roi_to_min_max(roi):
    '''
    :param roi: json type file that contains roi
    :return: extend as used in pyplot.imshow
    '''
    pt1, pt2 = roi_to_two_pts(roi)

    xmin = min(pt1[0], pt2[0])
    xmax = max(pt1[0], pt2[0])
    ymin = min(pt1[1], pt2[1])
    ymax = max(pt1[1], pt2[1])
    return xmin, xmax, ymin, ymax

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