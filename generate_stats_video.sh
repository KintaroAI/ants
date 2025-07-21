ffmpeg -framerate 30 -i stats-frames/frame_%06d.png -vsync 0 -vf "crop=2*floor(iw/2):2*floor(ih/2)" -c:v libx264 -pix_fmt yuv420p stats.mp4
