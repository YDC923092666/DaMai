import json
configFile = './json.txt'

def test():
    with open(configFile, 'r', encoding= 'utf-8') as f:
        config = f.read()
        jsonTxt = json.loads(config)
        print(jsonTxt)
        return jsonTxt

def printResult(price=None):
    rtDic = None #返回的结果
    if price:
        jsonTxt = test()
        performBases = jsonTxt['performBases']

        priceIndex = None  # 价格的索引
        dateIndex = None  # 场次的索引
        for i in range(0, len(performBases)):
            tmp = performBases[i]["performs"][0]["skuList"]
            for j in range(0, len(tmp)):
                if price == tmp[j]['price'] and tmp[j]['skuEnable'] is True:
                    priceIndex = j
                    dateIndex = i
                    break

        if priceIndex is not None and dateIndex is not None:
            rtDic = {
                "priceIndex": priceIndex,
                "dateIndex": dateIndex
            }
            return rtDic
        else:
            return None


if __name__ == '__main__':
    info = printResult(1680)
    print(info)
    print(info['dateIndex'])
    print(info['priceIndex'])