import pafy

_youtube_ex = "https://www.youtube.com/watch?v=9bZkp7q19f0"

vid = pafy.new(_youtube_ex)
print(vid.title)
print(vid.length)
print(*vid.audiostreams, sep = "\n")

aud = vid.audiostreams[2]
aud.download()