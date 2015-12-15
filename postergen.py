# imports
from imagetools import get_image_value, get_hue
from PIL import Image, ImageDraw, ImageColor
from subprocess import check_output, call
import json
import os
import math
from pprint import pprint
from joblib import Parallel, delayed
from multiprocessing import pool
import multiprocessing

# Set up parameters
POSTER_WIDTH = 24  # Inches
DPI = 300  # Dots per inch
POSTER_X = POSTER_WIDTH*DPI
POSTER_Y = 0  # I don't like this, change it
IMAGE_PATH = 'frozen.jpg'
VIDEO_PATH = 'frozen.mp4'
FFMPEG_BIN_DIR = 'ffmpeg/bin/'
FRAME_DIR = 'frames/'


'''
def histogram_correct(segments):
    counter = 1
    for segment in segments:
        print("Correcting value of segment #"+str(counter)+" of "+str(len(segments)))
        l_dif = round(segment.image.value-segment.frame.value)
        if(l_dif!=0):
            segment.frame.image = luminate(segment.frame.image, l_dif)
        counter+=1
    return segments
'''

def histogram_correct(segments):
    for segment in segments:
        old_lum = segment.frame.value
        l_dif = round(segment.value-segment.frame.value)
        print(l_dif)
        if(l_dif!=0):
            segment.frame.image = luminate(segment.frame.image, l_dif)
    return segments

def luminate(image, l_dif):
    image = image.convert("HSV")
    for x in range (0, image.size[0]):
        for y in range (0, image.size[1]):
            pixel = image.getpixel((x,y))
            new_lum = pixel[2]+ l_dif
            new_lum = clamp(0,254,new_lum)
            image.putpixel((x,y),(pixel[0],pixel[1],new_lum))
    return image




def pprint_poster(segments, x_sections, y_sections):
    x_width = segments[0].frame.image.size[0]*x_sections
    y_height = segments[0].frame.image.size[1]*y_sections

    image = Image.new("RGB",(x_width,y_height))

    for segment in segments:
        x_offset = segment.position[0]*segment.frame.image.size[0]
        y_offset = segment.position[1]*segment.frame.image.size[1]
        pprint(str(x_offset)+" "+str(y_offset))
        box = (x_offset,y_offset,x_offset+segment.frame.image.size[0],y_offset+segment.frame.image.size[1])
        #pprint(box)
        image.paste(segment.frame.image, (box))

    image.save("test/final4.jpg","JPEG")

def color_print(segments, x_sections, y_sections):
    x_width = segments[0].frame.image.size[0]*x_sections
    y_height = segments[0].frame.image.size[1]*y_sections

    image = Image.new("RGB",(x_width,y_height))

    for segment in segments:
        x_offset = segment.position[0]*segment.frame.image.size[0]
        y_offset = segment.position[1]*segment.frame.image.size[1]
        pprint(str(x_offset)+" "+str(y_offset))
        box = (x_offset,y_offset,x_offset+segment.frame.image.size[0],y_offset+segment.frame.image.size[1])
        #pprint(box)
        image.paste(segment.frame.image, (box))

        print((segment.hue,100, segment.value))
        color = ImageColor.getrgb("hsv("+str(segment.hue)+",50%,"+str(segment.value)+"%)")
        draw = ImageDraw.Draw(image)
        draw.rectangle(box, color,color)

    image.save("test/colors.jpg","JPEG")



def create_poster_sections(image, x_sections, y_sections):
    x_width = image.size[0]/x_sections
    y_height = image.size[1]/y_sections

    segments = []

    for x in range(0, x_sections):
        for y in range(0, y_sections):
            segment = PosterSegment()
            segment.position = (x,y)
            x_offset = int(x*x_width)
            y_offset = int(y*y_height)
            box = ((x_offset, y_offset, x_offset+int(x_width), y_offset+int(y_height)))
            segment.image = image.crop(box)
            segments.append(segment)
    return segments


def clamp(min, max, num):
    if num < min:
        num = min
    elif num > max:
        num = max
    return num

def calculate_frame_dimensions(video):
    video_params = get_video_details(video)
    num_of_frames = math.floor(float(video_params['duration']))  # 1 second = 1 frame
    print(num_of_frames)
    ratio = video_params['width']/video_params['height']  # original frame size ratio
    #frame_width = math.floor(POSTER_X/math.floor(POSTER_X/math.sqrt((POSTER_X*POSTER_Y*ratio)/num_of_frames)))  # formula for finding width of new frame
    frame_width = math.sqrt((POSTER_X*POSTER_Y*ratio)/num_of_frames)  # formula for finding width of new frame
    #frame_height = math.floor(frame_width/ratio)
    frame_height = frame_width/ratio
    return math.floor(frame_width), math.floor(frame_height)


def get_video_details(video):
    ffprobe_output = check_output(os.path.join(FFMPEG_BIN_DIR, 'ffprobe.exe')+" "+video +
                                  " -v quiet -print_format json -show_streams")
    json_data = json.loads(ffprobe_output.decode('utf-8'))
    video_details = {}
    for i in json_data['streams']:
        if i['codec_type'] == "video":
            video_details = {'width': i['width'],
                             'height': i['height']}
    ffprobe_output = check_output(os.path.join(FFMPEG_BIN_DIR, 'ffprobe.exe')+" "+video +
                                  " -v quiet -print_format json -show_entries format=duration")
    json_data = json.loads(ffprobe_output.decode('utf-8'))
    video_details['duration'] = json_data['format']['duration']

    return video_details


def generate_frames(video, width):
    cmd = os.path.join(FFMPEG_BIN_DIR, 'ffmpeg.exe')+" -i " + video + " -f image2 -vf \"scale="+str(width)+":-1, fps=fps=1\" "+FRAME_DIR+"out%04d.jpg"
    call(cmd)


class PosterSegment:
    def __init__(self):
        self.image = None
        self.position = None
        self.brightness = None
        self.hue = None





def print_poster(image, x_num, y_num, segments):
    #final = Image.new(mode="RGB", size=((int(POSTER_X), int(POSTER_Y))))
    final = Image.new(mode="RGB", size=((image.size[0],image.size[1])))

    x_width = image.size[0]/x_num
    y_height = image.size[1]/y_num

    x_count = 0
    y_count = 0
    for segment in segments:
        x_offset = int(x_count*x_width)
        y_offset = int(y_count*y_height)
        final.paste(segment.image, (x_offset, y_offset, x_offset+int(x_width), y_offset+int(y_height)))
        x_count+=1
        if(x_count==x_num):
            x_count=0
            y_count+=1
    print(y_count)
    print(x_count)
    final.save("test/final.jpg", "JPEG")


if __name__ == "__main__":

    def main():

        num_cores = multiprocessing.cpu_count()


        #Load image and validate
        print("Calculating dimensions...")
        image = Image.open(IMAGE_PATH)
        global POSTER_Y
        POSTER_Y = POSTER_X/(image.size[0]/image.size[1])

        #Determine dimensions of frames
        frame_dims = calculate_frame_dimensions(VIDEO_PATH)
        num_frames_x = math.floor(POSTER_X/frame_dims[0])
        num_frames_y = math.floor(POSTER_Y/frame_dims[1])

        #Split image into sections
        print("Generating poster sections...")
        segments = create_poster_sections(image, num_frames_x, num_frames_y)

        for segment in segments:
            segment.value = get_image_value(segment.image)
            segment.hue = get_hue(segment.image)
        #segments = Parallel(n_jobs=num_cores)(delayed(get_value)(segment) for segment in segments)


        #Rank segments by value
        segments = sorted(segments, key=lambda x: x.value)

        #Create frames using FFmpeg
        print("Extracting movie frames")
        #generate_frames(VIDEO_PATH, frame_dims[0])

        #Load frames into memory
        frames = []
        count = 1
        for file in os.listdir(FRAME_DIR):
            print("Processing file "+str(count)+" of "+str(len(os.listdir(FRAME_DIR))))
            frame = PosterSegment()
            frame.image = Image.open(os.path.join(FRAME_DIR, file))
            frame.value = get_image_value(frame.image)
            frames.append(frame)
            count+=1

        #Sort frames by value
        frames = sorted(frames, key=lambda x: x.value)


        if(len(segments)>len(frames)):
            x = 0
            for x in range(len(frames), len(segments)):
                frame = PosterSegment()
                frame.value = frames[len(frames)-1].value
                frame.image = frames[len(frames)-1].image
                frames.append(frame)

        i = 0
        for segment in segments:
            segment.frame = frames[i]
            i+=1

        #newPool = pool.Pool(processes=4)
        #newPool.map(histogram_correct, segments)
        #segments = Parallel(n_jobs=num_cores)(delayed(histogram_correct)(segment) for segment in segments)




        #segments = histogram_correct(segments)

        #pprint(segments)
        color_print(segments, num_frames_x, num_frames_y)
        #pprint_poster(segments, num_frames_x, num_frames_y)

    main()







#Rank frames by value
#Assign each section a frame based on value
#Reassemble poster

