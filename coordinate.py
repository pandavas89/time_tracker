#coordinate to time
import autosize

c0_width = 55
c_width = autosize.col_width
spacing = 1
row_height= 16
margin = 5

def x2hour(x):
    global c0_width, c_width, spacing
    length = x - c0_width + c_width
    count = length//(c_width+spacing)
    return count

def y2day(y):
    global spacing, row_height
    height = y - (row_height * 3 + spacing * 2)
    count = height// (row_height + spacing)
    return count
