from bs4 import BeautifulSoup
import os,re,traceback
from httpx import AsyncClient
import asyncio

FILE_PATH = os.path.dirname(__file__)
Audio_PATH = os.path.join(FILE_PATH,"Audio")
baseurl = "https://genshin-impact.fandom.com/wiki/Genshin_Impact_Wiki"

async def get_url(url):
    async with AsyncClient() as client:
        req = await client.get(
            url=url
        )
    return req.text

async def download(url,char_name,file_name):
    print("正在下载{} 的 {}".format(char_name,file_name))
    print(url)
    try:
        async with AsyncClient() as client:
            req = await client.get(
                url=url
            )

        while(1):
            if os.path.exists(os.path.join(Audio_PATH,char_name)):
                with open (os.path.join(os.path.join(Audio_PATH,char_name),file_name), 'wb') as f:
                    f.write(req.content)
                    f.close
                print("下载完成!")
                break
            else:
                os.makedirs(os.path.join(Audio_PATH,char_name), exist_ok=True)
    except:
        traceback.print_exc()
        print("下载失败，该文件不存在。")

async def main():
    base_data = await get_url(baseurl)
    content_bs = BeautifulSoup(base_data, 'lxml')
    raw_data_5star = content_bs.find_all("div",class_='card_container card_5 hidden')
    raw_data_4star = content_bs.find_all("div",class_='card_container card_4 hidden')
    raw_data = raw_data_5star + raw_data_4star
    char_list = {}
    for i in raw_data:
        char_url = "https://genshin-impact.fandom.com" + i.find("a")["href"] + "/Voice-Overs/Chinese"
        if i.find("a")["title"] != "Traveler":
            char_list[i.find("a")["title"]] = char_url

    for i in char_list.keys():
        cahr_voice_data = await get_url(char_list[i])
        voice_bs = BeautifulSoup(cahr_voice_data, 'lxml')
        voice_data = voice_bs.find_all("table",class_='wikitable')

        #voice_data = voice_bs.find_all("span",class_='audio-button custom-theme hidden')
        tasks = []
        if len(voice_data)//2 == 6:
            audio_index = [0,4,8]
        else:
            audio_index = [0,len(voice_data)//2]
        
        temp_title = ""
        for g in audio_index:
            for k in voice_data[g].tbody.find_all("tr")[1:]:
                if len(k.find_all("th")) == 0:
                    audio_title = temp_title
                else:
                    audio_title = k.find_all("th")[0].text
                    temp_title = audio_title

                audio_url = []
                for j in k.td.find_all("span",class_='audio-button custom-theme hidden'):
                    audio_url.append(j.find_all("a")[0]["href"])

                audio_chinese_title = ''.join(re.findall('[\u4e00-\u9fa5]', audio_title))

                if len(audio_url) == 1:
                    tasks.append(
                        download(audio_url[0],i,"{}.ogg".format(audio_chinese_title)))
                elif len(audio_url) > 1:
                    for index,j in enumerate(audio_url):
                        tasks.append(
                            download(j,i,"{}{}.ogg".format(audio_chinese_title,str(index+1))))

                #await download(audio_url,i,"{}.ogg".format(audio_chinese_title))

                #audio_url = k.find("a")["href"]
                #print(audio_url)

        await asyncio.wait(tasks)

    #os.makedirs(file, exist_ok=True)

if __name__ == "__main__":
    asyncio.run(main())