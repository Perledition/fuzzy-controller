# import standard modules
import warnings

# import third party modules

# import project related modules
# from matplotlib import pyplot as plt


# assumes static gradients / slope
# TODO: Documentation
# TODO: function creator
# TODO: get visuals
class MembershipValidator:

    def __init__(self, category: dict):
        self.category = category
        self.slopes = self._get_slopes()

    def _get_slopes(self):

        # set up an empty dict as return value
        slopes = dict()

        # iterate over each member in the given category to define the slope
        for function, values in self.category.items():
            try:

                # access the values from the category
                min_value = values["lower_end"]
                max_value = values["center"]
                upper_min_value = values["upper_end"]

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

    def _calculate_membership(self, function, value):
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
            elif (value > center) and (value < upper_border):
                membership = 1 - ((value - center) * m)
            else:
                membership = 0.0

            return membership

        except (KeyError, TypeError) as exc:
            warnings.warn(f"{exc} found in calculating membership of {value} in function {function}, zero was assigned")
            return 0.0

    def _generate_memberships(self, value):

        # iterate over all membership functions and calculate the membership "likelihood"
        for function in list(self.category.keys()):
            membership = self._calculate_membership(function, value)
            yield function, membership

    def get_memberships(self, value, return_type="dict"):

        # ensure return_type is valid
        assert return_type in ["dict", "list"], "return type must be specified as dict or list"

        # create a return variable as dict or list
        return_structure = lambda x: dict() if x is "dict" else list()
        results = return_structure(return_type)

        # generate membership value for each function
        for function, membership in self._generate_memberships(value):
            if return_type == "dict":
                results[function] = membership

            elif return_type == "list":
                results.append(membership)

        return results

    def get_visual(self):
        pass


# test
category = {
    "very_low": {"lower_end": 0, "center": 0, "upper_end": 50},
    "low": {"lower_end": 0, "center": 50, "upper_end": 100},
    "medium": {"lower_end": 50, "center": 100, "upper_end": 150},
    "high": {"lower_end": 100, "center": 150, "upper_end": 200},
    "very_high": {"lower_end": 150, "center": 200, "upper_end": 200}
}

mv = MembershipValidator(category)
print(mv.get_memberships(90, return_type="list"))
