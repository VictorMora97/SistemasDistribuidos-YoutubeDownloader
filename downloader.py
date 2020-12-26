#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' Implementacion de la parte del servidor '''

import sys
import Ice
from downloader_scheduler import DownloadSchedulerI
from work_queue import WorkQueue
import IceStorm
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
import Downloader # pylint: disable=C0413

KEY = 'IceStorm.TopicManager.Proxy'

class SchedulerFactoryI(Downloader.SchedulerFactory):
    ''' Factoria de Schedulers '''

    dicc = {}

    def __init__(self, tareas, estado=None):
        self.tareas = tareas
        self.estado = estado

    def make(self, name=None, current=None):
        '''
        Crear un nuevo Scheduler y actualizar diccionario. Mostrar por pantalla.
        Fuentes externas consultadas:
          https://docs.python.org/3/library/uuid.html
          https://www.tutorialpython.com/listas-en-python/
          https://www.youtube.com/watch?v=Ycu5Re7bEUE
        '''
        servant = DownloadSchedulerI(self.tareas, self.estado)
        proxy = current.adapter.addWithUUID(servant)
        name = Ice.identityToString(proxy.ice_getIdentity())
        print('\nNuevo Scheduler --> %s\n' % (proxy))
        (self.dicc).update({name:proxy})
        return Downloader.DownloadSchedulerPrx.checkedCast(proxy)

class Server(Ice.Application):
    ''' Servidor '''

    def run(self, args):
        broker = self.communicator()
        topic_mgr_proxy = self.communicator().propertyToProxy(KEY)
        if  topic_mgr_proxy is None:
            print("property {0} not set".format(KEY))
            return 1
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)
        if not topic_mgr:
            print(': invalid proxy')
            return 2

        try:
            topic = topic_mgr.retrieve('ProgressTopic')
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create('ProgressTopic')

        adapter = broker.createObjectAdapter("Adapter")
        control_descarga = Downloader.ProgressEventPrx.uncheckedCast(topic.getPublisher())
        tareas = WorkQueue(control_descarga)
        servant = SchedulerFactoryI(tareas)
        proxy = adapter.addWithUUID(servant)
        servant.estado = Downloader.ProgressEventPrx.uncheckedCast(topic.subscribeAndGetPublisher({}, proxy))
        print(proxy, flush=True)
        adapter.activate()
        tareas.start()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
