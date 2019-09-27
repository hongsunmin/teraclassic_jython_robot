import sys, signal, subprocess
import datetime, time, logging, re, collections
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
from time import sleep

class StopWatch:
    def __init__(self):
        self.start_time = 0
        self.stop_time = 0

    def start(self):
        self.start_time = time.time()
        return self.start_time

    def stop(self):
        self.stop_time = time.time()
        return self.stop_time

    def get_elapsed_time(self):
        return self.stop_time - self.start_time

    def get_elapsed_time_str(self):
        return str(self.stop_time - self.start_time)


class MissmatchException:
	def __init__(self):
		pass


class Resource:
    PROGRESS_IMAGE_RECT = None
    MISSION_PANEL_DEVA_3RD = None


class GameRobot:
    def __init__(self):
        logging.basicConfig(filename='robot.log', level=logging.DEBUG, format='%(asctime)s - [%(levelname)s] (%(filename)s:%(lineno)d) > %(message)s')
        logging.info('game robot init.')
        
        self.setting()
        self.connectDevice()
        
        self._lastProgressImage = None
        self._appKilled = False
        self._missionStopwatch = StopWatch()
        self._missionStopwatch.start()
        self._locationStopwatch = StopWatch()
        self._autoButtonStopwatch = StopWatch()
        self._arenaSkillClick = False
        
    
    def setting(self):
        SnapshotInfo = collections.namedtuple('SnapshotInfo', 'fileName rect')
        MissionProgressInfo = collections.namedtuple('MissionProgressInfo', 'rect highlightColor')
        MissionPanelInfo = collections.namedtuple('MissionPanelInfo', 'leftTouchPos completeTouchPos completePixelCheckPos progressSnapshotInfo')
        
        self._scale = 1
        
        Resource.PROGRESS_IMAGE_RECT = SnapshotInfo(fileName='./sc/ingNo.png', rect=(600, 450, 38, 15))
        Resource.MISSION_PANEL_BLOOD_PRIEST = MissionPanelInfo(leftTouchPos=(250, 225), completeTouchPos=(900, 610), completePixelCheckPos=(796, 583), progressSnapshotInfo=Resource.PROGRESS_IMAGE_RECT)
        Resource.MISSION_PANEL_MAMMOTH = MissionPanelInfo(leftTouchPos=(250, 295), completeTouchPos=(900, 610), completePixelCheckPos=(796, 583), progressSnapshotInfo=Resource.PROGRESS_IMAGE_RECT)
        Resource.MISSION_PANEL_DEVA_3RD = MissionPanelInfo(leftTouchPos=(250, 365), completeTouchPos=(600, 610), completePixelCheckPos=(490, 583), progressSnapshotInfo=Resource.PROGRESS_IMAGE_RECT)
        Resource.MISSION_PANEL_ARCHEOPTERYX = MissionPanelInfo(leftTouchPos=(250, 435), completeTouchPos=(600, 610), completePixelCheckPos=(490, 583), progressSnapshotInfo=Resource.PROGRESS_IMAGE_RECT)
        Resource.MISSION_PANEL_INFECTED = MissionPanelInfo(leftTouchPos=(250, 505), completeTouchPos=(600, 610), completePixelCheckPos=(490, 583), progressSnapshotInfo=Resource.PROGRESS_IMAGE_RECT)
        
    
    def connectDevice(self):
        logging.debug('connecting device...')
        self._device = MonkeyRunner.waitForConnection()
        logging.debug('connected to device.')
        
    
    def snapshot(self, capture=True):
        if capture:
            logging.debug('take snapshot.')
            self._lastSnapshot = self._device.takeSnapshot()
        else:
            logging.debug('last snapshot.')
        return self._lastSnapshot
    
    def subSnapshot(self, rect, capture=True):
        return self.snapshot(capture).getSubImage(rect)
    
    
    def getScreenRawPixel(self, x, y, capture=True):
        pixel = self.snapshot(capture).getRawPixel(x * self._scale, y * self._scale)
        logging.debug('x:%d y:%d pixel %s' % (x * self._scale, y * self._scale, pixel))
        return pixel
    

    def touch(self, x, y):
        try:
            self._device.touch(x * self._scale, y * self._scale, MonkeyDevice.DOWN_AND_UP)
            logging.debug('touched (%d, %d)' % (x * self._scale, y * self._scale))
        except:
            logging.error('broken connection. re-connect device...')
            self._device.reboot("None")
            self.connectDevice()
            logging.info('re-connected device')
        sleep(2)
    
    def setPackageName(self, packageName):
        self._packageName = packageName
        

    def setActivityName(self, activityName):
        self._activityName = activityName
    
    
    def readyMission(self, first=False):
        runComponent = self._packageName + '/' + self._activityName
        
        if first:
            sleep(5)
            self._device.wake()
            sleep(5)
            self._device.shell("input keyevent MENU")
            sleep(5)
        
        # check foreground game process
        started = False
        while True:
            focusApp = self._device.shell("dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
            p = re.compile('mCurrentFocus=.*{(.*)}')
            m = p.search(focusApp)
            if m is None or m.group(1).find(runComponent) == -1:
                logging.info('app is not running. start %s' % runComponent)
                self._device.startActivity(component=runComponent)
                logging.info('started app.')
                started = True
                
                # wait intro
                sleep(15)
                self.touch(680, 325)
            else:
                break
        
        # check lost login
        if self._betweenTuple(self.getScreenRawPixel(598, 490), (-1, 55, 101, 167), (-1, 56, 101, 168)) and self._betweenTuple(self.getScreenRawPixel(595, 515, False), (-1, 32, 72, 137), (-1, 32, 74, 140)):
            logging.info('lost login. click re-login.')
            self.touch(740, 515)
            started = True
            # wait screen change
            sleep(10)
        
        # check main
        while started and True:
            if self._betweenTuple(self.getScreenRawPixel(584, 123), (-1, 229, 229, 237), (-1, 255, 255, 255)) and self._betweenTuple(self.getScreenRawPixel(908, 123, False), (-1, 252, 252, 255),  (-1, 255, 255, 255)):
                logging.info('main screen. start to play game.')
                
                # wait network operations
                sleep(15)
                
                self.touch(838, 460)
                self.touch(666, 260)
                self.touch(1224, 659)
                
                # check duplicate login
                if self._betweenTuple(self.getScreenRawPixel(746, 489), (-1, 55, 100, 168), (-1, 56, 101, 169)) and self._betweenTuple(self.getScreenRawPixel(449, 490, False), (-1, 71, 81, 109), (-1, 71, 81, 110)) and self._betweenTuple(self.getScreenRawPixel(738, 415, False), (-1, 22, 25, 36), (-1, 22, 26, 36)):
                    logging.info('duplicate login. click confirm button.')
                    self.touch(880, 515)
                
                # wait screen change
                sleep(5)

                # check character select screen
                if self.getScreenRawPixel(1170, 639) == (-1, 54, 100, 167) and self.getScreenRawPixel(36, 33, False) == (-1, 255, 255, 255):
                    logging.info('character select screen. click game start button.')
                    self.touch(1312, 664)
                
                # wait game screen
                sleep(30)
                break
            else:
                sleep(10)
        
        # check event popup
        while self.getScreenRawPixel(1140, 659) == (-1, 255, 255, 255):
            logging.info('close event popup.')
            self.touch(1140, 659)
        
        # check character dead screen
        if self.getScreenRawPixel(1170, 639) == (-1, 50, 96, 164) and self._betweenTuple(self.getScreenRawPixel(1170, 615, False), (-1, 23, 26, 26), (-1, 24, 27, 37)):
            logging.info('character dead.')
            self.touch(1260, 655)
            
            # wait screen change
            sleep(10)
            
            if self.getScreenRawPixel(1251, 72) == (-1, 225, 232, 245) and self.getScreenRawPixel(492, 625, False) == (-1, 4, 5, 7):
                self.touch(1251, 72)
            
                
    def doMission(self):
        first = True
        
        while True:
            now = datetime.datetime.now()
            today = datetime.date.today()
            start1 = datetime.datetime.combine(today, datetime.time(hour=20, minute=0, second=0))
            end1 = datetime.datetime.combine(today, datetime.time(hour=23, minute=59, second=59))
            start2 = datetime.datetime.combine(today, datetime.time(hour=0, minute=0, second=0))
            end2 = datetime.datetime.combine(today, datetime.time(hour=8, minute=0, second=0))
            
            arena_start = datetime.datetime.combine(today, datetime.time(hour=12, minute=00, second=0))
            arena_end = datetime.datetime.combine(today, datetime.time(hour=18, minute=30, second=59))
            
            if True or now >= start1 and now <= end1 or now >= start2 and now <= end2:
                logging.info('play time!!!')
                if first:
                    self.readyMission(first)
                
                try:
                    if now >= arena_start and now <= arena_end:
                        self._do3vs3Arena()
                    else:
                        self._doMission(first)
                except MissmatchException:
                    self._killApp()
                    first = True
                    continue
                
                if first == True:
                    first = False
                sleep(5)
            else:
                logging.info('break time!!! kill app.')
                self._killApp()
                first = True
                sleep(60)
            
            
    def saveSnapshot(self, snapshotInfo):
        subImage = self.snapshot().getSubImage(snapshotInfo.rect)
        subImage.writeToFile(snapshotInfo.fileName, 'png')
        return subImage
        
    
    def saveFullscreen(self):
        snapshot = self.snapshot().writeToFile('./sc/shot2.png', 'png')
        return snapshot
        
        
    def _doMission(self, first):
        missionRes = Resource.MISSION_PANEL_INFECTED
        
        # check SOTANG Dialog
        pixel1 = self.getScreenRawPixel(1255, 75)
        pixel2 = self.getScreenRawPixel(845, 73, False)
        if not self._betweenTuple(pixel1, (-1, 225, 231, 245), (-1, 225, 232, 247)) and pixel2 != (-1, 15, 21, 33):
            checkCount = 0
            while True:
                # Open Sotang Dialg
                logging.info('Sotang Dialog closed. OPEN!!. pixel1 %s pixel2 %s' % (pixel1, pixel2))
                self.touch(242, 125)
                
                checkCount += 1
                pixel1 = self.getScreenRawPixel(1255, 75)
                pixel2 = self.getScreenRawPixel(845, 73, False)
                if self._betweenTuple(pixel1, (-1, 225, 231, 245), (-1, 225, 232, 247)) and self._betweenTuple(pixel2, (-1, 15, 21, 32), (-1, 15, 21, 33)):
                    break
                elif checkCount >= 3:
                    raise MissmatchException
        
            # Click Sotang Left Menu
            self.touch(missionRes.leftTouchPos[0], missionRes.leftTouchPos[1])
            
        if first:
            logging.debug('Mission first process.')
            self._lastProgressImage = self.saveSnapshot(missionRes.progressSnapshotInfo)
            self._locationStopwatch.start()
            self._autoButtonStopwatch.start()
        
        # Reset mission location
        self._locationStopwatch.stop()
        if first or self._locationStopwatch.get_elapsed_time() >= 300:
            self._locationStopwatch.start()
            logging.info('Reset mission location process.')
            self._clickCompleteMissionButton(missionRes)
            self._clickAutoButton()
            self.touch(242, 125)

        # Check Auto mode OFF
        self._autoButtonStopwatch.stop()
        if first or self._autoButtonStopwatch.get_elapsed_time() >= 60:
            self._autoButtonStopwatch.start()
            newProgresssImage = self.saveSnapshot(missionRes.progressSnapshotInfo)
            # Click X Btn, Close Dialog.
            logging.info('Check auto activation process.')
            self.touch(1255, 75)
            self._clickAutoButton()
            self.touch(242, 125)
            
        # Check SOTANG Finished
        pixel = self.getScreenRawPixel(missionRes.completePixelCheckPos[0], missionRes.completePixelCheckPos[1])
        if not self._betweenTuple(pixel, (-1, 56, 101, 167), (-1, 73, 113, 171)):
            self._clickCompleteMissionButton(missionRes)
            self._missionStopwatch.stop()
            logging.info('Finished. time %s pixel %s' % (self._missionStopwatch.get_elapsed_time_str(), pixel))
            self._missionStopwatch.start()
    
    
    def _do3vs3Arena(self):
        # check Arena Menu
        pixel1 = self.getScreenRawPixel(44, 33)
        pixel2 = self.getScreenRawPixel(45, 230, False)
        if pixel1 != (-1, 255, 255, 255) and not self._betweenTuple(pixel2, (-1, 239, 240, 241), (-1, 239, 240, 241)):
            checkCount = 0
            while True:
                # Open check Arena Menu
                logging.info('Arena Menu closed. OPEN!!. pixel1 %s pixel2 %s' % (pixel1, pixel2))
                self.touch(1295, 28)
                self.touch(248, 95)
                self.touch(680, 220)
                self.touch(1220, 660)
                
                checkCount += 1
                pixel1 = self.getScreenRawPixel(44, 33)
                pixel2 = self.getScreenRawPixel(45, 230, False)
                if pixel1 == (-1, 255, 255, 255) and self._betweenTuple(pixel2, (-1, 239, 240, 241), (-1, 239, 240, 241)):
                    break
                elif checkCount >= 3:
                    raise MissmatchException
                
                sleep(3)
        
        
        if self._betweenTuple(self.getScreenRawPixel(1017, 635), (-1, 55, 100, 168), (-1, 56, 102, 170)):
            self.touch(1220, 660)
        
        if self.getScreenRawPixel(346, 180) == (-1, 0, 0, 0) and self._betweenTuple(self.getScreenRawPixel(747, 549, False), (-1, 55, 100, 168), (-1, 56, 101, 169)):
            self._arenaSkillClick = False
            self.touch(940, 575)
        
        if self._betweenTuple(self.getScreenRawPixel(180, 32), (-1, 0, 0, 0), (-1, 1, 0, 0)) and self._betweenTuple(self.getScreenRawPixel(358, 32, False), (-1, 0, 0, 0), (-1, 1, 0, 0)) and self._betweenTuple(self.getScreenRawPixel(538, 32, False), (-1, 0, 0, 0), (-1, 1, 0, 0)) and self._betweenTuple(self.getScreenRawPixel(893, 32, False), (-1, 0, 0, 0), (-1, 1, 0, 0)) and self._betweenTuple(self.getScreenRawPixel(1070, 32, False), (-1, 0, 0, 0), (-1, 1, 0, 0)) and self._betweenTuple(self.getScreenRawPixel(1250, 32, False), (-1, 0, 0, 0), (-1, 1, 0, 0)):
            self._clickAutoButton()
            
            # Set target
            self.touch(180, 32)
            self.touch(358, 32)
            self.touch(538, 32)
            self.touch(893, 32)
            self.touch(1070, 32)
            self.touch(1250, 32)
            
            if self._arenaSkillClick:
                logging.info('Click skill button.')
                self.touch(1250, 643)
                self.touch(1250, 643)
            
                self.touch(1236, 542)
                self.touch(1236, 542)
            
                self.touch(1416, 479)
            
                self.touch(1142, 642)
            else:
                self._arenaSkillClick = True


    def _clickCompleteMissionButton(self, missionRes):
        logging.info('Click complete button.')
        self.touch(missionRes.completeTouchPos[0], missionRes.completeTouchPos[1])
    
    
    def _clickAutoButton(self):
        # Click Auto Btn
        pixel = self.getScreenRawPixel(1338, 384)
        if not self._betweenTuple(pixel, (-1, 218, 218, 218), (-1, 255, 255, 255)):
            logging.info('Click auto button. pixel %s' % (pixel, ))
            self.touch(1350, 375)


    def _betweenTuple(self, base, min, max):
        return (min[1] <= base[1] <= max[1]) and (min[2] <= base[2] <= max[2]) and (min[3] <= base[3] <= max[3])
    
    
    def _killApp(self):
        logging.info('kill app. %s' % self._packageName)
        self._device.shell('am force-stop %s' % self._packageName)


if __name__ == "__main__":
    robot = GameRobot()
    robot.setPackageName('com.kakaogames.tera')
    robot.setActivityName('com.meteoritestudio.prom1.MainActivity')
    robot.doMission()
#     robot.saveFullscreen()
#     robot.getScreenRawPixel(346, 180)