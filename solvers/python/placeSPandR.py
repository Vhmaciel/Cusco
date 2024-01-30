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

        P_Xt = [ Int('pxt_%s' % i) for i in range(spaces_counter) ]
        P_Rt = [ Int('prt_%s' % i) for i in range(spaces_counter) ]
        P_Lt = [ Int('plt_%s' % i) for i in range(spaces_counter) ]
        P_tns = [ Int('ptns_%s' % i) for i in range(spaces_counter) ]
        P_flipped = [ Bool('pFlipped_%s' % i) for i in range(spaces_counter) ]
        P_gate = [ Int('pgate_%s' % i) for i in range(spaces_counter) ]
        N_Xt = [ Int('nxt_%s' % i) for i in range(spaces_counter) ]
        N_Rt = [ Int('nrt_%s' % i) for i in range(spaces_counter) ]
        N_Lt = [ Int('nlt_%s' % i) for i in range(spaces_counter) ]
        N_tns = [ Int('ntns_%s' % i) for i in range(spaces_counter) ]
        N_flipped = [ Bool('nFlipped_%s' % i) for i in range(spaces_counter) ]
        N_gate = [ Int('ngate_%s' % i) for i in range(spaces_counter) ]
        misallignedGate = [ Bool('mg_%s' % i) for i in range(spaces_counter) ]
        cost = Int('cost')

        s.add(cost >= 0)

        for i in range(spaces_counter):
            s.add(P_Xt[i] >= 0)
            s.add(N_Xt[i] >= 0)
            s.add(And(P_tns[i] >= 0, P_tns[i] < spaces_counter))
            s.add(And(N_tns[i] >= 0, N_tns[i] < spaces_counter))
            
        for i in range(spaces_counter): # Atribui os gates dos dispositivos para as variáveis do resolvedor
            for j in range(spaces_counter):
                s.add(Implies(P_tns[i]==j, P_gate[i]==pcirc[j].gate))
                s.add(Implies(N_tns[i]==j, N_gate[i]==ncirc[j].gate))

        for i in range(spaces_counter):
            for j in range(spaces_counter): # Atribui os valores da netlist para as variáves do resolvedor. Inverte a atribuição caso o transistor esteja invertido. Regra de implicação de valores
                s.add(If(P_flipped[i], Implies(P_tns[i]==j, And(P_Rt[i]==pcirc[j].drain, P_Lt[i]==pcirc[j].source)), Implies(P_tns[i]==j, And(P_Rt[i]==pcirc[j].source, P_Lt[i]==pcirc[j].drain))))
                s.add(If(N_flipped[i], Implies(N_tns[i]==j, And(N_Rt[i]==ncirc[j].drain, N_Lt[i]==ncirc[j].source)), Implies(N_tns[i]==j, And(N_Rt[i]==ncirc[j].source, N_Lt[i]==ncirc[j].drain))))


        for i in range(spaces_counter):
            for j in range(spaces_counter):
                if i != j: 
                    s.add(
                        If(And((P_Xt[i] >= P_Xt[j] + 2), (P_Lt[i] != P_Rt[j])), (P_Xt[i] >= P_Xt[j] + 2 + 2),
                            If(And((P_Xt[i] >= P_Xt[j] + 2), (P_Lt[i] == P_Rt[j])), (P_Xt[i] == P_Xt[j] + 2),
                                If(And((P_Xt[i] + 2 <= P_Xt[j]), (P_Rt[i] != P_Lt[j])), (P_Xt[i] + 2 + 2 <= P_Xt[j]),
                                    If(And((P_Xt[i] + 2 <= P_Xt[j]), (P_Rt[i] == P_Lt[j])), (P_Xt[i] + 2 == P_Xt[j]), False)
                                )
                            )
                        )
                    )
                    s.add(
                        If(And((N_Xt[i] >= N_Xt[j] + 2), (N_Lt[i] != N_Rt[j])), (N_Xt[i] >= N_Xt[j] + 2 + 2),
                            If(And((N_Xt[i] >= N_Xt[j] + 2), (N_Lt[i] == N_Rt[j])), (N_Xt[i] == N_Xt[j] + 2),
                                If(And((N_Xt[i] + 2 <= N_Xt[j]), (N_Rt[i] != N_Lt[j])), (N_Xt[i] + 2 + 2 <= N_Xt[j]),
                                    If(And((N_Xt[i] + 2 <= N_Xt[j]), (N_Rt[i] == N_Lt[j])), (N_Xt[i] + 2 == N_Xt[j]), False)
                                )
                            )
                        )
                    )
                    s.add(N_Xt[i] != N_Xt[j])
                    s.add(P_Xt[i] != P_Xt[j])
                    s.add(P_tns[i] != P_tns[j])
                    s.add(N_tns[i] != N_tns[j])

        # for i in range(spaces_counter): # Regra que testa se algum dos gates está desalinhado entre as redes. O gate é dado como alinhado se estiver pareado com um valor 0 (vazio)
        #     misallignedGate[i] = And(And(P_gate[i]!=N_gate[i], P_gate[i]!=0), N_gate[i]!=0)
        #     s.add(misallignedGate[i]==False)

        s.add(max(P_Xt)==max(N_Xt))


        h = s.minimize(max(P_Xt))     


        if(s.check()==sat):
            m = s.model()
            print("PMOS")
            for i in range(spaces_counter):
                print('pos:' + str(m.eval(P_Xt[i])) + '| piece: ' + str(m.eval(P_tns[i])) + ' | f: ' + str(m.eval(P_flipped[i])) + ' - |' + str(m.eval(P_Lt[i]))+ ' ' + str(m.eval(P_gate[i])) + ' ' + str(m.eval(P_Rt[i]))+'|')
            print("NMOS")
            for i in range(spaces_counter):
                print('pos:' + str(m.eval(N_Xt[i])) + '| piece: ' + str(m.eval(N_tns[i])) + ' | f: ' + str(m.eval(N_flipped[i])) + ' - |' + str(m.eval(N_Lt[i]))+ ' ' + str(m.eval(N_gate[i])) + ' ' + str(m.eval(N_Rt[i]))+'|')

            print(s.statistics())

            # print(m.eval(cost))
            # print(s.model())
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