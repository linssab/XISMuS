import cv2
import time
import SpecRead

video = cv2.VideoCapture(1)
a = 0
image_no = 1

while True:
    a = a + 1
    check, frame = video.read()

    cv2.imshow("camera",frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('p'):
        cv2.imwrite(SpecRead.dirname+'image_{0}.png'.format(image_no),frame)
        frame_path = SpecRead.dirname+'image_{0}.png'.format(image_no)
        print("image {} saved!".format(frame_path))
        image_no = image_no + 1

video.release()
cv2.destroyAllWindows

