from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from tethys_sdk.gizmos import TableView
from tethys_sdk.gizmos import SelectInput
from tethys_sdk.gizmos import Button

from math import pi
from math import log10

from .model import SessionMaker, FlowDurationData


@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    pipeRoughness = {
        'Riveted Steel': 0.0009, 'Concrete': 0.0003, 'Wood Stave': 0.00018,
        'Cast Iron': 0.00026, 'Galvanized Iron': 0.00015, 'Commercial Steel': 0.000045,
        'Drawn Turbing': 0.0000015, 'Plastic': 0, 'Glass': 0
    }

    materialSelectInput = []
    for v, k in pipeRoughness.iteritems():
        materialSelectInput.append((v, float(k)))

    materialDropdown = SelectInput(display_text='Select Pipe Material',
                                   name='materialDropdown',
                                   multiple=False,
                                   options=materialSelectInput,
                                   initial=['Commercial Steel'],
                                   original=False)

    input_tbv = TableView(column_names=('Input', 'Value', 'Units'),
                          rows=[('Length', 739, '[ M ]'),
                                ('Diameter', 1.5, '[ M ]'),
                                ('Flow', 9.208, unicode('[ M' + u'\u00b3' + '/s ]')),
                                ('Elevation Head', 135, '[ M ]')],
                          hover=True,
                          striped=True,
                          bordered=False,
                          condensed=True,
                          editable_columns=(False, 'valueInput'),
                          row_ids=[21, 25, 31])

    submit_button = Button(
                    display_text='Calculate Capacity',
                    name='submit',
                    attributes='form=parameters-form',
                    submit=True
    )

    context = {
        'materialDropdown': materialDropdown,
        'input_tbv': input_tbv,
        'submit_button': submit_button
    }

    return render(request, 'hydropower/home.html', context)


def calculate_capacity(request):
    """
    Controller for the app home page.
    """

    pipeChacteristics = {}
    if request.POST and 'submit' in request.POST:
        print request.POST
        pipeMaterial = float(request.POST['materialDropdown'])
        diameter = float(request.POST['valueInput25'])
        flow = float(request.POST['valueInput31'])
        density = 998
        kinViscosity = 0.00000112
        turbineEfficiency = 0.53
        RDRatio = pipeMaterial / diameter
        XSArea = pi * (diameter/2.0)**2
        aveVelocity = flow/XSArea
        reynolsN = (aveVelocity * diameter) / kinViscosity
        flowType = 'Laminar' if reynolsN < 2000 else 'Turbulent'
        massFR = density * flow
        frictionFactor = 64 / reynolsN if flowType == 'Laminar' else (1 / (-1.8 * log10((RDRatio / 3.7)**1.11 + (6.9 / reynolsN))))**2


        pipeChacteristics.update({
            'Density': density, 'Kinematic Viscosity': kinViscosity, 'Roughness/Diameter': RDRatio,
            'Cross Sectional Area': XSArea, 'Average Velocity': aveVelocity,
            'Reynolds Number': reynolsN, 'Flow Type': flowType, 'Mass Flow Rate': massFR,
            'Friction Factor': frictionFactor, 'Turbine Efficiency': turbineEfficiency
        })

    print pipeChacteristics

    # session = SessionMaker()
    #
    # flow_data = session.query(FlowDurationData).all()
    #
    # #flow_data = session.query(FlowDurationData).filter(
    # #    FlowDurationData.site == "'" + siteVar + "'")
    # #)
    # for row in flow_data:
    #     a = row.flow
    #     print a
    #
    # session.close()

    context = {}

    return render(request, 'hydropower/capacity.html', context)