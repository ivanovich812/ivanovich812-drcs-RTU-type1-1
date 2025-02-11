from time import sleep

ControlCounter = -128
TimeDelta = 1

while True:
    ControlCounter += 1
    if ControlCounter == 127:
        ControlCounter = -128

    sleep(1)


# while True:
#     Time = TimeNow - TimeMark
#     if Time < TimeDelta:
#         isPUActive = True
#     else:
#         isPUActive = False
#
#     sleep(TimeDelta)
