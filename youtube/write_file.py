def write_file(file, result):

    fs = open(file, 'w', encoding="utf-8")

    for video in result:
        fs.write(video["title"] + "\n")
        fs.write(video["link"] + "\n")
        fs.write(video["time"] + "\n\n")
        # print(video["title"])

    fs.close()


def write_latest_video(youtube, channelId, file, tag_list, result):

    # response = api_activity(youtube, channelId)
    # result = extract_video(response, tag_list)
    print(result)
    write_file(file, result)
    print("written")