import re

from app.lib import helpers

HUNK_REGEX = re.compile(r'@@ -([\d]*),([\d]*) \+([\d]*),([\d]*) @@')


class Chunk(object):
    """
    A Chunk is a collection of source code lines reflecting a change from one
    iteration a code block to another. Chunk lines beginning with a '+' denote
    a line that did not exist in the base file and was added in the new file.
    Similarly, Chunk lines beginning with a '-' denote a line that exists in
    the base file and is not present in the new file.

    The key aspect of a Chunk is the header, or Hunk. Hunks are assumed to be
    in the default form: @@ -A,B +C,D @@
        A: The line number of the first line in the Chunk with respect to
           the base file.
        B: The number of lines in the Chunk with respect to the base file.
        C: The line number of the first line in the Chunk with respect to
           the new file.
        D: The number of lines in the Chunk with respect to the new file.
    """
    def __init__(self, chunk_lines):
        """
        The first element in the given chunk_lines is the Hunk line, which is
        preserved as self.raw_hunk. Any text following @@ -A,B +C,D @@ in the
        Hunk line is discarded as it is unnecessary. The remaining lines in the
        given chunk_lines are saved as values in a dictionary. Each line's key
        is an integer representing the source code line number of that line in
        the new file.
        """
        self.raw_hunk = re.split(r'(@@[^@]*@@)', chunk_lines[0])[1]
        # [A, B, C, D]
        self.hunk = self.__parse_hunk(self.raw_hunk)

        self.lines = {}
        for i, line in helpers.enumerate_iter(chunk_lines[1:], offset=self.hunk[2]):
            self.lines[i] = line

    def get_raw_hunk(self):
        return self.raw_hunk

    def get_hunk(self):
        return self.hunk

    def get_base_hunk(self):
        return self.hunk[:2]

    def get_lines(self):
        return self.lines

    def __parse_hunk(self, raw_hunk):
        hunk_list = list(HUNK_REGEX.search(raw_hunk).groups())
        return list(map(int, hunk_list))


class Patch(object):
    """
    A Patch is a collection of Chunks. The start of each Chunk is denoted by
    a Hunk of the form: @@ -A,B + C,D @@.
    """
    def __init__(self, patch_str):
        self.patch = patch_str

        self.lines = self.patch.split("\n")
        if self.lines[-1] == "":
            self.lines = self.lines[:-1] # Remove trailing empty line

        self.chunks = []
        temp = []
        for line in self.lines:
            if line[:2] == "@@" and len(temp) == 0:
                temp.append(line)
            elif line[:2] == "@@" and len(temp) != 0:
                self.chunks.append(Chunk(temp))
                temp = [line]
            elif line[:2] != "@@" and len(temp) == 0:
                pass
            else:
                temp.append(line)
        self.chunks.append(Chunk(temp))

    def get_patch(self):
        return self.patch

    def get_lines(self):
        return self.lines

    def get_chunks(self):
        return self.chunks

    def get_hunks(self):
        return [h.get_hunk() for h in self.chunks]

    def get_chunk_by_line(self, line_number):
        for chunk in self.chunks:
            if line_number in chunk.get_lines().keys():
                return chunk
        return None
