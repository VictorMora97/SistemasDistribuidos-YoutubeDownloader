#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' Implementacion de la parte del cliente '''

import sys
import os
import binascii
import cmd
import uuid
import random
import Ice
# pylint: disable=C0413
Ice.loadSlice('downloader.ice')
# pylint: enable=C0413
import Downloader

BLOCK_SIZE = 10240

class Comandos(cmd.Cmd):
    '''
    Petición de acciones mediante el Shell. Fuentes consultadas:
       - https://docs.python.org/3/library/cmd.html
       - https://pymotw.com/2/cmd/
       - https://coderwall.com/p/w78iva/give-your-python-program-a-shell-with-the-cmd-module
    '''
    intro = ('\n Bienvenid@ a Youtube Downloader. Escribir la acción deseada:\n \n   -Conectarse: conectar <endpoint>               \n   -Crear Scheduler: nuevo_scheduler \n   -Descargar cancion: add_download <url> \n   -Listar las canciones: lista_canciones \n   -Obtener cancion: get <nombre> \n   -Salir: salir \n')

    prompt = 'Accion --> '
    cliente = None

    @property
    def activo(self):
        ''' Se encuentra conectado o no lo está '''
        if self.cliente is None:
            return False
        return self.cliente.factoria is not None

    def do_conectar(self, line):
        '''Conectarse a la factoria (excepto si ya se esta conectado)'''
        if self.activo:
            print('\n Ya estas conectad@ \n')
            return None
        self.cliente.conectar_factoria(line)

    def do_nuevo_scheduler(self, line):
        '''Crear un nuevo scheduler (si se esta conectado), nombre con uuid.
           Fuentes consultadas: https://docs.python.org/3/library/uuid.html'''
        if not self.activo:
            print('Necesitas estar conectado a una factoria')
            return None
        self.cliente.make_scheduler(str(uuid.uuid4))

    def do_lista_canciones(self, line):
        '''Mostrar las canciones descargadas por el servidor'''
        if not self.activo:
            print('Necesitas estar conectado a una factoria')
            return None
        lista_canciones = self.cliente.scheduler.getSongList()
        if not lista_canciones:
            print('Ninguna canción descargada')
        else:
            for song in lista_canciones:
                print('\n%s\n' % song)

    def do_add_download(self, line):
        '''Añadir nueva descarga mediante una url de youtube'''
        if not self.activo:
            print('Necesitas estar conectado a una factoria')
            return None
        self.cliente.add_download(line)

    def do_get(self, line):
        '''Obtener la canción descargada'''
        if not self.activo:
            print('Necesitas estar conectado a una factoria')
            return None
        self.cliente.get(line)

    def do_salir(self, line):
        '''Salir de la aplicacion'''
        return True

class Cliente(Ice.Application):
    ''' Metodos del cliente '''
    dicc_schedulers = {}
    factoria = None

    @property
    def scheduler(self):
        '''
        Crear un scheduler si no hay ninguno. Fuentes consultadas:
          https://www.tutorialpython.com/listas-en-python/
          https://stackoverflow.com/questions/306400/how-to-randomly-select-an-item-from-a-list
          https://www.programiz.com/python-programming/property
        '''
        if not self.dicc_schedulers:
            self.make_scheduler(str(uuid.uuid4()))
        return random.choice(list(self.dicc_schedulers.values()))

    def conectar_factoria(self, proxy):
        ''' Conectarse a la factoria. Avisar si la conexión se realiza'''
        proxy_factoria = self.communicator().stringToProxy(proxy)
        self.factoria = Downloader.SchedulerFactoryPrx.checkedCast(proxy_factoria)
        if self.factoria:
            print('\n Conectado Correctamente \n')
        else:
            print('\n Introducir el endpoint \n')

    def add_download(self, url):
        ''' Añadir nueva descarga con el scheduler, se le pasa la url del audio a descargar '''
        if url is '':
            print('Es necesaria una url de youtube')
        else:
            self.scheduler.addDownloadTask(url)

    def get(self, cancion, destino='/home/victor/Escritorio/canciones'):
        '''
        Transferencia de ficheros entre el cliente y el servidor.
        Implementación copiada de transfer_snippet.py (ofrecido en el enunciado)
        Destino de los audios especificado. Fuentes consultadas:
          https://docs.python.org/3/library/os.path.html
          https://www.bogotobogo.com/python/python_files.php
        '''
        if cancion is not '':
            transfer = self.scheduler.get(cancion)
            with open(os.path.join(destino, cancion), "wb") as file_contents:
                remote_eof = False
                while not remote_eof:
                    data = transfer.recv(BLOCK_SIZE)
                    # Remove additional byte added by str() at server
                    if len(data) > 1:
                        data = data[1:]
                    data = binascii.a2b_base64(data)
                    remote_eof = len(data) < BLOCK_SIZE
                    if data:
                        file_contents.write(data)
                transfer.end()
        else:
            print('Sin canciones')

    def make_scheduler(self, nombre):
        '''
        Crear nuevo scheduler si se esta conectado  a la factoria.
        Fuentes consultadas: https://www.youtube.com/watch?v=Ycu5Re7bEUE
        '''
        self.dicc_schedulers[nombre] = self.factoria.make(nombre)

    def run(self, argv):
        comandos = Comandos()
        comandos.cliente = self
        comandos.cmdloop()
        return 0

sys.exit(Cliente().main(sys.argv))
