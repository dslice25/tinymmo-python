from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory, ClientCreator
from twisted.protocols import basic

from StringIO import StringIO
import json
import zipfile
import sys

class GameClientFactory(ClientFactory):
    
  def __init__(self, client):
    
    self.client = client

  def startedConnecting(self, connector):
    print 'Started to connect.'
    #self.client.chatManager.add_message('Started to connect')

  def clientConnectionLost(self, connector, reason):
    print 'Lost connection.  Reason:', reason
    #self.client.chatManager.add_message('Lost connection.')

  def clientConnectionFailed(self, connector, reason):
    print 'Connection failed. Reason:', reason
    #self.client.chatManager.add_message('Connection failed.')
  
  def buildProtocol(self, addr):
    #self.client.chatManager.add_message('Connected.')
    print 'Connected.'
    self.client.connected()
    return GameClientProtocol(self.client)

class GameClientProtocol(basic.LineReceiver):
  
  def __init__(self, client):
    
    self.client = client
    self.client.set_protocol(self)
   
  def connectionMade(self):
    print "Connection made"
    #self.client.chatManager.add_message('Connection made.')

  def connectionLost(self, reason):
    print "Connection lost",reason
    #self.client.chatManager.add_message('Connection lost.')

  def send(self, data):
    line = ""
    try:
      line = json.dumps(data)
    except:
      print "Could not dump json",data

    self.transport.write(line + "\r\n")

  def lineReceived(self, line):
    data = { 'type': 'error', 'message': 'could not process line %s' % line }
    try:
      data = json.loads(line)
    except:
      print "Could load json",line

    self.client.process(data) 

