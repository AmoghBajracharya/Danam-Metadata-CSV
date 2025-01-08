import codecs


def manual_fixes(df, filename):
    file = open(filename, 'r', encoding='UTF-8')
    for line in file.readlines():

        parts = line.split(",")
        row = int(parts[0])
        col = parts[1]
        val = parts[2].replace("\n","")
        df.at[row, col] = val
    return df