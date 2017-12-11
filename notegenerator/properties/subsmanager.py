from notegenerator.properties import PropertyFactory

class SubsManager(object):
    """ Helper class to manage our substitutions file. Able to open subs file
    and create appropriate property classes.  Will manage making calls to
    generate choices from list of the property values and will handle resetting
    properties that are static on single notes"""

    def __init__(self, subs):
        """

        :param subs: dict of substitutions
        """
        self.props = self._buildproperties(subs)
        self.staticProps = [p for p in self.props if p.static]

    def _buildproperties(self, subs):
        """

        :type subs: dictionary object with key as name of the property and
            value as parameters (i.e. possible values, static, type, etc)
        """
        fac = PropertyFactory()
        props = []
        for k, v in subs.items():
            p = fac.makeProperty(k, **v)
            props.append(p)
        return props

    def _reset(self):
        """
            Resets the properties that are static
        """
        for s in self.staticProps:
            s.hasChosen = False

    @property
    def mappings(self):
        """
        :return: dictionary of template variables and selected values
        """
        self._reset()
        d = {}
        for p in self.props:
            d[p.name] = p.chooseVal()
        # d = {s.name: s.chooseVal() for s in self.props}
        return d
