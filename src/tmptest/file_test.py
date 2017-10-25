input = open('text2.txt', 'r')

text = input.read()

text = text.replace('\n', '\',\'')

print text

