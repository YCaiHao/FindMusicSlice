import os
import json
from random import randint
from sys import argv
from pychorus import find_and_output_chorus
from pydub import AudioSegment


def getNPList (path):
    """
        获取一个List，元素类型为 (文件名, 文件路径)
    """
    l = []
    # 遍历文件，把所有mp3文件加入数组
    for root, dirs, files in os.walk(path):
        for file in files:
            # name: 文件名， ext： 文件后缀
            name, ext = os.path.splitext(file)
            if (ext == ".mp3"):
                # ("name", "../name.mp3")
                l.append((name, os.path.join(path, file)))
    return l

def getRandomMP3(path, clip_length):
    """
        随机获得一个mp3音频片段
    """
    snd = AudioSegment.from_mp3(path)
    # 略过前20面
    random = randint(20 * 1000, len(snd) - clip_length * 1000)
    return snd[random:random + clip_length * 1000]


def processMP3 (name, path, destPath):
    """
        处理mp3音频文件，找寻音乐高潮部分，生产新的mp3文件，并添加渐入渐出效果
    """
    # 渐入渐出时长
    FADE_DURATION = 3000
    # 音频长度（s）
    CLIP_LENGTH = 20

    # 找到音乐高潮并导出为.wav格式
    wavPath = os.path.join(musicDirPath, name + ".wav")
    result = find_and_output_chorus(path, wavPath, CLIP_LENGTH + 1)
    
    if  result is not None:
        # 载入找到的音乐高潮.wav文件为其添加渐入渐出效果
        snd = AudioSegment.from_wav(wavPath)
    else:
        #当找不到音乐高潮时，采用随机的方式获取
        snd = getRandomMP3(path, CLIP_LENGTH)
    
    # 渐入
    snd = snd.fade(from_gain=-15.0, start=0, duration=FADE_DURATION)
    # 渐出
    snd = snd.fade(to_gain=-15.0, start=len(snd) - FADE_DURATION, duration=FADE_DURATION)
    # 导出音乐高潮文件，格式为mp3
    mp3Path = os.path.join(destPath, name + ".mp3")
    snd.export(mp3Path)

    if result is not None:
        # 删除中间.wav文件
        os.remove(wavPath)
        return True
    else:
        return False    


def removeDir (path):
    """
        删除指定文件夹内的所有内容包括这个文件夹本身
    """
    for root, dirs, files in os.walk(path):
        for f in files:
            os.remove(os.path.join(path, f))
        for d in dirs:
            removeDir(os.path.join(path, d))
    os.rmdir(path)


if __name__ == "__main__":
    if len(argv) >= 2:
        topPath = argv[1]
        
        if not os.path.isdir(topPath):
            print("路径输入错误，需要文件路径")
            exit(0)

        nameAndPathList = getNPList(topPath)

        musicDirPath = os.path.join(topPath, "music")
        if os.path.exists(musicDirPath):
            removeDir(musicDirPath)

        os.mkdir(musicDirPath)
        musicJSON = []
        for name, path in nameAndPathList:
            processMP3(name, path, musicDirPath)
            mp3Path = os.path.join(musicDirPath, name + ".mp3")
            musicJSON.append({name: "music" + "/" + name + ".mp3"})
            print(f"写出[{mp3Path}]完成。。。")
        
        # 导出json文件
        jsonFilePath = os.path.join(musicDirPath, "MusicInfo.json")
        with open(jsonFilePath, "w") as f:
            json.dump(musicJSON, f)
            print(f"写出[{jsonFilePath}]完成。。。")
    else:
        print("请输入文件夹路径！")