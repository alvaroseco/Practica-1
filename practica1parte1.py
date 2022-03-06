# -*- coding: utf-8 -*-
import random
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Value, Array


NPROD = 3 #Numero de Productores
NCONS = 1 #Numero de Consumidores
N = 5 #Cuantos numeros tiene que producir cada productor


#Esta funcion dada una lista devuelve el menor valor de la lista (que no sea -1) y su posicion
def lower(lista):
    aux = [0]*len(lista)
    maximo = max(lista)
    for i in range(len(lista)):
        if lista[i] == -1:
            aux[i] = maximo + 1
        else:
            aux[i] = lista[i]
            
    minimo = aux[0]
    index = 0
    
    for i in range(1, len(aux)):
        if aux[i] < minimo and aux[i] != -1:
            minimo = aux[i]
            index = i
            
    return minimo, index

    

def productor(lista, buffer, pid):
    
     v = 0
     
     for k in range(N):
         v += random.randint(0,5)
         print('prod:', pid, 'iter:', k, 'v:', v)
         lista[2*pid].acquire() # wait empty
         buffer[pid] = v
         lista[2*pid+1].release() # signal nonEmpty
     
     v = -1
     lista[2*pid].acquire() # wait empty
     buffer[pid] = v
     lista[2*pid+1].release() # signal nonEmpty
     


def consumidor(lista, buffer):  
    
    numeros = []
    
    for pid in range(NPROD):
        lista[2*pid+1].acquire() # wait nonEmpty
        
    while [-1]*NPROD != list(buffer):
        
        v, pid = lower(buffer)
        print('anade:', v, 'de Prod', pid)
        numeros.append(v)
        print (f"numeros: {numeros}")
        lista[2*pid].release() # signal empty
        lista[2*pid + 1].acquire() # wait nonEmpty
    
    print ('Valor final de la lista:', numeros)
    
    

def main():
     buffer = Array('i', NPROD)
    
     lista_sem = [] #Creamos una lista de semaforos de forma que por cada relacion productor consumidor haya dos semaforos, una empty y otro nonEmpty
     #De esta forma lista_sem[2*pid] y lista_sem[2*pid +1] son los semaforos empty y nonEmpty del productor pid respectivamente
     for i in range(NPROD):
         lista_sem.append(BoundedSemaphore(1))# empty valdria Lock()
         lista_sem.append(Semaphore(0)) # nonEmpty para poder hacer un signal primero
     
     lp = []# lista procesos
     
     for pid in range(NPROD):
         lp.append(Process(target=productor, args=(lista_sem, buffer, pid)))
     lp.append(Process(target=consumidor, args=(lista_sem, buffer)))    
     
     for p in lp:
         p.start()
     for p in lp:
         p.join()



if __name__ == "__main__":
 main()    
           

        