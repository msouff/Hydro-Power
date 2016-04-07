from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from tethys_sdk.gizmos import TableView, TextInput, SelectInput, Button

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

    text_input = TextInput(display_text='Enter Water Temperature',
                           name='inputAmount',
                           placeholder='20.00',
                           append=unicode(u'\u00b0' + 'C'))

    input_tbv = TableView(column_names=('Input', 'Value', 'Units'),
                          rows=[('Length', 739, '[ M ]'),
                                ('Diameter', 1.5, '[ M ]'),
                                ('Flow', 9.208, unicode('[ M' + u'\u00b3' + '/s ]')),
                                ('Elevation Head', 135, '[ M ]')],
                          hover=True,
                          striped=True,
                          bordered=True,
                          condensed=True,
                          editable_columns=(False, 'valueInput'),
                          row_ids=[0 , 1, 2, 3])

    bends_tbv = TableView(column_names=('Bends', 'Count'),
                          rows=[('90 Smooth (Flanged)', 0),
                                ('90 Smooth (Threaded)', 0),
                                ('90 Miter', 0),
                                ('45 Threaded Elbow', 1),
                                ('Threaded Union', 121)],
                          hover=True,
                          striped=True,
                          bordered=True,
                          condensed=True,
                          editable_columns=(False, 'BCountInput'),
                          row_ids=[0, 1, 2, 3, 4])

    inlets_tbv = TableView(column_names=('Inlets', 'Count'),
                          rows=[('Reentrant', 0),
                                ('Sharp Edge', 1),
                                ('Well-Rounded', 0),
                                ('Slightly-Rounded', 0)],
                          hover=True,
                          striped=True,
                          bordered=True,
                          condensed=True,
                          editable_columns=(False, 'ICountInput'),
                          row_ids=[0, 1, 2, 3])

    exits_tbv = TableView(column_names=('Exit', 'Count'),
                          rows=[('Reentrant (Turb)', 0),
                                ('Sharp Edge (Turb)', 1),
                                ('Rounded (Turb)', 0),
                                ('Gradual Contraction', 0),
                                ('30 Degree', 0),
                                ('45 Degree', 0),
                                ('60 Degree', 0)],
                          hover=True,
                          striped=True,
                          bordered=True,
                          condensed=True,
                          editable_columns=(False, 'ECountInput'),
                          row_ids=[0, 1, 2, 3, 4, 5, 6])

    submit_button = Button(
                    display_text='Calculate Capacity',
                    name='submit',
                    attributes='form=parameters-form',
                    submit=True
    )

    context = {
        'materialDropdown': materialDropdown,
        'text_input': text_input,
        'input_tbv': input_tbv,
        'bends_tbv': bends_tbv,
        'inlets_tbv': inlets_tbv,
        'exits_tbv': exits_tbv,
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
        diameter = float(request.POST['valueInput1'])
        flow = float(request.POST['valueInput2'])
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