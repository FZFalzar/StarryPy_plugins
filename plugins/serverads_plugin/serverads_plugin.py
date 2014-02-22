#===========================================================
#   ServerAds Plugin
#   Author: FZFalzar/Duck of Brutus.SG Starbound (http://steamcommunity.com/groups/BrutusSG)
#   Version: v0.1
#   Description: Broadcasts defined messages(ServerAds) at a preset duration
#===========================================================

import random
from base_plugin import SimpleCommandPlugin
from plugins.core.player_manager import permissions, UserLevels
from threading import Timer

class ServerAds(SimpleCommandPlugin):
    """
    Broadcasts pre-defined messages at set intervals to all players
    """
    name = "serverads_plugin"
    depends = ["command_dispatcher"]
    commands = ["ads_reload", "ads_interval"]
    auto_activate = True

    def activate(self):
        super(ServerAds, self).activate()
        self.load_config()
        self.ads_thread = None
        self.prevMsgIdx = 0
        self.rNum = 0
        self.start_broadcasting()

    def load_config(self):
        try:
            self.serverads_list = self.config.plugin_config["serverads_list"]
            self.serverads_prefix = self.config.plugin_config["serverads_prefix"]
            self.interval = self.config.plugin_config["serverads_interval"]
        except Exception as e:
            self.logger.info("Error occured! %s" % e)
            if self.protocol is not None:
                self.protocol.send_chat_message("Reload failed! Please check config.json! Then do /ads_reload")
                self.protocol.send_chat_message("Initiating with default values...")
            self.serverads_list = ["Welcome to the server!", "Have a nice stay!"]
            self.serverads_prefix = "[SA]"
            self.interval = 30
    def save_config(self):
        self.config.plugin_config['serverads_list'] = self.serverads_list
        self.config.plugin_config['serverads_prefix'] = self.serverads_prefix
        self.config.plugin_config['serverads_interval'] = self.interval
        self.config.save()

    def start_broadcasting(self):
        if self.ads_thread is not None:           
            self.ads_thread.stop()
            self.logger.info("Broadcast thread stopped!")
            del self.ads_thread
        self.ads_thread = ThreadedTimer(self.interval, self.broadcast)
        self.ads_thread.start()
        self.logger.info("Broadcast thread started!")

    def broadcast(self):
        #make sure we do not re-broadcast the last message, for variety
        if len(self.serverads_list) > 1:
            while self.rNum == self.prevMsgIdx:
                #randomly pick from the array 
                self.rNum = random.randint(0, len(self.serverads_list) - 1)
            #override previous index
            self.prevMsgIdx = self.rNum
            self.logger.info("%s %s" % (self.serverads_prefix, self.serverads_list[self.rNum]))
            self.factory.broadcast("%s ^#00FF00;%s" % (self.serverads_prefix, self.serverads_list[self.rNum]), 0, "", "ServerAds")
        elif len(self.serverads_list) <= 1:
            self.logger.info("%s %s" % (self.serverads_prefix, self.serverads_list[0]))
            self.factory.broadcast("%s ^#00FF00;%s" % (self.serverads_prefix, self.serverads_list[0]), 0, "", "ServerAds")
            
    @permissions(UserLevels.ADMIN)
    def ads_reload(self, data):
        """Reloads values from configuration. Syntax: /ads_reload"""
        self.protocol.send_chat_message("ServerAds reloading!")        
        self.load_config()
        self.start_broadcasting()
        self.protocol.send_chat_message("ServerAds reloaded!")
        self.protocol.send_chat_message("A restart is necessary as there is currently no other way to reload config.json. Sorry for the inconvenience!")

    @permissions(UserLevels.ADMIN)
    def ads_interval(self, data):
        """Sets interval for display of serverads. Syntax: /ads_interval [duration in seconds]"""
        if len(data) == 0:
            self.protocol.send_chat_message(self.ads_interval.__doc__)
            self.protocol.send_chat_message("Current interval: %s seconds" % self.interval)
            return
        num = data[0]
        try:
            self.interval = int(num)
            self.protocol.send_chat_message("Interval set -> %s seconds" % self.interval)
        except:
            self.protocol.send_chat_message("Invalid input! %s" % num)
            self.protocol.send_chat_message(self.ads_interval.__doc__)
            return
        
        self.save_config()
        self.load_config()
        self.start_broadcasting()
            

class ThreadedTimer(object):
    #original source, stackoverflow
    """
    Provides an interface for an interruptible timer thread
    """
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False