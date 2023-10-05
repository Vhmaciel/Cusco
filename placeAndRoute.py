from z3 import *
from data import Device

# Return minimum of a vector; error if empty
def min(vs):
  m = vs[0]
  for v in vs[1:]:
    m = If(v < m, v, m)
  return m

# Return maximum of a vector; error if empty
def max(vs):
  m = vs[0]
  for v in vs[1:]:
    m = If(v > m, v, m)
  return m

def placement_SPandR(circuit):         # Função que faz o posicionamento de transistores, dada uma netlist 
    
    pmos_counter = 0
    nmos_counter = 0
    pcirc = []
    ncirc = []

    w = 2
    d = 2 


    for inst in circuit:        # Faz a contagem e separação de transistores 
        if inst.rtype == 'PMOS': 
            pmos_counter += 1
            pcirc.append(inst)
        if inst.rtype == 'NMOS': 
            nmos_counter += 1
            ncirc.append(inst)
        #print(inst)
            
    print('Pmos: ' + str(pmos_counter) + ' Nmos: ' + str(nmos_counter))
        
    if pmos_counter != nmos_counter:    # Testa se a rede é equilibrada ou não
        print('Non-balanced net')
        if pmos_counter>nmos_counter:           # Caso a rede seja desbalanceada, são criados dispositivos "dummy" e inseridos na rede com menos dispositivos
            while pmos_counter>nmos_counter:    
                nmos_counter +=1                # Se aumenta a contagem de dispositivos da menor rede até que ela tenha o mesmo tamanho da maior
                ncirc.append(Device(0,0,0,0,rtype='NMOS'))   # A igualdade de dispositivos, com inserção de dummies, é necessária para o alinhamento dos gates posteriormente
        else:
            while nmos_counter>pmos_counter:
                pmos_counter +=1
                pcirc.append(Device(0,0,0,0,rtype='PMOS'))
    else:  
        print('Balanced net')

    spaces_counter=pmos_counter     # Atribui a contagem da rede para uma variável apenas

    for t in range(1):
        s = Optimize()

        Xt = [ Int('xt%s' % i) for i in range(spaces_counter) ]
        Xs = [ Int('xs%s' % i) for i in range(spaces_counter) ]
        Rt = [ Int('rt%s' % i) for i in range(spaces_counter) ]
        Lt = [ Int('lt%s' % i) for i in range(spaces_counter) ]
        Rs = [ Int('rs%s' % i) for i in range(spaces_counter) ]
        Ls = [ Int('ls%s' % i) for i in range(spaces_counter) ]

        for i in range(spaces_counter):
            s.add(Xt[i] >= 0)
            s.add(Xs[i] >= 0)

        for i in range(spaces_counter):
            for j in range(spaces_counter):
                if i != j: 
                    s.add(
                        If(And((Xt[i] >= Xs[j] + w), Lt[i] != Rs[j]), (Xt[i] >= Xs[j] + d + w),
                            If(And((Xt[i] >= Xs[j] + w), Lt[i] == Rs[j]), (Xt[i] == Xs[j] + w),
                                If(And((Xt[i] + w <= Xs[j]), Rt[i] != Ls[j]), (Xt[i] + w + d <= Xs[j]),
                                    If(And((Xt[i] + w <= Xs[j]), Rt[i] != Ls[j]), (Xt[i] + w == Xs[j]), unsat)
                                )
                            )
                        )
                    )
                else:
                    s.add(Xt[i] == Xs[j])


        h = s.minimize(max(Xt))     

        print(s.check())
        print(s.model())
        print(h.value())


        
        
#-----------------------------------------------------------------------------------------------------------

        # if s.check()==sat:  # Chama o resolvedor e testa se existe uma solução
        #     print(s.check())    # Se existe, apresenta o resultado
        #     m = s.model()

        #     print('PMOS:')
        #     flagAppend = True
        #     ppos = []
        #     npos = []
        #     for i in range(pmos_counter):
        #         print('pos:' + str(i) + '| piece: ' + str(m.eval(pPiecePlacement[i]+1)) + ' | f: ' + str(m.eval(pFlipped[i])) + ' - |'+str(m.eval(pSource[i]))+ ' ' + str(m.eval(pGate[i])) + ' ' + str(m.eval(pDrain[i]))+'|')
        #         pcirc[int(str(m.eval(pPiecePlacement[i])))].position = i
        #         pcirc[int(str(m.eval(pPiecePlacement[i])))].flipped = bool(m.eval(pFlipped[i]))
        #         if flagAppend:
        #             ppos.append(int(str(m.eval(pSource[i]))))
        #             flagAppend = False

        #         if int(str(m.eval(pDrain[i]))) == 0:
        #             flagAppend = True
        #             if i == len(pDrain)-1:
        #                 ppos.append(int(str(m.eval(pDrain[i]))))
        #         else:
        #             ppos.append(int(str(m.eval(pDrain[i]))))
                    
        #     print(ppos)
            
            
        #     print('\nNMOS:')
        #     flagAppend = True
        #     for i in range(nmos_counter):
        #         print('pos:' + str(i) + '| piece: ' + str(m.eval(nPiecePlacement[i]+1)) + ' | f: ' + str(m.eval(nFlipped[i])) + ' - |'+str(m.eval(nSource[i]))+ ' ' + str(m.eval(nGate[i])) + ' ' + str(m.eval(nDrain[i]))+'|')
        #         ncirc[int(str(m.eval(nPiecePlacement[i])))].position = i
        #         ncirc[int(str(m.eval(nPiecePlacement[i])))].flipped = bool(m.eval(nFlipped[i]))
        #         if flagAppend:
        #             npos.append(int(str(m.eval(nSource[i]))))
        #             flagAppend = False

        #         if int(str(m.eval(nDrain[i]))) == 0:
        #             flagAppend = True
        #             if i == len(nDrain)-1:
        #                 npos.append(int(str(m.eval(nDrain[i]))))
        #         else:
        #             npos.append(int(str(m.eval(nDrain[i]))))

        #     print(npos)

        #     pcirc.sort(key=lambda x: x.position, reverse=False)
        #     ncirc.sort(key=lambda x: x.position, reverse=False)

        #     return pcirc, ncirc, ppos, npos

        # else:   # Caso não exista solução, adiciona 1 dispositivo dummy nas redes pmos e nmos, inserindo artificialmente uma quebra de difusão. As quebras são inseridas até que exista uma solução
        #     pcirc.append(Device(0,0,0,0,rtype='PMOS'))
        #     ncirc.append(Device(0,0,0,0,rtype='NMOS'))
        #     nmos_counter +=1
        #     pmos_counter +=1
        #     spaces_counter +=1