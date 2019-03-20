import xlrd
import urllib.request
import json

def xls2dict(filepath):
    data = xlrd.open_workbook(filepath)
    table = data.sheets()[0]
    nor = table.nrows
    nol = table.ncols
    dict = []
    for i in range(1, nor):
        item = {}
        for j in range(nol):
            title = table.cell_value(0, j)
            value = table.cell_value(i, j)
            item[title] = value
        dict.append(item)
    return dict


def api_request(url, method="GET", body=None):
    data = None

    try:
        if method == "GET":
            data = urllib.request.urlopen(url, timeout=20).read()
        elif method == "POST":
            req = urllib.request.Request(url,data=body)
            response = urllib.request.urlopen(req, timeout=20)
            data = response.read()

        data = json.loads(data)
    except:
        pass
    return data
