#! /usr/bin/env python

"""

 
"""
import os
import datetime
import urllib.request as urllib2

#import matplotlib as mpl
#mpl.use('Agg')
from matplotlib.pyplot import *
from optparse import OptionParser

stations = []
stations.append(['74494','Chattam']) # Chattam, MA
stations.append(['74389','Gray']) # Gray Maine
stations.append(['72518','Albany']) # ALbany NY
stations.append(['04417','Summit']) # Summit, Greenland
stations.append(['89009','SouthPole']) # Summit, Greenland


basedir = "/pwv_plots/"
basedir = os.path.join(os.path.dirname(__file__), 'pwv_plots')
os.makedirs(basedir, exist_ok=True)

def system_except(cmd):
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("Command '%s' returned non-zero exit status %d" %(cmd, ret))

def get_wvr_data(stationId = 0, date=None):
    """
    stationId = 0, 1, 2
    date = '20150501' or nothng for now
    """
    station = stations[stationId]
    
    if date != None:
        now = datetime.datetime.strptime(date,'%Y%m%d')
    else:
        now = datetime.datetime.now()
        
    today =('%s'%now)[0:10]
    month = '%02d'%int(now.month)
    year = now.year
    lastday = now.day
    #print(today, month, year, lastday)

    urlbase = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST'
    url = '%s&YEAR=%s&MONTH=%s&FROM=all&TO=%s12&STNM=%s'\
          %(urlbase,year,month,lastday,station[0])
    print(url)

    # read files
    content = str(urllib2.urlopen(url).read())
    lines = content.split('\\n')
    datetimelist = []
    valuelist = []
    nlines = np.size(lines)
    newline = 0

    # parse the content of latest content
    for i in range(nlines):
        line = lines[i]
        if ("Observation time" in line):
            sline = line.split(':')
            day  = sline[1][5:7]
            hr =  sline[1][8:10]
            dt = datetime.datetime(int(year),int(month),int(day),int(hr),0,0)
            datetimelist.append(dt)
            newline = i

        if "Precipitable water" in line:
            sline = line.split(':')
            pwv = float(sline[1])
            valuelist.append(pwv)
            newline = 0
        
        if (newline != 0) and i > newline+30:
            #print datetimelist[-1],newline, i
            newline = 0
            datetimelist.pop()

    return {'datetime': datetimelist, 'value': valuelist, 'station':station}
  
def plot_pwv(d):

    t= d['datetime']
    pwv = d['value'] 
    station = d['station']
    year = d['datetime'][0].year
    month = int(d['datetime'][0].month)

    # make a plot for this month and save
    plf = figure()
    subpl = plf.add_subplot(1, 1, 1)
    subpl.plot_date(t,pwv,'.-')
    subpl.set_title('PWV from %s radio-sonde data for %s-%02d'%(station[1],year,month))
    subpl.set_xticklabels(\
                          [litem.get_text() for litem in subpl.get_xticklabels()], \
                          fontsize='small', rotation=30, ha='right')
    subpl.set_ylabel('PWV [mm]')
    subpl.xaxis.set_major_formatter(\
                                    matplotlib.dates.DateFormatter('%m-%d'))
    subpl.yaxis.set_major_formatter( \
                                     matplotlib.ticker.ScalarFormatter(useOffset=False))
    subpl.grid()
    ylim([0,50])
    xl = xlim()
    xlim([xl[0]-1,xl[0]+32])
   
    savefig('%s/PWV_%s%02d_%s_lin.png'%(basedir,year,month,station[0]))
    ylim([0.1,100])
    yscale('log')
    savefig('%s/PWV_%s%02d_%s_log.png'%(basedir,year,month,station[0]))

def mod_index():
        
        print("### Modifying html/index.html ...")

        now = datetime.datetime.now()
        today =('%s'%now)[0:10]

        datelist = get_datelist()
        latest = datelist[-1]
        platest = datelist[-2]
        print(latest, platest)
        system_except('mv %s/index.html %s/index.html.bak'%(basedir,basedir))
        
        f = open('%s/index.html.bak'%(basedir),'r')
        lines = f.readlines()
        f.close()
            
        f = open('%s/index.html'%(basedir),'w')
        mostrecent = False
        for line in lines:
            if "Updated" in line:
                f.write("Updated %s \n"%today)
                continue
            if ('var pwv_fname =' in line) and (platest in line):
                f.write(line.replace(platest,latest))
                continue
            if 'var date =' in line and (platest in line):
                f.write(line.replace(platest,latest))
                continue
            if 'iframe src=' in line and (platest in line):
                f.write(line.replace(platest,latest))
                continue
            if 'javascript:set_date(\'%s\')'%latest in line:
                mostrecent = True
                f.write(line)
                print("most recent: %s"%line)
                continue
            if ('javascript:set_date(\'%s\')'%platest in line) and (mostrecent == False):
                f.write(line.replace(platest,latest))
                f.write(line)
                print("older %s"%line)
            else:
                f.write(line)
                
        f.close()
            
        return

def get_datelist():
    """
    Gets the dates for which we have plots
    
    """
    import glob
    from pylab import sort

    # gets the dates
    cwd = os.getcwd()
    os.chdir(basedir)
    files = sort(glob.glob('PWV_20????_74494_lin.png'))
    
    datelist = []
    for f in files:
        datelist.append(f.split('_')[1])

    os.chdir(cwd)
    return datelist

def get_datetime_from_isodatetime(isodatetime):
    """
    Return a datetime.datetime object for given ISO-8601 date/datetime string.

    The argument isodatetime should be in YYYY-MM-DDThh:mm:ss or YYYY-MM-DD
    (in the latter case, 00:00:00 is assumed).
    Return 0001-01-01T00:00:00 if an invalid string is given.
    """

    datelist = isodatetime.split('T')
    if len(datelist) == 1:  # date only
        timelist = [0, 0, 0]
        datelist = datelist[0].split('-')
    elif len(datelist) == 2:  # date and time
        timelist = datelist[1].split(':')
        datelist = datelist[0].split('-')
    else:
        print("Date %s is invalid." % isodatetime)
        return datetime.date(1, 1, 1)
    
    
    if (len(datelist) == 3) and (len(timelist) == 3):
        microsec = int(1e6 * (float(timelist[2]) - int(float(timelist[2]))))
        timelist[2] = int(float(timelist[2]))
        return datetime.datetime( \
            int(datelist[0]), int(datelist[1]), int(datelist[2]), \
            int(timelist[0]), int(timelist[1]), int(timelist[2]), microsec )
    else:
        print("Date '%s' is invalid." % isodatetime)
        return datetime.date(1, 1, 1)



if __name__ == '__main__':
    usage = '''
  
    '''

    #options ....
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--date",
                      dest="date",
                      type= 'string',
                      help="date for which we want to plot ther pwv. None by default")
    
    
    (options, args) = parser.parse_args()

    date = datetime.date(2024, 1, 1)
    date = date.strftime('%Y%m%d')
    print(date)
    
    for id in [4]:
        d = get_wvr_data(stationId = id, date = date)
        try:
            year = d['datetime'][0].year
            print(d)
            plot_pwv(d)
        except:
            print('plot failed for station %i, date %s' % id, date)
    #mod_index()

    #system_except('rsync -auv --progress %s /n/holylfs04/LABS/kovac_lab/www/dbarkats/'%basedir)
