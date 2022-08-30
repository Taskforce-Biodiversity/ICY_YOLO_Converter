import xml.etree.ElementTree as ET
import statistics
import os
import cv2

#
directory = 'INPUT'
fdir = os.listdir(directory)
number_of_labels = len(fdir)

valid_percentage = 0.20
valid_images = valid_percentage * number_of_labels

# Multiclass sets,
Diptera = {'dt', 'vg', 'mg', 'zv', 'wv', 'bv'}
Coleoptera = {'wk', 'kt', 'bt', 'lk', 'lb', 'sk', 'bk'}
# Neuroptera = {'gv'}
# Hemiptera = {'wt', 'bl', 'cc'}
Hymenoptera = {'hp', 'sw', 'bw', 'sc', 'w', 'br', 'gw', 'bj', 'hm', 'gw', 'mi'}
Lepidoptera = {}

label_class = 0

img_width = 4440
img_height = 11600

print(f'images for validation : {abs(valid_images)}')

print()


for i, file in enumerate(fdir):
    ##############################################################
    if i < valid_images:
        path = 'valid'
    else:
        path = 'train'
    print(file)
    print(f'files: {i+1}/{len(fdir)}')
    print(path)

    print()

    # Resizing
    ##############################################################
    if file.endswith('.jpg'):
        # continue
        img = cv2.imread(f"{directory}/{file}")
        new_img = cv2.resize(img, (4440, 11600), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'OUTPUT/{path}/images/{file}', new_img)

    ##############################################################
    if file.endswith('.xml'):
        tree = ET.parse(f"{directory}/{file}")
        root = tree.getroot()
        rois = root[2]
        rect_dict = {}
        dict_list = []

        ##############################################################
        for index, roi in enumerate(rois):
            # Select only rectangles, skip Polylines
            if "plugins.kernel.roi.roi2d.ROI2DRectangle" == rois[index][0].text:
                # specify spec_name as the first two letters from the name of the roi (vg_004 => vg)
                try:
                    spec_name = roi[2].text[:2]
                except TypeError:  # Exception for missing values
                    spec_name = 'other'

                # check if first two letters of the name of the bounding box e.g.(vg) are present in one of the sets
                ##############################################################
                if spec_name in Diptera:
                    label_class = 1
                    # print(spec_name, 'Diptera')
                elif spec_name in Coleoptera:
                    label_class = 2
                    # print(spec_name, 'Coleoptera')
                elif spec_name in Hymenoptera:
                    label_class = 3
                    # print(spec_name, 'Hymenoptera')
                # elif spec_name in Lepidoptera:
                #     label_class = 4
                #     # print(spec_name, 'Lepidoptera')
                else:
                    label_class = 0

                ##############################################################
                rect_list = [label_class, roi[13][0].text, roi[13][1].text,
                             roi[14][0].text, roi[14][1].text]
                dict_list.append(rect_list.copy())
            else:
                # everything except rectangles (polylines) will be skipped
                continue
                ##############################################################
        file = file.strip('xml')
        with open(f'OUTPUT/{path}/labels/{file}txt', 'w') as txt_file:
            for label in dict_list:
                class_as_int, tlx, tly, brx, bry = label
                tlx = float(tlx)
                tly = float(tly)
                brx = float(brx)
                bry = float(bry)

                # yolo needs center y, cen
                ##############################################################
                # print(tlx, tly, brx, bry)
                center_x = statistics.mean([brx, tlx])
                center_y = statistics.mean([bry, tly])
                width = brx - tlx
                height = bry - tly
                width = abs(width)
                height = abs(height)

                # normalize
                ##############################################################
                n_center_x = center_x / img_width
                n_center_y = center_y / img_height

                n_width = width / img_width
                n_height = height / img_height

                print(class_as_int, n_center_x, n_center_y, n_width, n_height, file=txt_file)
