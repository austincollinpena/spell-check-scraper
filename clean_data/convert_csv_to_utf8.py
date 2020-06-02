with open('./just_values.csv', 'rb') as source_file:
    with open('./just_values_compat.csv') as dest_file:
        contents = source_file.read()
        a = contents.encode('utf-8')
        dest_file.write(contents.decode('ISO-8859-1').encode('utf-8'))
