
import adbutils
from logzero import logging, setup_logger
import time
import subprocess
import os
import functools


def func_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)  # 需要先运行一下函数，记录开始时间和结束时间。
        end = time.time()
        print('%s 运行时间: %s s' % (func.__name__, (end - start)))

    return wrapper


@func_time
def main(package_name):
    logger = setup_logger(level=logging.DEBUG)

    # adbutils.adb.connect('192.168.2.151')
    d = adbutils.adb.device()
    print(d)

    folder_path = 'D:\\ALOG\\'
    test_count = 5000

    d.app_stop(package_name)

    current_time = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
    monkey_log_file_name = "monkey_log_" + current_time + ".log"
    monkey_log_file_path = os.path.join(folder_path, monkey_log_file_name)

    monkey_log_file_path_flg = '> ' + monkey_log_file_path
    sc = d.screenrecord("/sdcard/log_ScreenRecord.mp4")
    record_start = time.time()
    logger.info('ScreenRecord start !')

    cmd = ' '.join(['adb', 'shell', 'monkey', '-p', package_name, '--pct-syskeys', '0', '--pct-nav', '0',
                    '--pct-rotation', '0', '--pct-trackball', '0', '--pct-anyevent', '0',
                    '--pct-touch', '74', '--pct-motion', '25', '--throttle', '450', '-v', '-v', '-v',
                    str(test_count), monkey_log_file_path_flg])
    # print(cmd)
    try:
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
        for i in range(test_count):
            test_return = subprocess.Popen.poll(p)
            time.sleep(3)
            if test_return is None:
                logger.info('running...')
                if int((time.time()-record_start) > 120):
                    print((time.time()-record_start))
                    sc.stop()
                    record_start = time.time()
                    sc = d.screenrecord("/sdcard/log_ScreenRecord.mp4")
                    time.sleep(3)

            else:
                logger.info(p.stdout.read())
                break

        logger.info(monkey_log_file_path)
        logger.info('test end !')

        time.sleep(3)
        current_time = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
        screen_record_file_name = 'log_ScreenRecord_' + current_time + '.mp4'
        screen_record_file_path = os.path.join(folder_path, 'ScreenRecord', screen_record_file_name)
        sc.stop_and_pull(screen_record_file_path)
        logger.info(screen_record_file_path)

        log_file_name = 'log_' + current_time + '.log'
        log_file_path = os.path.join(folder_path, log_file_name)
        d.sync.pull('/sdcard/log.log', log_file_path)

    except ConnectionAbortedError:
        print('test error!!')
        logger.debug('设备连接已断开！')
        file = '/sdcard/log.log'
        cmd = ' '.join(['adb', 'pull', file, 'D:/ALOG/'])
        with os.popen(cmd) as p:
            r = p.read()
            if r:
                logger.debug(r)

        file = "/sdcard/log_ScreenRecord.mp4"
        cmd = ' '.join(['adb', 'pull', file, 'D:/ALOG/log_ScreenRecord.mp4'])
        with os.popen(cmd) as p:
            r = p.read()
            if r:
                logger.debug(r)




if __name__ == '__main__':

    main(package_name)
