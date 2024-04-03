#Author- bwees
#Description- Set Part Mass

import adsk.core, adsk.fusion, adsk.cam, traceback

commandId = 'SetPartMass'
commandName = 'Set Part Mass'
commandDescription = 'Apply a weight to selected bodies or occurrences'

app = None
ui = None

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
materialsMap = {}

app = adsk.core.Application.get()
if app:
    ui  = app.userInterface
    
class WeightCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = ApplyWeightHandler()
            cmd.execute.add(onExecute)
            onDestroy = WeightCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            onInputChanged = WeightNewSelectionHandler()
            cmd.inputChanged.add(onInputChanged)
            onValidateInputs = WeighValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            # keep the handler referenced beyond this function
            handlers.append(onValidateInputs)
            handlers.append(onExecute)
            handlers.append(onDestroy)
            handlers.append(onInputChanged)


            # Define the inputs.
            inputs = cmd.commandInputs
            
            global commandId
            selectionInput = inputs.addSelectionInput(commandId + '_selection', 'Select', 'Select bodies or occurrences')
            selectionInput.setSelectionLimits(1)
            selectionInput.selectionFilters = ['SolidBodies', 'Occurrences', 'RootComponents']

            string_value_input = inputs.addStringValueInput('material_name', 'Material Name', '')
            string_value_input.isPassword = False

            mat_name_warning_message = "Please enter a material name"
            mat_name_warning = inputs.addTextBoxCommandInput('mat_name_warning', 'Text Box', mat_name_warning_message, 1, True)
            mat_name_warning.isFullWidth = True

            text_box_message = "<b>Metric:</b> kg, g<br><b>Imperial:</b> lbmass, ouncemass"
            text_box_input = inputs.addTextBoxCommandInput('text_box_input', 'Text Box', text_box_message, 2, True)
            text_box_input.isFullWidth = True

            value_input = inputs.addValueInput(commandId + '_mass', 'Mass', 'g', adsk.core.ValueInput.createByString('1.00 g'))
            value_input.minimumValue = 0

            calculation_output_message = "Select a body or component to set the weight"
            calculation_output = inputs.addTextBoxCommandInput('calculation_output', 'Text Box', calculation_output_message, 4, True)
            calculation_output.isFullWidth = True

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    
def getVolumeOfSelection(selection):
    volume = 0
    for i in range(selection.selectionCount):
        volume += selection.selection(i).entity.getPhysicalProperties().volume
    return volume

def getMassOfSelection(selection):
    mass = 0
    for i in range(selection.selectionCount):
        mass += selection.selection(i).entity.getPhysicalProperties().mass
    return mass

def getSelectedEntities(selectionInput):
    entities = []
    for x in range(0, selectionInput.selectionCount):
        mySelection = selectionInput.selection(x)
        selectedObj = mySelection.entity
        if type(selectedObj) is adsk.fusion.BRepBody or type(selectedObj) is adsk.fusion.Component:
            entities.append(selectedObj)
        elif type(selectedObj) is adsk.fusion.Occurrence:
            entities.append(selectedObj.component)
    return entities

def applyMaterialToEntities(material, entities):
    for entity in entities:
        entity.material = material

def getMaterial(materialName):
    materialLibs = app.materialLibraries
    material = None
    for materialLib in materialLibs:
        materials = materialLib.materials
        try:
            material = materials.itemByName(materialName)
        except:
            pass
        if material:
            break
    return material

class WeightNewSelectionHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            changed_input = args.input
            inputs = args.input.parentCommand.commandInputs
            massInput: adsk.core.ValueCommandInput = inputs.itemById(commandId + '_mass')
            selection: adsk.core.SelectionCommandInput = inputs.itemById(commandId + '_selection')
            calculation_output: adsk.core.TextBoxCommandInput = inputs.itemById('calculation_output')
            mat_name_warning: adsk.core.TextBoxCommandInput = inputs.itemById('mat_name_warning')
            material_name: adsk.core.TextBoxCommandInput = inputs.itemById('material_name')

            volume = getVolumeOfSelection(selection)
            mass = massInput.value*1000
            try:
                density = mass / volume
                calculation_output.text = "Volume: {}\nCalculated Density: {}".format(str(round(volume, 3)) + " cm^3", str(round(density, 3)) + " g/cm^3")
            except ZeroDivisionError:
                calculation_output.text = "Select a body or component to set the weight"

            if material_name.value == "":
                mat_name_warning.formattedText = "<b>Please enter a material name</b>"
            elif app.activeProduct.materials.itemByName(material_name.value) is not None:
                mat_name_warning.formattedText = "<b>Material with name already exists!</b>"
            else:
                mat_name_warning.formattedText = ""

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class ApplyWeightHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs
            for input in inputs:
                if input.id == commandId + '_selection':
                    selection = input
                elif input.id == 'material_name':
                    material_name = input
                elif input.id == commandId + '_mass':
                    massInput = input

            entities = getSelectedEntities(selection)

            volume = getVolumeOfSelection(selection)
            mass = massInput.value*1000
            density = (mass / volume)*1000

            matLib = app.materialLibraries.itemByName('Fusion Material Library')
            existingMaterial = matLib.materials.itemByName('Steel')


            # Copy the existing material into 
            newMaterial = app.activeProduct.materials.addByCopy(existingMaterial, material_name.value)
            densityProp: adsk.core.FloatProperty = newMaterial.materialProperties.itemByName('Density')
            densityProp.value = density

            applyMaterialToEntities(newMaterial, entities)
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class WeighValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)

        mat_name = eventArgs.inputs.itemById("mat_name_warning")
        calculations = eventArgs.inputs.itemById("calculation_output")

        if not mat_name or not calculations:
            return

        if calculations.text != "Select a body or component to set the weight" and mat_name.text == "":
            # OK button enabled
            eventArgs.areInputsValid = True
        else:
            # OK button disabled
            eventArgs.areInputsValid = False

class WeightCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        cmdDef = ui.commandDefinitions.itemById(commandId)
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription) # no resource folder is specified, the default one will be used

        onCommandCreated = WeightCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)

        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
