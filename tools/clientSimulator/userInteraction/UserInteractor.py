# Copyright (c) 2014-2015, Intel Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from criterion.InclusiveCriterion import InclusiveCriterion
from testGenerator.TestLauncher import TestLauncher
from userInteraction.DynamicCallHelper import DynamicCallHelper


class UserInteractor:

    """
        Define all user interactions the program can have.

        Allows to run the interactive mode and dynamics menus.
    """

    def __init__(self, testLauncher, criterions):
        """
            Init function of user interactor

            :param testLauncher: object which allows to run tests
            :type testLauncher: TestLauncher
        """

        self.__testLauncher = testLauncher
        self.__criterions = criterions

    @classmethod
    def getMenu(cls, options):
        """
            Dynamic Menu Generator :

            :param options: dictionnary containing, the invite string
            and the function to launch
            :type options: dict
        """

        testQuit = True

        options[len(options)] = \
            ("Go Back", lambda: False)
        while testQuit:
            print("\nPlease Make a choice : ")
            for numMenu, (sentenceMenu, fonc) in sorted(options.items()):
                print("\t{}. {}".format(numMenu, sentenceMenu))

            choice = input("Your Choice : ")

            try:
                testQuit = options[int(choice)][1]()
            except (KeyError, ValueError) as e:
                print("Invalid Choice : {}".format(e))

    def launchInteractiveMode(self):
        """
            Interactive Mode : Set up a menu which allow
            users to personnalize a Test and to Launch it
        """
        optionsMenu = {
            0: ("Edit Vector", self.__editVector),
            1: ("Apply Configuration", self.__applyConfiguration),
            2: ("Launch Script", self.__launchScript)
        }

        UserInteractor.getMenu(optionsMenu)

    def __applyConfiguration(self):
        """
            Apply the configuration described in the
            current criterions state.
        """

        self.__testLauncher.executeTestVector(self.__criterions)

        return True

    def __launchScript(self):
        """
            Display the menu which let the user choose an available
            script to run.
        """

        optionScript = {
            num: ("{} scripts".format(script),
                  DynamicCallHelper(self.__testLauncher.executeScript, script))
            for num, script in enumerate(self.__testLauncher.scripts)
        }

        UserInteractor.getMenu(optionScript)

        return True

    def __setCriterion(self, criterion, value):
        criterion.currentValue = value

    def __removeCriterionValue(self, criterion, value):
        criterion.removeValue(value)

    def __editCriterion(self, criterion):
        """
            Allow to change the value of a criterion through a menu.

            :param criterion: the criterion to edit
            :type criterion: Criterion
        """

        optionEditCriterion = {}
        for possibleValue in [x for x in criterion.allowedValues()
                              if not x in criterion.currentValue
                              and not x == criterion.noValue]:
            optionEditCriterion[
                len(optionEditCriterion)] = (
                "Set {}".format(possibleValue),
                DynamicCallHelper(
                    self.__setCriterion,
                    criterion,
                    possibleValue))

        if InclusiveCriterion in criterion.__class__.__bases__:
            # Inclusive criterion : display unset value (default when empty)
            for possibleValue in criterion.currentValue:
                optionEditCriterion[
                    len(optionEditCriterion)] = (
                    "Unset {}".format(possibleValue),
                    DynamicCallHelper(
                        self.__removeCriterionValue,
                        criterion,
                        possibleValue))
        else:
            # Exclusive criterion : display default value
            optionEditCriterion[
                len(optionEditCriterion)] = (
                "Set Default",
                DynamicCallHelper(
                    self.__setCriterion,
                    criterion,
                    criterion.noValue))

        UserInteractor.getMenu(optionEditCriterion)

        return True

    def __editVector(self):
        """
            Allow to change the value of several criterions through a menu.
        """

        optionEdit = {
            num: ("Edit {}".format(cri.__class__.__name__),
                  DynamicCallHelper(self.__editCriterion, cri))
            for num, cri in enumerate(self.__criterions)
        }

        UserInteractor.getMenu(optionEdit)

        return True
