def hexdump(text='hello world',step = 16,sep = 8,ten = False):    
    for i in range(0,len(text),step):
        sub = text[i: i+step]
        #print(sub)
        out = '%08x ' % i
        out += '%08d '% i if ten else ''
        out += '| '
        stage1 = ' '.join(['%02x' % c for c in sub]) +' '
        stage1 += '   ' * (step-len(sub))   
        out += ' '.join([stage1[j: j+sep*3] for j in range(0,len(stage1),sep*3)])
        out += '| '
        out += ' '.join([chr(c) if 0x20 <= c < 0x7F else '.' for c in sub] )
        print(out)#[start end]

#hexdump( b'123456',step = 16,ten = True)
#print(len(b'123456'))x
