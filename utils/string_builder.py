from io import StringIO

class StringBuilder:
     _file_str = None

     def __init__(self, string: str = None):
         self._file_str = StringIO(string)

     def AppendLine(self, string: str):
         self._file_str.write(string)
         self._file_str.write("\n")

     def Append(self, string: str):
         self._file_str.write(string)

     def Build(self):
        return self._file_str.getvalue()

     def __str__(self):
         return self._file_str.getvalue()