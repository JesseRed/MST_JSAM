import numpy as np
import matplotlib.pyplot as plt
import seaborn
import matplotlib.style
import matplotlib as mpl

def set_axis_style(ax, data1, data2, labels=''):
    major_labels = ['']*12
    ax.get_xaxis().set_tick_params(direction='out', which = 'major')
    ax.get_yaxis().set_tick_params(direction='in', which = 'minor', length=0.0, width = 0.0, color= 'r')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_yticks(np.arange(1, len(labels) + 1))
    ax.set_yticks(np.arange(0.5, len(labels) + 0.5), minor=True)
    ax.set_yticklabels(major_labels, minor=False)
    ax.set_yticklabels(labels, minor=True)

    ax.set_ylim(0, len(labels))
    xmax = max(np.max(np.max(data1,0)),np.max(np.max(data2,0)) )
    ax.set_xlim(-0.1, xmax+2)

def my_violinplot(data1, data2):
    """Violin plot
    
    Arguments:
        data1 {[list of lists]} -- liste ueber die Probanden mit darin listen ueber Bloecke
        data2 {[list of lists]} -- liste ueber die Probanden mit darin listen ueber Bloecke
    """    
    data1 = np.asarray(data1)
    data2 = np.asarray(data2)
    mpl.rcParams['figure.figsize'] = [8.0, 6.0]
    mpl.rcParams['figure.dpi'] = 80
    mpl.rcParams['savefig.dpi'] = 100

    mpl.rcParams['font.size'] = 12
    mpl.rcParams['legend.fontsize'] = 'large'
    mpl.rcParams['figure.titlesize'] = 'medium'
    #fs = 10  # fontsize

    posya1 = np.linspace(0.4,11.4,12)
    pos1 = list(posya1)
    posya2 = np.linspace(0.6,11.6,12)
    pos2 = list(posya2)
    legendpos = list(np.linspace(1,12,12).astype(np.uint8))
   
    #plt.subplots(nrows=1, ncols=1, figsize=(6, 6))
    fig = plt.figure(figsize=(8,12))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.1,0.1,0.9,0.9])
    ax.set_title('my violon plot')
    ax.set_ylabel('blocks')
    ax.set_xlabel('corr sequences')
    ax.grid(axis = 'y', which='major', color = 'k', linewidth=.5, linestyle = ':')

    bp1 = ax.violinplot(data1, pos1, vert=False, widths=0.7,
                        showmeans=False, showextrema=True, showmedians=False)
    bp2 = ax.violinplot(data2, pos2, vert=False, widths=0.7,
                        showmeans=False, showextrema=True, showmedians=False)
    for p in bp2['bodies']:
        p.set_facecolor('grey')
    set_axis_style(ax, data1, data2, labels = legendpos)
    #bp.set_title('my violin plot')
    #plt.set_title('Custom violinplot 1', fontsize=fs)

    # quartile1, medians, quartile3 = np.percentile(data1.T, [25, 50, 75], axis=1)
    # whiskers = np.array([
    #     adjacent_values(sorted_array, q1, q3)
    #     for sorted_array, q1, q3 in zip(data1, quartile1, quartile3)])
    # whiskersMin, whiskersMax = whiskers[:, 0], whiskers[:, 1]


    ax.scatter(np.mean(data1,0), posya1, marker='o', color='black', s=40, zorder=3)
    #ax.scatter(np.median(data1,0), posya1, marker='v', color='black', s=30, zorder=3)
    ax.scatter(np.mean(data2,0), posya2, marker='o', color='black', s=40, zorder=3)
    #ax.scatter(np.median(data2,0), posya2, marker='v', color='black', s=30, zorder=3)

    #ax.hlines(inds, quartile1, quartile3, color='k', linestyle='-', lw=5)
    #ax.hlines(inds, whiskersMin, whiskersMax, color='k', linestyle='-', lw=1)

    #loesche oben
    for index,b in enumerate(bp1['bodies']):
        m = np.mean(b.get_paths()[0].vertices[:, 1])
        b.get_paths()[0].vertices[:, 1] = np.clip(b.get_paths()[0].vertices[:, 1], np.NINF, m)
        b.set_color('b')

    for index,b in enumerate(bp2['bodies']):
        m = np.mean(b.get_paths()[0].vertices[:, 1])
        b.get_paths()[0].vertices[:, 1] = np.clip(b.get_paths()[0].vertices[:, 1], m, np.inf)
        b.set_color('r')

    #plt.axvline(x=0.0, color='black', lw = 2)
    #plt.suptitle("Violin Plotting Examples")
    #plt.subplots_adjust(hspace=0.4)
    #plt.setp(plt,marker='+')
    plt.show()



    
def my_forestplot(data1, data2):
    """Forest plot
    
    Arguments:
        data1 {[list of lists]} -- liste ueber die Probanden mit darin listen ueber Bloecke
        data2 {[list of lists]} -- liste ueber die Probanden mit darin listen ueber Bloecke
    """    
    data1 = np.asarray(data1)
    data2 = np.asarray(data2)
    mpl.rcParams['figure.figsize'] = [8.0, 6.0]
    mpl.rcParams['figure.dpi'] = 80
    mpl.rcParams['savefig.dpi'] = 100

    mpl.rcParams['font.size'] = 12
    mpl.rcParams['legend.fontsize'] = 'large'
    mpl.rcParams['figure.titlesize'] = 'medium'
    #fs = 10  # fontsize

    posya1 = np.linspace(0.4,11.4,12)
    pos1 = list(posya1)
    posya2 = np.linspace(0.6,11.6,12)
    pos2 = list(posya2)
    legendpos = list(np.linspace(1,12,12).astype(np.uint8))
   
    #plt.subplots(nrows=1, ncols=1, figsize=(6, 6))
    fig = plt.figure(figsize=(8,12))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.1,0.1,0.9,0.9])
    ax.set_title('my violon plot')
    ax.set_ylabel('blocks')
    ax.set_xlabel('corr sequences')
    ax.grid(axis = 'y', which='major', color = 'k', linewidth=.5, linestyle = ':')

    bp1 = ax.violinplot(data1, pos1, vert=False, widths=0.7,
                        showmeans=False, showextrema=True, showmedians=False)
    bp2 = ax.violinplot(data2, pos2, vert=False, widths=0.7,
                        showmeans=False, showextrema=True, showmedians=False)
    for p in bp2['bodies']:
        p.set_facecolor('grey')
    set_axis_style(ax, data1, data2, labels = legendpos)
    #bp.set_title('my violin plot')
    #plt.set_title('Custom violinplot 1', fontsize=fs)

    # quartile1, medians, quartile3 = np.percentile(data1.T, [25, 50, 75], axis=1)
    # whiskers = np.array([
    #     adjacent_values(sorted_array, q1, q3)
    #     for sorted_array, q1, q3 in zip(data1, quartile1, quartile3)])
    # whiskersMin, whiskersMax = whiskers[:, 0], whiskers[:, 1]


    ax.scatter(np.mean(data1,0), posya1, marker='o', color='black', s=40, zorder=3)
    #ax.scatter(np.median(data1,0), posya1, marker='v', color='black', s=30, zorder=3)
    ax.scatter(np.mean(data2,0), posya2, marker='o', color='black', s=40, zorder=3)
    #ax.scatter(np.median(data2,0), posya2, marker='v', color='black', s=30, zorder=3)

    #ax.hlines(inds, quartile1, quartile3, color='k', linestyle='-', lw=5)
    #ax.hlines(inds, whiskersMin, whiskersMax, color='k', linestyle='-', lw=1)

    #loesche oben
    for index,b in enumerate(bp1['bodies']):
        m = np.mean(b.get_paths()[0].vertices[:, 1])
        b.get_paths()[0].vertices[:, 1] = np.clip(b.get_paths()[0].vertices[:, 1], np.NINF, m)
        b.set_color('b')

    for index,b in enumerate(bp2['bodies']):
        m = np.mean(b.get_paths()[0].vertices[:, 1])
        b.get_paths()[0].vertices[:, 1] = np.clip(b.get_paths()[0].vertices[:, 1], m, np.inf)
        b.set_color('r')

    #plt.axvline(x=0.0, color='black', lw = 2)
    #plt.suptitle("Violin Plotting Examples")
    #plt.subplots_adjust(hspace=0.4)
    #plt.setp(plt,marker='+')
    plt.show()