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

        Xt = [ Int('xt_%s' % i) for i in range(spaces_counter) ]
        Rt = [ Int('rt_%s' % i) for i in range(spaces_counter) ]
        Lt = [ Int('lt_%s' % i) for i in range(spaces_counter) ]
        tns = [ Int('tns_%s' % i) for i in range(spaces_counter) ]
        pFlipped = [ Bool('pFlipped_%s' % i) for i in range(spaces_counter) ]
        cost = Int('cost')

        s.add(cost >= 0)

        for i in range(spaces_counter):
            s.add(Xt[i] >= 0)
            s.add(And(tns[i] >= 0, tns[i] < spaces_counter))
            

        for i in range(spaces_counter):
            for j in range(spaces_counter): # Atribui os valores da netlist para as variáves do resolvedor. Inverte a atribuição caso o transistor esteja invertido. Regra de implicação de valores
                s.add(If(pFlipped[i], Implies(tns[i]==j, Lt[i]==pcirc[j].drain), Implies(tns[i]==j, Rt[i]==pcirc[j].source)))
                s.add(If(pFlipped[i], Implies(tns[i]==j, Rt[i]==pcirc[j].source), Implies(tns[i]==j, Lt[i]==pcirc[j].drain)))  
            # if i < spaces_counter-1:    
            #     s.add(Or(Or(Rt[i]==Lt[i+1], Rt[i]==0), Lt[i+1]==0))   # O lado direito de um dispositivo deve ser igual ao lado esquerdo do seu vizinho ou igual a 0

        for i in range(spaces_counter):
            for j in range(spaces_counter):
                if i != j: 
                    s.add(
                        If(And((Xt[i] >= Xt[j] + 2), Lt[i] != Rt[j]), And(Xt[i] >= Xt[j] + 2 + 2, cost == 2),
                            If(And((Xt[i] >= Xt[j] + 2), Lt[i] == Rt[j]), (Xt[i] == Xt[j] + 2),
                                If(And((Xt[i] + 2 <= Xt[j]), Rt[i] != Lt[j]), And(Xt[i] + 2 + 2 <= Xt[j], cost == 2),
                                    If(And((Xt[i] + 2 <= Xt[j]), Rt[i] != Lt[j]), (Xt[i] + 2 == Xt[j]), False)
                                )
                            )
                        )
                    )
                    s.add(Xt[i] != Xt[j])
                    s.add(tns[i] != tns[j])
                           

        h = s.minimize(cost)     


        if(s.check()==sat):
            m = s.model()
            for i in range(spaces_counter):
                print('pos:' + str(m.eval(Xt[i])) + '| piece: ' + str(m.eval(tns[i])) + ' | f: ' + str(m.eval(pFlipped[i])) + ' - |' + str(m.eval(Lt[i]))+ ' ' + 'GATE INFO' + ' ' + str(m.eval(Rt[i]))+'|')

            print(m.eval(cost))
            print(s.model())
            #print(h.value())
        else:
            print("UNSAT")


        
        
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