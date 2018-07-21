import numpy as np
from binarySearch import binarySearch

BINARY_SEARCH_START = 0.0
BINARY_SEARCH_END = 1000000.0


class FdWpcnBase(object):
    def __init__(self, gain):
        # channel gain
        self.gain = gain

        # number of ue
        self.ueCount = len(gain)

        self.flag = 2 ** (self.ueCount) - 1
        # dp map
        # init 0
        self.dpMap = {0: 0.0}

        # record the user position
        self.traceMap = {}

        # isDone
        self.isDone = False

    # dp to determine the user schedule.
    # flag: the left user set
    def dp(self, flag):
        if flag in self.dpMap:
            return self.dpMap[flag]

        tmpFlag = flag

        maxTmp = -1
        maxIndex = -1
        for i in range(self.ueCount):
            base = 1 << i

            if tmpFlag & base:
                # ue_i is in the left user set

                cur = self.getThroughput(tmpFlag, i, base)

                if cur > maxTmp:
                    maxTmp = cur
                    maxIndex = i

        self.traceMap.update({flag: maxIndex})
        self.dpMap.update({flag: maxTmp})
        return self.dpMap[flag]

    # sub-class override
    def getThroughput(self, tmpFlag, i, base):
        raise Exception("Unsupport.")

    # return throughput
    def getThroughputResult(self):
        return self.dp(self.flag)

    # get the user position
    def getUserPositionResult(self):

        # check dp done
        if not self.isDone:
            self.dp(self.flag)

        retval = []
        flag = self.flag
        while flag:
            nt = self.traceMap[flag]
            retval.append(self.gain[nt])
            flag -= 2 ** nt

        # need reverse
        retval.reverse()
        return retval


# express for sumThroughput bianry search
class SumExpress(object):
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2

    def fun(self, x):
        return np.log(1 + x) - x / (1 + x) - self.r1 - self.r2 / (1 + x)


# express for fairThroughput bianry search

class FairExpress(object):
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2

    def fun(self, x):
        return self.r1 * x - np.log(1 + self.r2 * x)


# handle the sum-throughput maximization
class SumFdWpcn(FdWpcnBase):
    def getThroughput(self, tmpFlag, i, base):
        r1 = self.dp(tmpFlag - base)
        r2 = self.gain[i]

        # binary search
        eps = SumExpress(r1, r2)
        bs = binarySearch(0, BINARY_SEARCH_END, eps.fun)
        x = bs.getResult()

        return np.log(1 + x) - x / (1 + x)


# handle the fair-throughput maximization
class FairFdWpcn(FdWpcnBase):
    def getThroughput(self, tmpFlag, i, base):
        r1 = self.dp(tmpFlag - base)
        r2 = self.gain[i]

        ## handle single user situation
        if r1 == 0.0:

            ## single user use sum-throughput expression
            eps = SumExpress(r1, r2)
            bs = binarySearch(0, BINARY_SEARCH_END, eps.fun)
            x = bs.getResult()
            return np.log(1 + x) - x / (1 + x)

        if r2 < r1:
            return 0.0
        eps = FairExpress(r1, r2)
        bs = binarySearch(0, BINARY_SEARCH_END, eps.fun)

        x = bs.getResult()
        return r1 * x / (1 + x)


if __name__ == "__main__":
    # gain = np.abs(np.random.rand(4) * 10)

    gain = [79, 65, 95]
    obj = SumFdWpcn(gain)
    print(obj.getThroughputResult())
    print(obj.getUserPositionResult())

    fair = FairFdWpcn(gain)
    print(fair.getThroughputResult())
    print(fair.getUserPositionResult())
