import cv2
import numpy as np


def detect_camera_movement(frames, diff_threshold=30, match_threshold=0.7, min_matches=10):
    """
    frames: List of np.ndarray (BGR images)
    diff_threshold: Threshold for mean frame difference (for simple detection)
    match_threshold: Ratio threshold for feature matching (Lowe's ratio test)
    min_matches: Minimum good matches to consider for homography
    Returns: List of frame indices where significant camera movement is detected
    """
    movement_indices = []
    orb = cv2.ORB_create()
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    for i in range(1, len(frames)):
        prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)

        # 1. Simple difference (frame differencing)
        diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = np.mean(diff)
        if mean_diff > diff_threshold:
            movement_indices.append(i)
            continue

        # 2. Homography with feature matching
        kp1, des1 = orb.detectAndCompute(prev_gray, None)
        kp2, des2 = orb.detectAndCompute(curr_gray, None)
        if des1 is None or des2 is None:
            continue
        matches = bf.knnMatch(des1, des2, k=2)
        good = []
        for m, n in matches:
            if m.distance < match_threshold * n.distance:
                good.append(m)
        if len(good) > min_matches:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if H is not None:
                dx = H[0, 2]
                dy = H[1, 2]
                da = np.arctan2(H[1, 0], H[0, 0])
                # If translation or angle is large, there is camera movement
                if abs(dx) > 5 or abs(dy) > 5 or abs(np.degrees(da)) > 2:
                    movement_indices.append(i)
    return movement_indices 