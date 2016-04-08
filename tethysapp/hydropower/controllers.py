from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404

from tethys_sdk.gizmos import TableView, TextInput, SelectInput, Button, LinePlot

from math import pi
from math import log10

from .model import SessionMaker, FlowDurationData


@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    session = SessionMaker()
    sitesQuery = session.query(FlowDurationData.site).distinct()

    sitesList = []
    for site in sitesQuery:
        sitesList.append((str(site[0]).replace('_', ' '), str(site[0])))

    siteDropdown = SelectInput(display_text='Select Site',
                               name='siteDropdown',
                               multiple=False,
                               options=sitesList,
                               initial=['Salto de Jimenoa'],
                               original=False)

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
                                ('Elevation Head', 135, '[ M ]')],
                          hover=True,
                          striped=True,
                          bordered=True,
                          condensed=True,
                          editable_columns=(False, 'valueInput'),
                          row_ids=[0, 1, 2])

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
                                ('Rounded (Turb)', 0)],
                          hover=True,
                          striped=True,
                          bordered=True,
                          condensed=True,
                          editable_columns=(False, 'ECountInput'),
                          row_ids=[0, 1, 2])

    gradContraction_tbv = TableView(column_names=('Contraction', 'Count'),
                                    rows=[('30 Degree', 0),
                                          ('45 Degree', 0),
                                          ('60 Degree', 0)],
                                    hover=True,
                                    striped=True,
                                    bordered=True,
                                    condensed=True,
                                    editable_columns=(False, 'GCountInput'),
                                    row_ids=[0, 1, 2])

    submit_button = Button(
                    display_text='Calculate Capacity',
                    name='submit',
                    attributes='form=parameters-form',
                    submit=True
    )

    session.close()

    context = {
        'siteDropdown': siteDropdown,
        'materialDropdown': materialDropdown,
        'text_input': text_input,
        'input_tbv': input_tbv,
        'bends_tbv': bends_tbv,
        'inlets_tbv': inlets_tbv,
        'exits_tbv': exits_tbv,
        'gradContraction_tbv': gradContraction_tbv,
        'submit_button': submit_button
    }

    return render(request, 'hydropower/home.html', context)


def calculate_capacity(request):
    """
    Controller for the app home page.
    """

    if request.POST and 'submit' in request.POST:
        session = SessionMaker()

        capacityList = []
        siteVar = request.POST['siteDropdown']
        flow_data = session.query(FlowDurationData).filter(FlowDurationData.site == siteVar)

        for row in flow_data:
            flow = row.flow

            pipeMaterial = float(request.POST['materialDropdown'])
            length = float(request.POST['valueInput0'])
            diameter = float(request.POST['valueInput1'])
            elevHead = float(request.POST['valueInput2'])

            density = 998
            kinViscosity = 0.00000112
            turbineEfficiency = 0.53
            gravity = 9.81
            RDRatio = pipeMaterial / diameter
            XSArea = pi * (diameter/2.0)**2
            aveVelocity = flow/XSArea
            reynolsN = (aveVelocity * diameter) / kinViscosity
            flowType = 'Laminar' if reynolsN < 2000 else 'Turbulent'
            massFR = density * flow
            frictionFactor = 64 / reynolsN if flowType == 'Laminar' else (1 / (-1.8 * log10((RDRatio / 3.7)**1.11 + (6.9 / reynolsN))))**2

            smooth90F = 0.3 * float(request.POST['BCountInput0'])
            smooth90T = 0.9 * float(request.POST['BCountInput1'])
            miter90 = 1.1 * float(request.POST['BCountInput2'])
            elbow45T = 0.4 * float(request.POST['BCountInput3'])
            unionT = 0.08 * float(request.POST['BCountInput4'])

            reentrant = 0.8 * float(request.POST['ICountInput0'])
            sharpeEdge = 0.5 * float(request.POST['ICountInput1'])
            wellRounded = 0.03 * float(request.POST['ICountInput2'])
            slightlyRounded = 0.12 * float(request.POST['ICountInput3'])

            reentrantT = 1.05 * float(request.POST['ECountInput0'])
            sharpeEdgeT = 1.05 * float(request.POST['ECountInput1'])
            roundedT = 1.05 * float(request.POST['ECountInput2'])

            degree30 = 0.02 * float(request.POST['GCountInput0'])
            degree45 = 0.04 * float(request.POST['GCountInput1'])
            degree60 = 0.07 * float(request.POST['GCountInput2'])

            totalK = smooth90F + smooth90T + miter90 + elbow45T + unionT + reentrant + sharpeEdge + wellRounded +\
            slightlyRounded + reentrantT + sharpeEdgeT + roundedT + degree30 + degree45 + degree60

            minorLosses = totalK * (aveVelocity**2 / (2 * gravity))
            frictionLoss = (frictionFactor * length * aveVelocity**2) / (diameter * 2 * gravity)

            totalHeadLoss = minorLosses + frictionLoss
            turbineHead = elevHead - totalHeadLoss

            capacity = (turbineHead * density * flow * turbineEfficiency * gravity) / 1000
            capacityList.append((int(row.percent), round(float(flow), 2), round(float(capacity), 2)))

        sortedCapList = sorted(capacityList, key=lambda x: x[0])

        plotData = []
        for i in sortedCapList:
            value = list(i)
            value.remove(value[0])
            plotData.append(value)

        capacity_tbv = TableView(column_names=('Percent (%)', unicode('Flow (M' + u'\u00b2' + ' / S)'),
                                               'Capacity (kW)'),
                                 rows=sortedCapList,
                                 hover=True,
                                 striped=True,
                                 bordered=True,
                                 condensed=True,
                                 editable_columns=(False, False, False),
                                 row_ids=[range(0, len(sortedCapList))])

        line_plot_view = LinePlot(height='100%', width='100%', engine='highcharts',
                                  title='Flow capacity Curve', subtitle=siteVar.replace('_', ' '),
                                  spline=True, x_axis_title= 'Q', x_axis_units='M^2/S',
                                  y_axis_title='Capacity', y_axis_units='kW', series=[{'name': 'Capacity',
                                                                                       'color': '#277554',
                                                                                       'marker': {'enabled': False},
                                                                                       'data': plotData
                                                                                       }]
                                  )

        session.close()

        context = {
            'capacity_tbv': capacity_tbv,
            'line_plot_view': line_plot_view
        }

    else:
        raise Http404("No request was submitted.")

    return render(request, 'hydropower/capacity.html', context)