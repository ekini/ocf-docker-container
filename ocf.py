#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code is heavily based on inqbus.ocf.generic, see https://pypi.python.org/pypi/inqbus.ocf.generic

import os
import sys
import inspect

from xml.etree import ElementTree
import exits


class Parameter(dict):
    def __init__(self, longdesc, shortdesc, ocftype="string", required=False, unique=False, default=None):
        super(Parameter, self).__init__(longdesc=longdesc, shortdesc=shortdesc, ocftype=ocftype, required=required, unique=unique, default=default)


class Agent(object):
    allowed_methods = ["meta-data", "validate-all", "start", "stop", "monitor", "notify"]
    name = "agent"
    version = "1.0"
    longdesc = "Resource agent"
    shortdesc = "RA"
    params = {}
    timeout = 30
    meta_data_timeout = 5

    def not_implemented(self):
        raise exits.OCF_ERR_UNIMPLEMENTED("not implemented")

    def run(self, argv):
        if argv[1] in self.allowed_methods:
            func = getattr(self, argv[1].replace("-", "_"), self.not_implemented)
            func()
        else:
            raise exits.OCF_ERR_UNIMPLEMENTED("not implemented")

    def get_meta_data(self):
        """
        Derive a pacemaker conform xml description of the plugins services
        """
        params = self.params
        eResourceAgent = ElementTree.Element("resource-agent", {"name": self.name, "version": self.version})
        ElementTree.SubElement(eResourceAgent, "version").text = "1.0"

        ElementTree.SubElement(eResourceAgent, "longdesc", {"lang": "en"}).text = self.longdesc
        ElementTree.SubElement(eResourceAgent, "shortdesc", {"lang": "en"}).text = self.shortdesc

        eParameters = ElementTree.SubElement(eResourceAgent, "parameters")
        for param in self.params.keys():
            parameter = ElementTree.SubElement(eParameters, "parameter", {"name": param})
            ElementTree.SubElement(parameter, "longdesc", {"lang": "en"}).text = params[param]["longdesc"]
            ElementTree.SubElement(parameter, "shortdesc", {"lang": "en"}).text = params[param]["shortdesc"]
            if params[param]["required"]:
                parameter.set("required", "1")
            if params[param]["unique"]:
                parameter.set("unique", "1")

            eContent = ElementTree.SubElement(parameter, "content", {"type": params[param]["ocftype"]})
            if params[param]["default"]:
                eContent.set("default", params[param]["default"])

        eActions = ElementTree.SubElement(eResourceAgent, "actions")
        implemented_actions = set([name.replace("_", "-") for name, method in inspect.getmembers(self, predicate=inspect.ismethod)]) & set(self.allowed_methods)
        for action in implemented_actions:
            eAction = ElementTree.SubElement(eActions, "action", {"name": action, "timeout": str(getattr(self, action.replace("-", "_") + "_timeout", self.timeout))})

        return eResourceAgent

    def meta_data(self):
        xml_meta_data = self.get_meta_data()
        sys.stdout.write("""<?xml version="1.0"?>
<!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
""")
        ElementTree.ElementTree(xml_meta_data).write(sys.stdout)
        sys.stdout.write("\n")

    def monitor(self):
        raise exits.OCF_NOT_RUNNING("monitor: not running")

    def _get_loader(self, name):
        return getattr(self, "_param_" + name + "_loader", None)

    def validate_all(self):
        # check required params
        for param in (param for param in self.params if (self.params[param]["required"] and not self.params[param]["default"])):
            if not self.param(param):
                raise exits.OCF_ERR_ARGS("Argument '%s' is required but not provided" % param)
        # try to load all params
        for param in self.params.keys():
            custom_loader = self._get_loader(param)
            if custom_loader:
                try:
                    self.param(param)
                except Exception as e:
                    raise exits.OCF_ERR_ARGS("Argument '%s' is wrong (%s)" % (param, str(e)))

    def param(self, name):
        env = os.environ
        custom_loader = self._get_loader(name)
        if custom_loader:
            return custom_loader(env.get("OCF_RESKEY_%s" % name, self.params[name]["default"]))
        else:
            return env.get("OCF_RESKEY_%s" % name, self.params[name]["default"])

if __name__ == "__main__":
    pass
