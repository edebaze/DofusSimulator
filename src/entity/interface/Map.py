from globals import *


class Map:
    def create(self):
        """
                create the map
            :return:
            """
        global x, y, map
        x = 0
        y = 0

        # -- clean canvas
        can.delete(ALL)

        # -- define map matrix
        map = []
        while y < MAP_HEIGHT:
            map.append(self.create_rectangles_coord(y))
            y = y + BOX_DIM

        # ---------------------------------------------------------------------------
        # TRACE BOXES
        # -- first part
        a = 0
        while a < NUM_BOX_WIDTH:
            al = map[a]
            b = 0
            while b < NUM_BOX_HEIGHT:
                al1 = al[b]
                can.create_rectangle(al1[0], al1[1], al1[2], al1[3], fill='grey')
                b += 2
            a += 2

        # -- second part
        a = 1
        while a < NUM_BOX_WIDTH:
            al = map[a]
            b = 1
            while b < NUM_BOX_HEIGHT:
                al1 = al[b]
                can.create_rectangle(al1[0], al1[+1], al1[2], al1[3], fill='grey')
                b = b + 2
            a = a + 2

        can.pack()

    # __________________________________________________________________________________________________________________
    @staticmethod
    def create_rectangles_coord(y):
        x = 0
        liste = []
        while x < MAP_WIDTH:
            liste.append([x, y, x + BOX_DIM, y + BOX_DIM])
            x = x + BOX_DIM
        return liste