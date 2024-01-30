from z3 import *
from data import Device

def placement(circuit):         # Função que faz o posicionamento de transistores, dada uma netlist 
    
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

    while True:
        s = Solver()
        
        pPiecePlacement, pSource, pGate, pDrain, pFlipped = [], [], [], [], []
        misallignedGate = []
        nPiecePlacement, nSource, nGate, nDrain, nFlipped = [], [], [], [], []
        

        for i in range(spaces_counter):     # Inicializa as listas das variáveis do resolvedor
            pPiecePlacement.append(Int('p_spa'+str(i)))     # Variáveis para a região p
            pSource.append(Int('p_sou'+str(i)))
            pGate.append(Int('p_g'+str(i)))
            pDrain.append(Int('p_drain'+str(i)))
            pFlipped.append(Bool('p_f'+str(i)))

            misallignedGate.append(Bool('mg'+str(i)))       # Variável de alinhamento de gate

            nPiecePlacement.append(Int('n_spa'+str(i)))     # Variáveis para a região n
            nSource.append(Int('n_sou'+str(i)))
            nGate.append(Int('n_g'+str(i)))
            nDrain.append(Int('n_drain'+str(i)))
            nFlipped.append(Bool('n_f'+str(i)))            
        
#-----------------------------------------------------------------------------------------------------------

        for i in range(spaces_counter):
            s.add(And(pPiecePlacement[i]>=0, pPiecePlacement[i]<spaces_counter))    # Aloca os espaços para o posicionamento dos dispositivos pmos
            s.add(And(nPiecePlacement[i]>=0, nPiecePlacement[i]<spaces_counter))    # Aloca para nmos 
            if i < spaces_counter-1:
                s.add(Or(Or(pDrain[i]==pSource[i+1], pDrain[i]==0), pSource[i+1]==0))   # O lado direito de um dispositivo deve ser igual ao lado esquerdo do seu vizinho ou igual a 0
                s.add(Or(Or(nDrain[i]==nSource[i+1], nDrain[i]==0), nSource[i+1]==0))   # Regra feita para a aglutinação de transistores

            for j in range(i+1, spaces_counter):
                s.add(pPiecePlacement[i] != pPiecePlacement[j])     # Nenhum espaço pode ser igual ao outro, garantindo a unicidade de posições e que não haja sobreposição de dispositivos
                s.add(nPiecePlacement[i] != nPiecePlacement[j])
                
#-----------------------------------------------------------------------------------------------------------

        for i in range(spaces_counter):
            for j in range(spaces_counter): # Atribui os valores da netlist para as variáves do resolvedor. Inverte a atribuição caso o transistor esteja invertido. Regra de implicação de valores
                s.add(If(pFlipped[i], Implies(pPiecePlacement[i]==j, pSource[i]==pcirc[j].drain), Implies(pPiecePlacement[i]==j, pSource[i]==pcirc[j].source)))
                s.add(If(pFlipped[i], Implies(pPiecePlacement[i]==j, pDrain[i]==pcirc[j].source), Implies(pPiecePlacement[i]==j, pDrain[i]==pcirc[j].drain)))             
                s.add(If(nFlipped[i], Implies(nPiecePlacement[i]==j, nSource[i]==ncirc[j].drain), Implies(nPiecePlacement[i]==j, nSource[i]==ncirc[j].source)))
                s.add(If(nFlipped[i], Implies(nPiecePlacement[i]==j, nDrain[i]==ncirc[j].source), Implies(nPiecePlacement[i]==j, nDrain[i]==ncirc[j].drain)))

#-----------------------------------------------------------------------------------------------------------

        for i in range(spaces_counter): # Atribui os gates dos dispositivos para as variáveis do resolvedor
            for j in range(spaces_counter):
                s.add(Implies(pPiecePlacement[i]==j, pGate[i]==pcirc[j].gate))
                s.add(Implies(nPiecePlacement[i]==j, nGate[i]==ncirc[j].gate))
   
#-----------------------------------------------------------------------------------------------------------

        for i in range(spaces_counter): # Regra que testa se algum dos gates está desalinhado entre as redes. O gate é dado como alinhado se estiver pareado com um valor 0 (vazio)
            misallignedGate[i] = And(And(pGate[i]!=nGate[i], pGate[i]!=0), nGate[i]!=0)
            s.add(misallignedGate[i]==False)

#-----------------------------------------------------------------------------------------------------------

        if s.check()==sat:  # Chama o resolvedor e testa se existe uma solução
            print(s.check())    # Se existe, apresenta o resultado
            m = s.model()

            print('PMOS:')
            flagAppend = True
            ppos = []
            npos = []
            for i in range(pmos_counter):
                print('pos:' + str(i) + '| piece: ' + str(m.eval(pPiecePlacement[i]+1)) + ' | f: ' + str(m.eval(pFlipped[i])) + ' - |'+str(m.eval(pSource[i]))+ ' ' + str(m.eval(pGate[i])) + ' ' + str(m.eval(pDrain[i]))+'|')
                pcirc[int(str(m.eval(pPiecePlacement[i])))].position = i
                pcirc[int(str(m.eval(pPiecePlacement[i])))].flipped = bool(m.eval(pFlipped[i]))
                if flagAppend:
                    ppos.append(int(str(m.eval(pSource[i]))))
                    flagAppend = False

                if int(str(m.eval(pDrain[i]))) == 0:
                    flagAppend = True
                    if i == len(pDrain)-1:
                        ppos.append(int(str(m.eval(pDrain[i]))))
                else:
                    ppos.append(int(str(m.eval(pDrain[i]))))
                    
            print(ppos)
            
            
            print('\nNMOS:')
            flagAppend = True
            for i in range(nmos_counter):
                print('pos:' + str(i) + '| piece: ' + str(m.eval(nPiecePlacement[i]+1)) + ' | f: ' + str(m.eval(nFlipped[i])) + ' - |'+str(m.eval(nSource[i]))+ ' ' + str(m.eval(nGate[i])) + ' ' + str(m.eval(nDrain[i]))+'|')
                ncirc[int(str(m.eval(nPiecePlacement[i])))].position = i
                ncirc[int(str(m.eval(nPiecePlacement[i])))].flipped = bool(m.eval(nFlipped[i]))
                if flagAppend:
                    npos.append(int(str(m.eval(nSource[i]))))
                    flagAppend = False

                if int(str(m.eval(nDrain[i]))) == 0:
                    flagAppend = True
                    if i == len(nDrain)-1:
                        npos.append(int(str(m.eval(nDrain[i]))))
                else:
                    npos.append(int(str(m.eval(nDrain[i]))))

            print(npos)

            pcirc.sort(key=lambda x: x.position, reverse=False)
            ncirc.sort(key=lambda x: x.position, reverse=False)

            print(s.statistics())

            return pcirc, ncirc, ppos, npos

        else:   # Caso não exista solução, adiciona 1 dispositivo dummy nas redes pmos e nmos, inserindo artificialmente uma quebra de difusão. As quebras são inseridas até que exista uma solução
            pcirc.append(Device(0,0,0,0,rtype='PMOS'))
            ncirc.append(Device(0,0,0,0,rtype='NMOS'))
            nmos_counter +=1
            pmos_counter +=1
            spaces_counter +=1