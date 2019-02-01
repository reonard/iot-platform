import xlrd

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
