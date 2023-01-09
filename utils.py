"""
ver 1.1.2 - 20230109
============================================================
                       업데이트 내역
------------------------------------------------------------
ver. 1.1.2 마지막 티어가 출력되지 않는 오류 수정
ver. 1.1.1 티어의 인터벌 수가 다르면 경고 메시지 출력
ver. 1.1.0 배포 20230109
ver. 1.0.0 Initial Commit 20230109
============================================================
"""

import json

class TextGridJSON:
    def __init__(self):
        pass

    def tg_to_json(self, file_name, json_name):
        """
        # tg_to_json(file_name: str, json_name: str(not .json))
        ## 텍스트그리드를 JSON 포맷으로 바꾸는 메소드
        
        ### 1) 메타데이터
        아래 라인들은 텍스트그리드 파일이면 무조건 위치가 고정되어 있으며,
        JSON 파일의 메타데이터 항목(level 1)에 들어간다

        >>> {
        >>>     "metadata": object {
        >>>         "title": string,
        >>>         "xmin": number(float),
        >>>         "xmax": number(float),
        >>>         "tier_size": number(int)
        >>>     }
        >>> }

        ### 2) 티어 배열
        각 티어는 JSON 파일에 item 항목(level 1)으로 저장되며,
        이들을 모두 포함하는 items 항목은 배열이자 리스트이다.
        따라서 각 티어별로 인덱스가 부여된다.

        item은 하위 항목으로 header와 content를 가진다.
        이들은 level 2 항목이고, 이 중에서 content는 배열이다.
        item은 Python에선 리스트 타입으로 처리되는데,
        item에 속하는 header는 딕셔너리 타입이고
        content는 리스트 타입이다.
        각 인터벌(level 3)은 딕셔너리 하나에 해당하게 된다.

        하나의 티어가 시작할 때 무조건 그 티어의 정보가 나오므로
        다음과 같이 header 딕셔너리에 추가한다.

        >>> 'item': list [
        >>>     'header': object {
        >>>         'class': string,
        >>>         'name': string,
        >>>         'xmin': number(float),
        >>>         'xmax': number(float),
        >>>         'type': string,
        >>>         'size': number(int)
        >>>     },
        >>>     'content': list [
        >>>         {
        >>>             num: number(int),
        >>>             xmin: number(float),
        >>>             xmax: number(float),
        >>>             text: string
        >>>         },
        >>>         ...
        >>>     ]
        >>> ]
        """
        file = open(file_name, 'r', encoding='utf-16be')
        lines = file.readlines()

        # 메타데이터 획득
        if lines[5] != "tiers? <exists> \n":
            return

        metadata = {}
        metadata['ready_listing'] = 'yes'
        metadata['title'] = file_name
        metadata['xmin'] = float(lines[3][7:-2])
        metadata['xmax'] = float(lines[4][7:-2])
        metadata['tier_size'] = int(lines[6][7:-2])

        # 티어별 아이템 획득
        items = []

        item = []
        header = {}
        content = []
        interval = {}
        for line in lines[8:]:
            if (line[0:8] == '    item' and line != '    item [1]:\n') or lines.index(line) == len(lines) - 1:
                content.append(interval)
                item.append(header)
                item.append(content)
                items.append(item)

                item = []
                header = {}
                content = []
                interval = {}
                # 새로운 item이 시작될 때마다 리셋한다.
            else:
                # 사실 여기서 else로 나누지 않고 바로 elif로 line[:13] = '        class'라고 해도
                # 실행하는 데에 아무런 문제가 없다.
                # 다만 각 티어가 구분되는 모습을 보이기 위해
                # 임의로 else로 넣은 다음 다시 조건문을 사용한 것.
                if line[:13] == '        class':
                    header["class"] = line[17:-3]
                elif line[:12] == '        name':
                    header["name"] = line[16:-3]
                elif line[:12] == '        xmin':
                    header["xmin"] = float(line[15:-2])
                elif line[:12] == '        xmax':
                    header["xmax"] = float(line[15:-2])
                elif line[:23] == '        intervals: size':
                    header["type"] = 'interval'
                    header["size"] = int(line[26:-2])
                
                elif line[:19] == '        intervals [' and line != '        intervals [1]:\n':
                    content.append(interval)
                    interval = {}
                    interval["num"] = int(line[19:-3])
                    # 새로운 인터벌이 시작될 때마다 인터벌 딕셔너리 리셋
                elif line == '        intervals [1]:\n':
                    interval["num"] = 1
                elif line[:16] == '            xmin':
                    interval["xmin"] = float(line[19:-2])
                elif line[:16] == '            xmax':
                    interval["xmax"] = float(line[19:-2])
                elif line[:16] == '            text':
                    interval["text"] = line[20:-3]
        content.append(interval)
        item.append(header)
        item.append(content)
        items.append(item)

        ### JSON 파일 작성 ###
        json_lines = ''
        json_lines += '{\n    "metadata": {\n'

        # metadata
        for key, value in metadata.items():
            json_line = (' '*8) + '"' + key + '": '
            if type(value) == str:
                json_line += '"' + value + '",\n'
            else:
                json_line += str(value) + ',\n'
            json_lines += json_line
        json_lines = json_lines[:-2]
        json_lines += '\n    },\n    "item": [\n'

        # tiers
        for item in items:
            json_lines += '        {\n'
            for item_sub in item:
                # header
                if type(item_sub) == dict:
                    json_line = (' '*12) + '"header": {\n'
                    for key, value in item_sub.items():
                        json_line += (' '*16) + '"' + key + '": '
                        if type(value) == str:
                            json_line += '"' + value + '",\n'
                        else:
                            json_line += str(value) + ',\n'
                    json_line = json_line[:-2]
                    json_lines += json_line
                    json_lines += '\n            },\n'

                #content
                else:
                    json_lines += (' '*12) + '"content": [\n'
                    for cnt in item_sub:
                        json_lines += (' '*16) + '{\n'
                        for key, value in cnt.items():
                            json_lines += (' '*20) + '"' + key + '": '
                            if type(value) == str:
                                json_lines += '"' + value.replace('\\', '/').replace('\"', '\'') + '",\n'
                            else:
                                json_lines += str(value) + ',\n'
                        json_lines = json_lines[:-2]
                        json_lines += '\n' + (' '*16) + '},\n'
                    
                    json_lines = json_lines[:-2]
                    json_lines += '\n' + (' '*12) + ']'
                    json_lines += '\n        },\n'

        # 마무리
        json_lines = json_lines[:-2]
        json_lines += '\n    ]\n'
        json_lines += '}\n'

        with open(json_name + '.json', 'w', encoding='utf-8') as fn:
            fn.write(json_lines)
            fn.close()

    def json_to_list(self, json_name, csv_name):
        """
        # json_to_list(json_name: str(not .json), csv_name(not .txt or .csv))
        ## JSON 파일을 리스트로 바꾸는 메소드

        순서도를 그려보면 조금 더 명확해진다.
        크게 줄기를 짚어보자면,
        1) 일단 첫 번째 티어의 첫 번째 요소에서 라인을 추출한다.
        2) 그 다음 티어의 동일 인덱스 요소가 시작하는 시간이 같다면, 그것도 라인으로 뽑아낸다.
        3) 그렇게 티어를 모두 돌아다닌다.
        4) 모든 티어를 한 바퀴 돌았다면, 첫 번째 티어의 두 번째 요소의 라인을 추출한다.
        5) 위를 반복한다.
        6) 빈 라인은 입력하지 않도록 한다.
        7) 첫 번째 티어의 모든 요소를 입력하였다면 루프를 탈출한다.
        """
        item = json.load(open(json_name + '.json', 'r', encoding='utf-8'))["item"]

        lines = []
        line = {}

        i = 0 # index of tiers
        j = 0 # index of intervals
        k = 0 # index of items in lines

        isSameLen = True

        for num in range(len(item)):
            if num != 0:
                if item[num]["header"]["size"] != item[num-1]["header"]["size"]:
                    isSameLen = False

        while True:
            if j == len(item[i]["content"]) - 1:
                break

            line["tmin"] = item[i]["content"][j]["xmin"]
            line["tier"] = item[i]["header"]["name"]
            line["tmax"] = item[i]["content"][j]["xmax"]
            line["text"] = item[i]["content"][j]["text"]

            i += 1

            if line['text'] == "":
                line = {}
                if i >= len(item):
                    i = 0
                    j += 1
                continue
            else:
                lines.append(line)
                line = {}
                k = len(lines) - 1
                if i == len(item):
                    i = 0
                    j += 1
                    continue
                else:
                    if lines[k]["tmin"] == item[i]["content"][j]["xmin"]:
                        continue
                    else:
                        j += 1
                        continue

        new_lines = 'tmin' + '\t' + 'tier' + '\t' + 'text' + '\t' + 'tmax' + '\n'
        for line in lines:
            new_line = ''
            for _, value in line.items():
                new_line += str(value) + '\t'
            new_line = new_line[:-1]
            new_line += '\n'
            new_lines += new_line

        """
        pandas 모듈을 불러오면 바로 csv 파일로 바꿀 수 있다.
        그러나 그렇게 하면 PyQt5로 응용 프로그램을 만들었을 때 크기가 지나치게 커진다.
        (pandas는 용량이 큰 모듈 중 하나이다)
        그래서 탭으로 칼럼을 구분시킨 txt 파일로 뽑는 것으로 대체했다.
        해당 txt 파일은 엑셀에서 불러오면 칼럼이 자동으로 나뉜다.
        """
        with open(csv_name + '.txt', 'w', encoding='utf-8') as fn:
            fn.write(new_lines)
            fn.close()

        return isSameLen
