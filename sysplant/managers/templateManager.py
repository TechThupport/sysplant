# -*- coding:utf-8 -*-
import json

from typing import Union

import importlib.resources as pkg_resources

from sysplant import data as pkg_data
from sysplant import templates as pkg_templates
from sysplant.templates import iterators as pkg_iterators
from sysplant.templates import resolvers as pkg_resolvers
from sysplant.templates import stubs as pkg_stubs

from sysplant.constants.sysplantConstants import SysPlantConstants
from sysplant.abstracts.abstractFactory import AbstractFactory
from sysplant.managers.nimGenerator import NIMGenerator


class TemplateManager(AbstractFactory):
    """Main class responsible for template handling: tag replacement or erase with content generated by __coder bot

    Args:
        AbstractFactory (_type_): _description_
    """

    def __init__(
        self, arch: str = "x64", language: str = "nim", syscall: str = "syscall"
    ) -> None:
        super().__init__()

        # Define language template
        if arch not in ["x86", "x64", "wow"]:
            raise NotImplementedError("Sorry architecture not implemented yet")
        if language not in ["nim"]:
            raise NotImplementedError("Sorry language not supported ... yet ?!")
        if syscall not in ["syscall", "sysenter", "int 0x2h"]:
            raise NotImplementedError(
                "Sorry syscall instruction not supported ... yet ?!"
            )

        self.__lang = language
        self.__arch = arch
        self.__syscall = syscall

        # Set coder bot
        if self.__lang == "nim":
            self.__coder = NIMGenerator()

        try:
            # Alaways load prototypes & typedefinitions
            self.__load_prototypes()
        except Exception as err:
            raise SystemError(f"Unable to load prototypes: {err}")

        try:
            # Always load initial template
            self.data = self.__load_template(pkg_templates, f"base.{self.__lang}")
        except Exception as err:
            raise SystemError(f"Unable to load base template: {err}")

        # Initialize seed
        self.__seed = self.generate_random_seed()

    def __str__(self) -> str:
        return self.data

    def __load_prototypes(self) -> None:
        # Load supported functions prototypes
        data = self.__load_template(pkg_data, "prototypes.json")
        self.__prototypes = json.loads(data)

    def __load_template(self, pkg_module: str, name: str) -> str:
        if name is None:
            raise ValueError("Template name can not be null")

        # Check only extension dot is set
        if not name.replace(".", "", 1).replace(f"_{self.__arch}", "", 1).isalpha():
            raise ValueError("Invalid template name")

        # Adapt module based on what to load
        raw = pkg_resources.open_text(pkg_module, name)
        return raw.read()

    def load_stub(self, name) -> str:
        try:
            # Load initial stub template
            self.data = self.__load_template(pkg_stubs, f"{name}.{self.__lang}")
        except Exception as err:
            raise SystemError(f"Unable to load {name} stub: {err}")

        return self.data

    def list_supported_syscalls(self) -> list:
        return self.__prototypes.keys()

    def list_common_syscalls(self) -> list:
        return SysPlantConstants.COMMON_SYSCALLS

    def list_donut_syscalls(self) -> list:
        return SysPlantConstants.DONUT_SYSCALLS

    def set_debug(self) -> None:
        if self.logger.isDebug():
            # Generate debug constant based on log level condition
            debug_const = self.__coder.generate_debug(True)
            self.replace_tag("SPT_DEBUG", debug_const)
        else:
            self.remove_tag("SPT_DEBUG")

    def set_seed(self, seed: int = 0) -> str:
        if seed != 0:
            self.__seed = seed

        # Set SEED declaration
        seed_code = self.__coder.generate_seed(self.__seed)
        self.replace_tag("SPT_SEED", seed_code)

        return self.data

    def set_iterator(self, name: str) -> str:
        # Get iterator template from package
        data = self.__load_template(pkg_iterators, f"{name}.{self.__lang}")
        self.replace_tag("SPT_ITERATOR", data)

        return self.data

    def set_resolver(self, name: str) -> str:
        # Get resolver template from package
        data = self.__load_template(pkg_resolvers, f"{name}.{self.__lang}")
        self.replace_tag("SPT_RESOLVER", data)

        return self.data

    def set_caller(self, name: str, resolver: str) -> str:
        # Get caller function from package
        data = self.__load_template(pkg_stubs, f"{name}_{self.__arch}.{self.__lang}")
        self.replace_tag("SPT_CALLER", data)

        # Replace resolver functions in stub
        func_resolver = (
            "SPT_GetRandomSyscallAddress"
            if resolver == "random"
            else "SPT_GetSyscallAddress"
        )

        # Adapt caller with proper options
        self.replace_tag("FUNCTION_RESOLVE", func_resolver)
        self.replace_tag("SYSCALL_INT", self.__syscall)

        # Set debug interruption on debug state
        if self.logger.isDebug():
            self.replace_tag("DEBUG_INT", "int 3")
        else:
            self.remove_tag("DEBUG_INT")

        return self.data

    def generate_stubs(self, names: list) -> str:
        self.logger.debug(
            f"\t. Hooking selected functions: {','.join(names)}", stripped=True
        )
        stubs_code = ""

        # Resolve all headers for functions to hook
        for n in names:
            params = self.__prototypes.get(n)
            # Avoid unsupported functions
            if params is None:
                raise NotImplementedError(f"Unsupported syscall {n}")

            # Calculate function hash
            fhash = self.get_function_hash(self.__seed, n)

            # Generate stub
            stubs_code += self.__coder.generate_stub(n, params, fhash)

        # Replace syscall stubs
        self.replace_tag("SPT_STUBS", stubs_code)

        return self.data

    def generate_definitions(self) -> str:
        code = self.__coder.generate_definitions()
        self.replace_tag("TYPE_DEFINITIONS", code)

        return self.data

    def scramble(self) -> str:
        generated = set()
        for name in SysPlantConstants.INTERNAL_FUNCTIONS:
            randomized = self.generate_random_string(SysPlantConstants.RANDOM_WORD_SIZE)
            # Avoid function collisions
            while randomized in generated:
                randomized = self.generate_random_string(
                    SysPlantConstants.RANDOM_WORD_SIZE
                )

            # Store already set function name
            generated.add(randomized)

            # Replace name in code
            self.data = self.data.replace(name, randomized)

        return self.data
