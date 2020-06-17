"""
spreadsheet.py

implements a basic spreadsheet with column and row references
"""
import csv

def read_cell(v):
    try:
        v = float(v)
        if v == int(v):
            return int(v)
        return float(v)
    except:
        return v

class SpreadsheetRow(object):
    """implements a single row within a spreadsheet
    """
    def __init__(self, colmap, row):
        self.colmap = colmap
        self.row    = row

    def __getitem__(self, v):
        """get a cell number, or a column name
        """
        if type(v) == int:
            return self.row[v]
        elif v in self.colmap:
            index = self.colmap[v]
            return self.row[index]
        raise Exception("No such column name or row index in spreadsheet row: " + str(v))

class Spreadsheet(object):
    def __init__(self, header, rows):
        self.header = [h for h in header]
        self.colmap = { }
        for i in xrange(len(self.header)):
            self.colmap[self.header[i]] = i
        self.rows   = [SpreadsheetRow(self.colmap, r) for r in rows]

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, v):
        """get a row number, or a column name
        """
        if type(v) == int:
            return self.rows[v]
        elif v in self.colmap:
            index  = self.colmap[v]
            column = [ row[index] for row in self.rows ]
            return column
        raise Exception("No such column name or row number in Spreadsheet")

    @staticmethod
    def read_csv(fname,header=True,*args,**kwargs):
        """reads in a spreadsheet from a csv file
        """
        with open(fname, 'r') as f:
            reader = csv.reader(f,*args,**kwargs)
            rows   = [ ]
            for row in reader:
                if header is True:
                    header = row
                else:
                    row = [ read_cell(v) for v in row ]
                    rows.append(row)
                    
            return Spreadsheet(header, rows)
