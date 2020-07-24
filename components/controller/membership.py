# import standard modules
import warnings

# import third party modules

# import project related modules
# from matplotlib import pyplot as plt


# assumes static gradients / slope
# TODO: Documentation
# TODO: get visuals
class MembershipValidator(object):

    def __init__(self, category: dict, category_name="undefined", is_output=False):
        self.category = category
        self.category_name = category_name
        self.is_output = is_output

        self.max, self.min = self._find_interval()
        self._category_normalizer()
        self.slopes = self._get_slopes()

    def _value_normalizer(self, value: float):
        # use a min max normalizer to center the values around 0 and 1
        return (value - self.min)/(self.max-self.min)

    def denormalize_value(self, value: float):
        # denormalize values to get exact values within the given range
        return ((self.max - self.min) * value) + self.min

    def _category_normalizer(self):
        for member, ranges in self.category.items():
            for key, value in ranges.items():
                ranges[key] = self._value_normalizer(value)

    @staticmethod
    def _is_flat(le: float, cen: float, ue: float):
        if (le == cen) or (cen == ue):
            return True
        else:
            return False

    def get_member_coordinates(self, member_name: str):
        assert self.is_output is True, "coordinates are only available for memberships declared as output"

        try:
            member = self.category[member_name]
            if member["lower_end"] == member["center"]:
                return (member["center"], 0), (member["center"], 1), (member["upper_end"], 0), (1, 0)
            elif member["center"] == member["upper_end"]:
                return (member["lower_end"], 0), (member["upper_end"], 1), (member["upper_end"], 0), (0, 1)
            else:
                return (member["lower_end"], 0), (member["center"], 1), (member["upper_end"], 0), (0, 0)

        except KeyError as exc:
            warnings.warn(f"{member_name} is not a valid member of {self.category_name}: {exc}")
            return (), (), ()

    @staticmethod
    def is_smaller(curr: float, new: float):
        return True if new < curr else False

    @staticmethod
    def is_larger(curr: float, new: float):
        return True if new > curr else False

    def _find_interval(self):

        # initialize default values for max and min
        value_max = 0
        value_min = 0

        # loop over the complete category to find the max and min values
        for _, ranges in self.category.items():

            # check for new min value
            if self.is_smaller(value_min, ranges["lower_end"]):
                value_min = ranges["lower_end"]

            # check for new max value
            if self.is_larger(value_max, ranges["upper_end"]):
                value_max = ranges["upper_end"]

        return value_max, value_min

    def _get_slopes(self):

        # set up an empty dict as return value
        slopes = dict()

        # iterate over each member in the given category to define the slope
        for function, values in self.category.items():
            try:

                # access the values from the category
                min_value = self._value_normalizer(values["lower_end"])
                max_value = self._value_normalizer(values["center"])
                upper_min_value = self._value_normalizer(values["upper_end"])

                # calculate the lower the slope m for the given values
                # ASSUMPTION: linear without slope change and lower_end is 0 on y axis while center is 1 on y axis
                # slope = delta y / delta x
                if min_value == max_value:
                    m = -1 * (0 - 1) / (max_value - upper_min_value)
                else:
                    m = (1-0)/(max_value-min_value)

                slopes[function] = m

            except (KeyError, ZeroDivisionError) as exc:

                # hand out warnings to the user, that a problem was found within the configuration and assign value
                # to keep the program running
                msg = f"{exc} error found for function {function} in subset of values:"
                warnings.warn(msg)
                warnings.warn(self.category[function])
                warnings.warn("slope of 0.5 was assigned - this can break the overall system efficiency!")
                warnings.warn("fix the inputs to make sure the controller works properly")
                slopes[function] = 0.5

        return slopes

    def _calculate_membership(self, function: str, value: float):
        try:
            # get slope, center and borders for the given function
            m = self.slopes[function]
            lower_border = self.category[function]["lower_end"]
            center = self.category[function]["center"]
            upper_border = self.category[function]["upper_end"]

            # make sure the value lays within the defined range and correct the value if needed
            if value < lower_border:
                value = lower_border
            elif value > upper_border:
                value = upper_border

            # check if value lays within the upper or the lower range and calculate the membership
            if (value > lower_border) and (value < center):
                membership = (value-lower_border) * m
            elif value == center:
                membership = 1.0
            elif (value > center) and (value < upper_border) and (center != lower_border):
                membership = 1 - ((value - center) * m)
            elif (value > center) and (value < upper_border) and (center == lower_border):
                membership = 1 + ((value-center) * m)
            else:
                membership = 0.0

            return membership

        except (KeyError, TypeError) as exc:
            warnings.warn(f"{exc} found in calculating membership of {value} in function {function}, zero was assigned")
            return 0.0

    def _generate_memberships(self, value: float):

        # iterate over all membership functions and calculate the membership "likelihood"
        for function in list(self.category.keys()):
            membership = self._calculate_membership(function, value)
            yield function, membership

    def get_memberships(self, value: float, return_type="dict"):

        # ensure return_type is valid
        assert return_type in ["dict", "list"], "return type must be specified as dict or list"

        # create a return variable as dict or list
        return_structure = lambda x: dict() if x is "dict" else list()
        results = return_structure(return_type)

        # generate membership value for each function
        to_check = self._value_normalizer(value)
        for function, membership in self._generate_memberships(to_check):
            if return_type == "dict":
                results[function] = membership

            elif return_type == "list":
                results.append(membership)

        return results

    def get_visual(self):
        pass



