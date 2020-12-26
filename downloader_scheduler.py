#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
''' Implementacion del Scheduler '''
import binascii
import Ice
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
import Downloader # pylint: disable=C0413

class TransferI(Downloader.Transfer):
    '''
    Transferencia de ficheros entre cliente y servidor.
    Implementación copiada de transfer_snippet.py (ofrecido en el enunciado)
    '''
    def __init__(self, local_filename):
        self.file_contents = open(local_filename, 'rb')

    def recv(self, size, current=None):
        '''Send data block to client'''
        return str(
            binascii.b2a_base64(self.file_contents.read(size), newline=False)
        )

    def end(self, current=None):
        '''Close transfer and free objects'''
        self.file_contents.close()
        current.adapter.remove(current.id)

class DownloadSchedulerI(Downloader.DownloadScheduler, Downloader.ProgressEvent):
    '''
    Scheduler para usar las funciones. Fuentes externas consultadas:
      https://recursospython.com/guias-y-manuales/conjuntos-sets/
      https://doc.zeroc.com/ice/3.7/language-mappings/python-mapping/
      server-side-slice-to-python-mapping/asynchronous-method-dispatch-amd-in-python
    '''
    descargados = set()
    def __init__(self, tareas, estado):
        self.tareas = tareas
        self.estado = estado

    def addDownloadTask(self, url, current=None):
        ''' Añadir descarga '''
        callback = Ice.Future()
        self.tareas.add(callback, url, self.descargados)
        return callback

    def getSongList(self, current=None):
        ''' Obtener la lista de canciones '''
        return list(self.descargados)

    def get(self, filename, current=None):
        ''' Obtener el audio '''
        proxy = current.adapter.addWithUUID(TransferI(filename))
        return Downloader.TransferPrx.checkedCast(proxy)
