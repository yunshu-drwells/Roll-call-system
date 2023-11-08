import logging
import configparser


class LoadConfig:
    # 从配置文件读取配置
    def getParser(self):
        # 创建配置文件解析器
        config = configparser.ConfigParser()
        config.read('config.ini')  # 指定配置文件的路径
        # 从配置文件中读取值
        pause = config['USED']['pause']
        hardware = config['USED']['hardware']
        character = config['USED']['character']
        chosenClass = config['USED']['chosenclass']
        logging.info(
            "通过配置文件读取到pause:%s, hardware:%s, character:%s, chosenClass:%s",
            pause, hardware, character, chosenClass)
        self.params = {
            'pause' : pause,
            "hardware": hardware,
            "character": character,
            "chosenclass": chosenClass,
        }
        return self.params

    # 保存配置到配置文件
    def saveParser(self):
        config = configparser.ConfigParser()
        config['USED'] = {}
        for k in self.params.keys():
            # print(self.params[k])
            config['USED'][k] = self.params[k]
        with open('config.ini', 'w') as cf:
            config.write(cf)


if __name__ == "__main__":
    lc = LoadConfig()
    pars = lc.getParser()
    print(pars['chosenclass'])
    lc.saveParser()

    '''
    config = configparser.ConfigParser()
    config.read('config.ini')  # 指定配置文件的路径
    # 从配置文件中读取值
    speed = config['USED']['speed']
    hardware = config['USED']['hardware']
    character = config['USED']['character']
    chosenClass = config['USED']['chosenClass']
    soundDeviceIndex = config['USED']['soundDeviceIndex']
    randomStudentnum = config['USED']['randomStudentnum']
    logging.info(
        "通过配置文件读取到speed:%s, hardware:%s, character:%s, chosenClass:%s, soundDeviceIndex:%s, randomStudentnum:%s",
        speed, hardware, character, chosenClass, soundDeviceIndex, randomStudentnum)

    params = {
        "speed": speed,
        "hardware": hardware,
        "character": character,
        "chosenClass": chosenClass,
        "soundDeviceIndex": soundDeviceIndex,
        "randomStudentnum": randomStudentnum,
    }
    print(params)
    '''

'''
[USED]
speed = 1
hardware = cuda
character = paimon
chosenClass = 123
soundDeviceIndex = 3
randomStudentnum = 1
'''