# split-video-by-srt-python

[split-video-by-srt](https://github.com/adueck/split-video-by-srt) in python

***requires ffmpeg***

You can use this python script to automatically split video files up into seperate chunks based on timecodes from an .srt subtitle file.

Use:
```Shell
py srt-split.py [video file] [subtitle file] (optional)[output format]
```

Changes comparing to the original repo:
- The script asks if you want the clips to be just numerated or named according to the subtitles contents
- The script creates a .srt file to every clip

As of now the srt for a clip is just the subtitle with the same timecodes, later I might fix it to be any subtitles situated midst the clip start and finish
