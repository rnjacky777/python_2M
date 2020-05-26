from hexdump import *
fd = open('D:\\Neople\\DFO\\ImagePacks2\\sprite_character_common_aura_18_west_gold.NPK','rb')
a = fd.read()

b = hexdump(a)

fd.close()
fd1 = open('eee.txt','w')
fd1.write(b)