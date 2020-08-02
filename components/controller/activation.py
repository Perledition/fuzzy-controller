# import standard modules

# import third party modules

# import project related modules


class PolygonGravity:

    def __init__(self, max_height=1, min_height=0):
        self.flat_side = (0, 0)
        self.max_height = max_height
        self.min_height = min_height
        self.poly = None

    @staticmethod
    def _solve_linear(y, m, intercept):
        return (y-intercept)/m, y

    def _calculate_corners(self, le, ue, cut, slope, side="left"):

        side = {"left": 0, "right": 1}[side]
        end = [le, ue][side-1]

        if self.flat_side[side] == 1:

            flat_end = lambda x: ue if x is 1 else le
            flat_point = (flat_end(side), cut)
            normal_point = (end, self.min_height)

            result = [0, 0]
            result[side] = flat_point
            result[1-side] = normal_point
            return result

        else:

            # define points be aware that there is a switch related to the right or left side
            if side is 0:
                # define intercept in order to be able to solve coordinates with linear function
                b = -(slope*le)
                lower_point = (end, self.min_height)
                upper_point = (self._solve_linear(cut, slope, b))

            else:
                # define intercept in order to be able to solve coordinates with linear function
                b = ue*slope
                upper_point = (end, self.min_height)
                lower_point = (self._solve_linear(cut, -slope, b))
            return [lower_point, upper_point]

    def _define_polygon(self, le, ue, cut, slope):

        # calculate polygon corners for the left side
        left_side = self._calculate_corners(le, ue, cut, slope, side="left")
        right_side = self._calculate_corners(le, ue, cut, slope, side="right")

        return tuple(left_side + right_side)

    def _calculate_centroid(self):
        x_list = [abs(coor[0]) for coor in self.poly]
        y_list = [abs(coor[1]) for coor in self.poly]
        _len = len(self.poly)

        x = sum(x_list) / _len
        y = sum(y_list) / _len

        return (x, y)

    def get_centroid(self, lower_end, upper_end, cut, slope, flat_side=(0, 0)):

        # overwirte flat_side to see whether some calculations can be ignored
        self.flat_side = flat_side
        self.poly = self._define_polygon(lower_end, upper_end, cut, slope)

        assert len(self.poly) >= 4, f"only {len(self.poly)} points found, it's not enought for a polygon"
        return self._calculate_centroid()