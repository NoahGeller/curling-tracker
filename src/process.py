import sys
from datetime import timedelta
import csv
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def make_csv(input_name):
    """
    Parse an ASCII file and duplicate it in .csv format, returning the name of
    the new file.
    """
    new_name = input_name.split('.')[0] + '.csv'
    with open(input_name, 'r') as input_file:
        with open(new_name, 'w', newline='') as output_file:
            output_writer = csv.writer(output_file)
            for line in input_file:
                current_pair = line.split(' -> ')
                current_pair[1] = current_pair[1][:-1]
                output_writer.writerow(current_pair);
    return new_name


def parse_csv(csv_file):
    """
    Parse a .csv file and return a pair of lists of times and positions.
    The times are stored as ints in units of milliseconds, and the positions
    are stored as ints in units of centimeters.

    Since we have two imprecise position samples per time, we store the average
    of the two.
    """
    raw_times = []
    raw_pos = []
    with open(csv_file, 'r', newline='') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            raw_times.append(row[0])
            raw_pos.append(row[1])

    times = []
    for t in raw_times:
        hms = t.split(':')
        seconds_milli = hms[2].split('.')
        delta = timedelta(
                    hours=int(hms[0]),
                    minutes=int(hms[1]),
                    seconds=int(seconds_milli[0]),
                    milliseconds=int(seconds_milli[1]),
                )
        times.append(int(delta / timedelta(milliseconds=1)))
    start_time = times[0]
    times = [t-start_time for t in times]

    pos = []
    for p in raw_pos:
        pos.append(int(p[:-3]))

    return (np.array(times), np.array(pos))


def func(x, m, b):
    return m * x + b


def fit_to_curve(times, xpos):
    e = np.repeat(1., times.shape[0])
    popt, pcov = curve_fit(func, times, xpos, sigma=e)
    p = func(times, *popt)
    plt.plot(times, p, 'r-')
    return popt[0]


def main():
    if len(sys.argv) == 1:
        print("Need to supply input file(s).")
        return

    for filename in sys.argv[1:]:
        csv_file = make_csv(filename)
        times, xpos = parse_csv(csv_file)
        times, xpos = times[:-5], np.gradient(xpos[:-5])
        prediction = fit_to_curve(times, xpos)
        plt.plot(times, xpos)
        plt.show()


if __name__ == "__main__":
    main()
