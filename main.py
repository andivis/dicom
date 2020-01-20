import sys
import os

if os.path.isdir('library'):
    sys.path.insert(0, os.getcwd() + '/library')

import logging
import re
import random
import json

# pip packages
import lxml.html as lh

import helpers

from helpers import get
from website import Website

class Dicom:
    def getInformation(self):
        for self.ciodIndex, ciod in enumerate(self.ciods):
            try:
                newItems = self.getCiod(self.ciods[ciod])
                self.output(newItems)
            except Exception as e:
                helpers.handleException(e)

    def getCiod(self, ciod):
        results = []

        ciodId = get(ciod, 'id')

        found = False

        self.moduleIndex = 0

        # get the things it links to
        for linkToModule in self.ciodToModules:
            if get(linkToModule, 'ciod') == ciodId:
                logging.info(f'CIOD: {self.ciodIndex + 1} of {len(self.ciods)}: {ciodId}. Module: {self.moduleIndex + 1}: {get(linkToModule, "module")}.')

                self.moduleIndex += 1

                newItems = self.getModule(ciod, linkToModule)
                
                results += newItems

                found = True
            # reached end of possible results
            elif found:
                break

        return results

    def getModule(self, ciod, linkToModule):
        results = []

        moduleId = get(linkToModule, 'module')

        # get the main object
        module = get(self.modules, moduleId)
        
        found = False

        # get the things it links to
        for linkToAttribute in self.moduleToAttributes:
            if get(linkToAttribute, 'module') == moduleId:
                self.outputUrl(ciod, linkToAttribute)

                newItem = self.getAttribute(ciod, module, linkToAttribute)

                if newItem:
                    results.append(newItem)
                
                found = True
            # reached end of possible results
            elif found:
                break

        return results

    def getAttribute(self, ciod, module, linkToAttribute):
        result = {
            'CIOD': get(ciod, 'name'),            
            'module': get(module, 'name')
        }

        tag = get(linkToAttribute, 'tag')

        # get the main object
        tag = tag.replace(',', '')
        tag = tag.replace('(', '')
        tag = tag.replace(')', '')
        tag = tag.lower()

        attribute = get(self.attributes, tag)

        if not attribute:
            return {}

        # the keys we want and what name to use for the output
        keys = {
            'tag_number': 'tag',
            'tag_keyword': 'keyword',
            'tag_value_multiplicity': 'valueMultiplicity',
            'tag_value_representation': 'valueRepresentation'
        }

        for key in keys:
            result[key] = get(attribute, keys[key])

            # add the name
            if key == 'tag_value_representation':
                result[key] = f'{get(self.valueRepresentations, result[key])} ({result[key]})'                
            elif key == 'tag_keyword':

                result[key] = self.getKeywordString(linkToAttribute)
                
                # to keep the right order of columns in the output file
                # add the name            
                type = get(linkToAttribute, 'type')
                result['tag_type'] = f'{get(self.types, type)} ({type})'

        website = Website()
        html = get(linkToAttribute, 'description')
        plainText = website.getXpath(html, ".", True)
        plainText = plainText.strip()

        result['tag_description'] = plainText
        result['tag_description_code_dict'] = self.getCodeDictionary(ciod, module, linkToAttribute, attribute)

        return result

    def getKeywordString(self, linkToAttribute):
        result = 'ds.'

        moduleId = get(linkToAttribute, 'module')
        
        path = get(linkToAttribute, 'path')
        path = path.replace(moduleId + ':', '')

        parts = path.split(':')

        newParts = []

        for i, part in enumerate(parts):
            attribute = get(self.attributes, part)

            if not attribute:
                continue

            newPart = get(attribute, 'keyword')

            newParts.append(newPart)

        result += '[0].'.join(newParts)

        return result

    def getCodeDictionary(self, ciod, module, linkToAttribute, attribute):
        result = {}
        
        for externalReference in get(linkToAttribute, 'externalReferences'):
            referenceUrl = get(externalReference, 'sourceUrl')

            reference = get(self.references, referenceUrl)

            # parse the html
            website = Website()

            # get the terms tables        
            elements = website.getXpath(reference, "//dl[../p/strong/text() = 'Defined Terms:' or ../p/strong/text() = 'Enumerated Values:']")

            for element in elements:
                terms = website.getXpathInElement(element, "//dt")
                definitions = website.getXpathInElement(element, "//dd")

                # pairs of dt and dd tags
                for i, term in enumerate(terms):
                    if i >= len(definitions):
                        break

                    term = term.text_content().strip()
                    definition = definitions[i].text_content().strip()
                    
                    result[term] = definition

        if str(result) == "{'DCMR': 'DICOM Content Mapping Resource', 'SDM': 'SNOMED DICOM Microglossary (Retired)'}":
            result = ''

        return result

    def output(self, newItems):
        if not newItems:
            return

        fields = []

        for key in newItems[0]:
            fields.append(key)

        if not os.path.exists(self.outputFile):
            helpers.toFile(','.join(fields), self.outputFile)

        logging.info(f'Writing results {self.outputFile}')
        
        for i, item in enumerate(newItems):

            line = []

            for key in fields:
                line.append(get(item, key))

            helpers.appendCsvFile(line, self.outputFile)

    def outputUrl(self, ciod, linkToAttribute):
        ciodId = get(ciod, 'id')
        
        path = get(linkToAttribute, 'path')
        path = path.replace(':', '/')

        url = f'https://dicom.innolitics.com/ciods/{ciodId}/{path}'

        helpers.appendToFile(url, self.urlListFile)

    def getJsonFile(self, fileName):
        if not '/' in fileName:
            fileName = os.path.join(self.options['inputDirectory'], fileName)

        file = helpers.getFile(fileName)
        
        return json.loads(file)

    def __init__(self, options):
        self.options = options

        # top level
        self.ciods = self.getJsonFile('ciods.json')

        # link to second level
        self.ciodToModules = self.getJsonFile('ciod_to_modules.json')

        # second level
        self.modules = self.getJsonFile('modules.json')

        # link to third level
        self.moduleToAttributes = self.getJsonFile('module_to_attributes.json')
        
        # link to third level
        self.attributes = self.getJsonFile('attributes.json')

        # detailed description for an attribute
        self.references = self.getJsonFile('references.json')

        self.types = self.getJsonFile('resources/tag-types.json')

        self.valueRepresentations = self.getJsonFile('resources/tag-value-representations.json')

        self.outputFile = os.path.join('output', 'results.csv')
        self.urlListFile = os.path.join('output', 'urls.csv')        
        
        helpers.makeDirectory('output')
        
        helpers.removeFile(self.outputFile)
        helpers.removeFile(self.urlListFile)

class Main:
    def run(self):
        self.dicom.getInformation()
        self.cleanUp()

    def cleanUp(self):
        logging.info('Done')

    def __init__(self):
        helpers.setUpLogging()
        
        logging.info('Starting')

        self.options = {
            'inputDirectory': 'input'
        }

        # read the options file
        helpers.setOptions('options.ini', self.options)

        self.dicom = Dicom(self.options)

main = Main()
main.run()
