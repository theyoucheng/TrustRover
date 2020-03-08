import cv2
 
# Opens the Video file
cap= cv2.VideoCapture('/Users/David/Documents/3002_project/VID_046.MOV')
i=0
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == False:
        break
    if i < 10:
        cv2.imwrite('./test_route/video_frames/0{0}{1}'.format(i,'.jpg'),frame)
    else:
        cv2.imwrite('./test_route/video_frames/{0}{1}'.format(i,'.jpg'),frame)

    
    i+=1
    if i == 500:
        break
 
cap.release()
cv2.destroyAllWindows()