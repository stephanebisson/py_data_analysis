
class Table(object):
    
    LINE_SEPARATOR = '\n'
    COLUMN_SEPARATOR = '\t'
    
    def __init__(self, content=None):
        if content:
            self.__load_content(content.split(self.LINE_SEPARATOR))
        
    def __load_content(self, lines):
        self.header_spec = self.__build_headers_spec(self.__split_line(lines[0]))
        print "the headers are:"
        print self.get_headers()
        self.rows = [TableRow(self.header_spec, self.__split_line(line)) for line in lines[1:] if line is not None and len(line.strip()) > 0]
        print "loaded %d rows" % len(self.rows)
        
    def __build_headers_spec(self, headers):
        spec = {}
        for i, header in enumerate(headers):
            spec[header] = i
        return spec
        
    def __split_line(self, line):
        line = line.strip()
        return [l for l in line.split(self.COLUMN_SEPARATOR) if l is not None]
        
    def get_headers(self):
        h2 = {}
        for k, v in self.header_spec.items():
            h2[v] = k
        parts = []
        for i in range(len(h2.keys())):
            parts.append(h2[i])
        return parts
        
    def load(self, filename):
        with open(filename, 'r') as f:
            self.__load_content(f.readlines())
            
    def save(self, filename, headers=None):
        with open(filename, 'w') as f:
            if headers is None: headers = range(len(self.header_spec.keys()))
            
            ordered_headers = []
            all_headers = self.get_headers()
            for h in headers:
                ordered_headers.append(all_headers[h])
            f.write(self.COLUMN_SEPARATOR.join(ordered_headers) + self.LINE_SEPARATOR)
                
            for row in self.rows:
                line_elements = row.elements
                ordered_line_elements = []
                for h in headers:
                    ordered_line_elements.append(line_elements[h])
                f.write(self.COLUMN_SEPARATOR.join(ordered_line_elements) + self.LINE_SEPARATOR)

class TableRow(object):
    def __init__(self, header_spec, elements):
        self.header_spec = header_spec
        self.elements = elements
        
    def __get_header_index(self, header_name):
        for k, v in self.header_spec.items():
            if k.upper() == header_name.upper(): return v
        
    def __getattr__(self, name):
        index = self.__get_header_index(name.strip('_'))
        return self.elements[index].strip()
        
    def set(self, column_name, value):
        index = self.__get_header_index(column_name.strip('_'))
        self.elements[index] = value
        
    def __str__(self):
        return str(self.elements)
        

import unittest

class TableTests(unittest.TestCase):
    
    def setUp(self):
        self.table1 = Table( \
"""numero\tNAME
1\tjoe
2\tcool
""")
    
    def test_read_a_value(self):
        self.assertEqual("1", self.table1.rows[0].numero)
        self.assertEqual("joe", self.table1.rows[0].name)
        self.assertEqual("2", self.table1.rows[1].NUMERO)
        self.assertEqual("cool", self.table1.rows[1].NAME)
        
    def test_read_with_underscores(self):
        self.assertEqual("1", self.table1.rows[0]._numero)
        self.assertEqual("joe", self.table1.rows[0].name_)
        self.assertEqual("2", self.table1.rows[1]._NUMERO)
        self.assertEqual("cool", self.table1.rows[1]._NAME_______)
        
    def test_load_from_file(self):
        with open('temp.temp', 'w') as out:
            out.write('col1\tcol2\tcol3\n')
            out.write('aa\tbb\tcc\n')
            out.write('111\t222\t333\n')
        table = Table()
        table.load('temp.temp')
        self.assertEqual('333', table.rows[1].col3)
        self.assertEqual(2, len(table.rows))
        
        self.assertEqual(2, len(self.table1.rows))
        
    def test_save_to_file(self):
        self.table1.save('temp2.temp')
        
        table2 = Table()
        table2.load('temp2.temp')
        
        self.assertEqual("1", table2.rows[0].numero)
        self.assertEqual("joe", table2.rows[0].name)
        self.assertEqual("2", table2.rows[1].NUMERO)
        self.assertEqual("cool", table2.rows[1].NAME)
        
    def test_save_some_columns(self):
        temp_filename = 'temp3.temp'
        self.table1.save(temp_filename, headers=[1])
        table = Table()
        table.load(temp_filename)
        self.assertEqual({'NAME':0}, table.header_spec)
        self.assertEqual(["joe"], table.rows[0].elements)
        self.assertEqual(["cool"], table.rows[1].elements)
        
    def test_change_a_value(self):
        row = TableRow({'FIRST':0, 'SECOND': 1}, ["allo", "bye"])
        self.assertEqual("allo", row.first)
        self.assertEqual("bye", row.second)
        
        row.set("first", "coucou")
        self.assertEqual("coucou", row.first)
        
        row.set("second", row.second + " hey ho")
        self.assertEqual("bye hey ho", row.second)
                
        