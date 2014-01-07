# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# PiKamPicamServer.py - Picam server for PiKam 
#
# Copyright (C) 2013: Michael Hamilton
# The code is GPL 3.0(GNU General Public License) ( http://www.gnu.org/copyleft/gpl.html )
#
from twisted.internet import reactor, protocol

import cPickle as Pickler
from datetime import datetime
import StringIO

import picam

from piKamServer import PiKamRequest, PiKamServerProtocal
from piKamServer import SCENE_OPTIONS,AWB_OPTIONS,METERING_OPTIONS,IMXFX_OPTIONS,COLFX_OPTIONS,ISO_OPTIONS,ENCODING_OPTIONS


class PiKamPicamServerProtocal(PiKamServerProtocal):
            
    def shoot(self, cmd):
        request = cmd['args']
        print vars(request)

        imageType = request.encoding if request.encoding else 'jpg'
        imageFilename = 'IMG-' + datetime.now().isoformat().replace(':','_') + '.' + imageType
        print imageType, imageFilename

        picam.config.imageFX = IMXFX_OPTIONS.index(request.imxfx)
        picam.config.exposure = SCENE_OPTIONS.index(request.scene) if request.scene else 0
        picam.config.meterMode = METERING_OPTIONS.index(request.metering)
        picam.config.awbMode = AWB_OPTIONS.index(request.awb)
        picam.config.ISO = int(request.iso) if ISO_OPTIONS.index(request.iso) != 0 else 0
        
        picam.config.sharpness = int(request.sharpness) if request.sharpness else 0            # -100 to 100
        picam.config.contrast = int(request.contrast)  if request.contrast else 0               # -100 to 100
        picam.config.brightness = int(request.brightness)   if request.brightness else 0           #  0 to 100
        picam.config.saturation = int(request.saturation)  if request.saturation else 0             #  -100 to 100
        #picam.config.videoStabilisation = 0      # 0 or 1 (false or true)
        picam.config.exposureCompensation  = int(request.ev)  if request.ev else 0  # -10 to +10 ?
        #picam.config.rotation = 90               # 0-359
        picam.config.hflip = int(request.hflip)  if request.hflip else 0                  # 0 or 1
        picam.config.vflip = int(request.vflip) if request.vflip else 0                   # 0 or 1
        #picam.config.shutterSpeed = 20000         # 0 = auto, otherwise the shutter speed in ms
        
        image = picam.takePhoto()
        buffer = StringIO.StringIO()
        image.save(buffer, "JPEG" if imageType == 'jpg' else imageType)
        imageBinary = buffer.getvalue()
        buffer.close()
        print imageFilename, str(len(imageBinary))
        if imageBinary:
            data = {'type':'image', 'name':imageFilename, 'data':imageBinary}
        else:
            data = {'type':'error', 'message':'Problem reading captured file.'}
        # data = {'type':'error', 'message':'Problem during capture.'}
        # Turn the dictionary into a string so we can send it in Netstring format.
        message = Pickler.dumps(data)
        print str(len(message))
        # Return a Netstring message to the client - will include the jpeg if all went well
        self.transport.write(str(len(message)) + ':' + message + ',')
 
    def prepareCamera(self, cmd):
        pass

       
def main():
    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = PiKamPicamServerProtocal
    reactor.listenTCP(8000,factory)
    reactor.run()

if __name__ == '__main__':
    main()