# -*- coding: utf-8 -*-
import random
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array


NPROD = 3 #Numero de Productores
NCONS = 1 #Numero de Consumidores
N = 5 #Cuantos numeros tiene que producir cada productor
K = 3 #Numero maximo de elementos que puede haber de un Productor en el buffer

#Esta funcion dada una lista comprueba las primeras posiciones de cada productor y devuelve el minimo (que no sea -1) y su pid
def lower(lista):
    aux = [lista[K*pid] for pid in range(NPROD)]
    
    maximo = max(aux)
    for i in range(len(aux)):
        if aux[i] == -1:
            aux[i] = maximo + 1

    minimo = aux[0]
    pid = 0
    
    for i in range(1, len(aux)):
        if aux[i] < minimo and aux[i] != -1:
            minimo = aux[i]
            pid = i
    return minimo, pid



def add_data(buffer, mutex, cuantos_elementos, pid, data):
    mutex.acquire() # wait mutex
    try:
        buffer[K*pid + cuantos_elementos[pid]] = data
        cuantos_elementos[pid]+=1
        print('add',data, 'de productor', pid, 'buffer', list(buffer))
    finally:
        mutex.release() # signal mutex


def get_data(buffer, mutex, cuantos_elementos, numeros):
    mutex.acquire() #wait mutex
    try:
        data, pid = lower(buffer)
        numeros.append(data)
        for i in range(cuantos_elementos[pid] - 1): #corremos las posiciones en el segmento del buffer de pid
            buffer[pid*K + i] = buffer[pid*K + (i+1)]
        cuantos_elementos[pid] -= 1
        print('get',data,'de productor', pid, 'buffer', list(buffer))
        
    finally:
        mutex.release() # signal mutex
    return data, pid



def productor(lista_sem, mutex, buffer, pid, cuantos_elementos):
    
     v = 0
     
     for k in range(N):
         v += random.randint(1,2)
         lista_sem[2*pid].acquire() # wait empty
         add_data(buffer, mutex, cuantos_elementos, pid, v)
         lista_sem[2*pid+1].release() # signal nonEmpty
     
     v = -1
     lista_sem[2*pid].acquire() # wait empty
     add_data(buffer, mutex, cuantos_elementos, pid, v)
     lista_sem[2*pid+1].release() # signal nonEmpty
     


def consumidor(lista_sem, mutex, buffer, cuantos_elementos):  
    
    numeros = []
    for pid in range(NPROD):
        lista_sem[2*pid+1].acquire() # wait nonEmpty
        
    while [buffer[K*i] for i in range(NPROD)] != [-1]*NPROD:
        data, pid = get_data(buffer, mutex, cuantos_elementos, numeros)
        print('numeros:', numeros)
        lista_sem[2*pid].release() # signal empty
    
    print ('Valor final de la lista:', numeros)
    
    

def main():
     buffer = Array('i', NPROD*K)
     
     cuantos_elementos = Array('i', NPROD)
    
     lista_sem = [] #Creamos una lista de semaforos de forma que por cada relacion productor consumidor haya dos semaforos, una empty y otro nonEmpty
     #De esta forma lista_sem[2*pid] y lista_sem[2*pid +1] son los semaforos empty y nonEmpty del productor pid respectivamente

     for i in range(NPROD):
         lista_sem.append(BoundedSemaphore(K))# empty valdria Lock()
         lista_sem.append(Semaphore(0)) # nonEmpty para poder hacer un signal primero
     
     mutex = Lock() 
     
    
     lp = []# lista procesos
     
     for pid in range(NPROD):
         lp.append(Process(target=productor, args=(lista_sem, mutex, buffer, pid, cuantos_elementos)))
     lp.append(Process(target=consumidor, args=(lista_sem, mutex, buffer, cuantos_elementos)))    
     
     for p in lp:
         p.start()
     for p in lp:
         p.join()

if __name__ == "__main__":
 main() 