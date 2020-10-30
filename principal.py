from classes.xml_to_automaton import createAutomaton
from classes.TimedAutomaton import SupervisorTemporizado,ObservadorTemporizado
from colorama import Fore,Style,init # lib pra deixar texto colorido
import sys

init() # funcoes do colorama não funcionam se não der esse init



# ==========   TESTE DO SUPERVISOR ==============


automata = createAutomaton("supervisor.xmd")
subsys_1 = createAutomaton("subsistema_1.xmd")
subsys_2 = createAutomaton("subsistema_2.xmd")

#atemp = AutomatoTemporizado(automata,[subsys_1])
#atemp = AutomatoTemporizado(automata)
atemp = SupervisorTemporizado(automata,[subsys_1,subsys_2])

atemp.carregar_mapa_verificacao("mapa_estados_csv.txt")

atemp.gerar_mapa_de_estados()
atemp.print_processing_status()
#atemp.print_mapa_de_estados()
#atemp.print_mapa_de_verificacao()

if atemp.comparar_mapas(False) == True:
    print(Fore.GREEN+"\nTABELAS IGUAIS\n"+Style.RESET_ALL)
else:
    print(Fore.RED+"\nTABELAS DIFERENTES\n"+Style.RESET_ALL)

#atemp.gravar_parametros("supervisor.xmd","new_supervisor.xmd")


# ==============================================
# ==============================================



# ============== TESTE DO OBSERVADOR ==============

observer = createAutomaton('observer(supervisor).xmd')
supervisor = createAutomaton('supervisor.xmd')
subsys_1 = createAutomaton("subsistema_1.xmd")
subsys_2 = createAutomaton("subsistema_2.xmd")

atemp = ObservadorTemporizado(observer,supervisor,[subsys_1,subsys_2])

atemp.gerar_sequencias(True)
atemp.print_processing_status()
atemp.print_sequencias()
    

# =================================================
# =================================================