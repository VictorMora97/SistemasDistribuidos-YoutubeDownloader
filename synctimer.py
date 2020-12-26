#!/usr/bin/python3
# -*- coding: utf-8 -*-
''' Synctimer para la sincronización de servidores '''
import sys
import time
import Ice
import IceStorm
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
import Downloader # pylint: disable=C0413

KEY = 'IceStorm.TopicManager.Proxy'

class SyncTimer(Ice.Application):
    ''' Actua como publisher con un temporizador '''
    def run(self, args):
        topic_mgr_proxy = self.communicator().propertyToProxy(KEY)
        if topic_mgr_proxy is None:
            print("property {0} not set".format(KEY))
            return 1
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)
        if not topic_mgr:
            print(': invalid proxy')
            return 2
        try:
            topic = topic_mgr.retrieve("SyncTopic")
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create("SyncTopic")

        publisher = Downloader.SyncEventPrx.uncheckedCast(topic.getPublisher())
        self.shutdownOnInterrupt()

        while not (self.communicator()).isShutdown():
            publisher.requestSync()
            time.sleep(5.0)
        return 0

if __name__ == '__main__':
    app = SyncTimer()
    sys.exit(app.main(sys.argv))
