import os
import shutil

video_path = "videos"
images_path = os.path.abspath("images")
videos_path = os.path.abspath("videos")
distribute_path = os.path.abspath("distribute")

shutil.rmtree(images_path)
os.makedirs(images_path)
shutil.rmtree(videos_path)
os.makedirs(videos_path)
shutil.rmtree(distribute_path)
os.makedirs(distribute_path)