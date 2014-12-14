# -*- coding:utf-8 -*-
import log
from Queue import Queue
from threading import Thread
import traceback
import os,signal,sys

LOG = log.get_logger('zxLogger')
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
# ThreadPool implementation
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 

class ThreadPool(object):
    def __init__(self, size):
        self.size = size
        self.tasks = Queue(size)
        for i in range(size):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func,args,kargs))

    def wait_completion(self):
        self.tasks.join()

class Worker(Thread):
    def __init__(self, taskQueue):
        Thread.__init__(self)
        self.tasks = taskQueue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func ,args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except:
                #LOG.error(str(e))
                LOG.error(traceback.format_exc())

            finally:
                self.tasks.task_done()

class Terminate_Watcher:
    """this class solves two problems with multithreaded
    programs in Python, (1) a signal might be delivered
    to any thread (which is just a malfeature) and (2) if
    the thread that gets the signal is waiting, the signal
    is ignored (which is a bug).

    The watcher is a concurrent process (not thread) that
    waits for a signal and the process that contains the
    threads.

    I have only tested this on Linux.  I would expect it to
    work on the Macintosh and not work on Windows.

    The Watcher should be instantiated before the threads were
    created. It would kill threads when Ctrl-C was pressed.

    """

    def __init__(self):
        """ Creates a child thread, which returns.  The parent
            thread waits for a KeyboardInterrupt and then kills
            the child thread.
        """
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError: pass
