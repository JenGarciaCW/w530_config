#!/usr/bin/env python
import subprocess
import time
import calendar
import json
import re
from datetime import datetime


normal_background = '#121212'
normal_color = '#FFFFFF'
set_background = '#FFDE03'
set_color = '#000000'
warn_background = ''
warn_color = ''
danger_background = ''
danger_color = ''

example_dict = {
    "full_text": "E: 10.0.0.1 (1000 Mbit/s)",
    "short_text": "10.0.0.1",
    "color": "#00ff00",
    "background": "#1c1c1c",
    "border": "#ee0000",
    "border_top": 1,
    "border_right": 0,
    "border_bottom": 3,
    "border_left": 1,
    "min_width": 300,
    "align": "right",
    "urgent": False,
    "name": "ethernet",
    "instance": "eth0",
    "separator": True,
    "separator_block_width": 9,
    "markup": None
}

def parse_sensors():
    sensors_lines = subprocess.check_output('sensors', shell=True).splitlines()
    sensors_dict = dict()
    for line in sensors_lines:
        if 'Physical' in line:
            temp_regex = r'^\s*Physical.*:\s+\+(\d+.\d+).*\s+\(high\s+=\s+\+(\d+.\d+).*,\s+crit\s+=\s+\+?(\d+.\d+).*\)'
            result = re.match(temp_regex, line)
            if result:
                sensors_dict['temp'] = result.group(1)
                sensors_dict['high'] = result.group(2)
                sensors_dict['crit'] = result.group(3)
                result.groups()
        elif 'fan' in line:
            fan_regex = r'fan\d+:\s+(\d+\s+RPM)'
            result = re.match(fan_regex, line)
            if result:
                sensors_dict['fan'] = result.group(1)
    return sensors_dict

def parse_mem(line, mem_str):
    mem_regex = r'^\s*{}:\s+(\d+)\s+(\d+)\s+(\d+).*$'.format(mem_str)
    result = re.match(mem_regex, line)
    ret_dict = dict()
    if result:
        ret_dict['total'] = result.group(1)
        ret_dict['used'] = result.group(2)
        ret_dict['free'] = result.group(3)
    return ret_dict

def parse_ifconfig(interface):
    ifconfig_lines = subprocess.check_output('/sbin/ifconfig {}'.format(interface), shell=True).splitlines()
    ifconfig_dict = {"status": False}
    for line in ifconfig_lines:
        if 'flags' in line:
            flags_regex = r'^[^\s]*:\s+flags=\d+<(.*)>\s.*$'
            result = re.match(flags_regex, line)
            if result:
                if 'RUNNING' in result.group(1):
                    ifconfig_dict["status"] = True

        elif ('inet' in line) and (ifconfig_dict["status"]):
            ip_regex = r'^\s+inet (\d+.\d+.\d+.\d+).*$'
            result = re.match(ip_regex, line)
            if result:
                ifconfig_dict['ip'] = result.group(1)

        elif ('packets' in line) and (ifconfig_dict["status"]):
            status_regex = r'^\s+(.X)\s+packets\s+(\d+).*\((\d+.\d\s.*)\).*$'
            result = re.match(status_regex, line)
            if result:
                ifconfig_dict[result.group(1)] = {"packets": result.group(2), "bytes": result.group(3)}

    return ifconfig_dict

def parse_leds():
    pass

def parse_hdd():
    df_lines = subprocess.check_output('df', shell=True).splitlines()
    df_dict = dict()
    for line in df_lines:
        if '/dev/' in line:
            temp_regex = r'\/dev.*?\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+%)\s(\/\w*)\s*$'
            result = re.match(temp_regex, line)
            if result:
                if result.group(5) is '/':
                    key = 'root'
                elif 'home' in result.group(5):
                    key = 'home'
                else:
                    key = None

                if key:
                    df_dict[key] = {
                        "blocks": result.group(1),
                        "used": result.group(2),
                        "available": result.group(3),
                        "use": result.group(4)
                    }


    return df_dict               #sensors_dict['temp'] = result.group(1)


def get_value(key, line):
    element_regex = r'^\s+{}:\s+(.+)\s*$'.format(key)
    result = re.match(element_regex, line)
    if result:
        return result.group(1)

def parse_bat():
    bat_lines = subprocess.check_output('upower -i /org/freedesktop/UPower/devices/battery_BAT0', shell=True).splitlines()
    bat_data = dict()
    for line in bat_lines:
        if 'state' in line:
            bat_data['state'] = get_value('state', line)
        elif 'capacity' in line:
            bat_data['capacity'] = float(get_value('capacity', line).replace('%', ''))
        elif 'energy:' in line:
            bat_data['energy'] = float(get_value('energy', line).replace('Wh', ''))
        elif 'energy-full:' in line:
            bat_data['energy-full'] = float(get_value('energy-full', line).replace('Wh', ''))
        elif 'energy-rate:' in line:
            bat_data['energy-rate'] = float(get_value('energy-rate', line).replace('W', ''))
    return bat_data

def get_caps_status(leds_dict):
    caps_status_dict = {
        "name": "caps",
        "full_text": " CAPS ",
        "short_text": "CAPS",
        "separator": True
    }
    # Check led array in string 1 is set 0 is unset
    if subprocess.check_output('xset q | grep LED', shell=True)[65] is '1':
        caps_status_dict["color"] = set_color
        caps_status_dict["background"] = set_background
    else:
        caps_status_dict["color"] = normal_color
        caps_status_dict["background"] = normal_background

    return caps_status_dict

def get_num_status(leds_dict):
    num_status_dict = {
        "name": "num",
        "full_text": " NUM ",
        "short_text": "NUM",
        "separator": True
    }
    num_status_dict["background"] = normal_background

    return num_status_dict

def get_scroll_status(leds_dict):
    scroll_status_dict = {
        "name": "num",
        "full_text": " NUM ",
        "short_text": "NUM",
        "separator": True
    }
    scroll_status_dict["background"] = normal_background

    return scroll_status_dict

def get_fan_status():
    pass

def get_wifi_status():
    pass

def get_eth_status():
    pass

def get_mem_status():
    free_lines = subprocess.check_output('free', shell=True).splitlines()
    free_dict = dict()
    for line in free_lines:
        if 'Mem' in line:
            free_dict['mem'] = parse_mem(line, 'Mem')
        elif 'Swap' in line:
            free_dict['swap'] = parse_mem(line, 'Swap')
    print free_dict
    mem_status_dict = {
    "full_text": "E: 10.0.0.1 (1000 Mbit/s)",
    "short_text": "10.0.0.1",
    "color": "#00ff00",
    "background": "#1c1c1c",
    "border": "#ee0000",
    "border_top": 1,
    "border_right": 0,
    "border_bottom": 3,
    "border_left": 1,
    "min_width": 300,
    "align": "right",
    "urgent": False,
    "name": "ethernet",
    "instance": "eth0",
    "separator": True,
    "separator_block_width": 9,
    "markup": None
}
    return mem_status_dict

def get_hdd_status():
    pass

def get_cpu_load_status():
    pass

def get_cpu_temp_status():
    pass

def get_batt_status():
    bat_data = parse_bat()
    percentage = bat_data['energy']/bat_data['energy-full']*bat_data['capacity']
    bat_color = normal_color
    bat_back = normal_background

    if 'discharging' in bat_data['state']:
        status = 'BAT'
        time = bat_data['energy'] / bat_data['energy-rate']
        if time < 1 and time >= 0.5:
            bat_color = warn_color
            bat_back = warn_background
        elif time < 0.5:
            bat_color = danger_color
            bat_back = danger_background

    else:
        status = 'CHR'
        time = (bat_data['energy-full'] - bat_data['energy'])/bat_data['energy-rate']

    hours = int(time)
    minutes = int((time * 60) % 60)
    seconds = int((time * 3600) % 60)

    bat_status_dict = {
        "full_text": "%s %0.2f%c %02d:%02d:%02d" % (status, round(percentage, 2), '%', hours, minutes, seconds),
        "short_text": "%s %d%c %02d:%02d" % (status[0], int(percentage), '%', hours, minutes),
        "color": bat_color,
        "background": bat_back,
        "name": "battery",
        "separator": True,
    }
    return bat_status_dict

def get_date(now):
    date = "{} {}, {}".format(calendar.month_abbr[now.month], now.day, now.year)
    short_date = "{}/{}/{}".format(now.day, now.month, str(now.year)[2:])

    date_dict = {
        "full_text": date,
        "short_text": short_date,
        "color": normal_color,
        "background": normal_background,
        "name": "date",
        "separator": True,
    }

    return date_dict


def get_hour(now):
    hour = now.strftime('%I:%M:%S %p')
    short_hour = now.strftime('%H:%M')
    hour_dict = {
        "full_text": hour,
        "short_text": short_hour,
        "color": normal_color,
        "background": normal_background,
        "name": "hour",
        "separator": True,
    }

    return hour_dict


def main():
    sensors_data = parse_sensors()
    ethr_data = parse_ifconfig('enp0s25')
    wifi_data = parse_ifconfig('wlp3s0')
    hdd_data = parse_hdd()
    # print hdd_data
    # print get_mem_status()
    # print ethr_data
    # print wifi_data
    # print sensors_data
    print '{ "version": 1 }'
    print '['
    print '[]'
    while True:
        now = datetime.now()
        status_list = list()
        status_list.append(get_caps_status(""))
        status_list.append(get_batt_status())
        status_list.append(get_date(now))
        status_list.append(get_hour(now))
        print ',{}'.format(json.dumps(status_list))
        time.sleep(1)


if __name__ == '__main__':
    main()