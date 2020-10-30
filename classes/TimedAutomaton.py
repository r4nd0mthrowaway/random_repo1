
import time
import xml.etree.ElementTree as ET
from .automata import *
import re
from colorama import Fore,Style,init
init()


class __AutomatoTemporizado:
    def __init__(self):
        self.__recursiveMonitor=0
        self.__processingTime=0.0

    def print_processing_status(self):
        print("\n ├── Made ",self.__recursiveMonitor,"iterations whithin",str(self.__processingTime),"seconds ──┤")
    
    def realizar_operacao(self):
        self.__recursiveMonitor = self.__recursiveMonitor + 1

    def init_timer(self):
        self.__processingTime = (time.time() - self.__processingTime)
    def stop_timer(self):
        self.__processingTime = (time.time()-self.__processingTime)















class SupervisorTemporizado(__AutomatoTemporizado):
    
    def __init__(self,automato,lista_subsistemas=[]):
        if len(lista_subsistemas) == 0: print("NENHUM SUBSISTEMA FORNECIDO")

        self.__main_automaton = automato
        self.__subsystem_list = {y:x for y,x in enumerate(lista_subsistemas)}
        self.__parameter_list=dict() # key: estados -> value: ( key: eventos -> value: lista de delays e flags )
        self.__tabela_verificacao=dict()
        
        super().__init__()

    def __supervisorTemporizado(self,c_state,subsys_stateList,tick_elapsed=0):
        self.realizar_operacao()
        if c_state in self.__parameter_list.keys():
            # pesquisa, para ver se o estado do supervisor já se encontra adicionado
            # Tempo linear de busca, em um tamanho crescente de itens, com o máximo = numero de estados do supervisor
            #print("Already added",c_state.name)
            return
        
        #print("chegando em",c_state.name, "com delay ",tick_elapsed," subsys: ",subsys_stateList)
        self.__parameter_list[c_state]=[[x for _,x in subsys_stateList.items()],{}] # 1 = dicionarios de eventos -> {flags}
        # adiciona a lista de parametros, a chave 'estado do supervisor'

        # PRIMEIRO VALIDAR A LISTA DE SUBSISTEMAS
        for ss_index,ss_state in subsys_stateList.items(): # iterando na lista de subestados,
            #print("substate",ss_index,": ",ss_state.name)
            for sub_auto_event,sub_dest_ in self.__subsystem_list[ss_index].transitions[ss_state].items():
                # iterando nos eventos correspondentes a esses estados,
                ev_properties = re.split('\[|,|]',sub_auto_event.name)[0:-1] # nome,delay_inf,delay_sup
                # separando o nome do evento exemplo: (id_do_evento[delay_inferior,delay_superior])
                # EV_PROPERTIES[0] == ID
                # EV_PROPERTIES[1] == DELAY INFERIOR
                # EV_PROPERTIES[2] == DELAY SUPERIOR

                listHas=False # supervisor possui este evento?
                for c_events_ in self.__main_automaton.transitions[c_state].keys(): #eventos no estado do supervisor
                    if c_events_.name == ev_properties[0]:
                        listHas=True # estado(supervisor) possui o evento do sub_sistema
                        break
                
                new_delay = max(int(ev_properties[1])-tick_elapsed,0)
                #pegando o delay original e subtraindo do delay atual

                enabled=False
                prohibited=False
                if new_delay == 0: # se delay atual == 0, o evento pode estar habilitado
                    enabled=True
                    if int(ev_properties[1]) > 0 and not listHas:
                        prohibited=True # PROIBIDO: QUANDO JÁ SE PASSOU O TICK,
                                        # PORÉM O ESTADO DO SUPERVISOR NÃO TEM O EVENTO
                
                
                self.__parameter_list[c_state][1][sub_auto_event] = [new_delay,enabled,prohibited]
                # adiciona os parametros na lista :)
        
        #======
        # preparando para recursão, e evoluir a leitura do supervisor
        # essa parte, lista mais nos parametros do supervisor, do que os dos subsistemas

        for sup_ev_,sup_dest_ in self.__main_automaton.transitions[c_state].items(): # olhando na lista evento->destino do supervisor
            # SUP_EV_ == EVENTO DO SUPERVISOR
            # SUP_DEST_ == ESTADO DE DESTINO COM ESSE EVENTO
            #print("Event ",sup_ev_.name)
            if sup_ev_.name == "tick": # se for um tick, só aumenta o tick atual, não muda a lista de subsistemas (até porque neenhum subsistema movimenta com tick)
                self.__supervisorTemporizado(sup_dest_,subsys_stateList,tick_elapsed+1)
            else:
                new_subsys_stateList = subsys_stateList.copy() # duplica a lista de estados sos subsistemas, pra não ter várias referências iguais e mudar a lista ao longo da execução
                
                assoc_delay=False # se existe um delay > 0
                for ss_index,new_ss_state in subsys_stateList.items(): # iterando na lista de subsistemas, procurando correspondencia
                    for subsys_event,subsys_dest in self.__subsystem_list[ss_index].transitions[new_ss_state].items():
                        ev_prop = re.split('\[|,|]',subsys_event.name)[0:2]
                        # separando o nome do evento do subsistema exemplo: (id_do_evento[delay_inferior,delay_superior])
                        # ev_prop[0] == ID
                        # ev_prop[1] == DELAY INFERIOR
                        # ev_prop[2] == DELAY SUPERIOR
                        if sup_ev_.name == ev_prop[0]:
                            new_subsys_stateList[ss_index]=subsys_dest
                            if int(ev_prop[1]) > 0: # PARTE MUITO IMPORTANTE !! => DIFERENFCIAR O DELAY DE CADA EVENTO!!!!
                                assoc_delay=True
                self.__supervisorTemporizado(sup_dest_,new_subsys_stateList,tick_elapsed if not assoc_delay else 0)
    
    def gerar_mapa_de_estados(self):
        if len(self.__subsystem_list) == 0:
            print("NENHUM SUBSISTEMA FORNECIDO")
            return
        # PARAMETROS:
        # ESTADO INICIAL
        # DICIONARIO DE ESTADOS INICIAIS DOS SUBSISTEMAS
        self.init_timer()
        self.__supervisorTemporizado(self.__main_automaton.initial_state,{x:y.initial_state for x,y in self.__subsystem_list.items()})
        self.stop_timer()
    
    def print_mapa_de_estados(self):
        if len(self.__parameter_list) == 0:
            print("\nTABELA NÃO PROCESSADA\n")
            return
        print("\nTABELA GERADA\n")
        cpp=0
        while cpp < len(self.__parameter_list):
            for state_,itemList in self.__parameter_list.items():
                if state_.name == str(cpp):
                    print(f'{int(state_.name):02d}',end=" | ")
                    for xx in itemList[0]:
                        print(xx.name,end=" ")
                    print("| ",end="")
                    for ev_,properties in itemList[1].items():
                        print(re.split('\[|,|]',ev_.name)[0],end=" ")
                        print(properties[0],end=" ")
                        for prop in properties[1:]:
                            print("True  " if prop == True else "False ",end="")
                        print("| ",end="")
                    print()
            cpp=cpp+1

    def carregar_mapa_verificacao(self,tabelaFile):
        file = open(tabelaFile, 'r')
        lines = file.readlines()
        self.__tabela_verificacao=dict()
        count = 0
        # Strips the newline character
        for line in lines:
            line_spl = re.split('\;',line.strip())
            try:
                current_id=int(line_spl[0])
                self.__tabela_verificacao[current_id] = [[],{}]
                
                subsystem_list = re.split('\,',line_spl[1])
                
                for substate_item in subsystem_list:
                    self.__tabela_verificacao[current_id][0].append(substate_item)

                count=2
                while count < len(line_spl):
                    self.__tabela_verificacao[current_id][1][line_spl[count]] = [line_spl[count+1],line_spl[count+2],line_spl[count+3]]
                    count=count+4

            except IndexError as e:
                print("ERROR!!!\n",e)
        
    def print_mapa_de_verificacao(self):
        print("\nTABELA DE VERIFICACAO\n")
        if len(self.__tabela_verificacao.items()) <= 0:
            print("TABELA DE VERIFICACAO VAZIA / NAO CRIADA!")
            return
        for key_,tuple_ in self.__tabela_verificacao.items():
            print(f'{int(key_):02d}',end=" | ")
            for subsys in tuple_[0]:
                print(subsys,end=" ")
            print("|",end=" ")
            for event_name,param_list in tuple_[1].items():
                print(event_name,end=" ")
                for item in param_list:
                    if item == "TRUE":
                        item = "True "
                    elif item == "FALSE":
                        item = "False"
                    print(item,end=" ")
                print("|",end=" ")
            print()

    def comparar_mapas(self,consolePrint=True):
        problema=False
        print("\ncomparar_mapas\n")
        if len(self.__tabela_verificacao.items()) <= 0:
            print("TABELA DE VERIFICACAO VAZIA / NAO CRIADA!")
            return
        cpp=0
        while cpp < len(self.__parameter_list):
            for state_,itemList in self.__parameter_list.items():
                if state_.name == str(cpp):
                    if consolePrint: print(f'{int(state_.name):02d}',end=" | ")
                    for xx in itemList[0]:
                        if str(xx.name) in self.__tabela_verificacao[int(state_.name)][0]:
                            if consolePrint: print(Fore.GREEN+""+xx.name,end=" ")
                        else:
                            if consolePrint: print(Fore.RED +""+ xx.name,end=" ")
                            problema=True
                        if consolePrint: print(Style.RESET_ALL,end="")
                    if consolePrint: print("| ",end="")
                    for ev_,properties in itemList[1].items():
                        ev_trimmname = re.split('\[|,|]',ev_.name)[0]
                        if ev_trimmname in self.__tabela_verificacao[int(state_.name)][1].keys():
                            if consolePrint: print(Fore.GREEN+""+ev_trimmname,end=" ")
                        else:
                            if consolePrint: print(Fore.RED+""+ev_trimmname,end=" ")
                            problema=True
                        if consolePrint: print(Style.RESET_ALL,end="")
                        
                        if str(properties[0]) == self.__tabela_verificacao[int(state_.name)][1][ev_trimmname][0]:# and prt:
                            if consolePrint: print(Fore.GREEN+""+str(properties[0]),end=" ")# delay
                        else:
                            if consolePrint: print(Fore.RED+""+str(properties[0]),end=" ")
                            problema=True
                        if consolePrint: print(Style.RESET_ALL,end="")
                        countt=1
                        for prop in properties[1:]:
                            if str(prop).lower() == self.__tabela_verificacao[int(state_.name)][1][ev_trimmname][countt].lower():# and prt:
                                if consolePrint: print(Fore.GREEN+"True  " if prop == True else Fore.GREEN+"False ",end="")
                            else:
                                if consolePrint: print(Fore.RED+"True  " if prop == True else Fore.RED+"False ",end="")
                                problema=True
                            if consolePrint: print(Style.RESET_ALL,end="")
                            countt=countt+1
                        if consolePrint: print("| ",end="")
                    if consolePrint: print()
            cpp=cpp+1
        return True if not problema else False

    def gravar_parametros(self,oldFileName,newFileName=None):
        tree = ET.parse(oldFileName)
        root = tree.getroot()

        states = root.findall('./data/state') #MUITO IMPORTANTE, NÃO TIRE O ./ e nem o data!!!

        for supv_state,param_list in self.__parameter_list.items():
            for s in states:
                name = s.findall('name')[0].text
                if supv_state.name == name:
                    props = s.find('properties')
                    insert_index = len(list(props))
                    for ev_item,param_list in self.__parameter_list[supv_state][1].items():
                        ev_element = ET.Element('event')
                        ev_element.set('id',re.split('\[',ev_item.name)[0])
                        ev_element.set('delay',str(param_list[0]))
                        ev_element.set('elg',str(param_list[1]))
                        ev_element.set('phb',str(param_list[2]))
                        props.insert(insert_index,ev_element)
                        insert_index=insert_index+1
                    break
        writer = ET.ElementTree(root)
        writer.write(oldFileName if newFileName == None else newFileName)
        print(Fore.GREEN+"ARQUIVO",newFileName,"CRIADO"+Style.RESET_ALL)

















class ObservadorTemporizado(__AutomatoTemporizado):

    def __init__(self,observador,supervisor,lista_subsistemas=[]):
        if len(lista_subsistemas) == 0: print("NENHUM SUBSISTEMA FORNECIDO")

        self.__observer = observador
        self.__supervisor = supervisor
        self.__subsystem_list = {y:x for y,x in enumerate(lista_subsistemas)}
        self.__parameter_list=dict() # key: estados -> value: ( key: eventos -> value: lista de delays e flags )

        super().__init__()

    def __old__observadorTemporizado(self,c_state,list_head,tick_elapsed=0):
        for evt_,dest_ in self.__supervisor.transitions[c_state].items():
            if not (evt_.name == 'tick'):
                if dest_ not in self.__parameter_list[list_head]:
                    self.__parameter_list[list_head].append(dest_)
                    self.__observadorTemporizado(dest_,list_head)
        # iniciando, agora tick = 0
        # não é garantido quantos ticks aconteceram, porém pode-se inferir o mínimo
        # usando os eventos dos sub-sistemas

        # para todos os eventos(supervisor) no observador,
        #     consultar estados anteriores (parametros) que chegam em quais da iteração atual(observador)
        #         fazendo acompanhamento da sequencia pelos acessíveis via tick no supervisor
        #     adicionado todos os que andam por tick, seleciona o próximo evento do observador
        #     se ultima transição não for tick, adiciona nova lista, partindo do estado (supervisor) anterior


        


        pass
    def gerar_sequencias(self,noSelfLoop=True):
        self.init_timer()

        #================INICIALIZANDO============
        self.realizar_operacao()
        if self.__observer.initial_state not in self.__parameter_list.keys():
            self.__parameter_list[self.__observer.initial_state] = list()
        supervisor_states = self.__estadosPorNome(self.__observer.initial_state) # pega a lista de estados do supervisor no estado (observador) atual
        for supp_state in supervisor_states: #itera sobre
            for sup_ev,sup_dest in self.__supervisor.transitions[supp_state].items():
                if sup_ev.name == 'tick':
                    if noSelfLoop and supp_state.name == sup_dest.name:
                        continue
                    #print("from",supp_state.name,"to",sup_dest.name)
                    self.__parameter_list[self.__observer.initial_state].append([supp_state]+self.__recursiveTickRelated(supp_state,noSelfLoop)) # inicializando uma lista, sendo a chave = estado que veio da transição não-tick ( é a do observador )

        
        for obs_new_ev,obs_new_dest in self.__observer.transitions[self.__observer.initial_state].items():
            self.__observadorTemporizado(self.__observer.initial_state,obs_new_ev,obs_new_dest,noSelfLoop)
        #=========================================
        
        self.stop_timer()


    '''
    {
        observer_state: {
            observer_last_event: list_supervisor_sequence
        }
    }
    '''    

    def __observadorTemporizado(self , obs_lastState , obs_lastEvent , obs_actualState,noSelfLoop):
        self.realizar_operacao()
        # chegando em um estado(observer), atraves de 1 evento não-tick (unica opção, pois observer n tem tick)
        # pegar o correspondente no supervisor aquele evento, colocá-lo como índice
        # adicionar todos os estados(supervisor) que ele alcançe com tick no supervisor
        if obs_actualState not in self.__parameter_list.keys():
            self.__parameter_list[obs_actualState] = list()
            sup_lastStateList = self.__estadosPorNome(obs_lastState)
            sup_event = self.__obsEvToSupEv(obs_lastEvent)
            for sl_state in sup_lastStateList:
                if sup_event in self.__supervisor.transitions[sl_state].keys():
                    current_head = self.__supervisor.transitions[sl_state][sup_event]
                    current_vect = [current_head]+self.__recursiveTickRelated(current_head,noSelfLoop)
                    #if len(current_vect) > 1:
                    self.__parameter_list[obs_actualState].append(current_vect)
            
            for obs_new_ev,obs_new_dest in self.__observer.transitions[obs_actualState].items():
                self.__observadorTemporizado(obs_actualState,obs_new_ev,obs_new_dest,noSelfLoop)

    def print_sequencias(self):
        for head_,list_ in self.__parameter_list.items():
            print("No estado: ",head_.name)
            print(list_,end="\n\n")
        print(len(self.__parameter_list.items()),"estados")

        '''
        if next_sup_head not in self.__parameter_list.keys():
            self.__parameter_list[next_sup_head]=list()

        sup_actualStates = self.__estadosPorNome(obs_actualState)

        tickList = __recursiveTickRelated(next_sup_head)
        
        for sup_stateIter in sup_actualStates:
            for sup_ev_,sup_dest_ in self.__supervisor.transitions[sup_stateIter].items():
                if sup_ev_.name == 'tick':
                    if sup_stateIter not in self.__parameter_list.keys():
                        self.__parameter_list[sup_stateIter] = list()
                    self.__parameter_list[sup_stateIter].append(sup_dest_)

        supervisor_iter_head=self.__getIterHead(obs_lastState,obs_lastEvent)
        
        for supp_state in supervisor_states:
            for sup_evt_,sup_dest_ in self.__supervisor.transitions[supp_state].items():
                if sup_evt_.name == 'tick':
                    if supv_lastState not in self.__parameter_list.keys():
                        self.__parameter_list[supp_state] = list()
                    self.__parameter_list[supp_state].append(sup_dest_)

        # chegando em um estado do observador,
        # carregando o estado anterior
        # listar (sup) o anterior, e para cada estado(sup)
        # pegar qual o destino com o evento que leva ao estado atual(obs)

        for obs_ev_,obs_dest_ in self.__observer.transitions[obs_state].items(): #iterando por evento e destino no estado do observador:
            matching=False
            while not matching:
                for ev_,dest_ in self.__supervisor.transitions[supp_state].items():
                    if ev_.name == 'tick':
                        self.__parameter_list[supp_state].append(dest_)
                        self.__observadorTemporizado(obs_state,supp_state,dest_)

            self.__observadorTemporizado(obs_dest_,supp_state,self.__supervisor.transitions[supp_state].)
            '''

    def __obsEvToSupEv(self,obs_event):
        for ev_item in self.__supervisor.events_set():
            if ev_item.name == obs_event.name:
                return ev_item
        return None

    def __recursiveTickRelated(self,sup_initial,noSelfLoop,last=[]):
        if sup_initial not in last:
            for sup_ev,sup_dest in self.__supervisor.transitions[sup_initial].items():
                if sup_ev.name == 'tick':
                    if noSelfLoop and sup_initial.name == sup_dest.name:
                        continue
                    #print("from",sup_initial.name,"to",sup_dest.name)
                    return [sup_dest]+self.__recursiveTickRelated(sup_dest,noSelfLoop,last+[sup_initial])
        return []



    def __getIterHead(obs_state,obs_event):
        sup_lastStates = self.__estadosPorNome(obs_state)
        for sup_lstate in sup_lastStates:
            for sl_evt,sl_dest_ in self.__supervisor.transitions[sup_lstate]:
                if sl_evt.name == obs_event.name:
                    return sl_dest_



    def __estadosPorNome(self,c_state):
        lista_ret = list()
        obs_currentStates = re.split("[\(\)\,]",c_state.name)[1:-1] if c_state.name[0] == '(' else re.split("[\(\)\,]",c_state.name)
        for state_name in obs_currentStates:
            supervisor_state = None
            for matching_state in self.__supervisor.states_set():
                if matching_state.name == state_name:
                    lista_ret.append(matching_state)
                    break
        return lista_ret














if __name__ == "__main__":
    state_list = [State("st_1"),State("st_2")]
    event_list_1 = [Event("ev_1"),Event("ev_2"),Event("tick")]
    event_list_2 = [Event("ev_1[1,-1]"),Event("ev_2[0,0]")]
    transition_list_1 = {}
    transition_list_1[state_list[0]] = {}
    transition_list_1[state_list[1]] = {}
    transition_list_1[state_list[0]][event_list_1[0]] = state_list[0]
    transition_list_1[state_list[0]][event_list_1[2]] = state_list[1]
    transition_list_1[state_list[1]][event_list_1[0]] = state_list[1]
    transition_list_1[state_list[1]][event_list_1[1]] = state_list[0]

    transition_list_2 = {}
    transition_list_2[state_list[0]] = {event_list_2[0]:state_list[1]}
    transition_list_2[state_list[1]] = {event_list_2[1]:state_list[0]}
    
    
    test_automaton = Automaton(transition_list_1,state_list[0])
    subsys_automaton = Automaton(transition_list_2,state_list[0])
    atemp = AutomatoTemporizado(test_automaton,[subsys_automaton])
    atemp.print_processing_status()
    atemp.gerar_mapa_de_estados()
    atemp.print_mapa_de_estados()




'''

    # =-=-=-=-   MODELO   -=-=-=
    {
        estado_supervisor: [
            lista_subestados_correspondentes,
            {
                evento_subsistema: [ delay,enabled,prohibited ]
            }
        ]
    }

'''