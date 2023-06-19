import sys

import asyncio
import time

from airtouch4pyapi import AirTouch, AirTouchStatus, AirTouchVersion

def print_groups(groups):
    for group in groups:
        print(f"Group Name: {group.GroupName:15s} | Group Number: {group.GroupNumber:3d} | PowerState: {group.PowerState:3s} | IsOn: {group.IsOn:3s} | OpenPercent: {group.OpenPercent:3d} | Temperature: {group.Temperature:3.1f} | Target: {group.TargetSetpoint:3.1f} | ControlMethod: {group.ControlMethod:19s} | BelongToAc: {group.BelongsToAc:2d} | Spill: {group.Spill}")

def print_attr(obj):
    max_length = 0
    for x in dir(obj):
        if x[:2] != '__' and len(x) > max_length:
            max_length = len(x)
    for x in dir(obj):
        if x[:2] != '__':
            print(f"{x:{str(max_length) + 's'}} : {getattr(obj, x)}")

async def updateInfoAndDisplay(ip):
    at = AirTouch(ip)
    await at.UpdateInfo()
    if(at.Status != AirTouchStatus.OK):
        print("Got an error updating info.  Exiting")
        return
    print("Updated Info on Groups (Zones) and ACs")
    print("AC INFO")
    print("----------")
    acs = at.GetAcs()
    for ac in acs:
        print_attr(ac)
    print("----------\n\n")
    print("GROUP/ZONE INFO")
    print("----------")
    groups = at.GetGroups()
    print_groups(groups)
    val = input("Do you want to turn them all off, wait 10 seconds, turn them all back on? (y/n): ")
    if(val.lower() == "y"):
        for group in groups:
            await at.TurnGroupOffByName(group.GroupName)
        print("GROUP/ZONE INFO AFTER TURNING ALL OFF")
        print("----------")
        print_groups(groups)
        time.sleep(10)
        for group in groups:
            await at.TurnGroupOnByName(group.GroupName)
        await at.TurnAcOn(0)
        print("GROUP/ZONE INFO AFTER TURNING ALL ON")
        print("----------")
        print_groups(groups)
    val = input("Do you want to increment set points by 1 degree then back down by 1? (y/n): ")
    if(val.lower() == "y"):
        for group in groups:
            to_temp = int(group.TargetSetpoint) + 1
            await at.SetGroupToTemperatureByGroupName(group.GroupName, to_temp)
        print("GROUP/ZONE INFO AFTER SET TEMP + 1")
        print("----------")
        print_groups(groups)
        time.sleep(5)
        for group in groups:
            to_temp = int(group.TargetSetpoint) -1
            await at.SetGroupToTemperatureByGroupName(group.GroupName, to_temp)
        print("GROUP/ZONE INFO AFTER SET TEMP + 1")
        print("----------")
        print_groups(groups)
        
    val = input("Do you want to set group 0's mode to heat then back to cool? (y/n): ")
    if(val.lower() == "y"):
        await at.SetCoolingModeByGroup(0, 'Heat')
        print("AC INFO AFTER SETTING GROUP 0 to HEAT")
        print("----------")
        print_acs(acs)
        time.sleep(5)
        await at.SetCoolingModeByGroup(0, 'Cool')
        print("AC INFO AFTER SETTING GROUP 0 to COOL")
        print("----------")
        print_acs(acs)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("nom nom nom give me an IP of an AirTouch system")
        sys.exit(1)
    asyncio.run(updateInfoAndDisplay(sys.argv[1]))
